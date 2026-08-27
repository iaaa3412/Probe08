import time
import os
import sys
from instruments.gpib_base import GPIBInstrument

class Keithley2636B(GPIBInstrument):
    def __init__(self, config_key='smu'):
        # Same reason Keithley2400 takes one: the default ('smu') keeps
        # every existing caller unaffected, but a SECOND 2636B added as a
        # custom Setup-tab instrument needs to read/write ITS OWN slot,
        # not collide with the real SMU's.
        super().__init__(config_key)
        # Same fix as Keysight33512B/Keithley2400 - opening the VISA session
        # doesn't mean the instrument is actually powered on, so an
        # unguarded reset() here could crash straight out of the
        # constructor (VI_ERROR_NLISTENERS on the write) and take the whole
        # Accretech connect sweep down with it, not just this one driver.
        if self.is_present():
            try:
                self.reset()
            except Exception as e:
                print(f"[SMU] reset failed: {e}")

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

    def get_current_limit(self, channel):
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
        """Average COUNT readings inside the SMU, so measure.* returns the mean.

        The 26xxB's own filter, the same contract as Keithley2400.set_averages:
        set it, then a single normal read comes back already averaged. Doing
        this in the instrument rather than in a GUI loop is one source cycle
        and one bus round-trip per die instead of COUNT of each.

        REPEAT_AVG, not MOVING_AVG: a moving average carries readings across a
        source change, so the first value after switching dies would still be
        weighted by the previous one.

        NOT verified against hardware - the 2636B is on the Accretech bench and
        was not connected when this was written.
        """
        count = max(1, int(count))
        if count > 1:
            self.write(f"{channel}.measure.filter.count = {count}")
            self.write(f"{channel}.measure.filter.type = {channel}.FILTER_REPEAT_AVG")
            self.write(f"{channel}.measure.filter.enable = {channel}.FILTER_ON")
        else:
            self.write(f"{channel}.measure.filter.enable = {channel}.FILTER_OFF")

    def in_compliance(self, channel) -> bool:
        reading = self.query(f"print({channel}.source.compliance)")
        return str(reading).strip().lower() == "true"