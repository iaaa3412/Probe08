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
        self.write(f":SOUR:CURR:LEV {amps}")

    def set_current_limit(self, channel, amps):
        self.write(f":SENS:CURR:PROT {amps}")

    def set_voltage_limit(self, channel, volts):
        self.write(f":SENS:VOLT:PROT {volts}")

    def set_nplc(self, channel, nplc: float):
        self.write(f":SENS:CURR:NPLC {nplc}")
        self.write(f":SENS:VOLT:NPLC {nplc}")
        self.write(f":SENS:RES:NPLC {nplc}")

    def measure_current(self, channel):
        self.write(":SENS:FUNC 'CURR'")
        self.write(":FORM:ELEM CURR")
        return _read_element(self.query(":READ?"), 0)

    def measure_voltage(self, channel):
        self.write(":SENS:FUNC 'VOLT'")
        self.write(":FORM:ELEM VOLT")
        return _read_element(self.query(":READ?"), 0)

    def measure_resistance(self, channel):
        self.write(":SENS:FUNC 'RES'")
        self.write(":FORM:ELEM RES")
        return _read_element(self.query(":READ?"), 0)

    def in_compliance(self, channel) -> bool:
        for q in (":SENS:CURR:PROT:TRIP?", ":SENS:VOLT:PROT:TRIP?"):
            reading = self.query(q)
            if str(reading).strip() in ("1", "true", "True"):
                return True
        return False
