import time
import os
import sys
from instruments.gpib_base import GPIBInstrument

class Keysight34461A(GPIBInstrument):
    def __init__(self):
        super().__init__('dmm')
        self.reset()

    def reset(self):
        self.write("*RST")
        self.write("*CLS")

    def measure_voltage_dc(self):
        reading = self.query("MEASure:VOLTage:DC?")
        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0

    def measure_current_dc(self):
        reading = self.query("MEASure:CURRent:DC?")
        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0

    def set_nplc(self, nplc: float):
        """Set integration time (power line cycles) for voltage and current modes."""
        self.write(f"VOLT:DC:NPLC {nplc}")
        self.write(f"CURR:DC:NPLC {nplc}")

    def set_current_range(self, range_a: float):
        """Set DC current measurement range (e.g. 1e-4 for 100 µA)."""
        self.write(f"CURR:DC:RANG {range_a}")

    def set_sample_count(self, n: int):
        """Set number of samples per trigger (for averaging)."""
        self.write(f"SAMP:COUN {max(1, int(n))}")

    def measure_current_dc_avg(self, averages: int = 1) -> float:
        """Take N current-DC readings and return their mean."""
        total = 0.0
        for _ in range(max(1, averages)):
            reading = self.query("MEASure:CURRent:DC?")
            try:
                total += float(reading)
            except (ValueError, TypeError):
                pass
        return total / max(1, averages)

    def measure_resistance(self, wire_mode=2):
        if wire_mode == 4:
            reading = self.query("MEASure:FRESistance?")
        else:
            reading = self.query("MEASure:RESistance?")

        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0