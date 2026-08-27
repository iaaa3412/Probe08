import time
import os
import sys
from instruments.gpib_base import GPIBInstrument

class Keysight34461A(GPIBInstrument):
    def __init__(self):
        super().__init__('dmm')
        self._averages = 1
        # Same fix as Keysight33512B/Keithley2636B/Keithley2400 - opening
        # the VISA session doesn't mean the instrument is actually powered
        # on, so an unguarded reset() here could crash straight out of the
        # constructor (VI_ERROR_NLISTENERS on the write) and take the whole
        # Accretech connect sweep down with it, not just this one driver.
        if self.is_present():
            try:
                self.reset()
            except Exception as e:
                print(f"[DMM] reset failed: {e}")

    def reset(self):
        self.write("*RST")
        self.write("*CLS")
        self._averages = 1

    # MEASure:...? reconfigures and returns ONE sample, so it silently ignores
    # any averaging that was set up. Both readers therefore route through the
    # averaged path whenever averaging is on - otherwise set_averages() would
    # look like it worked while every reading was still a single sample.

    def measure_voltage_dc(self):
        if self._averages > 1:
            return self._averaged_read("VOLT:DC")
        reading = self.query("MEASure:VOLTage:DC?")
        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0

    def measure_current_dc(self):
        if self._averages > 1:
            return self._averaged_read("CURR:DC")
        reading = self.query("MEASure:CURRent:DC?")
        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0

    def set_nplc(self, nplc: float):
        self.write(f"VOLT:DC:NPLC {nplc}")
        self.write(f"CURR:DC:NPLC {nplc}")

    def set_current_range(self, range_a: float):
        self.write(f"CURR:DC:RANG {range_a}")

    def set_sample_count(self, n: int):
        self.write(f"SAMP:COUN {max(1, int(n))}")

    def set_averages(self, channel, count: int):
        """Average COUNT readings inside the meter.

        Same contract as Keithley2400.set_averages: set it, then one ordinary
        measure_* call returns the mean. The Truevolt takes a burst of
        SAMPle:COUNt readings per trigger and CALCulate:AVERage accumulates the
        statistics over it, so measure_current_dc() below reads the mean back
        rather than a single sample.

        `channel` is accepted and ignored - this meter has one input, and the
        uniform signature is what lets the runner treat every instrument alike.

        NOT verified against hardware - the 34461A is on the Accretech bench
        and was not connected when this was written.
        """
        count = max(1, int(count))
        self._averages = count
        self.write(f"SAMP:COUN {count}")
        self.write("CALC:AVER:STAT ON" if count > 1 else "CALC:AVER:STAT OFF")

    def _averaged_read(self, func: str):
        """One triggered burst, then the mean the meter computed over it."""
        self.write(f"CONF:{func}")
        self.write("CALC:AVER:CLE")
        self.write("INIT")
        self.query("*OPC?")
        reading = self.query("CALC:AVER:AVER?")
        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0

    def measure_current_dc_avg(self, averages: int = 1) -> float:
        averages = max(1, int(averages))
        if averages > 1:
            try:
                self.set_averages(None, averages)
                return self._averaged_read("CURR:DC")
            except Exception:
                pass    # fall through to reading it out one at a time
        total = 0.0
        for _ in range(averages):
            reading = self.query("MEASure:CURRent:DC?")
            try:
                total += float(reading)
            except (ValueError, TypeError):
                pass
        return total / averages

    def measure_resistance(self, wire_mode=2):
        if wire_mode == 4:
            reading = self.query("MEASure:FRESistance?")
        else:
            reading = self.query("MEASure:RESistance?")

        try:
            return float(reading)
        except (ValueError, TypeError):
            return 0.0