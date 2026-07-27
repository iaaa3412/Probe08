from instruments.gpib_base import GPIBInstrument


class HP3458A(GPIBInstrument):
    def __init__(self):
        super().__init__('dmm_eg')
        if self.inst:
            try:
                # Out of reset the 3458A does not assert EOI on its responses,
                # so every read sits waiting for a terminator that never comes
                # and times out - verified on this bench: "ID?" timed out until
                # this was sent, then returned 'HP3458A\r\n'. END ALWAYS only
                # changes output termination, not any measurement setting.
                self.write("END ALWAYS")
            except Exception as e:
                print(f"[DMM_EG] END ALWAYS failed, reads may time out: {e}")

    def get_id(self) -> str:
        return self.query("ID?") or ""

    def _triggered_reading(self, func: str) -> float:
        if not self.inst:
            return 0.0
        try:
            self.write(f"FUNC {func}")
            self.write("TRIG SGL")
            return float(self.inst.read())
        except Exception:
            return 0.0

    def measure_voltage_dc(self) -> float:
        return self._triggered_reading("DCV")

    def measure_current_dc(self) -> float:
        return self._triggered_reading("DCI")

    def measure_resistance(self, wire_mode=2) -> float:
        return self._triggered_reading("OHMF" if wire_mode == 4 else "OHM")
