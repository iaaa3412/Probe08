from instruments.gpib_base import GPIBInstrument


def _read_element(raw, index, default=0.0):
    try:
        parts = str(raw).strip().split(",")
        return float(parts[index])
    except (ValueError, TypeError, IndexError):
        return default


class Keithley2400(GPIBInstrument):
    def __init__(self):
        super().__init__('smu_eg')
        self.reset()

    def get_id(self) -> str:
        return self.query("*IDN?") or ""

    def reset(self):
        self.write("*RST")

    def set_voltage(self, channel, volts):
        self.write(":SOUR:FUNC VOLT")
        self.write(f":SOUR:VOLT:LEV {volts}")

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
