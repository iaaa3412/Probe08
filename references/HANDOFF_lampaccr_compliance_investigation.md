# Handoff: lampaccr compliance/current investigation (Accretech, LAMP project)

Written 2026-08-25 for a fresh Claude Code session to pick up from. Everything
below is verified against real code/real hardware logs from this session
unless explicitly marked as a hypothesis or open question.

## Project orientation

- Repo: `c:\automationproject\labviewtest` (git, GitHub remote
  `https://github.com/iaaa3412/Probe08.git`, branch `master`).
- This is "ATA" (Atomica Test Application) - a Tkinter GUI driving
  Accretech and Electroglas wafer probers over GPIB.
- Data for this specific project ("LAMP") lives on
  `\\prober\M\ETL\proberautomation\LAMPATA\` (network share). The recipe file
  discussed here is `\\prober\M\ETL\proberautomation\LAMPATA\probe_cards\LaMP_HP_b.csv`.
- User is testing on the **Accretech** system, card `LaMP_HP_b`, recipe
  `lampaccr`. Confirmed by the user: **the probe needles are physically
  touching the wafer** (ruled out "no wafer loaded"/misalignment as the
  explanation for what follows).
- On Windows, invoking scripts against the `\\prober\...` UNC path via the
  Bash tool is unreliable (silent file-not-found even on valid paths).
  Writing a script to a file then running it via the **PowerShell tool**
  against the UNC path works reliably - use that pattern for anything
  touching the network share.

## Hardware / GPIB architecture (Accretech bench)

Five instruments, connected in `gui/app.py`'s `init_hardware()`:

| Role | Driver file | Class |
|---|---|---|
| Prober | `instruments/accretech_uf200r.py` | `AccretechUF200R` |
| SMU | `instruments/keithley_2636b.py` | `Keithley2636B` |
| DMM | `instruments/keysight_34461a.py` | `Keysight34461A` |
| Switch matrix | `instruments/keithley_707b.py` | `Keithley707B` |
| Wave gen | `instruments/keysight_33512b.py` | `Keysight33512B` |

All GPIB I/O goes through `instruments/gpib_base.py`'s `GPIBInstrument`
(`write()`/`query()` are thin PyVISA passthroughs, default timeout 3000 ms).

**SMU and switch matrix are both TSP (Lua-based Test Script Processor)
instruments, not SCPI.** Every `write()` is a literal Lua statement, every
`query()` is a `print(...)` Lua call whose return is parsed back.

### Keithley 2636B (SMU) - `instruments/keithley_2636b.py`

Two independent channels, `smua`/`smub`. Full driver, as of this session:

```python
class Keithley2636B(GPIBInstrument):
    def __init__(self):
        super().__init__('smu')
        self.reset()                      # smua.reset(); smub.reset() - once, at connect

    def reset(self):
        self.write("smua.reset()")
        self.write("smub.reset()")

    def set_voltage(self, channel, volts):
        self.write(f"{channel}.source.func = {channel}.OUTPUT_DCVOLTS")
        self.write(f"{channel}.source.levelv = {volts}")

    def turn_output_on(self, channel):
        self.write(f"{channel}.source.output = {channel}.OUTPUT_ON")

    def turn_output_off(self, channel):
        self.write(f"{channel}.source.output = {channel}.OUTPUT_OFF")

    def set_current(self, channel, amps):
        self.write(f"{channel}.source.func = {channel}.OUTPUT_DCAMPS")
        self.write(f"{channel}.source.leveli = {amps}")

    def set_current_limit(self, channel, amps):
        self.write(f"{channel}.source.limiti = {amps}")

    def get_current_limit(self, channel):        # added this session - real readback
        reading = self.query(f"print({channel}.source.limiti)")
        try:
            return float(reading)
        except Exception:
            return None

    def set_voltage_limit(self, channel, volts):
        self.write(f"{channel}.source.limitv = {volts}")

    def measure_current(self, channel):
        reading = self.query(f"print({channel}.measure.i())")
        try:
            return float(reading)
        except Exception:
            return 0.0

    def measure_voltage(self, channel):
        reading = self.query(f"print({channel}.measure.v())")
        try:
            return float(reading)
        except Exception:
            return 0.0

    def measure_resistance(self, channel):
        reading = self.query(f"print({channel}.measure.r())")
        try:
            return float(reading)
        except Exception:
            return 0.0

    def set_nplc(self, channel: str, nplc: float):
        self.write(f"{channel}.measure.nplc = {nplc}")

    def set_averages(self, channel: str, count: int):
        # REPEAT_AVG filter - one query returns an already-averaged value.
        # NOT verified against hardware per the original in-code note (written
        # before the 2636B was connected) - now IS on a connected bench, so
        # this is a candidate to actually verify if the investigation below
        # points at averaging.
        count = max(1, int(count))
        if count > 1:
            self.write(f"{channel}.measure.filter.count = {count}")
            self.write(f"{channel}.measure.filter.type = {channel}.FILTER_REPEAT_AVG")
            self.write(f"{channel}.measure.filter.enable = {channel}.FILTER_ON")
        else:
            self.write(f"{channel}.measure.filter.enable = {channel}.FILTER_OFF")

    def in_compliance(self, channel) -> bool:      # added this session - real query
        reading = self.query(f"print({channel}.source.compliance)")
        return str(reading).strip().lower() == "true"
