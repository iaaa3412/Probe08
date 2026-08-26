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

### Suggested next steps (current - both DC extremes now positively
CLEARED; narrowed to an AC/dynamic effect specific to real contact)

Both the "true open" (dangling column, real die columns 7/8 included) and
"true short" (HI+LO shorted together inside the switch matrix, no external
wire) tests came back completely clean on both channels, at both the tight
recipe limit and each channel's loose limit - see the two result sections
directly above. The SMU, the 707B switch matrix, and the cabling/columns
themselves are now positively cleared, not just unimplicated. The anomaly
exists ONLY with a real wafer in real mechanical contact, and is neither a
clean short nor a clean open from the SMU's own perspective.

**Sharper signature, worth noting**: the clean baseline readings above
DECAY toward a low floor (e.g. 6.89e-13 -> 2.80e-13 A) - normal parasitic-
capacitance settling. The real-contact anomaly readings (Run 1/Run 2/the
channel A-B test earlier in this doc) are FLAT/non-decaying (e.g. -36.25,
-36.25, -36.27, -36.33, -36.21 µA). A one-time charging transient should
look like the clean baseline eventually does, not stay flat indefinitely -
a flat, sustained, non-decaying offset is more consistent with something
continuously driving it (e.g. line-frequency/50-60Hz or other AC pickup
being averaged/rectified into an apparent DC reading by the measurement)
than with a single capacitive charge event.

1. **`lampaccr`'s `check1`-`check4` results should not be trusted as-is
   while the wafer is actually in contact** - real, reproducible, and now
   proven to require both contact and (at minimum) columns 5-8, with every
   instrument/matrix/cabling explanation directly tested and cleared. The
   DMM-based 2-wire check remains the trustworthy stand-in for "is this pad
   pair open" in the meantime.
2. **Next GPIB-only test - NPLC sweep under real contact**: with the wafer
   actually touching (die 'third' or 'fourth'), sweep `{channel}.measure.
   nplc` widely (e.g. 0.01, 0.1, 1, 10, 25 - the instrument's practical
   range) at a fixed `limiti` loose enough not to clip (or accept
   compliance and just watch `measure.i()`'s value change with NPLC), same
   crosspoints each time. If the offset shrinks substantially as NPLC
   approaches a multiple of the true local line period (16.67 ms @ 60 Hz /
   20 ms @ 50 Hz), that's a strong, specific confirmation of line-frequency
   AC pickup - and would mean the instrument's own configured line
   frequency (`localnode.linefreq` or similar - verify the TSP property
   name against the 2636B reference manual, not guessed here) should be
   checked against the ACTUAL local mains frequency, since a mismatch would
   explain why the recipe's own nplc=1/nplc=10 settings aren't already
   rejecting it. If the offset barely changes across the NPLC sweep, that
   rules out simple line-frequency pickup specifically and points at a
   higher-frequency or non-periodic AC/dynamic mechanism instead.
3. **Physical/non-GPIB test, if available**: an oscilloscope or LCR-style
   AC measurement directly at the point of contact (needle-to-probe-card
   connector, or as close to the actual touchdown as safely accessible)
   would show directly whether there's a real AC signal riding on the node
   under contact, and at what frequency - the single most direct way to
   confirm or refute the AC-coupling theory, but outside GPIB script scope.
4. If `lampaccr` needs to keep using the SMU (not the DMM) for this check,
   1 µA compliance is not achievable while this contact-dependent leakage
   exists - it would need either the AC path found and fixed/filtered, a
   loosened compliance, or the offset characterized/subtracted, and none of
   those should happen before step 2 (and ideally step 3) narrow it further.

### Suggested next steps item 2 RUN - dangling a REAL die column is ALSO
clean (fresh session, same day, GPIB only)

Physical precondition per the user (not GPIB-verifiable): **pins 7 and 8's
probe-card-side wires manually disconnected**, dangling, nothing
downstream - this time NOT spare columns, but die **'third'**'s own actual
recipe crosspoints (`2A08,2B07` for `smua`, mirrored as `2C08,2D07` for
`smub` on channel B's rows) - the exact columns that read ~-55 to -62 µA
with voltage overflow every single time a real wafer was in contact.

Same procedure as the pins-1/2 test: matrix opened fully first (both
outputs confirmed off, error queue confirmed empty beforehand), then per
channel - close its HI/LO crosspoints on columns 7/8, source 10 V,
`limiti` at that channel's established clean threshold (`smua`=1e-4A,
`smub`=1e-3A), read `measure.v()`/`measure.i()` x5/`source.compliance`,
output off, crosspoints open.

**Result - clean on both channels, same as pins 1/2:**
- `smua` (`2A08`+`2B07`, limiti=1e-4): `measure.v()`=10.0005 V (valid),
  `measure.i()` x5 = 5.15e-13 -> 2.45e-13 A (decaying, sub-picoamp),
  `compliance`=false.
- `smub` (`2C08`+`2D07`, limiti=1e-3): `measure.v()`=10.0008 V (valid),
  `measure.i()` x5 = 8.20e-13 -> 6.14e-13 A (decaying, sub-picoamp),
  `compliance`=false. Error queue stayed at 0 throughout (the earlier
  stale entries are gone as of this session - unrelated to this result).

**This is the decisive version of the test.** Per the interpretation this
was designed against: a clean result on the SAME columns that are
anomalous under real wafer contact means the fault is not in that column's
own cabling/connector/routing up to the disconnect point - it requires the
far end to actually be touching a wafer. Combined with everything already
eliminated this investigation (switch matrix rows in general - both spare
and real columns dangling behave identically; cross-channel interference;
chuck-to-wafer DC continuity; chuck/SMU/switch ground potential), essentially
every candidate is now ruled out except the real needle-to-wafer contact
interaction itself. Since the DC-based checks (continuity, ground potential)
came back negative, the leading remaining theory is something **AC/
capacitive rather than DC** - e.g. a capacitive coupling path between the
needle/pad and some reference (chuck, adjacent structure, or the wafer body
itself) that only exists under actual mechanical contact and wouldn't show
up on a handheld DC meter at all. Not yet isolated further; a scope or LCR-
style AC measurement at the point of contact (not a plain ohmmeter) would be
the natural way to test this next, if the bench has one - outside GPIB
script scope for now.

### Short-through-the-switch test - the OTHER DC bracket, also completely
clean (fresh session, same day, GPIB only, no physical changes)

Idea (from the user): instead of physically shorting the pins-7/8 wires
outside the prober, create the short entirely INSIDE the 707B - close both
the HI row and the LO row onto the SAME column. E.g. for `smua`: close
`2A07` (HI) and `2B07` (LO) together - both rows now land on column 7's
single node, tying `smua`'s HI directly to its own LO through the switch's
own relay contacts. No wire beyond the matrix is involved at all - this is
as close to "test the switch matrix itself" as it gets. Mirrored for
`smub` via `2C07`+`2D07`.

Tested at two limits per channel: the recipe's actual `1e-6A` (the value
that's actually failing against a real wafer - the most diagnostic
comparison) and each channel's own established "clean" threshold (1e-4 for
`smua`, 1e-3 for `smub`), for context.

**Result: textbook-clean compliance clamp on both channels, at every
limit tested - no overflow anywhere:**

