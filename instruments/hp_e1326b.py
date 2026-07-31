"""HP/Agilent E1326B 5.5-digit multimeter in the E1300A mainframe.

This is a full multimeter, not a breakout. The E1326B is a B-size register-based
VXI module; the mainframe's SCPI driver gives it an error queue, buffers, status
registers and reading memory, and it works stand-alone with signals landed on
its own faceplate terminals. Two are installed internally on this bench, broken
out to banana terminals by E1326-80005 adapters (that part IS just a breakout -
HI, LO, COM and I on banana plugs, no electronics).

Measurement functions (manual, "Functional Description"):

    DC voltage           MEAS:VOLT:DC?
    RMS AC voltage       MEAS:VOLT:AC?
    4-wire resistance    MEAS:FRES?
    2-wire resistance    MEAS:RES?     SCANNING MULTIMETER ONLY
    temperature          MEAS:TEMP?    thermistor / RTD / thermocouple

There is NO current measurement function. The "Current HI/LO" terminals are the
internal current SOURCE the meter uses for resistance: it drives a known current
and senses the resulting voltage on Input HI/LO.

STAND-ALONE MEANS 4-WIRE ONLY. The manual is explicit - "Only 4-wire
measurements can be made with the stand-alone multimeter" - and the command
syntax enforces it: channel_list is optional on MEASure:FRESistance? but
mandatory on MEASure:RESistance?. On probe03 the relay card wires sense and
source separately to the probe card, which is exactly the 4-wire arrangement, so
resistance here is measure_resistance_4w() and never a 2-wire call.

ADDRESSING. The module's logical address switch decides everything. Secondary
address = logical address / 8, and the address must be a multiple of 8 or the
mainframe leaves the module unassigned - present and powered, but with no GPIB
address at all. Factory setting is 24, i.e. secondary address 03
(GPIB0::9::3::INSTR), and the manual warns that with more than one multimeter
you MUST move the others, "as there can only be one instrument per secondary
address". Two modules left at the factory 24 collide and neither is assigned,
which is consistent with what a bus scan finds here: nothing at 9::3.
"""

from instruments.gpib_base import GPIBInstrument


class HPE1326B(GPIBInstrument):
    """One E1326B multimeter at its own GPIB secondary address."""

    def get_id(self) -> str:
        """*IDN? if the mainframe's SCPI driver answers it.

        The E1326B manual documents *RST, *CLS and SYST:ERR? but never *IDN?;
        the switchbox cards in the same mainframe do answer it, so it is worth
        asking. Presence is established by serial poll regardless.
        """
        try:
            return self.query("*IDN?") or ""
        except Exception:
            return ""

    def reset(self):
        """*RST - returns the multimeter to the idle state."""
        self.write("*RST")

    def clear_status(self):
        self.write("*CLS")

    def error(self) -> str:
        """SYST:ERR? - one entry off the error queue."""
        return self.query("SYST:ERR?") or ""

    def drain_errors(self, limit: int = 10) -> list:
        found = []
        for _ in range(limit):
            entry = self.error()
            if not entry or entry.strip().startswith(("+0,", "0,")):
                break
            found.append(entry)
        return found

    # -- measurements -------------------------------------------------------

    def _measure(self, command: str) -> float:
        resp = self.query(command)
        if resp is None:
            raise RuntimeError(f"no response to {command!r}")
        return float(str(resp).strip().split(",")[0])

    def measure_voltage_dc(self, rng=None, resolution=None) -> float:
        return self._measure(self._with_range("MEAS:VOLT:DC?", rng, resolution))

    def measure_voltage_ac(self, rng=None, resolution=None) -> float:
        """True RMS AC volts."""
        return self._measure(self._with_range("MEAS:VOLT:AC?", rng, resolution))

    def measure_resistance_4w(self, rng=None, resolution=None) -> float:
        """4-wire ohms - the only resistance mode a stand-alone E1326B has.

        Ranges are 232 / 1861 / 14894 / 119156 / 1048576 ohms, or AUTO.
        """
        return self._measure(self._with_range("MEAS:FRES?", rng, resolution))

    def measure_temperature(self, transducer: str, type_: str) -> float:
        """MEAS:TEMP? <transducer>,<type> - e.g. ('THER', 5000), ('RTD', 85)."""
        return self._measure(f"MEAS:TEMP? {transducer},{type_}")

    @staticmethod
    def _with_range(base: str, rng, resolution) -> str:
        if rng is None:
            return base
        if resolution is None:
            return f"{base} {rng}"
        return f"{base} {rng},{resolution}"