```

Notes:
- **No `set_source_delay()` method exists on this driver at all** (unlike
  `instruments/keithley2400.py`, which has one for the Electroglas SMU).
  This means the recipe's `avg_delay` field is a no-op for this specific
  instrument. The Recipe tab's step editor already disables/zeroes the
  Avg Delay field specifically when `instrument == "SMU"` on the Accretech
  side for this reason (see `gui/recipe_panel.py`'s `_on_type_change`).
- `set_averages`/hardware averaging: a single `measure.i()` after
  `filter.count`/`filter.type=REPEAT_AVG`/`filter.enable=ON` internally
  averages N back-to-back readings and returns the mean from one query.

### Keithley 707B (switch matrix) - `instruments/keithley_707b.py`

```python
class Keithley707B(GPIBInstrument):
    def __init__(self):
        super().__init__('switch_matrix')

    def open_all(self):
        self.write("channel.open('allslots')")

    def close_channel(self, channel: str):
        self.write(f"channel.close('{channel}')")

    def close_crosspoint(self, row, column):
        self.write(f"channel.close('{row}{column}')")

    def open_crosspoint(self, row, column):
        self.write(f"channel.open('{row}{column}')")

    def read_crosspoint(self, crosspoint: str) -> bool:
        resp = self.query(f"print(channel.getstate('{crosspoint}'))")
        return str(resp).strip() == "1" if resp else False

    def query_state(self, channel_list: str) -> str:
        resp = self.query(f"print(channel.getstate('{channel_list}'))")
        return str(resp).strip() if resp else ""

    def query_mainframe_idn(self) -> str: ...   # localnode.model/serialno/revision
    def query_slot_info(self, slot: int) -> dict: ...   # per-slot card ID, row/col count
    def query_all_slots(self) -> dict: ...       # slots 1-4