| channel | limiti | measure.v() | measure.i() (5x) | compliance |
|---|---|---|---|---|
| smua | 1e-6 | -3.10e-05 V | 1.00000e-06, 1.00000e-06, 1.00001e-06, 1.00000e-06, 1.00001e-06 A | true |
| smua | 1e-4 | 9.78e-05 V | 9.99991e-05 ... 9.99996e-05 A | true |
| smub | 1e-6 | 5.96e-05 V | 1.00010e-06 (identical x5) A | true |
| smub | 1e-3 | 1.24e-03 V | 1.00229e-03 ... 1.00230e-03 A | true |

Voltage reads a small, valid, near-zero value every time (exactly what a
current-limited source should show into a real short - never overflows).
Current is pinned essentially exactly at the programmed `limiti` (within
normal calibration tolerance, tighter even than the gauge reference's own
example of a clean clamp), completely flat across all 5 reads, on BOTH
channels, at BOTH the tight recipe limit and the loose one. No error queue
entries. This is precisely the "textbook clamp" signature from
`references/gauge example.xlsx`, reproduced on THIS bench for the first
time this investigation.

**This is the decisive complementary result to the dangling-column test.**
Between the two, both DC extremes have now been directly tested on this
exact hardware, through the exact same rows/limits that are anomalous under
real wafer contact:
- True open (dangling, either spare columns 1/2 or die 'third's own
  columns 7/8): clean, sub-picoamp.
- True short (via the switch, same rows, same columns): clean, pinned
  exactly at the compliance limit, valid near-zero voltage.

**Neither extreme reproduces the anomaly.** The SMU's compliance
circuitry, the 707B switch matrix, and this signal path all behave
perfectly correctly and identically well on both channels (no more 3-10x
A-vs-B gap - that asymmetry is completely absent here) when facing a real
DC load of either kind. The failure is therefore not the instrument, not
the switch matrix, not generic cabling behavior - it requires the specific
electrical condition an actual wafer, in actual mechanical contact,
presents, which is neither a clean 0 ohm nor a clean infinite-impedance
node from this SMU's perspective. This continues to point at something
dynamic/capacitive in the real contact interaction rather than anything
resistive, matching the leading theory above.

### NPLC sweep RUN under real contact + broad SMU-settings battery -
quantitative confirmation of a periodic/AC disturbance (fresh session,
same day, GPIB only, wafer touching, pins 7/8 reconnected)

Die 'third' (`2A08`/`2B07` = `smua`, `2C08`/`2D07` = `smub`, pins 7/8
reconnected to the switch per the user), real wafer in contact. Six-part
battery, all at 10 V:

**Part 1 - NPLC sweep at each channel's own LOOSE/clean `limiti`
(1e-4 `smua`, 1e-3 `smub`) - does the settled current's MAGNITUDE depend on
integration time?**

| NPLC | smua current | smub current |
|---|---|---|
| 0.01 | -8.13 µA | -46.26 µA |
| 0.1  | -9.07 µA | -45.52 µA |
| 1    | -4.68 µA | -42.90 µA |
| 10   | -2.63 µA | -40.19 µA |
| 25   | -1.03 µA | -37.23 µA |

**Yes, clearly.** `smua`'s current drops ~8x from NPLC=0.1 to NPLC=25, and
from NPLC=1 upward scales almost exactly as 1/NPLC (current x NPLC is
roughly constant: 4.68, 26.3, 25.75) - the textbook signature of a
periodic disturbance being progressively averaged out by longer
integration, not a fixed real DC leakage (which NPLC would not change).
`smub` moves the same direction but far more weakly (~20% drop end to
end) - another channel-A-vs-B asymmetry, on top of every other one
recorded in this doc, suggesting a different coupling strength/path for
the two channels' rows rather than a fixed universal artifact. `measure.v()`
stayed valid at every point (`compliance=false` throughout, since this is
the loose-limit regime).

**Part 2 - same NPLC sweep at the REAL recipe `limiti`=1e-6A - does any
integration time let the source actually converge?**

| NPLC | smua current | smub current |
|---|---|---|
| 0.01 | -55.86 µA | -161.5 µA |
| 0.1  | -55.44 µA | -161.9 µA |
| 1    | -52.05 µA | -160.3 µA |
| 10   | -39.42 µA | -150.7 µA |
| 25   | -33.71 µA | -150.1 µA |

Same downward-with-NPLC trend, but **`measure.v()` overflowed and
`compliance`=true at every single NPLC value tested, on both channels** -
even the best case (NPLC=25) leaves a current 30-150x over the 1 µA limit,
so longer integration alone cannot rescue this measurement at the recipe's
actual intended limit. NPLC averaging clearly suppresses part of what's
happening but there is a large residual left over even at maximum
integration - this is not simply "integrate longer and the recipe's own
numbers would have worked."

**Part 3 - `source.highc` (compensation network tuned for driving high-
capacitance/reactive loads) forced ON, tight limiti=1e-6A, both channels:**
made things WORSE, not better - both `measure.v()` AND `measure.i()`
overflowed (`9.91e37`), where with the default `highc=0` only voltage did.
This is a genuine surprise and pushes back against a simple "just needs
capacitive-load compensation" framing of the leading theory - whatever
this load looks like to the source's control loop, the compensation network
built for capacitive loads makes it less stable, not more.

**Part 4 - `measure.autozero`** (OFF / ONCE / AUTO), `smua` only, tight
limit: no meaningful difference (-45.8/-46.5/-47.4 µA respectively, all
still overflow/compliant). Rules out autozero timing/internal-offset-
recalibration cycling as a factor.

**Part 5 - filter type MEDIAN vs REPEAT_AVG** (count=10), `smua` only,
tight limit: no meaningful difference (-47.5/-44.3 µA, both still
overflow/compliant). A median filter should reject sparse outliers/spikes
far better than an average would if the noise were spiky - getting the
same answer either way argues the disturbance is a persistent, continuous
signal rather than intermittent glitches.

