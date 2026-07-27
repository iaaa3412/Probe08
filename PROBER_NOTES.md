# Electroglas 2001X — working notes

Everything established by driving the machine at GPIB0::29 through an ADLINK
USB-3488A, July 2026. Measured unless marked otherwise. The authoritative
version of the protocol detail lives in the `instruments/electroglas_2001x.py`
module docstring; this is the orientation document.

---

## 1. Getting connected

**Chain:** `pyvisa` → `visa32.dll` → NI-VISA → `NiVisaTulip.dll` → ADLINK
`gpib-32.dll` → USB-3488A.

ADLINK ships no VISA of its own. NI-VISA reaches the adapter through the Tulip
passport, which is why `GPIB0::…` addresses work at all.

**Prober-side settings that must be right** (IO CONTROL MENU on the panel):

| Setting | Value |
|---|---|
| I/O PROTOCOL | ENHANCED |
| I/O PORT | GPIB-SP |
| GPIB ADDRESS | 29 |
| TERMINATOR | CR/LF |
| GPIB SRQ | DIS (works; enabling it is a possible future improvement) |
| TIMEOUT TIMER 1/2 | 5000 ms |

**`ON LINE` must be pressed after every power cycle.** It is not persistent.
Until then `X I/D` reads OFFLINE, the interface chip answers listener-detect
and serial polls, and every command byte is refused — which looks exactly like
a broken cable.

---

## 2. Protocol hazards

These caused most of the lost time. All are measured.

**Replies are asynchronous and unmatched.** An exchange is drain → write →
read; nothing binds a reply to the command that produced it. An uncollected
reply becomes the *next* command's answer, so readings come back one behind and
still look well-formed — `?P` returning `?S`'s status, `?E` returning `?P`'s
position.

**`SM15M111100000` makes every command acknowledge**, including `SP`/`SM`
config commands, and it is the *first* command in LaMP's init sequence. Leave
one ack uncollected and the prober refuses all further writes and shows
`EXTERNAL I/O TIMEOUT`. Recovery is a Selected Device Clear; draining alone
does not work.

**One conversation at a time.** `gui/app.py` polls prober status every 3
seconds on its own thread. A jog issued in that window lost its `MC` to the
poller and timed out *while the move completed*. Scripted runs doing identical
commands one-at-a-time were 36/36 clean. The driver now serialises all I/O on
an `RLock`; any new caller must go through it.

**A leaked VISA session cannot be cleared from inside.** If a crashed process
still holds the address, clearing and reopening will not help — kill the stale
process.

**Unsupported commands wedge the link** and latch error 35. Stay inside the
documented map.

**`?E` is read-and-clear.** The first read after a failure is the real answer;
a second reads `E0` regardless.

---

## 3. Verified commands

From Keysight IC-CAP's EG2001X driver documentation, all confirmed here:

| Command | Function | Reply |
|---|---|---|
| `MM` | move chuck (relative, microns) | `MC`/`MF` |
| `MA` | move absolute (microns) | `MC`/`MF` |
| `MD` | move relative (dies) | `MC`/`MF` |
| `ZU` / `ZD` | chuck up / down | `MC`/`MF` |
| `ZM` / `ZR` | Z absolute / relative (0.1 mil) | `MC`/`MF` |
| `MT` | rotate theta | `MC`/`MF` |
| `UL` / `LO` | chuck home (unload / load position) | `MC`/`MF` |
| `AA` / `PZ` / `IK` | auto align / auto profile / inker | `MC`/`MF` |

`MC` = Move Complete, `MF` = Move Failed. **Both are replies, not commands** —
the driver previously sent `MF` as a command. Reply case varies (`mc` and `MC`
both seen), so compare case-insensitively.

`HO` is the EG**1034X** home command, not this model's.

### Query map

| Query | Example | Meaning |
|---|---|---|
| `?S` | `SZDW1C0` | status: `ZD`/`ZU`, wafer no., cassette |
| `?P` | `X0Y0` | stage position, **die coordinates** |
| `?Z` | `Z2000` | Z position, 0.1-mil units |
| `?T` | `T-569` | theta, 1:1 with `MT`, unit unknown |
| `?E` | `E0` | error, read-and-clear |
| `?I` | `IX0Y0X84000Y51200D150` | wafer info, `D` = diameter mm |
| `?Y` | `G0B0U0` + 18×`D0` | good/bad/ugly counters, then bins |
| `?O` | `OM0A1P1B0S0W0H0T1D0K0` | options — M material handling, A auto
  align, P profiler, B wafer ID, S SECS, W wafer mapping, T thermal |
| `?C` `?F` `?H` `?N` `?Q` `?R` | | cassette, first die, home, bounds, —, run state |

