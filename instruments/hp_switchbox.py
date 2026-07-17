from instruments.gpib_base import GPIBInstrument


def _chan_spec(channel) -> str:
    return f"(@01{int(channel):02d})"


class HPSwitchbox(GPIBInstrument):
    def __init__(self, config_key: str):
        super().__init__(config_key)

    def get_id(self) -> str:
        return self.query("*IDN?") or ""

    def close_channel(self, channel):
        self.write(f"CLOS {_chan_spec(channel)}")

    def open_channel(self, channel):
        self.write(f"OPEN {_chan_spec(channel)}")

    def open_all(self):
        self.write("*RST")

    def read_channel(self, channel) -> bool:
        resp = self.query(f"CLOS? {_chan_spec(channel)}")
        return str(resp).strip() == "1"