```

**Crosspoint naming: `{slot}{row_letter}{column}`**, e.g. `"2A06"` = slot 2,
row A, column 6 (zero-padded to 2 digits, e.g. col 6 -> `06`). A recipe
step's `conn` field is a comma-separated list of these crosspoints, and
`_exec2_run_steps_once` in `gui/instrument_panel.py` closes every one of
them (`switch.close_channel(ch)`) before taking a reading, then opens them
again on the matching "open"-type step later in the recipe.

### Switch topology (row -> instrument/channel/polarity mapping) - `gui/switch_topology.py`

This is the **generic per-bench default** wiring convention, editable via a
Switch Settings panel and persisted to `switch_topology.yaml` in the active
working directory (`workdir.gui_system_dir()`):

```python
DEFAULT_TOPOLOGY = {
    "slots": [
        {"slot": "2", "cols": 12, "rows": ["A","B","C","D","E","F","G","H"]},
        {"slot": "4", "cols": 12, "rows": ["A","B","C","D","E","F","G","H"]},
    ],
    "row_roles": {
        "A": {"instrument": "SMU",  "channel": "A",   "polarity": "HI"},
        "B": {"instrument": "SMU",  "channel": "A",   "polarity": "LO"},
        "C": {"instrument": "SMU",  "channel": "B",   "polarity": "HI"},
        "D": {"instrument": "SMU",  "channel": "B",   "polarity": "LO"},
        "E": {"instrument": "DMM",  "channel": "",    "polarity": "LO"},
        "F": {"instrument": "DMM",  "channel": "",    "polarity": "HI"},
        "G": {"instrument": "WGEN", "channel": "CH1", "polarity": "HI"},
        "H": {"instrument": "WGEN", "channel": "CH2", "polarity": "HI"},
    },
}
```

`pin_channel(pin_no, row) -> f"{slot}{row}{col:02d}"` is the formula the
Recipe tab's "⚙ Compute Connection" button uses to turn a probe-card pin
number + role row into a crosspoint string. **IMPORTANT / UNRESOLVED: this
formula does NOT appear to explain `lampaccr`'s actual `hi`/`lo`/`conn`
values as recorded (see below) - flagged as an open question, do not
assume the generic topology mapping applies to this specific card without
checking further.**

## The `lampaccr` recipe - verbatim, as currently saved

Source: `\\prober\M\ETL\proberautomation\LAMPATA\probe_cards\LaMP_HP_b.csv`
(Accretech embeds a card's RECIPE/STEP rows directly in the card's own CSV -
no separate side file, unlike Electroglas which writes
`<card>.recipes.electroglas.csv`).

CSV header:
```
kind,recipe,pin,pad,net,seq,bench,minor_moves,shot_origin_x,shot_origin_y,name,type,mode,instrument,chan,target,hi,lo,level,limit,shape,freq,conn,min,max,avg_count,avg_delay,nplc,his,los,settle_delay,mrange,die,route
```

All 21 STEP rows, exactly as saved (this session changed only the four
`max` values on check1-4, from `1`/`1.000` to `1e-07` - see "What changed
this session" below):

```
STEP,lampaccr,,,,1,,,,,touch,delay,,,,,,,200,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,2,,,,,first,current,measure,SMU,A,,17:8,18:7,10.000,1e-06,,,"4A05,4B06",,,1,0,10,,,200,,1,switch
STEP,lampaccr,,,,3,,,,,settle,delay,,,,,,,100,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,4,,,,,check1,passfail,,,,first,,,,,,,,0,1e-07,,,,,,,,1,switch
STEP,lampaccr,,,,5,,,,,switch1,open,,,,first,,,,,,,"4A05,4B06",,,,,,,,,,,switch
STEP,lampaccr,,,,6,,,,,delay,delay,,,,,,,200.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,7,,,,,second,current,measure,SMU,A,,19:6,20:5,10.000,1e-06,,,"4A07,4B08",,,1,0,10,,,200,,2,switch
STEP,lampaccr,,,,8,,,,,settle,delay,,,,,,,100.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,9,,,,,check2,passfail,,,,second,,,,,,,,0.000,1e-07,,,,,,,,2,switch
STEP,lampaccr,,,,10,,,,,switch2,open,,,,second,,,,,,,"4A07,4B08",,,,,,,,,,,switch
STEP,lampaccr,,,,11,,,,,delay,delay,,,,,,,200.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,12,,,,,third,current,measure,SMU,A,,7:2,8:1,10.000,1e-06,,,"2A08,2B07",,,1,0,10,,,200,,3,switch
STEP,lampaccr,,,,13,,,,,settle,delay,,,,,,,100.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,14,,,,,check3,passfail,,,,third,,,,,,,,0.000,1e-07,,,,,,,,3,switch
STEP,lampaccr,,,,15,,,,,switch3,open,,,,third,,,,,,,"2A08,2B07",,,,,,,,,,,switch
STEP,lampaccr,,,,16,,,,,delay,delay,,,,,,,200.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,17,,,,,fourth,current,measure,SMU,A,,6:3,5:4,10.000,1e-06,,,"2A06,2B05",,,10,5,1,,,200,,4,switch
STEP,lampaccr,,,,18,,,,,settle,delay,,,,,,,100.000,,,,,,,,,,,,,,,switch
STEP,lampaccr,,,,19,,,,,check4,passfail,,,,fourth,,,,,,,,0.000,1e-07,,,,,,,,4,switch
STEP,lampaccr,,,,20,,,,,switch4,open,,,,fourth,,,,,,,"2A06,2B05",,,,,,,,,,,switch
STEP,lampaccr,,,,21,,,,,delay,delay,,,,,,,200.000,,,,,,,,,,,,,,,switch
```

Summarized per die:

| die | name | hi | lo | conn (switch crosspoints) | level | limit | check spec (min,max) |
|---|---|---|---|---|---|---|---|
| 1 | first  | `17:8` | `18:7` | `4A05,4B06` | 10.000 V | 1e-06 A | [0, 1e-07] A |
| 2 | second | `19:6` | `20:5` | `4A07,4B08` | 10.000 V | 1e-06 A | [0, 1e-07] A |
| 3 | third  | `7:2`  | `8:1`  | `2A08,2B07` | 10.000 V | 1e-06 A | [0, 1e-07] A |
| 4 | fourth | `6:3`  | `5:4`  | `2A06,2B05` | 10.000 V | 1e-06 A | [0, 1e-07] A |

**Open question / not resolved this session: what does the colon-separated
`hi`/`lo` field actually mean** (e.g. `"17:8"`)? It does not match
`switch_topology.pin_channel()`'s simple `pin_number` -> row/col formula
against the actual `conn` value recorded for the same step (e.g. `first`'s
`conn` is `4A05,4B06`, i.e. row A/pin 5 and row B/pin 6 by the generic
formula - which doesn't obviously correspond to `hi=17:8`/`lo=18:7` at
all). Two live hypotheses, neither confirmed:
1. `hi`/`lo` are literal probe-needle/pad identifiers on this specific,
   custom-wired card (not switch-matrix pin numbers at all), and `conn`
   was set independently/directly (e.g. imported from the original legacy
   LaMP software) rather than computed from `hi`/`lo` via
   `switch_topology`.
   Ask the user directly what "17:8" means (I did not get to ask this
   session).
2. The `hi:lo` in "17:8" is a leftover/unrelated field from a different
   legacy schema that happens to still be populated in this CSV but isn't
   actually consumed by anything in `_exec2_run_steps_once` - **check
   whether the execution code actually reads the `hi`/`lo` fields for a
   `current`-type step at all**, or whether it's purely decorative for
   this step type (it seems to matter for pass/fail wiring displays but
   the actual physical routing is 100% determined by `conn`, which is
   unambiguous and is what actually got verified/exercised this session).

## Execution code path - `gui/instrument_panel.py`, `_exec2_run_steps_once`

The `current`/`mode=="measure"` branch (this is what all four of
`first`/`second`/`third`/`fourth` are) does, in order, per step:

1. Close every crosspoint in `conn` (via the switch matrix).
2. If `level` (lvl) is set:
   - `smu.set_voltage(smu_ch, float(lvl))`
   - if `limit` is set: `smu.set_current_limit(smu_ch, float(limit))`, then
     (added this session) **read back** `smu.get_current_limit(smu_ch)` and
     log a warning if it differs from what was requested by >1%.
   - `smu.turn_output_on(smu_ch)`
   - `did_bias = True`
3. `smu.set_nplc(smu_ch, nplc)` if the step's `nplc` field is set (all four
   steps here use `nplc=10` except `fourth`, which uses `nplc=1`).
4. `mrange` (LaMP's fixed MeterRange) - **blank for every step in this
   recipe**, so current measurement is on autorange.
5. `avg_delay`/`set_source_delay` - **no-op on this driver** (method
   doesn't exist), regardless of the recipe's `avg_delay` value.
6. `self._exec2_settle(s, name, i)` - sleeps `settle_delay` ms (200 ms on
   all four steps) AFTER bias-on, BEFORE the first reading.
7. `i_raw = self._exec2_maybe_abs(s, self._exec2_measure_averaged(...))` -
   the actual reading. `_exec2_measure_averaged` uses hardware averaging
   (`set_averages` + a single `measure_current` call) whenever
   `avg_count > 1` and the driver supports it - true for `fourth`
   (avg_count=10), false for `first`/`second`/`third` (avg_count=1, so a
   single plain read).
8. (added this session) `smu.measure_voltage(smu_ch)` readback, then
   (added this session) `smu.in_compliance(smu_ch)` queried **while output
   is still on** - this is what produced the "⚠ SMU REPORTS COMPLIANCE"
   log lines below.
9. `smu.turn_output_off(smu_ch)` (only if `did_bias` - i.e. this step
   itself turned the bias on; an "apply"-mode step is the only kind meant
   to leave power on past its own step, per earlier work this session).
10. `i_a, i_unit, note = self._exec2_apply_target(...)`, then
    `record_result(...)`, then the log line.

`_exec2_maybe_abs` is a new step field this session, `abs_value` - **not
set on any `lampaccr` step**, so it has no effect here; every current value
recorded below is the real signed reading.

## What changed this session (chronological, all pushed to `master`)

1. Fixed cassette-advance protocol (`U` -> `L`, corrected STB targets) -
   unrelated to this investigation, mentioned for completeness.
2. Added "Absolute Value" checkbox (`abs_value` step field) - not used by
   `lampaccr`.
3. **Set `check1`-`check4`'s `max` from `1`/`1.000` A to `1e-07` A** (min
   stays `0`). Reasoning at the time: a real gauge-wafer reference dataset
   (Electroglas/2400, NOT this SMU - see caveat below) showed a clean,
   tight ~998.5-999 nA cluster whenever the SMU was in compliance at a 1
   µA limit, vs ~0.6-1.1 nA for real leakage - so 1e-07 A was picked as a
   round decade of margin between the two. **This threshold was derived
   from a DIFFERENT instrument (2400/Electroglas) on a DIFFERENT wafer
   (a "GAUGE" calibration wafer, not a real LAMP wafer) - it has NOT been
   validated against this SMU (2636B/Accretech) or against real LAMP die
   leakage data. Treat 1e-07 A as provisional, not a confirmed spec.**
4. Added `Keithley2636B.in_compliance(channel)` wiring into the
   `current`/measure branch - logs "⚠ SMU REPORTS COMPLIANCE" when true,
   diagnostic only, does not affect pass/fail.
5. Added `Keithley2636B.get_current_limit(channel)` (real TSP readback)
   wired in right after `set_current_limit` - logs a warning only if the
   instrument's reported limit differs from what was requested by >1%.
6. Auto "Refresh XY" on Accretech launch/switch-to (unrelated to this
   investigation).

## The actual anomaly - two real bench runs, both on `lampaccr`

### Run 1 (all four dies)

```
2. first  [current/measure via SMU]: close 4A05,4B06
   I = -5.513e-06 A  (bias 10.000 V via SMU)  (bias off)  ⚠ SMU REPORTS COMPLIANCE
   4. check1: FAIL  first = -5.51292e-06 A  spec [0, 1e-07]