`?X` and `?Y` are **not** position queries despite the names. Use `?P`.

`?A ?B ?K ?M ?V ?X` return nothing; `?G ?J` return `E-1` (not available).

---

## 4. Units

| Quantity | Unit | Example |
|---|---|---|
| `SP` Z parameters, `?Z`, `ZM`, `ZR` | **0.1 mil** | `SP9Z3500` = 350.0 mils |
| `.PMV` move coordinates, `MA`, `MM` | **microns** | `56336` = 56.336 mm |
| `MD`, `?P` | **die counts** | `X4Y1` |
| `MT`, `?T` | unknown, linear | |

---

## 5. Motion behaviour

- **The prober does not enforce travel limits on incremental moves.** Fifteen
  `MD +1 X` moves were each acknowledged and carried the chuck ~238 mm off the
  platen (error 38). Guarding is the host's job — `move_relative_die()` has a
  step cap and an optional die envelope.
- **Whether negative die indices work depends on the datum.** At the load
  position (bottom-right) they are refused; after `FIRST`/`FD` with the datum
  at wafer centre they are accepted.
- **Every XY move drives Z to the down limit first**, when Z is elevated.
- **A refused move still moves Z** — `MF` does not mean nothing happened.
- **After an out-of-platen error `?P` is not trustworthy** — the counter
  re-zeroes at a physical position that is not the origin. Re-home first.
- Typical timings: XY die move 0.4 s, Z move 0.3–0.7 s.

---

## 6. Touchdown — sensed, not commanded

**Z TRAVEL MODE must be EDGE SENSE (`SM5E`), not auto profile.**

The machine's original screen read `EDGE-SENSE.SEP`. LaMP's `SM5E2` (auto
profile) overwrote it, and that single setting made `ZU`, `ZD` **and** the
panel's `AUTO PROBE` all silent no-ops — they acknowledged `MC` and did
nothing, because auto profile waits on a profiler measurement that never
happens here. Switching to edge sense fixed all three at once.

How it works: the chuck rises until the **edge sensor** detects the needles
touching, then `SP5Z` overtravel is applied past that point. Overtravel is
therefore **needle pressure**, not a limit.

Measured with a card fitted:

```
ZD:  SZUW1C1 Z2990  ->  SZDW1C0 Z2000   needles clear
ZU:  SZDW1C0 Z2000  ->  SZUW1C1 Z2987   contact + overtravel
```

`ZU` found `Z2987` against a manual touchdown at `Z2990` — repeatable to
0.3 mil. **Contact height ≈ 299 mils.**

**Never use `ZM` to approach a probe card.** It is open-loop with no sensing.

---

## 7. Configuration: LaMP's values do not transfer

LaMP's 20-command init sequence was recovered from the real
`tblProberConfiguration`. Most of it is fine; the Z values are not — they suit
LaMP's probe card and optics.

| Parameter | LaMP | This machine | Reference prober |
|---|---|---|---|
| Z overtravel `SP5Z` | 3.70 mils | **1.50** | **1.00** |
| Z clearance `SP6Z` | 15.00 | 10.00 | 45.00 |
| Z up limit `SP7Z` | 420.00 | 300 → **400** | 380.00 |
| Z align `SP9Z` | 216.00 | 300 → **350** | 310.00 |
| Align scan vel `SP16V` | 2000 | **3000** | 3000 |

**`SP9Z` (Z ALIGN) is the alignment camera's focus height**, not just a limit.
LaMP's 216 left the wafer ~134 mils below focus and the video went featureless
grey. Measured sharp at **350 mils** here.

`MACHINE_INIT_SEQUENCE` in the driver applies LaMP's sequence with `SP7Z`/`SP9Z`
overridden, so the GUI's *Send LaMP Init* cannot undo the focus fix.
`PRE_LAMP_SETTINGS` records the originals — **there is no query that reads `SP`
parameters back**, so they survive only because they were photographed.

---

## 8. The wafer map lives on the PC

**The prober stores no die map.** LaMP kept it in `.PMA` file sets and drove
the stage to each coordinate.

```
recipe.PMA                  header: counts, paths, die size, electrical params
recipeMovesMajorX.PMV       absolute X, one per touchdown, microns
recipeMovesMajorY.PMV       absolute Y
recipeDeviceIDMajor.PMS     device IDs, one line per touchdown
recipeMoves/DeviceIDMinor.*  sub-site offsets; usually a single 0
```

### Die size is the step per touchdown, not the physical die

Proved across the recipe library. Two product families each ship a single-die
recipe *and* a quad recipe, and the quad's die size is exactly double in both
axes:

