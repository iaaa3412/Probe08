from instruments.gpib_base import GPIBInstrument


def _read_element(raw, index, default=0.0):
    try:
        parts = str(raw).strip().split(",")
        return float(parts[index])
    except (ValueError, TypeError, IndexError):
        return default


class Keithley2400(GPIBInstrument):
    def __init__(self, config_key='smu_eg'):
        # Electroglas keeps its own default ('smu_eg') so every existing
        # caller is unaffected. Accretech's model-swap option (Setup tab -
        # picking a 2400 for the "smu" slot) passes config_key="smu" so it
        # reads/writes the SAME instruments.yaml entry Keithley2636B would
        # for that slot, instead of colliding with Electroglas's own
        # 'smu_eg' entry.
        super().__init__(config_key)
        # Opening the session proves nothing about whether the 2400 is powered
        # on, so this *RST raised straight out of the constructor whenever it
        # was not - and gui/app.py builds every driver before it starts
        # handling errors, so that single exception aborted the entire connect
        # sequence and left the tab stuck on "Pinging hardware connections...".
        if self.is_present():
            try:
                self.reset()
            except Exception as e:
                print(f"[SMU_EG] *RST failed: {e}")

    def get_id(self) -> str:
        return self.query("*IDN?") or ""

    # The probe card is wired to the 2400's REAR terminals, but *RST leaves the
    # instrument on FRONT - and __init__ sends *RST on every connect. Measured
    # on the bench 2026-08-12, same bias and same closed relay channel:
    #
    #     FRON  10.00000 V   -2.704424e-12 A      (the empty front panel)
    #     REAR  10.00000 V    1.887367e-09 A      (the actual probe path)
    #
    # So every reading the GUI ever took was the front panel measuring nothing,
    # which is why a shorted target still PASSED. Asserted after any reset and
    # again when a bias is applied, because the failure is silent: picoamps out
    # of an open front panel look exactly like a very good die.
    TERMINALS = "REAR"

    # LaMP's fixed instrument setup, recovered from the executable's string
    # table (Lampexe/GPIB_COMMANDS.txt). These carry no recipe value and this
    # driver never sent them. Without them the path stays continuously biased
    # and the ~200 pA a closed relay channel contributes is swamped by the
    # cable settling downwards. Measured on the bench 2026-08-12, same shot and
    # same channels:
    #     without:  CH00..CH03 all BELOW the open baseline (pure decay)
    #     with:     CH00..CH03 read +207..+275 pA above it
    # sour:clear:auto on is the important one - it drops the output between
    # readings so each measurement re-applies the bias to a settled path.
    _FIXED_SETUP = (
        "sour:clear:auto on",
        "sens:aver:tcon rep",
        "syst:rsen off",          # 2-wire, not Kelvin
        "syst:azer on",
        "syst:azer:cach off",
        "syst:guar cabl",         # guarding, for low-current work
        "SOUR:VOLT:RANG 100",
    )

    def use_measurement_terminals(self):
        self.write(f":ROUT:TERM {self.TERMINALS}")

    def set_terminals(self, which: str):
        """Override which physical terminals this instance uses, live -
        TERMINALS above is a class-level DEFAULT (REAR, because that's how
        Peanut's original switch-matrix-routed probe cards were cabled),
        not something every project should be stuck with. A direct-wired
        recipe (see PeanutATA's probe08 bench, 2026-09) is typically
        hand-clipped to the FRONT panel instead, so needs to flip this
        without a code change every time. Setting self.TERMINALS (not the
        class attribute) shadows the class default for just this
        instance - use_measurement_terminals() reads self.TERMINALS
        either way, so every later set_voltage/set_current call picks up
        the override automatically, same as it already picks up the
        class default today. Applied immediately too, not just queued for
        the next source call, so an idle instrument reflects the change
        right away.
        """
        which = (which or "").strip().upper()
        if which not in ("FRONT", "REAR"):
            raise ValueError(f"terminals must be FRONT or REAR, got {which!r}")
        self.TERMINALS = which
        self.write(f":ROUT:TERM {self.TERMINALS}")

    def get_terminals(self) -> str:
        return self.TERMINALS

    def configure_for_measurement(self):
        self.use_measurement_terminals()
        for cmd in self._FIXED_SETUP:
            self.write(cmd)

    def reset(self):
        self.write("*RST")
        self.configure_for_measurement()

    def set_voltage(self, channel, volts):
        self.use_measurement_terminals()
        self.write(":SOUR:FUNC VOLT")
        self.write(":SOUR:VOLT:MODE FIX")
        self.write(f":SOUR:VOLT:LEV {volts}")

    def set_source_delay(self, seconds: float):
        self.write(f":SOUR:DEL {float(seconds)}")

    def set_averages(self, channel, count: int):
        """Average COUNT readings inside the instrument, LaMP's way.

        TCONtrol REPeat is set explicitly rather than relied on from the
        power-on setup: with MOVing the 2400 returns a rolling average, so the
        first reading after a source change is still weighted by the previous
        die's value.
        """
        self.write(f":SENS:AVER:COUN {int(count)}")
        if int(count) > 1:
            self.write(":SENS:AVER:TCON REP")
            self.write(":SENS:AVER:STATE ON")
        else:
            self.write(":SENS:AVER:STATE OFF")

    def set_current_range(self, channel, amps):
        """Fixed measurement range - LaMP's MeterRange.

        Explicit beats autorange here: autoranging hunts between readings,
        which costs time and puts a range change in the middle of a settling
        measurement.
        """
        self.write(f":SENS:CURR:RANGE {amps}")

    def turn_output_on(self, channel):
        self.write(":OUTP ON")

    def turn_output_off(self, channel):
        self.write(":OUTP OFF")

    def set_current(self, channel, amps):
        self.write(":SOUR:FUNC CURR")
        # FIXED, not the power-on default of AUTO/SWEep - without this the
        # 2400 has been seen falling back into its own auto-ohms-style
        # current selection instead of holding exactly the forced level a
        # recipe asked for. Verified against the bench's own confirmed-
        # working command sequence for a Kelvin resistance measurement -
        # see measure_resistance's own comment.
        self.write(":SOUR:CURR:MODE FIXED")
        self.write(f":SOUR:CURR {amps}")

    def set_current_limit(self, channel, amps):
        self.write(f":SENS:CURR:PROT {amps}")

    def set_voltage_limit(self, channel, volts):
        self.write(f":SENS:VOLT:PROT {volts}")

    def set_nplc(self, channel, nplc: float):
        self.write(f":SENS:CURR:NPLC {nplc}")
        self.write(f":SENS:VOLT:NPLC {nplc}")
        self.write(f":SENS:RES:NPLC {nplc}")

    def set_auto_zero(self, enabled: bool):
        """ON re-measures the instrument's own internal zero reference before
        every reading (cancels thermal/amplifier offset drift); OFF skips
        that and reads straight through. Confirmed on the bench: cuts a
        combined current+voltage read from ~1644ms to ~931ms at NPLC=1/
        avg=20 - the single biggest remaining cost after the combined-read
        fix. Real tradeoff, not a free one: without periodic re-zeroing,
        slow drift can creep into readings over a long run. Left as an
        explicit opt-in call, not part of _FIXED_SETUP, since Maddy and
        Cenfire share this driver and haven't been evaluated with it off."""
        self.write(f"syst:azer {'on' if enabled else 'off'}")

    def set_source_clear_auto(self, enabled: bool):
        """ON (the _FIXED_SETUP default, sent on every reset/connect) drops
        the output and re-applies the bias fresh before every :READ? -
        exactly what LaMP's own averaging relies on (see
        instrument_panel._exec2_measure_averaged's own comment: one :READ?
        with N internal averages instead of N separate ones, each a fresh
        source cycle). But a :READ? sent purely to log/record the actual
        delivered current/voltage - Maddy/Cenfire's Force Current step -
        produces that same drop-and-reapply transient as a side effect of
        just reading it back, with no averaging benefit to show for it.
        Confirmed on the bench (Cenfire, a marginal contact): reading a
        dependent sense step BEFORE that transient gave a clean, correct
        value every time; reading it AFTER (today's step order) gave
        near-zero every time - the transient was enough to collapse a weak
        contact's signal by the time the sense step got to it.

        Left ON by _FIXED_SETUP's default (unchanged) and only ever turned
        off here, explicitly, per recipe (see recipe_panel's Skip
        auto-clear on Force Current checkbox / is_fast_current_settle) -
        never a global driver change, since LaMP's own current-measure
        step genuinely needs it ON and shares this same driver."""
        self.write(f"sour:clear:auto {'on' if enabled else 'off'}")

    def measure_current(self, channel):
        self.write(":SENS:FUNC 'CURR'")
        self.write(":FORM:ELEM CURR")
        return _read_element(self.query(":READ?"), 0)

    def measure_voltage(self, channel):
        self.write(":SENS:FUNC 'VOLT'")
        self.write(":FORM:ELEM VOLT")
        return _read_element(self.query(":READ?"), 0)

    def measure_current_and_voltage(self, channel):
        """Both readings from a single acquisition, instead of
        measure_current()+measure_voltage()'s two separate ones - each
        separate call re-runs the full NPLC*averages integration from
        scratch, so two calls cost exactly double one call for no reason
        when both values come from the same forced/compliance pair
        anyway. Verified on the bench: a combined read returns identical
        values to the two separate calls, in the time of ONE of them
        (2703ms -> 1467ms at NPLC=1/avg=20).

        The 2400 ignores the requested element order and always returns
        VOLT before CURR regardless of what :FORM:ELEM asks for -
        confirmed on the bench: requesting CURR,VOLT and VOLT,CURR both
        came back as "+9.996V, -5.6e-11A". Read index 1 for current,
        0 for voltage to match what the instrument actually sends, not
        the request order."""
        self.write(":SENS:FUNC 'CURR','VOLT'")
        self.write(":FORM:ELEM CURR,VOLT")
        raw = self.query(":READ?")
        return _read_element(raw, 1), _read_element(raw, 0)

    def measure_resistance(self, channel, manual=False):
        # AUTO is the safe default - it uses the instrument's OWN internal
        # current source (auto-ranged) for the ohms reading, independent of
        # whatever SOUR:CURR happens to be sitting in the instrument. MANUAL
        # instead reuses whatever SOUR:CURR was last forced by set_current()
        # - correct ONLY for a recipe that deliberately forces a specific
        # current and then immediately reads ohms off the same pins with
        # this same call (Maddy TL's Kelvin Resistance step, confirmed on
        # the bench). For every other recipe - anything with no preceding
        # Force Current step, e.g. a standalone resistance check - SOUR:CURR
        # is whatever was last left behind (often 0 from *RST), so MANUAL
        # mode reads a manufactured 0 ohm every time regardless of the
        # actual pin. That was the direct-wiring 0-ohm bug: this call used
        # to hardcode MANUAL unconditionally. Now opt-in per recipe (Recipe
        # tab's "Manual mode" checkbox, RecipePanel.is_manual_mode()) -
        # blank/unset means AUTO, matching every recipe except Maddy TL.
        self.write(f":SENS:RES:MODE {'MANUAL' if manual else 'AUTO'}")
        self.write(":SENS:FUNC 'RESISTANCE'")
        self.write(":FORM:ELEM RES")
        return _read_element(self.query(":READ?"), 0)

    def in_compliance(self, channel) -> bool:
        for q in (":SENS:CURR:PROT:TRIP?", ":SENS:VOLT:PROT:TRIP?"):
            reading = self.query(q)
            if str(reading).strip() in ("1", "true", "True"):
                return True
        return False
