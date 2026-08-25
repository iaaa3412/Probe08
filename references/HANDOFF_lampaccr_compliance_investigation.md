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

**RESOLVED (this update): `hi`/`lo`'s colon-separated values are literal
`(pin, pad)` pairs copied straight from the card's own `PIN` rows.** Every
`PIN,,<pin>,<pad>,...` row in `LaMP_HP_b.csv` (8 total: (5,4) (6,3) (7,2)
(8,1) (17,8) (18,7) (19,6) (20,5)) is used exactly once across the four
steps' `hi`/`lo` fields, verified by direct match, e.g. `fourth`'s
`hi="6:3"` == PIN row `(6, 3)`. So `hi`/`lo` are real probe-needle/pad
identifiers on the physical card - traceability of which physical needle
is involved - but they live in a **completely separate numbering space
from `conn`'s switch-matrix column numbers**: `first`'s needles are pins
17/18 (per PIN table), but its `conn` (`4A05,4B06`) uses columns 5/6 on
slot 4 - no numeric relationship at all. `conn` is the actual, real
routing (independently set, not derived from `hi`/`lo` via
`switch_topology.pin_channel()`); `hi`/`lo` never feeds into that formula
at all. Not a bug - just two different ID systems sharing the same CSV
row. This is why the naive `pin_channel()` cross-check never lined up.

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

## Session 2 addendum (2026-08-25) - mystery very likely resolved