| Product | Recipe | DieSize | dies/shot |
|---|---|---|---|
| HP LaMP | `HP LaMP 21 PCMs` | 3521 × 1642 | 1 |
| HP LaMP | `HP LaMP electrical gauge` | **7042 × 3284** | 4 |
| LPLaMP | `LPLaMP 18 PCMs` | 2602 × 1642 | 1 |
| LPLaMP | `LPLaMP electrical whole wafer` | **5204 × 3284** | 4 |

Same product, same physical dies — only the touchdown footprint changed. So
setting the prober's die size to the quad makes one die-indexed move step a
whole shot, which is how a 4-die touchdown pattern is driven with `MD`.

Every `.PMV` coordinate is an exact integer multiple of that pitch.

Only 6 of 60 recipes surveyed are quad, all LaMP-family electrical ones;
everything else (CYRUS, Murphy, Sena, HOLLY, GIAL5) is single-die.

Corollary: the prober's SET PRMTR die size must match the recipe in use. A
reference prober showing `3.52100 MM` is the HP LaMP **single-die** value, not
a different product.

### Alignment comes first

The `.PMA` carries `PreAlignMessage=Align` and `PostAlignMessage=Make sure the
plate and the alligator clip are clamped down`, and
`XMoveFirstFromAlignSite`/`YMoveFirstFromAlignSite` give the offset **from the
align site to the first touchdown**. `.PMS` files contain literal `TARGET`
entries marking alignment targets rather than devices.

So the run is: align at the align site, offset to the first touchdown, then
walk the move list. Which panel operation performed that alignment is not
established here.

`DeviceIDMajor.PMS` carries **four IDs per line**, one per die in the quad:

```
93-01/83-71/93-02/83-72
NA/86-14/NA/NA            NA     = no die at that position
TARGET/41-71/TARGET/41-72 TARGET = alignment target
```

That matches the physical model — one touchdown contacts 4 dies through 8 pins,
and the relay multiplexes between them because a single SMU can only measure one
at a time.

`XMoveFirstFromAlignSite` / `YMoveFirstFromAlignSite` offset from the align site
to the first touchdown.

`gui/electroglas_pma.py` parses all of this; `split_quad_devices()` breaks out
the per-die IDs. Verified against real recipes including a 3125-touchdown map.

---

## 9. Panel vs GPIB

| Panel | GPIB |
|---|---|
| SET PRMTR / SET MODE / SET OPTION | `SP` / `SM` / `SO` |
| FIRST | `FD` |
| LOAD | `LO` — **this machine's home** |
| Z | `ZU` / `ZD` |
| X / Y green keys | `MA` / `MO` |
| **Joystick, DISK, LEARN, DIAG, STORE, PRINT, FIND TARG, DIG VID** | **none** |

There is no HOME key — LOAD is the datum, which is why the chuck powers up at
the load position.

`DISK` has no remote equivalent, so prober programs cannot be loaded over GPIB.
Combined with §8, that confirms the architecture: **the PC owns the map.**

Operator-only, per the operator: `AUTO PROBE`, `AUTO ALIGN`, `FIND TARG` are
not used on this setup. `ALIGN SCAN` sweeps right-to-left repeatedly for
correcting theta by eye.

Alignment sequence observed: `FIND TARG`, then `PAUSE/CONT` for the
illuminator; `LAMP` toggles light, `CAMR` toggles camera.

---

## 10. Diagnostics

In `references/`, all read-only unless noted:

| Script | Purpose |
|---|---|
| `adlink_gpib_scan.ps1` | raw 488 bus scan — **no Python needed** |
| `visa_probe.ps1` | what VISA can see |
| `ping_eg_test.py` | scan + ping every EG instrument |
| `probe_2001x.py` | full prober link diagnosis |
| `check_eg_state.py` | status / position / error snapshot |
| `test_eg_telemetry.py` | decoded telemetry |
| `unwedge_2001x.py` | escalating link recovery |
| `test_poller_vs_jog.py` | concurrency regression test |
| `restore_needle_pressure.py` | **writes** `SP5Z15` + `SP6Z100` |

---

## 11. Open items

- **`SP5Z` is still on LaMP's 3.70 mils.** Two independent sources say ~1–1.5.
  With a card fitted this is live needle pressure.
- `MT` theta unit unknown — check SET PRMTR page 2.
- `MO` (absolute die) never tested; `goto_die()` deliberately steps with `MD`.
- `move_to_start_die()` sends `MF`, which is a *reply* code — suspect.
- `DEFAULT_Z_LIMITS` is a hand-maintained mirror of `SP7Z`/`SP8Z`; update it
  when those change.
- Keithley 2400 and Agilent 6634B are not fitted, so the measurement half of
  the LaMP workflow is untested. Relay channel mapping is unverified —
  guessing it wrong energises the wrong die.