7. second [current/measure via SMU]: close 4A07,4B08
   I = -1.504e-05 A  (bias 10.000 V via SMU)  (bias off)  ⚠ SMU REPORTS COMPLIANCE
   9. check2: FAIL  second = -1.50442e-05 A  spec [0.000, 1e-07]
12. third [current/measure via SMU]: close 2A08,2B07
   I = -7.816e-06 A  (bias 10.000 V via SMU)  (bias off)  ⚠ SMU REPORTS COMPLIANCE
   14. check3: FAIL  third = -7.81649e-06 A  spec [0.000, 1e-07]
17. fourth [current/measure via SMU]: close 2A06,2B05
   10 readings averaged inside the Keithley2636B -> -6.34679e-05 A
   I = -6.347e-05 A  (bias 10.000 V via SMU)  [avg of 10, 5 ms apart]  (bias off)  ⚠ SMU REPORTS COMPLIANCE
   19. check4: FAIL  fourth = -6.34679e-05 A  spec [0.000, 1e-07]
Iteration complete — FAIL
```

### Run 2 (`fourth` only, shared later)

```
17. fourth [current/measure via SMU]: close 2A06,2B05
   10 readings averaged inside the Keithley2636B -> -5.60952e-05 A
   I = -5.61e-05 A  (bias 10.000 V via SMU)  [avg of 10, 5 ms apart]  (bias off)  ⚠ SMU REPORTS COMPLIANCE
   19. check4: FAIL  fourth = -5.60952e-05 A  spec [0.000, 1e-07]