**Part 6 - reversed source/measure roles**: sourced a small FIXED CURRENT
instead (1 nA, matching the gauge reference's real-leakage scale) with
`limitv`=10V, `smua` only. Hit the voltage ceiling (`measure.v()`=10.0019V,
i.e. voltage-compliant - could not source even 1 nA within 10 V, meaning
the true leakage at this node needs less than 1 nA at 10 V, consistent with
the DMM's near-infinite finding) - but `measure.i()` ALSO overflowed
(`9.91e37`) and `source.compliance`=true. So the disturbance overwhelms the
measurement in EITHER source mode (voltage- or current-sourcing), not just
the voltage-source configuration the recipe happens to use.

**Updated understanding**: the NPLC dependence is the strongest,
quantitative confirmation yet of a real periodic/AC-like disturbance riding
on the contact node (not a one-time capacitive transient, not a fixed DC
leak) - "flat, non-decaying across repeated reads" from the earlier
observation and "shrinks close to 1/NPLC" from this test are two
independent lines of evidence for the same thing. It is channel-A-vs-B
asymmetric in EXACTLY the way every other test in this doc has been. It is
NOT fixed by `highc` (gets worse), autozero mode, or filter type
(median vs average makes no difference - not spiky), and NPLC alone cannot
rescue the measurement back within the recipe's actual 1 µA limit even at
maximum integration. The disturbance is large enough to blow past the ADC
in current-source mode too, at a 1 nA target - i.e. it isn't specific to
how the SMU happens to be configured, it's present and dominant regardless
of source mode.

**Suggested next steps, updated**:
1. **NEXT TEST TO RUN - line frequency check, verified against
   `references/keith2636b manual.pdf` (added this session), 100% GPIB, no
   equipment needed.** Two real TSP attributes, confirmed in the manual
   (search "Line frequency configuration", section 2-15 / command ref
   7-137/7-139):
   - `localnode.linefreq` - the power line frequency (50 or 60) the
     instrument uses for NPLC aperture calculations.
   - `localnode.autolinefreq` - boolean. Factory default `true`: the
     instrument auto-detects the real line frequency at every power-up and
     sets `linefreq` accordingly. **Manually writing to `linefreq` directly
     silently flips `autolinefreq` to `false`** - so if anything ever set
     it explicitly in the past, auto-detection stopped from that point on
     and it may be sitting on a stale value.

   Step 1 (read-only, do this first, changes nothing):
   ```
   print(localnode.linefreq)
   print(localnode.autolinefreq)
   ```
   - `autolinefreq=true` -> it's been auto-detecting every power-up, so
     `linefreq` should reflect what the instrument itself measured at the
     wall; still worth reporting what number comes back - if it says 50 in
     a US facility (or 60 somewhere on 50 Hz mains), that's odd even with
     auto-detect on.
   - `autolinefreq=false` and `linefreq` looks right for the location ->
     probably not the cause.
   - `autolinefreq=false` and `linefreq` looks WRONG for the location ->
     likely root cause, one-line fix.

   Step 2 (only if step 1 looks suspicious, or to test the hypothesis
   directly): `localnode.linefreq = 60` (or `50`, whichever it wasn't),
   then re-run the exact same NPLC=1 current reading on die 'third'
   (contact still made, same crosspoints as the NPLC-sweep test above) and
   compare against that test's own NPLC=1 row. Sharp drop -> confirmed,
   fix is to leave it set correctly (or restore
   `localnode.autolinefreq = true` if auto-detect should just be trusted
   going forward). No real change -> restore `autolinefreq = true` and
   rule this specific theory out.

2. Since `highc` made it worse rather than better, don't keep chasing a
   pure-capacitance framing - an oscilloscope or spectrum-style
   measurement at the point of contact (needle/probe-card connector) that
   can show actual frequency content, not just "is there voltage," is the
   most direct remaining way to identify what this signal actually is, if
   equipment becomes available (none on hand as of this update).
3. The channel A-vs-B asymmetry (present in literally every test in this
   document, including this NPLC one) is consistent enough across
   completely different test types that it is worth tracing physically -
   compare the actual cable runs / connector positions for rows A/B vs
   rows C/D between the switch matrix and wherever they terminate, since a
   real pickup mechanism (proximity to a noise source, loop area, shielding
   quality) would plausibly differ that way, while a software/firmware
   explanation would not.
4. **Alternative source/measure pair - CORRECTED methodology (the line-
   frequency test below has since ruled that theory out, making this the
   leading next test).** Original version of this item wrongly assumed the
   DMM could be wired "in series" through the switch matrix to read
   current directly - it can't. The 707B is a crossbar: closing a row onto
   a column only ties that instrument in PARALLEL onto that column's one
   physical wire. There is no way to splice an instrument in series
   without physically breaking the wire (the same kind of manual step as
   the pin-disconnect tests earlier), so a true series ammeter reading via
   the DMM is not possible through crosspoints alone.

   **Corrected test**, using die 'third' (columns 8=HI, 7=LO, per its own
   `conn="2A08,2B07"`) as the concrete example - four crosspoints closed
   AT THE SAME TIME, two for biasing, two for sensing, both pairs landing
   on the exact same two physical columns:
   - Bias: close `2G08` (WGEN CH1, row G, onto column 8) and `2B07` (SMU-A
     LO, row B, onto column 7 - reused as the return per
     `switch_topology.py`'s own "wave" step convention). WGEN sources
     ~10 V DC (its "DC" output shape) across pins 7/8, same as the SMU
     normally does, just with WGEN supplying the HI side.
   - Sense: close `2F08` (DMM HI, row F, onto the SAME column 8) and
     `2E07` (DMM LO, row E, onto the SAME column 7) - **in parallel** with
     the bias, not in series. This only works because the DMM, in VOLTAGE
     mode, is high-impedance (megaohms) and barely loads the node - like
     clipping a voltmeter across a live wire without cutting it. **The DMM
     must stay in voltage mode** - in current/ammeter mode this same
     parallel wiring would look like a near dead-short across the WGEN's
     output.
   - Current is not read directly - it's inferred. The WGEN's output has a
     known, fixed source impedance (typically 50 ohm) and, unlike the SMU,
     does not actively servo to hold 10 V under load - its actual output
     voltage sags proportional to whatever current is drawn. So: read the
     real voltage at the pad with the DMM, then
     `I = (10 V - V_measured) / 50 ohm`.
   - Same offset current (inferred) still appearing this way -> further
     rules out a 2636B-specific quirk, since neither the sourcing nor the
     sensing instrument is the 2636B anymore. A clean/near-10V result
     instead would be a significant, surprising pivot needing
     reconciliation against the open/short bracket tests above.

### Line-frequency test RUN (step 1 above) - checked, then directly swap-
tested - RULED OUT (fresh session, same day, GPIB only)

**Step 1, read-only**: `localnode.linefreq = 60`, `localnode.autolinefreq
= true` - it has been auto-detecting at every power-up, and 60 Hz is
correct for this facility's mains. Nothing looks wrong on its face.

**Step 2, direct empirical swap-and-retest anyway** (per the plan's own
"or to test the hypothesis directly"): forced `localnode.linefreq = 50`
(confirmed this silently flips `autolinefreq` to `false`, exactly as the
manual says), then re-ran the identical NPLC=1 reading on die 'third',
same crosspoints/limits as the recorded NPLC-sweep baseline:

| channel | linefreq=50 (forced) | 60 Hz baseline (correct, auto-detected) |
|---|---|---|
| smua | -5.90e-06, -4.50e-06 A | -4.68e-06 A |
| smub | -3.360e-05, -3.305e-05 A | -4.290e-05 A |

**No meaningful change** - `smua` is essentially the same order of
magnitude (if anything marginally higher), `smub` is ~20% lower, well
inside the run-to-run variability already seen everywhere else in this
doc. A genuine line-frequency mismatch should have made the residual
noticeably WORSE at a deliberately wrong setting, not roughly the same.
Restored `localnode.autolinefreq = true` immediately after (confirmed via
readback) - never left forced.

**This specifically rules out "the instrument's line-frequency setting is
wrong" as the cause of the 1/NPLC scaling.** The setting was already
correct before this test even started. The 1/NPLC scaling itself remains
real and reproduced twice now - it's just not fixable/explained by
`localnode.linefreq`/`autolinefreq`. Either the disturbance really is mains
pickup at the (already correct) 60 Hz that NPLC-based integration can't
be tuned to reject any better than it already does, or the periodic-looking
scaling comes from something else entirely that happens to average down
with longer integration for unrelated reasons. The next items in the list
above (oscilloscope/spectrum check at the contact point; the WGEN+DMM
alternative source/measure pair) are now the more promising directions,
since the line-frequency-specific fix is closed off.

### New recipe added: `lampaccr_wgen` - runs the corrected WGEN+DMM test
through the actual Recipe/Run tab, not just an ad hoc GPIB script

Added directly to `\\prober\M\ETL\proberautomation\LAMPATA\probe_cards\
LaMP_HP_b.csv` (34 new rows: 1 `RECIPE` header row + 33 `STEP` rows -
backup saved alongside as `LaMP_HP_b.csv.bak_before_lampaccr_wgen_add`).
Verified by reading it back with `csv.DictReader` - all fields land in the
right named columns, existing `lampaccr` content untouched (line-by-line
diff against the pre-edit file showed zero changes to any existing row).

Mirrors `lampaccr`'s own per-die structure (touch -> 4 die blocks -> each
followed by a settle/check/open/delay sequence), but implements the
corrected WGEN+DMM methodology from the "Alternative source/measure pair"
item above instead of the SMU, for all four of `lampaccr`'s real dies -
same columns each die already uses (`first`=4/5,6 `second`=4/7,8
`third`=2/8,7 `fourth`=2/6,5), same die-attribution field. Per die N:

```
biasN    (wave/apply/WGEN/CH1/DC/10V)  - closes WGEN HI (row G) + SMU-A LO
                                          (row B, reused per switch_topology's
                                          own "wave" convention) onto the
                                          die's real HI/LO columns
waitN    (delay, 200ms)                - settle after bias-on, before read
readN    (current/measure/DMM)         - closes DMM HI/LO (rows F/E) onto
                                          the SAME two columns, in parallel
                                          with the still-live bias, DMM in
                                          DC CURRENT mode (changed from the
                                          original voltage-mode design - see
                                          "readN switched to current" below)
settleN  (delay, 100ms)                - mirrors lampaccr's own post-
                                          measure pacing
checkN   (passfail, target=readN,
          min=0, max=1e-07)            - PASS = current stayed near-zero
                                          (real leakage-scale); FAIL = a
                                          large current was drawn - mirrors
                                          lampaccr's own tightened check
                                          spec convention
openbiasN (open, target=biasN)         - releases the WGEN crosspoints
                                          (and turns its output off, since
                                          biasN is mode=apply)
openreadN (open, target=readN)         - releases the DMM crosspoints
delayN   (delay, 200ms)                - pacing before the next die
```

**readN switched to current (this update)**: originally `voltage`/measure -
see "IMPORTANT CAVEAT" and the "WGEN+DMM test actually RUN" section below
for why a single reading of either kind at this specific node has already
been shown to be unreliable. Worth being explicit about what DC CURRENT
mode means electrically here, since it's different from the voltage-mode
case: the DMM's ammeter input is LOW impedance (by design - an ammeter
needs a low burden voltage), so closing it in parallel onto the same two
columns as the WGEN's bias doesn't just "tap" the node non-invasively the
way voltage mode did - it creates a real near-short path across the WGEN's
own HI/LO output, in parallel with whatever the actual contact impedance
is. The "current-mode version" test already run (see below) measured
-2.70 to -3.83 nA this way, which does NOT match a simple "~10V into a
near-short through the DMM's ammeter" expectation (that would imply
current dominated by the WGEN's own ~50 ohm output impedance, i.e. tens of
mA, not nanoamps) - the mismatch between that expectation and the actual
reading is exactly what triggered the deeper isolation work below, and
that work's own conclusion (step 4, the decisive test) is that a single
reading here - current OR voltage, from any instrument - is not a
reliable/repeatable characterization of this node at all. Changing to
current mode does not resolve that; it's logged as requested, with this
caveat attached.

**Not yet re-run since this change** - `min`/`max`=0/1e-07 A is a
first-pass guess mirroring `lampaccr`'s own tightened check spec, not
validated against this recipe's own real data yet.

**IMPORTANT CAVEAT, not a fully SMU-free test**: `smua`'s LO row (row B)
is still closed onto each die's LO column, reused as the WGEN's return
path (see `biasN` above). `smua`'s HI row (row A) is never closed and
`smua.source.output` stays off the whole time, so the SMU's ACTIVE
sourcing/compliance circuitry plays no role in this test - but its LO
terminal, and whatever internal reference/ground that terminal ties back
to inside the instrument, is still physically part of the loop. This is
not a topology mistake - `switch_topology.py`'s default 8-row layout has
no dedicated WGEN LO row at all (all 8 rows are already SMU-A HI/LO,
SMU-B HI/LO, DMM HI/LO, WGEN CH1/CH2 HI-only), and the DMM's own LO can't
substitute as the return since it's a high-impedance sense input, not
something that can carry real bias current - a signal generator needs a
genuine low-impedance return, and SMU-A's LO row is the only one available
here that provides one.

Consequence for interpreting the result: an anomaly still appearing proves
it doesn't need the SMU's active sourcing/compliance behavior (still
meaningful) - it does NOT fully rule out the SMU's mere passive presence
(via that still-connected LO/ground path) playing some role, since that
path is genuinely still in the circuit. A truly SMU-free version would
need a physical clip lead from the WGEN's own LO terminal straight to a
chassis ground point, bypassing the switch matrix's row assignments
entirely - the same category of manual step as the earlier pin-disconnect
tests, not something achievable via crosspoints alone.

### WGEN+DMM test actually RUN (both variants) - result is NOT clean, and
the real finding is bigger than either variant alone suggested (fresh
session, same day, GPIB only, wafer touching, die 'third')

Ran both the original (current-mode) and corrected (voltage-mode) WGEN+DMM
methodology from the two sections above, then chased down why they
disagreed. Four steps, in order:

1. **Current-mode version** (`2G08`+`2B07` bias, `2F08`+`2E07` DMM in DC
   current mode): DMM read **-2.70 to -3.83 nA** - looked like the clean
   "real leakage" cluster from `references/gauge example.xlsx`.
2. **Voltage-mode version** (same crosspoints, DMM switched to DC voltage,
   current inferred via Ohm's law from WGEN's ~50 ohm source impedance):
   DMM read only **-0.5 to -2.2 mV** (not the ~10 V a clean open should
   show) - inferring **~200 mA**, wildly different from step 1 and not
   physically sane for a die that DMM's own plain 2-wire check has always
   read as open.
3. **Isolating why**: tested row B (`smua`'s LO, reused as the return per
   the "wave" convention) alone, output "off", on a spare column, DMM
   voltage-tapped on that same node - readback was tighter/quieter
   (~0.3-0.4 mV spread) than a genuinely floating pair on two different
   spare columns with nothing closed at all (~6 mV spread). This pointed
   at row B behaving as a low-impedance clamp rather than a passive wire
   when `source.output=OFF` (consistent with `OUTPUT_HIGHZ` not being a
   real constant on this instrument - confirmed nil earlier this session).
   Tried the fix of putting `smua` into a genuine 0 A current-source mode
   (`source.func=OUTPUT_DCAMPS`, `leveli=0`, `limitv=20`) instead of
   "output off," which should present true high impedance - the isolated
   test's noise level barely changed with the fix applied, which in
   hindsight was because the ORIGINAL isolation test never closed a DMM LO
   row either time, so it wasn't cleanly isolating the variable it meant
   to (a genuine methodology gap - flagging honestly rather than standing
   behind the row-B-is-a-clamp conclusion as confirmed).
4. **The decisive test**: bypassed the DMM's differential setup entirely
   and used `smua` itself - the SAME validated 0 A-current-source high-Z
   voltmeter trick - wired directly onto die 'third's own HI column
   (`2A08`+`2G08`, nothing else closed at all). Sanity check passed first:
   with WGEN's output off, `smua` correctly railed to its own 20 V
   compliance ceiling (`19.999 V`) - exactly what an ideal 0 A source
   should do into a genuinely open node, confirming the technique itself
   works. Then WGEN was commanded to 10 V and turned on:

   | read | smua.measure.v() |
   |---|---|
   | 1 | 2.658 V |
   | 2 | 0.813 V |
   | 3 | 0.332 V |
   | 4 | 4.207 V |
   | 5 | 9.430 V |

   **Five successive reads, no settling, no pattern, spanning nearly the
   entire 0-10 V range.** `smua.measure.i()` overflowed (`9.91e37`) during
   this too, even in current-source mode - the same overflow signature
   seen throughout this whole document, now reproduced with a completely
   different source instrument (WGEN) and a completely different SMU
   operating mode (0 A current source, not voltage source).

**This reframes steps 1-3 above and everything built on the "clean WGEN+
DMM result" premise (including the newly-added `lampaccr_wgen` recipe's
single-voltage-reading-per-die design)**: the physical contact node is not
settling to any stable value when actively driven, by ANY instrument -
SMU voltage-source, SMU current-source, and now WGEN, all three show
invalid/unstable readings at this exact real-contact node while all
reading perfectly clean on dangling wires, true shorts, and spare columns.
Steps 1 and 2's very different-looking numbers (-3 nA vs ~200 mA-
equivalent) were almost certainly both just single frozen snapshots of
this same underlying chaos, sampled at different instants by different
instruments with different aperture/integration behavior - neither
represents a real, repeatable DC value. **A single voltage or current
reading per die, from any instrument, is not a reliable way to
characterize this specific real-contact condition** - `lampaccr_wgen`'s
current design (one `readN` per die) should not be trusted to produce a
repeatable pass/fail until this is accounted for (e.g. many rapid reads
per die with the spread itself reported, not just one value against a
fixed min/max).