Fresh Claude Code session, different PC, picked this handoff up cold. GUI
was confirmed NOT running (user's word) - everything below is raw GPIB/USB
sent directly against the drivers in `instruments/`, unmodified, bypassing
the GUI/recipe engine entirely. **The prober driver was never imported or
touched** - the user only confirmed by hand that the chuck was already up
and the wafer in contact for the whole session below. Scripts lived in a
scratch dir, run via the Python 3.13 install on this PC
(`instruments.yaml`/`switch_topology.yaml` both read from
`\\prober\M\ETL\proberautomation\GUI System\`, confirmed identical to the
defaults in `gui/switch_topology.py`, so the E="DMM LO"/F="DMM HI" row
mapping is real on this bench, not just a generic default).

### What was run

1. **Read-only survey before touching anything**: all 5 instrument addresses
   present on the bus (`GPIB0::5/10/12/16`, `USB0::0x2A8D::0x1301::...`).
   Switch mainframe confirms 707B with two 7072 8x12 Semiconductor Matrix
   cards in slots 2 and 4 (matches the recipe's row/col usage exactly).
   SMU was idle/output-off on both channels, `limiti` at its post-reset
   default (0.1 A) - nothing was live when the session started.
   **Found `2E08` and `2F07` already closed** on the switch - a leftover
   from *this* investigation's own earlier suggested step ("close only
   `2A06,2B05`... measure with the DMM directly"), except it's die
   **'third'**'s pads (`2A08,2B07`), wired with DMM polarity, and it had
   been left closed rather than opened. Resistance is a scalar so the
   swapped HI/LO didn't matter for the reading (see below), but worth
   knowing the matrix was not in a fully-open state before this session.

2. **Per-die pad resistance via the DMM only, SMU never involved**: for all
   four dies, closed just the DMM's crosspoints (row F = DMM HI, row E =
   DMM LO) on the same two columns the recipe's SMU step already uses for
   HI/LO, then `MEASure:RESistance?` (2-wire - no SHI/SLO rows are wired in
   this topology at all), 3 reads each, channels reopened after each die:

   | die | crosspoints (DMM) | 3 reads |
   |---|---|---|
   | first  | `4F05,4E06` | `9.9e+37, 9.9e+37, 9.9e+37` Ω |
   | second | `4F07,4E08` | `9.9e+37, 9.9e+37, 9.9e+37` Ω |
   | third  | `2F08,2E07` | `9.9e+37, 9.9e+37, 9.9e+37` Ω |
   | fourth | `2F06,2E05` | `9766468.59, 9.9e+37, 9.9e+37` Ω |

   `9.9e+37` is the Keysight 34461A's own overload/open-circuit sentinel -
   i.e. **every single die read as a clean open circuit**, exactly the
   "near-infinite resistance" LAMP is supposed to show. `fourth`'s one
   9.77 MΩ blip on the very first read, immediately followed by two more
   full-overload reads with nothing else changed, reads as a relay-closure/
   contact-settling transient, not a real resistive path - it did not
   repeat. The pre-existing leftover pair (`2F07,2E08`, die 'third') read
   full overload too, for what it's worth, before any of this touched it.

   **This directly confirms the switch matrix + cabling + probe pad path is
   properly connected to the wafer for all four dies**, and that the DUT
   itself is exactly as high-impedance as expected - independent of the
   SMU, so this is not "no wafer contact" and not "switch/wiring fault."

3. **Direct SMU replication of the recipe's own 'fourth' step** (bypassing
   the recipe engine, same 10 V / 1 µA limit / `nplc=10`, closing
   `2A06,2B05` by hand): `get_current_limit` readback confirmed `1e-06`
   correctly programmed (again). But:
   - `smua.measure.v()` returned **`9.91e+37`** - the SMU's *own*
     TSP overflow/invalid-reading sentinel - while sourcing what should be
     a plain 10 V into a near-open load.
   - `smua.measure.i()` returned real-looking but large, drifting numbers
     across 5 unaveraged reads taken back-to-back
     (`-4.19e-05 -> -4.21e-05 A`, and on a second run
     `-5.04e-05 -> -5.06e-05 A`) - a different magnitude on each attempt,
     consistent with the original handoff's "5x-60x over limit, different
     every time" pattern, not a repeatable clamp.
   - `smua.source.compliance` = `True` throughout.
   - A **VISA timeout** (`VI_ERROR_TMO`) then occurred on the very next,
     completely ordinary `measure.i()` query in a follow-up script -
     the instrument didn't answer within 3 s. (Confirmed immediately after:
     both SMU channels' outputs were off and slot 2 was fully open - the
     `finally` cleanup in the failing script had already run before the
     timeout propagated, so nothing was left biased. No physical risk, but
     the timeout itself is a data point.)

4. **Ruled out remote-sense-with-open-leads** as the explanation for the
   voltage-overflow: `smua.sense` reads back `SENSE_LOCAL` (0) by default
   right after `reset()` on this instrument - already 2-wire, not 4-wire.
   Explicitly forcing `smua.sense = smua.SENSE_LOCAL` again before repeating
   the exact same bias made no difference (`measure.v()` still overflowed,
   `measure.i()` still read ~-5.05e-05 A, still "in compliance"). Whatever
   this is, it isn't a floating sense-lead artifact.

5. **Ruled out a scripting/config mistake** as the explanation: idle
   baseline (output off, nothing closed) reads perfectly clean -
   `measure.v()` ≈ -97 µV, `measure.i()` ≈ 7e-14 A, `errorqueue.count = 0`.
   `measure.rangev` correctly autoranged from 0.2 V (idle) to 20 V once
   10 V was commanded. The error queue stayed at 0 through the entire
   biased sequence - the SMU itself never flags an error, it just silently
   returns an overflow on the voltage read while returning plausible-looking
   numbers on the current read of the identical measurement.

### Revised understanding (superseded by the further testing below - kept
for the record of how the diagnosis narrowed)

Every finding above points the same direction: **the wafer/pad/switch/
cabling side is fine and behaves exactly as LAMP expects (near-infinite,
i.e. open, resistance on all four dies, confirmed by an instrument that
isn't even part of the suspect signal path).** The anomaly is specific to
what happens when the Keithley 2636B voltage-sources 10 V into that
genuinely-near-open node with an extremely tight 1 µA current limit - its
own voltage measurement invalidates itself, its current reading is
large/unstable/non-repeating, and communication with it degraded (one
timeout) shortly after.

### Further testing (same session, continued) - the offset is real, is
channel-specific, and is NOT voltage-dependent

The user asked to keep characterizing the SMU directly: both channels
(`smua`/`smub`), 10 V bias, current readback. Four more test batteries,
still never touching the prober:

1. **Both channels, all four dies, still at the recipe's 1e-6 A limit**
   (channel B has never actually been used by `lampaccr` - its rows in this
   topology are `C`=SMU-B HI, `D`=SMU-B LO): every one of the 8
   combinations overflowed `measure.v()` and reported `compliance=true`,
   but with a striking pattern - **`smub`'s current was ~3.0x `smua`'s on
   every single die** (113/36.3, 182/64.3, 188/61.7, 168/55.3 µA - all
   ≈3.0-3.1x), and the five back-to-back reads on every single test were
   flat to <1% - a real RC transient would decay visibly over that many
   reads a few ms apart; this didn't. Steady current, not a transient.

2. **Isolation test**: bias both channels at 10 V/1 µA with the switch
   matrix **fully open** - nothing closed, output floating. Result: clean,
   correct `measure.v()` (~10.0004/10.0006 V), current in the **1e-13-1e-14
   A** range (true instrument noise floor), `compliance=false`. So the
   overflow/large-current behavior does NOT exist in the SMU/cabling alone -
   it only appears once the switch matrix routes the channel through to a
   die.

3. **`limiti` sweep on die 'fourth'** (`smua` via 2A06/2B05, `smub` via
   2C06/2D05), 10 V fixed, `limiti` = 1e-6/1e-5/1e-4/1e-3 A: each channel
   has its own threshold where it snaps out of the overflow/compliance
   state into a clean, valid reading -
   - `smua`: still overflowing/compliant at 1e-5, clean at 1e-4 (settles to
     ≈**-12.3 µA**, `compliance=false`, valid V≈10.0V).
   - `smub`: still overflowing/compliant even at 1e-4, clean only at 1e-3
     (settles to ≈**-125.8 µA**, `compliance=false`, valid V≈10.0V) - again
     ≈10x `smua`'s clean value, on the exact same physical pads.
   This is the key structural fact: **once each channel's limit is loose
   enough to stop clipping, the current stops being noisy/invalid and
   becomes a clean, repeatable, channel-specific value** - i.e. there is a
   real current being drawn in the switch-matrix-side path, and it is
   different for the A/B row pair vs the C/D row pair on the *same*
   physical columns.

4. **Voltage sweep at each channel's own clean (non-compliant) `limiti`**
   (`smua` @ 1e-4 A, `smub` @ 1e-3 A), V = 0/0.5/1/2/5/10 - the decisive
   test. If the ≈12.3 µA / ≈126 µA currents above were real DUT conduction
   (resistive or diode-like), they would track the applied voltage,
   dropping toward 0 A as V→0. They did not:
   - `smua`: **-13.3 µA at V=0.0**, drifting only to -22 µA at V=10.0 -
     nearly flat across the whole 0-10 V range.
   - `smub`: **-118.2 µA at V=0.0**, only to -127 µA at V=10.0 - same flat
     pattern, ~9-10x larger.
   Voltage read back correctly (matching commanded V almost exactly) at
   every point in this sweep - it's only the *current* that stays
   essentially pinned near a fixed, non-zero, channel-specific value
   regardless of the voltage applied across the pads.

### Conclusion

**The wafer and its pads are fine.** The DMM's independent 2-wire check
(never touching the SMU) reads a clean open circuit on every one of the
four `lampaccr` dies, exactly the near-infinite resistance LAMP is supposed
to have, and the SMU's own isolation test (nothing closed on the switch)
shows the instrument itself is clean too (sub-picoamp noise floor) with
nothing connected. **The current failing every die is a real, roughly
voltage-independent, channel-specific offset/leakage current that only
appears once the Keithley 707B switch matrix is in the signal path** -
present even with 0 V commanded, ~3-10x larger on the SMU-B/row-C-D path
than the SMU-A/row-A-B path for the identical physical pads, and large
enough (tens to ~150 µA) that it alone blows through LAMP's intended 1 µA
compliance on every single measurement regardless of what the actual die
is doing. At the tight 1 µA limit the source can't supply this current
without hitting compliance, so it never settles to a stable operating
point - hence the invalid voltage readback and the noisy, oversized,
non-repeating current numbers documented back in Session 1. Loosen the
limit past this offset and the picture becomes completely clean and
repeatable (just not anywhere near the intended 1 µA regime).

Leading suspects for WHERE this offset current actually originates (not
yet isolated further - would need a handheld meter directly at the switch
matrix's row-bus terminals, which is a physical, not scriptable, check):
- A leaky/marginal relay or crosstalk within the 707B's own 7072 8x12
  matrix cards, specific to which rows are used (A/B vs C/D) rather than
  which columns (i.e. a per-row-bus characteristic, not a per-die one).
- A ground-loop/common-mode current between the switch mainframe's chassis
  and the SMU's LO reference, which would plausibly be close to
  voltage-independent (matches what was measured) and could differ between
  the B/D bus run and the A/B bus run if they're routed differently inside
  the card or backplane.
- Cabling/harness leakage between the matrix and the probe card connector,
  again specific to the row pair rather than the column/die.

### Control test, same session: chuck DOWN, needles NOT touching - the
offset REQUIRES contact (corrects the "switch matrix internal" lead above)

The user then separated the chuck (still never commanded by Claude - purely
reported/performed by the user) and asked to repeat the check. Same DMM
per-die sweep and same SMU 10V/1e-6A/both-channels/all-four-dies test,
needles now floating in air:

- **DMM**: unchanged - open circuit on all four dies, as expected with
  nothing touching.
- **SMU**: completely clean on BOTH channels, ALL FOUR DIES - valid
  ~10.00 V readback every time, current in the **1e-13-1e-12 A range**
  (indistinguishable from instrument noise floor), `compliance=false`
  throughout. The 36-65 µA (channel A) / 113-189 µA (channel B) offsets
  documented above are **completely gone**.

This reverses the leading suspect from "something inside the 707B/cabling
regardless of contact" to **something that requires actual needle-to-wafer
(or needle-to-chuck) contact to exist at all** - the earlier "isolation"
test only proved the SMU+cabling are clean with *nothing closed on the
switch*; this control proves they're ALSO clean with the switch closed
onto real columns, provided the needles simply aren't touching anything.
Since the DMM's own HI-to-LO-only measurement stays a clean open in both
the contact and no-contact conditions, the extra current in the contact
case is not flowing pad-to-pad - the leading physical explanation is a
leakage/ground-reference current that only completes once the needle
actually touches the wafer/chuck (e.g. needle -> wafer body -> grounded
chuck -> back to the SMU via chassis/earth, a path a 2-wire HI/LO-only
measurement would never see), which would also explain why the current
was close to voltage-independent (driven by a ground potential difference,
not by the programmed 10 V) and why channel A and channel B differed by
~3-10x on the identical physical pad (if their LO/guard references inside
the switch matrix aren't equally well tied to that same ground).

### Ruled out, same session: cross-channel interference between smua/smub

Hypothesis (from the user, worth testing directly): the consistent ~3-10x
smub-vs-smua ratio on every die could mean the two channels aren't
electrically isolated from each other (e.g. a shared LO/return), so each
channel's compliance loop is fighting the other's forced 10 V rather than
seeing its own die in isolation - which would also explain the universal
`measure.v()` overflow (two sources fighting over one node is a classic way
to get an undefined voltage reading).

Tested directly, chuck back in contact, die 'fourth': for each channel,
before biasing it, the OTHER channel's `source.output` was explicitly
forced to `OUTPUT_OFF` and read back to confirm - not just assumed - at
three checkpoints (immediately after forcing it, again right before the
tested channel's output turned on, and again during the tested channel's
bias). The other channel's own switch crosspoints were also never closed
in either direction, so there's no path through the matrix for it to
interfere via regardless of its internal state. Result: **identical
anomaly on both channels** - `smua` alone: overflow V, ≈-28.3 µA,
compliance=true, with `smub.source.output` confirmed `0` at every
checkpoint; `smub` alone: overflow V, ≈-115 to -147 µA (this run showed
more read-to-read drift than earlier ones, still all >>1e-6A), compliance=
true, with `smua.source.output` confirmed `0` throughout.

This rules out cross-channel interference: if smua/smub shared an internal
LO reference, that coupling would be a fixed hardware fact independent of
wafer contact, but the identical channel-alone sequence with the needles
NOT touching (same crosspoints, same one-channel-at-a-time approach, no-
contact control above) came back completely clean on both channels. An
effect that requires actual contact to appear is not explained by the two
channels sharing wiring inside the instrument or matrix - it needs the
wafer/chuck genuinely in the loop, consistent with the ground-path theory
above rather than this one. (Minor loose end: `smuX.OUTPUT_HIGHZ` read
back `nil` on this instrument/firmware, so the idle channel's `offmode`
could not be forced to a true floating high-Z during this test - it stayed
at the default `OUTPUT_NORMAL`. Its `source.output` was still confirmed
`0`/off at every checkpoint, and its own crosspoints were never closed, so
this doesn't reopen the cross-channel theory, but a firmware/model check on
the correct high-Z constant name would close this gap fully if revisited.)

### Ground-reference test procedure (how to actually run suggested next steps 2-4)

This needs a handheld multimeter, not GPIB - it's chassis/ground potential,
not the signal path.

**Before touching anything**: confirm both SMU channel outputs are OFF
(`smua.source.output`/`smub.source.output` = `OFF`) and the switch matrix
is fully open (`SwitchboxTestPanel`'s "■ ALL OPEN", or
`channel.open('allslots')`). Don't run this with the recipe/GUI live.

Three chassis points: **chuck/prober chassis** (exposed frame metal, or the
chuck's own ground lug if it has one), **SMU chassis** (2636B rear-panel
ground screw or LO connector shell), **switch mainframe chassis** (707B
rear-panel ground screw).

1. **Test A - DC voltage, all three pairs** (chuck↔SMU, chuck↔switch
   mainframe, switch mainframe↔SMU), handheld DMM on DC volts. Should read
   near 0V (low mV) on a clean single-point ground; anything meaningfully
   higher is a real ground potential difference.
2. **Test B - resistance/continuity, same three pairs**, outputs still off,
   nothing energized. Should read near 0Ω if directly bonded. A
   meaningfully high or open reading means those two "grounds" are only
   connected indirectly (e.g. via building AC ground through separate
   outlets), not a real bond.
3. **Test C - sanity check**: `V_offset (Test A) / R_path (Test B) ≈
   I_leak`. Compare against the already-measured clean offsets (`smua`
   ≈12.3 µA @ 1e-4A limit, `smub` ≈126 µA @ 1e-3A limit) - if the order of
   magnitude lines up, that's quantitative confirmation, not just
   correlation.
4. **If confirmed**: the standard fix is a low-impedance bonding strap
   directly between the prober chassis and the SMU/switch matrix chassis
   (a proper single-point ground) - flag to whoever owns the bench rather
   than improvising on production equipment. Re-run the `limiti` sweep
   (smua @1e-4A, smub @1e-3A) after any such fix to see whether the offsets
   shrink/disappear - that would be the definitive confirm-and-fix.

### Ground-loop theory ABANDONED, switch-matrix-internal leakage REOPENED as leading theory

User ran the handheld tests documented above directly:
- **Chuck-to-wafer-die: isolated** (no continuity). The wafer backside is
  NOT electrically touching the chuck on this setup - the needle→wafer→
  chuck→prober-ground return path this theory depended on does not exist.
- **Grounds (chuck vs SMU/switch mainframe): matched**, no meaningful
  potential difference found.

**This kills the ground-loop/chuck-contact theory.** Both of its physical
preconditions were checked directly and both came back negative.

**Second, more important new fact: the same over-limit anomaly reproduces
on the "GAUGE" calibration wafer (`references/gauge example.xlsx`'s own
wafer), not just real LAMP dies, when run against THIS SMU (2636B/
Accretech).** This reframes the whole investigation - it is very unlikely
to be "LAMP's real dies are unusually leaky" if a purpose-built
calibration wafer shows the identical problem on this exact electrical
chain. (Recall the ORIGINAL gauge data referenced earlier in this doc was
from the 2400/Electroglas side, a different instrument entirely, and
showed a clean tight clamp - this new observation is the SAME gauge wafer
concept, but actually run through THIS bench's SMU/switch matrix, and it
is NOT clean here.)

Combined with the earlier "isolation test" (switch fully open, nothing
closed -> SMU+cabling alone is clean) and "control test" (switch closed,
needle NOT touching anything -> also clean), plus now "any wafer, once
actually touched and routed through the switch -> anomalous," the leading
theory reverts to the ORIGINAL suspect from the first deep-dive session,
now with much stronger support: **something inside the Keithley 707B's
own matrix cards, backplane, or the cabling downstream of it - a leaky/
marginal relay or row-specific crosstalk (SMU-A on rows A/B vs SMU-B on
rows C/D) - not anything wafer/die/chuck/ground-specific.**

**Proposed next test - 100% GPIB, no physical/manual work needed**: close
a crosspoint on the SAME rows (A/B for smua, C/D for smub) but a COLUMN
with no physical needle wired to it at all (a "dead"/unused column on the
same matrix card slot, beyond whatever `lampaccr`'s PIN rows actually
use). Bias the SMU exactly as in the earlier limiti-sweep/voltage-sweep
tests and check the current:
- Clean (sub-pA, compliance=false) -> leakage genuinely requires
  something touched at the far end; wafer-adjacent theories aren't fully
  dead, worth reconsidering what "touched" is doing electrically even
  without a chuck-ground path.
- Still shows the same channel-specific offset (~12 µA smua / ~126 µA
  smub range, or whatever the current clean values are) -> conclusive
  proof it's entirely internal to the switch matrix/backplane/cabling,
  independent of any wafer, chuck, or ground reference.

Which columns are actually unused needs to be derived from the probe
card's own PIN rows (`\\prober\M\ETL\proberautomation\LAMPATA\
probe_cards\LaMP_HP_b.csv`'s `PIN` rows list every pin actually in use;
anything on slot 2/4 not listed there, within the card's 12-column range,
is fair game) - not yet done as of this update.

### Switch-matrix-internal-leakage test RUN - result is CLEAN, rules out
"purely internal to the 707B" (fresh session, same day, GPIB only)

Physical precondition per the user (not GPIB-verifiable - the 707B cannot
know what's on the far end of a column wire): the probe-card-side wires for
**pins 1 and 2 were manually disconnected**, dangling, nothing downstream.
Only the instrument-side row wires (SMU-A HI/LO, SMU-B HI/LO, DMM HI/LO,
WGEN1/2) remain wired as usual. Per the card convention (pins 1-12 = slot 2
cols 01-12, pins 13-24 = slot 4 cols 01-12 - confirmed via
`gui/switch_topology.py`/`gui/switch_debug_panel.py`, not something
`query_slot_info()` itself reports since that's a wiring convention, not a
matrix property): **pin 1 = `2A01`/`2C01`, pin 2 = `2B02`/`2D02`** - same
row buses (A/B for smua, C/D for smub) that show the large offset on the
real die columns (5-8), just routed to different, currently-dangling
columns.

Test: matrix opened fully first (`smua`/`smub` outputs confirmed off),
then for each channel - close its HI/LO crosspoints on pins 1/2, source
10 V, `limiti` at that channel's own already-established clean threshold
(`smua`=1e-4A, `smub`=1e-3A, from the earlier limiti-sweep), read
`measure.v()`/`measure.i()` x5/`source.compliance`, output off, crosspoints
open, repeat for the other channel.

**Result - clean on both channels:**
- `smua` (`2A01`+`2B02`, limiti=1e-4): `measure.v()`=10.0004 V (valid),
  `measure.i()` x5 = 6.89e-13 -> 2.80e-13 A (decaying, sub-picoamp),
  `compliance`=false.
- `smub` (`2C01`+`2D02`, limiti=1e-3): `measure.v()`=10.0008 V (valid),
  `measure.i()` x5 = 1.03e-12 -> 7.75e-13 A (decaying, sub-picoamp),
  `compliance`=false.

Both channels behave exactly like the very first "switch fully open"
isolation test - i.e. **this rules out a leak that is purely internal to
the 707B's rows/backplane independent of column**, per the interpretation
this test was designed against. The same row buses (A/B, C/D) that misbehave
on columns 5-8 are clean on columns 1/2 - so it is not "row A/row C always
leaks regardless of what's closed downstream."

Aside, not related to this result: the error queue showed `count=4` during
this test and was drained separately - all 4 are stale entries predating
this run (`-286 TSP Runtime error... attempt to index global 'channel' (a
nil value)` - i.e. a switch-matrix-style `channel.close(...)` command sent
to the *SMU's* GPIB address by mistake at some earlier point, not by this
script; plus a `Query UNTERMINATED` and two `Data type error`s). Worth
knowing something hit the wrong instrument address at some point during
this investigation's manual/raw-terminal work, but it doesn't touch this
test's result.

**Where this leaves the theory ranking**, combining every condition tested
across this whole investigation:
| condition | result |
|---|---|
| switch fully open, nothing closed | clean |
| real die columns (5-8) closed, needles NOT touching wafer | clean |
| dangling columns (1/2) closed, same rows as the real dies | clean |
| chuck-to-wafer DC continuity (handheld, other session) | isolated, no path |
| chuck vs SMU/switch ground potential (handheld, other session) | matched |
| cross-channel (other channel confirmed off) | anomaly persists - ruled out |
| real die columns (5-8) closed, needles touching wafer #1 | anomalous |
| real die columns (5-8) closed, needles touching wafer #2 (different wafer) | anomalous, same signature |

The only two conditions that reproduce the anomaly both require (a) actual
needle-to-wafer contact and (b) routing through columns 5-8 specifically -
every other combination, including this session's dangling-pin-1/2 test, is
clean. With the switch matrix itself now cleared (this test) and the DC
chuck-ground path separately cleared (handheld tests above), the leading
open theory is something **downstream of the switch matrix but specific to
columns 5-8's own cabling/connector/probe-card routing, that only shows up
under real wafer contact** - e.g. an AC/capacitive coupling path a DC
continuity check wouldn't catch, or a card-layout quirk (shared guard trace,
proximity to a wafer-common structure) specific to those needle positions.
Not yet isolated further - the natural next GPIB-only test would be the
same dangling-wire approach but on one of the ACTUAL die columns (5, 6, 7,
or 8) instead of the spare 1/2, if any of those can be safely disconnected
on the probe-card side the same way, to see whether the leak follows the
column even without a wafer present at all.

### Suggested next steps (current, supersedes the stale ground-loop-chasing
list this section used to have - ground-loop and switch-matrix-internal
are BOTH ruled out as of the dangling-pin-1/2 test above)

1. **`lampaccr`'s `check1`-`check4` results should not be trusted as-is
   while the wafer is actually in contact** - the anomaly is real,
   reproducible, and requires both contact AND columns 5-8 specifically.
   It is not a fixed instrument fault, not (per the DMM) a real pad-to-pad
   short, not the switch matrix's rows in general, and not a chuck/ground
   potential difference (all directly tested and ruled out). The DMM-based
   2-wire check remains the trustworthy stand-in for "is this pad pair
   open" in the meantime.
2. **The natural next GPIB-only test**: repeat the exact dangling-wire
   approach that was just run on spare pins 1/2, but this time on one of
   the ACTUAL die columns (5, 6, 7, or 8) - disconnect that column's
   probe-card-side wire, close its crosspoints, bias at that channel's
   clean `limiti`, and check whether the leak follows the COLUMN even with
   nothing (no probe card, no wafer) connected past it. This is the
   cleanest way to separate "the column's own cabling/connector inside the
   switch matrix enclosure or wiring harness" from "something specific to
   the probe card or needle itself downstream of that wire."
   - Clean -> the fault is downstream of the disconnect point entirely
     (probe card, needle, or the wafer-contact interaction itself) - not
     the column's wiring up to that point.
   - Still anomalous with the column dangling and disconnected -> the
     fault is in that specific column's own cabling/routing, independent
     of anything past it - but note this would then be in tension with the
     "requires actual contact" finding (a pure cabling fault shouldn't
     care whether a wafer is touched), so a positive result here would
     itself need reconciling with the contact-dependence already
     established - flag rather than assume either theory automatically
     wins.
3. Since contact is required, also worth comparing: do columns 5-8 (or
   just whichever specific one is tested) route through a physically
   different cable run, connector, or card position than columns 1/2 -
   e.g. a longer run, closer proximity to the chuck/prober wiring, or a
   different connector type - that a length/proximity-dependent
   AC/capacitive coupling theory would predict matters, unlike a pure DC
   fault.
4. If `lampaccr` needs to keep using the SMU (not the DMM) for this check,
   1 µA compliance is not achievable while this contact-dependent,
   column-5-8-specific leakage exists - it would need either the leak path
   found and fixed, a loosened compliance, or the offset characterized/
   subtracted, and none of those should happen before step 2 above narrows
   it further.