```

**Critically: in Run 2, the new `get_current_limit()` readback did NOT
fire a mismatch warning** - meaning the instrument confirmed
`smua.source.limiti` really is programmed to `1e-06` as requested. This
rules out "the SET command isn't landing on the instrument" as the
explanation.

### The core mystery

With `limiti` confirmed correctly programmed at 1e-06 A and
`source.compliance` reporting true, the actual measured current on every
single die, across two separate runs, is **5x to ~60x larger than the
compliance ceiling** (values seen: -5.5, -15, -7.8, -6.3(x2), -5.6 µA,
against a confirmed 1 µA limit) - and the magnitudes are NOT consistent
with each other the way a genuine steady-state clamp would be (a real
clamp should read very close to the same value, right at limiti, every
time - which is exactly what the (different-instrument) gauge reference
data showed: ~998.5-999 nA every single time it hit compliance). Here,
every reading is different AND every reading is well past the limit.

The user has confirmed **the probe needles are physically touching the
wafer** - so this is not "no wafer loaded"/mis-Z. All four dies fail this
way, every run so far, with different-but-all-large magnitudes.

### Ranked hypotheses (none confirmed yet)

1. **Real, systemic short/fault common to every die position** - something
   about the physical setup causing near-dead-short conditions on every
   touchdown regardless of die: bad probe card wiring, a wiring fault
   shared by all four die circuits, chuck grounding issue, or similar.
   The "different magnitude every time" pattern fits variable contact
   resistance against a genuine short better than it fits four
   independently-faulty semiconductor dies.
2. **SMU control-loop instability/overshoot on a hard short at very tight
   compliance (1 µA) with fast integration** (`nplc=1` on `fourth`,
   `nplc=10` - about 167-200 ms - on the other three, still short relative
   to real settling if genuinely oscillating). A real short with only 1 µA
   allowed can ring rather than settle cleanly, and a fast/averaged read
   could catch that ringing instead of a true steady value. This would
   still mean there IS a real fault - just that the exact number reported
   isn't trustworthy.
3. **NOT yet ruled out: whether `measure.filter` (hardware averaging, used
   on `fourth` only, avg_count=10) is somehow interacting with
   compliance/range in an unexpected way** - `first`/`second`/`third` all
   use avg_count=1 (no averaging) and STILL show the same anomaly, which
   argues against averaging being the root cause, but hasn't been
   explicitly isolated with an avg_count=1 vs 10 A/B comparison on the
   SAME die.
4. Something specific to the unresolved `hi`/`lo` colon-notation (see
   above) - if those fields turn out to matter for correct routing setup
   in a way the code isn't currently using them for, that could be a red
   herring or the actual root cause. Needs the user's input on what those
   fields mean.

## Diagnostic tools already available for the next session

- **`gui/switchbox_test_panel.py`** (`SwitchboxTestPanel`) - manual
  crosspoint control: "■ ALL OPEN", "↻ Read state", per-die 2-wire/4-wire
  preset buttons, individual crosspoint toggles. Use this to manually
  close ONLY `2A06,2B05` (fourth's crosspoints) with nothing else touched,
  and separately verify continuity/resistance with a plain ohmmeter or the
  DMM, independent of the SMU/recipe engine entirely - isolates whether
  the fault is in the switch matrix/cabling vs the SMU/compliance
  behavior itself.
- **`gui/prober_debug_panel.py`** (`ProberDebugPanel`) - includes a raw
  GPIB command send box (`_send_raw`), plus manual Z up/down, Go To Die,
  Read STB. Useful for sending ad hoc TSP queries directly, e.g.
  `print(smua.measure.i())`, `print(smua.source.compliance)`,
  `print(smua.source.limiti)`, without going through the recipe engine at
  all - a good way to isolate "is this an SMU/instrument-level behavior"
  from "is this specific to how the recipe engine sequences things."
- **`Keithley2636B.in_compliance(channel)`** and
  **`Keithley2636B.get_current_limit(channel)`** (both added this
  session, both already wired into the live current/measure log output) -
  already answer "is the instrument confirmed in compliance" and "is the
  limit confirmed correctly programmed," both of which came back
  positive/consistent on Run 2. The next useful readback to add, if
  needed, would be **`{channel}.source.leveli`** (actual current the
  source is trying to push, distinct from `measure.i()`, the sensed
  value) - comparing "what the source thinks it's doing" vs "what the
  ammeter reads" could reveal a sense-vs-source mismatch.

## Suggested concrete next steps

1. **Ask the user what `hi`/`lo`'s colon-separated values mean** for this
   card (e.g. "17:8") - this was flagged but not resolved this session.
2. **Isolate switch matrix vs SMU**: use `SwitchboxTestPanel` to close only
   `2A06,2B05` and measure continuity/resistance with something other than
   the recipe engine (DMM directly, or a handheld meter at the probe card
   connector) to see if there's a real short independent of the SMU's own
   compliance behavior.
3. **Try a much higher current limit temporarily** (e.g. 1 mA instead of 1
   µA) on a throwaway test step for `fourth` only, and see whether the
   measured current settles to a believable, consistent value (would
   support hypothesis 2, ringing/instability at too-tight a compliance) or
   stays wildly different each time even with more headroom (would argue
   against pure ringing, more towards a genuinely variable real fault).
4. **Directly query `smua.source.leveli`** (actual commanded/sensed source
   current, not just `measure.i()`) via the raw-command box in
   `ProberDebugPanel`, right after closing `2A06,2B05` and biasing on
   manually (bypassing the recipe engine), to compare source-side vs
   measure-side current.
5. Re-run with `nplc` raised well above 1 and/or `settle_delay` raised well
   above 200 ms on `fourth` specifically, to test whether a longer
   settle/integration converges the reading toward something closer to
   1 µA (supports ringing) or not (argues against it).
6. Once the true nature of the fault is understood, revisit whether
   `check1`-`check4`'s new `1e-07` A max threshold (step 3 above) is
   actually the right number - it was derived from a different
   instrument's data on a calibration wafer, not from real LAMP die
   behavior on this SMU.

## Reference: the "gauge wafer" data that shaped the (provisional) 1e-07 threshold

For context only - **this data is from the Keithley 2400 / Electroglas
side, explicitly NOT verified as representative of this GUI's own
behavior on that system, and NOT the same instrument as the 2636B this
investigation is about.** File: `references/gauge example.xlsx` (user-
supplied, not authored by this session). Key facts extracted:
- 21 rows, `fldWaferID="GAUGE"`, all at `fldSetVoltage=10`.
- Two clean clusters: real leakage ~0.6-1.1 nA; compliance-clamped ~998.5-
  999 nA (tight, consistent - a textbook clamp at a 1 µA limit).
- A `TARGET`-labeled die-ID position correlated with (but wasn't the only
  occurrence of) the compliance-clamped cluster - likely a human label on
  one instance of a known-bad/reference position, not a system-generated
  marker.
- An embedded chart, title "gold value vs test value" (`ABS(fldCurrent)`
  vs a cached reference series from an external, no-longer-attached
  workbook `'[1]081926'`), with a linear trendline and R² displayed -
  apparently a pass/fail check comparing a live run against a trusted
  baseline run.

This dataset established the *concept* of "compliance clamp = bad, tight
cluster near the limit = the tell" - but the 2636B/Accretech bench data
gathered in THIS session doesn't show a tight cluster near the limit at
all, which is exactly what makes the current anomaly worth digging into
rather than just trusting the gauge-derived threshold at face value.