This is also now the single most concrete piece of evidence in the whole
investigation for "real instability at the contact point" over any
instrument-specific theory - it survived a complete change of both the
sourcing instrument (WGEN instead of SMU) and the sensing method (SMU's
own current-source-mode voltmeter, completely independent of the DMM's
setup that produced steps 1-2's confusing numbers). The oscilloscope/
spectrum check at the point of contact remains the most direct way to
actually characterize this instability (frequency, amplitude, whether
it's periodic or chaotic) - everything GPIB-only has now been tried and
consistently shows instability without being able to characterize its
real nature further.

### CORRECTION to the above: the "chaotic instability" (step 4/Stage W)
was very likely my own methodology mistake, not a real finding - and the
current-mode reading IS repeatable (fresh session, same day, GPIB only)

The step-4 "decisive test" directly above closed `2A08` (row A, `smua`'s
HI) and `2G08` (WGEN) together, with `smua` actively configured as a 0 A
current source (`output=ON`) - **but `smua`'s own LO row (row B) was never
closed at all in that test.** Running an SMU's active current-source loop
with its own return/LO terminal completely disconnected from anything is
an invalid measurement setup on its own - there is no way for that
feedback loop to reference against anything real, and instability under
those conditions doesn't require any real fault at the contact point at
all. This was a real gap in that test's design, found while trying to
reconcile it against the result below - retracting the strength of that
"chaotic instability at the contact point" conclusion. It shouldn't have
been presented as settled.

**Direct repeatability check of the current-mode WGEN+DMM reading**
(user's own test requirement is literally "bias 10 V, read current" - this
checks whether that specific measurement, done via WGEN+DMM instead of the
SMU, is actually trustworthy): 10 FULLY INDEPENDENT trials on die 'third'
(`2G08`+`2B07` bias - `smua` output OFF this time, not actively sourcing
anything, just lending its LO row as the return, exactly as the original
current-mode test did; `2F08`+`2E07` DMM in DC current mode) - each trial
a complete close -> bias-on -> read x3 -> bias-off -> open cycle, not just
repeated reads within one continuous bias:

```
trial 1:  -2.54e-09, -3.28e-09, -2.75e-09 A
trial 2:  -4.03e-09, -2.96e-09, -3.22e-09 A
trial 3:  -3.17e-09, -4.47e-09, -2.93e-09 A
trial 4:  -3.64e-09, -4.11e-09, -3.33e-09 A
trial 5:  -3.98e-09, -3.81e-09, -3.20e-09 A
trial 6:  -3.61e-09, -3.81e-09, -2.82e-09 A
trial 7:  -2.76e-09, -3.78e-09, -3.30e-09 A
trial 8:  -4.24e-09, -3.26e-09, -3.29e-09 A
trial 9:  -3.18e-09, -4.13e-09, -3.01e-09 A
trial 10: -4.30e-09, -3.15e-09, -3.53e-09 A
```

All 30 readings across 10 independent bias cycles land in a tight
**-2.5 nA to -4.5 nA** band - genuinely repeatable, not a lucky single
snapshot. This directly supports (contrary to this doc's immediately-
preceding conclusion, and contrary to the caveat just attached to
`lampaccr_wgen`'s `readN` current-mode change above) that **the WGEN(10V)
+ DMM(current mode) reading, with `smua` genuinely off and only lending
its LO row as a passive return, IS a repeatable way to do "bias 10 V, read
current" on this node** - it just doesn't match the SMU's own reading at
all (nA here vs tens-to-hundreds of µA from the 2636B), and matches the
gauge reference's real-leakage cluster far better than anything the SMU
itself has produced on this bench.

**Still unresolved, flagged rather than papered over**: the voltage-mode
version of this exact same circuit (same crosspoints, `smua` in the same
state, only the DMM's function changed) read near-0 V instead of the
~9.9995 V that a genuine few-nA current into a very high DUT impedance
should produce - directly contradicting the current-mode result's
implied high impedance. That contradiction has NOT been explained yet -
possible next step: repeat the voltage-mode version with the same 10-trial
repeatability structure used here, to check whether IT is also repeatable
(just at a value that doesn't match simple Ohm's-law expectations, meaning
the DMM's own voltage-mode loading or some other effect needs
accounting for) or whether it was itself a one-off anomaly.

### New recipe added: `lampaccr_wgen_repeat` - the validated 10-trial
repeatability method as a real, runnable recipe (different structure from
`lampaccr_wgen`)

`lampaccr_wgen` (added earlier) does ONE bias-on/read/open cycle per die -
that structure was never actually what confirmed repeatability above; the
10-independent-cycles test was. Rather than editing `lampaccr_wgen` again,
added a separate recipe so both remain available side by side. Added
directly to `LaMP_HP_b.csv` (322 new rows: 1 `RECIPE` header + 321 `STEP`
rows - backup saved as
`LaMP_HP_b.csv.bak_before_lampaccr_wgen_repeat_add`). Verified via
`csv.DictReader` after writing - 321 unique STEP names, exactly 10
`current`-type read steps per die, `avg_count=3` on every read, correct
values in every named column - and a line-by-line diff against the
pre-edit file confirmed zero changes to any existing row (`lampaccr` and
`lampaccr_wgen` both untouched).

Same four real dies/columns as the other two recipes. Per die, the exact
validated structure repeated for **10 independent trials**, each its own
full close -> bias -> read -> open cycle (not just repeated reads within
one continuous connection):

```
bias{die}_{trial}    (wave/apply/WGEN/CH1/DC/10V) - closes WGEN HI (row G)
                                                      + smua's LO (row B,
                                                      passive return only -
                                                      smua.source.output is
                                                      never turned on
                                                      anywhere in this
                                                      recipe, matching the
                                                      validated test's own
                                                      setup, NOT the
                                                      retracted "smua as
                                                      active 0A current
                                                      source" methodology)
wait{die}_{trial}    (delay, 200ms)
read{die}_{trial}    (current/measure/DMM, avg_count=3) - three real,
                                                      independent DMM
                                                      queries per trial
                                                      ("read x3"), DMM
                                                      closed in parallel
                                                      onto the same two
                                                      columns as the bias
settle{die}_{trial}  (delay, 100ms)
check{die}_{trial}   (passfail, target=read{die}_{trial}, min=0,
                       max=1e-07) - mirrors lampaccr's own tightened spec
openbias{die}_{trial} (open, target=bias{die}_{trial}) - closes WGEN
                                                      output + opens its
                                                      crosspoints
openread{die}_{trial} (open, target=read{die}_{trial}) - opens the DMM's
                                                      crosspoints
delay{die}_{trial}   (delay, 200ms)
```

**Not yet run.** Once it is, the results table will have 4 dies x 10
trials x 3 reads = 120 individual current readings, plus the 10-trials-x-1
averaged value the passfail/results logic actually records per trial - a
direct, repeatable stand-in for the raw 30-per-die numbers already
gathered manually above, but reusable going forward through the normal
Run tab instead of another one-off script. Note this recipe only carries
forward the CURRENT-mode side of the validated methodology (the
still-unresolved voltage-mode contradiction noted just above is not yet
built into a recipe - would need its own variant with `readN` set back to
`voltage` if that gets tested with the same 10-trial structure next).

**REMOVED (this update)** - user didn't need 10 trials in recipe form.
All 322 rows deleted from `LaMP_HP_b.csv` (backup saved as
`LaMP_HP_b.csv.bak_before_lampaccr_wgen_repeat_remove`, verified `lampaccr`
and `lampaccr_wgen` both untouched). The validated methodology and its
30-reading result are still fully documented above if needed again -
just not present as a loadable recipe on the card anymore.

### Two real problems found checking `lampaccr_wgen`/`lampaccr_wgen_repeat`
directly - NOT ready to trust as-is (fresh session, same day)

User asked directly "is `lampaccr_wgen` good?" Checked the actual CSV rows
on the network share and the real pass/fail code - two separate, concrete
issues, independent of each other:

**1. The passfail checks will FAIL every die regardless of the actual
result.** `gui/instrument_panel.py`'s passfail evaluation
(`verdict = ((not mn or value >= float(mn)) and (not mx or value <=
float(mx)))`) compares the RAW SIGNED recorded value directly - no
implicit `abs()`. That only happens if the read step's own `abs_value`
field is set (`_exec2_maybe_abs`, applied once at the read step, not the
check step). Checked both recipes' actual `readN` rows on the CSV
directly - `abs_value` is empty on every one of them. Every current
reading observed in this entire investigation, from any instrument on any
die, has come back NEGATIVE. With `check1-4` at `min=0, max=1e-07`, a
real reading like -3e-09 fails the `>= 0` bound immediately regardless of
its magnitude - **both recipes as currently written will show FAIL on
every single die, every run**, independent of whether the die is actually
good. Fix: set `abs_value` on the `readN` steps (or change `min` to
something negative, e.g. `-1e-07`, to make the range symmetric).

**2. Bigger problem - the reading doesn't actually respond to the wafer at
all.** User put the chuck back down (no contact) and asked to verify the
method still makes sense. Ran the exact validated circuit (`2G08`+`2B07`
bias, `smua` output off/passive return, `2F08`+`2E07` DMM current mode),
5 independent trials, chuck down:

```
trial 1: -2.40e-09, -2.09e-09, -3.43e-09 A
trial 2: -2.29e-09, -2.88e-09, -2.40e-09 A
trial 3: -1.88e-09, -1.87e-09, -2.79e-09 A
trial 4: -2.56e-09, -1.98e-09, -1.81e-09 A
trial 5: -2.07e-09, -3.69e-09, -2.32e-09 A
```

**-1.8 nA to -3.7 nA - essentially indistinguishable from the in-contact
10-trial result (-2.5 to -4.5 nA) recorded above.** The reading does not
change whether a real wafer is touching the needle or not. This means the
~3 nA number that looked like a clean validation of the WGEN+DMM method is
actually a **fixed offset baked into the WGEN/DMM/row-B measurement path
itself** (most likely a real, small leakage/offset current in the wave
gen's own output stage, the DMM's input bias current, or the row-B/switch-
matrix path - not yet isolated further), not a measurement of the die at
all. It is repeatable, but it is not sensing the DUT.

**Practical consequence**: even after fixing problem 1's sign bug, neither
recipe can currently distinguish "real contact with a good (near-infinite)
die" from "nothing connected at all" - both read the same ~2-4 nA. It
would still likely catch a genuinely bad/leaky/shorted die if that fault
draws current well above this few-nA floor (a real short would blow past
it easily), but it cannot resolve down to the gauge reference's own
~0.6-1 nA "good die" scale - the method's own floor is already 3-5x above
that, before any real die leakage is even added in. **Do not treat this as
a validated replacement for `lampaccr`'s SMU-based check yet** - it needs
its own offset characterized and subtracted (or the offset's source found
and removed) before the small-signal numbers it produces mean anything
about the actual die.

**Problem 1 fixed (this update)**: `abs_value` set to `1` on all four
`readN` steps in `lampaccr_wgen` (verified - only those 4 fields changed,
backup `LaMP_HP_b.csv.bak_before_wgen_abs_value_fix`). Problem 2 (the
fixed-offset/not-sensing-the-die issue) is NOT fixed by this and has no
simple mechanical fix - `lampaccr_wgen` still should not be trusted as a
real pass/fail check until that's resolved.

### Where this leaves "is the SMU broken" - both textbook extremes already
passed; next step is a known-value load, not another instrument swap

Both true-open and true-short tests earlier in this doc came back
perfectly clean on the 2636B (sub-picoamp on open, pinned exactly at
`limiti` on short, on both channels) - the SMU already passed the two most
basic checks you can throw at it electrically, which argues against a
simple hardware fault in this unit. The WGEN+DMM comparison that looked
like it was building toward "a different instrument reads this cleanly"
has since been invalidated (the offset-doesn't-track-contact finding just
above) - it was never actually sensing the die, so it isn't evidence about
the SMU's correctness either way anymore.

**Most useful next GPIB-only test, not yet tried**: a KNOWN-VALUE load,
not another open/short extreme. If a precision resistor (ideally in the
1-10 Mohm range, closer to what a real high-impedance DUT should look
like than a dead short or true open) is available, connect it directly to
the SMU - bypassing the switch matrix and probe card entirely - source
10 V, and confirm the reading matches the resistor's known value to
within normal accuracy spec. Open and short only test the two extremes;
this tests whether the SMU is accurate on a real, moderate, non-trivial
impedance, which is closer to what the actual node under contact should
resemble if it's behaving like a real (if very high) resistance.

**Most direct way to test the specific chassis, if available**: swap in a
genuinely different physical SMU (a second 2636B, or any working bench
SMU) in place of this one and repeat the real-contact test on die 'third'
unchanged otherwise. Same anomaly on a different physical unit -> not this
chassis's hardware, a real property of the contact that any properly
functioning SMU would show. Clean result on the different unit -> points
specifically at this chassis (calibration, an internal fault, firmware) -
worth then checking this unit's calibration due date/status too, a
non-technical thing to rule out first if easy to check.

### Short test + open-in-voltage-mode RUN - the whole WGEN+DMM+row-B
measurement path does not respond to the external circuit AT ALL, in
either mode (fresh session, same day, GPIB only) - SUPERSEDES the
"validated, repeatable" framing given to the current-mode reading above

User asked for a shorting test (bracketing the other DC extreme, "with
limits on wavegen" since WGEN has no active current limit like the SMU -
just a fixed ~50 ohm output impedance). Forced a hard short between two
SPARE columns (01, 02 - not any real die) via WGEN CH2's row (H),
otherwise unused all session, closed onto both columns at once - ties them
together through that shared bus, no physical rewiring needed. Safety:
`SOURce1:VOLTage:LIMit` set to +/-1 V and the test voltage itself reduced
to 1 V (from the usual 10 V) before biasing into the short.

| condition | current mode | voltage mode |
|---|---|---|
| open (dangling, no bridge, spare columns) | -2 to -4 nA (Stage Y, no-contact test above) | mostly -0.3 to -1 mV, one wild outlier at **-325.7 mV** |
| real die, in contact (die 'third', 10 trials above) | -2.5 to -4.5 nA | ~-0.5 to -1.3 mV |
| deliberate short (forced via row H, spare columns) | -1.7 to -4.5 nA | ~-0.9 to -1.5 µV |

**Voltage mode reads near-0 V on all three conditions, including the
genuine open circuit** - which should read close to the full commanded
voltage (negligible current, negligible drop across WGEN's 50 ohm source
impedance) and does not. Current mode reads the same ~2-4 nA regardless of
load too. **Open, short, and real contact are electrically
indistinguishable through this measurement path, in either mode.** This is
not a property of the DUT or the contact - the measurement path itself
(WGEN via row G, DMM via rows F/E, `smua`'s row B as the return) is not
reflecting what is actually connected, under any of the three conditions
tested.

**This retracts the "validated, repeatable" framing given to the current-
mode reading in the correction section above.** Repeatable is not the same
as correct - the -2 to -4 nA number is real and reproducible, but it is
reproducible because it does not respond to anything, not because it is
measuring real leakage. That should have been caught by testing the open
condition in voltage mode earlier; it wasn't, and the intervening
conclusion overstated confidence in a number that turned out to be
disconnected from the actual circuit.

**Root cause not yet found** - leading suspect: row G (WGEN CH1's
designated crosspoint row per `switch_topology.py`) may not actually
deliver WGEN's signal to the switch matrix's columns at all. Every test in
this document before today used only rows A/B/C/D/E/F - **row G (and H) has
never been independently verified this entire investigation**, only
assumed correct from the topology file's declared mapping. A bad/miswired
row-G connection would explain every result above without needing any
theory about the DUT, the contact, or a "measurement path artifact" at
all - the column would simply never see WGEN's real signal regardless of
what else is connected.

**Suggested next step**: verify row G independently of everything else in
this chain - e.g. with a handheld meter directly at the switch matrix's
row-G terminal block (physical, not GPIB), or by finding a way to sense a
column driven by row G using an instrument/row combination not yet tried
in this investigation (rows C/D, the SMU's B-channel HI/LO, have also
never been used to sense a WGEN-driven column - worth trying before
assuming row G itself is bad, in case the issue is instead specific to
how row B/E behave rather than row G).

**Practical conclusion for now**: do not use the WGEN+DMM approach (either
mode) as a stand-in for `lampaccr`'s SMU-based check, and do not trust
`lampaccr_wgen`/`lampaccr_wgen_repeat`'s recorded values as meaningful
until row G (or whatever the real root cause turns out to be) is
independently confirmed working.

### ROOT CAUSE FOUND: it's row B, not row G - confirmed by swapping the
sensing instrument (fresh session, same day, GPIB only) - plus a real
infrastructure bug found and worked around along the way

Per the suggested next step above, tried sensing a WGEN-driven column with
`smub` (SMU channel B, rows C/D) instead of the DMM (rows F/E) - a
completely independent sensing instrument, sharing nothing with the DMM
setup except `smua`'s row B as the return. `smub` configured as a
validated 0 A current-source high-Z voltmeter (same technique as earlier
in this doc), with BOTH its HI and LO properly closed this time (unlike
the earlier retracted "chaotic instability" test, which left `smub`/`smua`'s
own LO floating - see the correction section above).

**Infrastructure bug found first, before trusting any of this**: the very
first attempt at this test returned nonsense - `smub.measure.v()` came
back as the literal string `true`, and later reads showed an impossible
~20 A "current" from a 0 A source. Diagnosed by sending distinctive marker
queries (`print(999000)`, `print(999001)`, ...) and comparing expected vs
actual: **every single response on this SMU connection was the answer to
the PREVIOUS query, not the current one** - a persistent one-query lag
that did not self-correct even after 6 additional flush attempts (each
new query just perpetuates the same one-item offset). Root cause of the
lag itself not identified (possibly a retry/duplicate-command artifact in
the VISA/ADLINK layer - this session already logged one real `VI_ERROR_TMO`
timeout on this same SMU earlier, so the link has shown at least one other
communication irregularity). **Workaround verified and used for
everything below**: send each query twice, keep the second response (the
real, current answer to the first send) - confirmed against a known value
(`smub.source.func` right after `reset()` correctly read exactly `1.0` =
`DCVOLTS`, the true default, only once this workaround was applied).

**With trustworthy reads confirmed, the actual result**:

| state | smub.measure.v() (via rows C/D) |
|---|---|
| WGEN off (0 V) | -19.4 mV |
| WGEN commanded to 10 V | 27.2, 35.2, 34.8, 37.4, 27.7 mV |

Tight and repeatable, but **still nowhere near 10 V - and this is via
completely different rows than the DMM's F/E.** Two independent sensing
instruments (DMM and `smub`), sharing nothing but `smua`'s row B, both see
the same collapse. This rules out the DMM specifically and rules out row G
specifically (a bad row G would not explain why a *different* sensing
path, through *different* rows, shows the identical symptom) - **the one
thing common to every failed WGEN test in this document is `smua`'s row B
being reused as the return.**

**Conclusion: row B is not a passive, high-impedance return the way the
"wave" step convention assumes - it is a real, low-impedance node that
clamps the whole circuit low, regardless of what WGEN commands and
regardless of which instrument senses the result.** This single
explanation accounts for every "doesn't respond to load" finding in the
entire WGEN investigation phase (the open/short/contact indistinguishability
above, the flat ~2-4 nA current floor, the near-0 V voltage-mode readings)
without needing a bad row G, a DMM-specific artifact, or any property of
the DUT/contact at all. It does NOT explain the ORIGINAL SMU-based
`lampaccr` anomaly (that circuit uses row A actively sourcing + row B as
its OWN channel's return together, a properly closed loop, not row B
borrowed passively by a different instrument) - this finding is specific
to the WGEN-as-source experiments, not a new explanation for the original
compliance mystery.

**This also means a genuinely SMU-free WGEN test is still not possible via
crosspoints alone** - not just "not fully independent" as flagged earlier,
but actively invalidated by row B's real behavior. A true SMU-free test
needs an actual physical low-impedance return for WGEN that is NOT row B -
e.g. a physical clip lead from WGEN's own LO terminal to a genuine chassis
ground point, bypassing the switch matrix's row assignments entirely (the
same category of manual step as the pin-disconnect tests earlier this
investigation).

### Hypothesis tested and NOT confirmed: "compliance doesn't clamp
negative current" - but the underlying observation it came from is real
and worth keeping (fresh session, same day, GPIB only)

User ran the actual `lampaccr` recipe (SMU-based, real wafer contact) and
observed: `9.02709e-08` A (90 nA, fine), `-1.15082e-05` A (-11.5 µA, way
over the 1 µA limit), `9.9999e-07` A (999.9 nA, essentially exactly AT the
+1 µA limit), `9.9999e-07` A (same). Sharp observation: the only reading
that blew through compliance was negative; the two that landed right at
the limit were positive. Hypothesis: `smua.source.limiti` might not
enforce the limit symmetrically - i.e. positive compliance works,
negative doesn't.

**Tested directly on a known, controlled short first** (same short-
through-the-switch method validated earlier in this doc: HI+LO tied
together on one column, `2A07`+`2B07` for `smua`, `2C07`+`2D07` for
`smub`), at `+10V` and `-10V`, same `1e-6A` limit:

| channel | +10V | -10V |
|---|---|---|
| smua | +1.00001 µA (clamped, valid V) | -1.00004 µA (clamped, valid V) |
| smub | +1.00011 µA (clamped, valid V) | -0.99998 µA (clamped, valid V) |

**Compliance clamps perfectly symmetrically in both directions on a real
short, both channels.** This rules out "the limit doesn't affect
negative" as a general instrument-level bug.

**Then tested the more targeted version on the actual real die** (die
'second', the -11.5 µA die from the user's screenshot, its real recipe
crosspoints `4A07`+`4B08`, real wafer contact), at the recipe's normal
`+10V` and then reversed to `-10V`:

| | measure.v() | measure.i() (5x) | compliance |
|---|---|---|---|
| +10V (normal) | overflow | -11.66, -11.75, -11.76, -11.78, -11.76 µA | true |
| -10V (reversed) | overflow | -63.5, -61.3, -57.4, -53.5, -50.4 µA | true |

**The current stays negative in BOTH directions, and is actually LARGER
at -10V.** This rules out the two clean explanations at once: not a
compliance-sign bug (already proven false on a real short above), and not
a simple diode/rectifying real structure either (reverse bias should flip
the sign or shrink the current dramatically - it did neither). The sign
does not track the applied voltage's sign or scale simply with its
magnitude, on this specific real-contact anomaly - consistent with the
earlier voltage-sweep finding in this same document (Stage H, current
roughly flat across 0-10V at tight compliance) that the anomalous current
here behaves like SMU control-loop instability against a difficult,
marginal load, not a real sign-dependent leakage/diode current. The
original observation (3 of 4 real dies landing exactly at +1 µA, one
blowing far past it negative) is still real and worth keeping in mind,
just not explained by an asymmetric compliance limit - more likely a
coincidence of which dies happened to hit the unstable regime that
particular run (recall from much earlier in this document: the same die
has shown different magnitudes on different runs, e.g. -5.5, -15, -7.8 µA
across various sessions - a die landing near +1 µA one run and something
else the next would be consistent with that same run-to-run variability).

### Real 39 kohm resistor test - textbook-perfect on every axis, closes
off "it's a generic SMU/compliance bug" for good (fresh session, same day,
GPIB only, no switch matrix at all)

User's own idea, and a very good one: wire a real, known, physically
symmetric resistor DIRECTLY to an SMU channel's HI/LO terminals - no
switch matrix, no wafer, no ambiguity about what's actually connected -
and deliberately try to hit compliance, reverse polarity, sweep NPLC,
toggle `highc`, everything this document has tried against the real
contact anomaly. First attempt used `smua` and the resistor turned out not
to be connected yet (~1e14 ohm estimated - open circuit, caught and
corrected). Second attempt found it was wired to `smub`, not `smua` -
corrected, and got a clean read: **~39,160 ohm measured at a loose limit,
matching the user's own ~39k estimate exactly.**

Full battery at the real recipe condition and beyond, all via `smub`:

| test | prediction (Ohm's law, R=39.16k) | actual |
|---|---|---|
| 10V / 1e-6A limit (recipe's real condition) | V=39mV, I=1.000µA, compliance=true | V=39.16mV, I=1.00012-1.00013µA, compliance=true |
| -10V / 1e-6A limit | V=-39mV, I=-1.000µA, compliance=true | V=-39.19mV, I=-0.999984 to -0.999990µA, compliance=true |
| voltage sweep 0/1/2/5/8/10V, 1e-6A limit | identical clamp once V exceeds ~39mV | identical V≈39mV/I≈1.0001µA at 1V through 10V; near-zero at 0V (correctly not clamped) |
| `limiti` sweep 1e-7/1e-6/1e-5/1e-4/1e-3 A | I and V scale exactly with Ohm's law at each limit; NOT in compliance at 1e-3A (since 10V/39k = 256µA < 1mA) | matches at every single limit - 1e-7A: V=3.80mV/I=99.98nA; 1e-6A: as above; 1e-5A: V=391.7mV/I=10.004µA; 1e-4A: V=3.916V/I=100.011µA; 1e-3A: V=10.0007V/I=255.384µA, **compliance correctly FALSE** (256µA is under the 1mA limit) |
| NPLC sweep 0.01/0.1/1/10/25 | should be flat if this is a real, stable resistor | **completely flat** - I=1.0000-1.0002µA at every NPLC value, no dependence at all |
| `source.highc` 0 vs 1 | shouldn't matter for a purely resistive load | **no difference** - V≈39.1-39.2mV, I≈1.00012-1.00024µA either way |

**Every single reading across every single condition matches simple Ohm's
law exactly.** No overflow, no instability, no negative-sign anomaly
regardless of polarity, no NPLC dependence (contrast: the real die showed
current dropping ~8x from NPLC 0.1->25), no `highc` sensitivity (contrast:
`highc=1` made the real die's overflow WORSE). This is the same physical
channel (`smub`) that reads 150-190 µA with overflow and instability on
the real wafer, behaving with textbook precision on a real 39 kohm load
that genuinely needs to clamp 256x over the 1 µA limit.

**This closes off the last remaining "maybe it's a generic SMU/compliance
bug" theory.** The 2636B correctly implements Ohm's law and current-limit
clamping for any normal resistive load, including one that legitimately
needs to hit compliance hard, with excellent precision, on both channels
(the earlier short-through-the-switch test already showed the same for
both channels at a dead short - see above), in both polarities, across
every NPLC and `highc` setting tried. The instability documented
throughout this entire investigation is not something this SMU model or
this specific unit does generically under compliance - it is specific to
the real needle-to-wafer contact condition. Nothing left to isolate via
GPIB alone from here - an oscilloscope or spectrum-analyzer-style
measurement directly at the point of contact remains the most direct
remaining way to characterize what that condition actually is.
