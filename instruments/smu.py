import time
import os
import sys
from instruments.gpib_base import GPIBInstrument

class Keithley2636B(GPIBInstrument):
    def __init__(self):
        super().__init__('smu')
        self.reset()

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
        """Set measurement integration time in power line cycles."""
        self.write(f"{channel}.measure.nplc = {nplc}")

    def in_compliance(self, channel) -> bool:
        """Returns True if the SMU is currently in compliance (limit reached)."""
        reading = self.query(f"print({channel}.source.compliance)")
        return str(reading).strip().lower() == "true"