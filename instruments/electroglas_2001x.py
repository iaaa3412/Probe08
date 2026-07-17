import time

from instruments.gpib_base import GPIBInstrument


class Electroglas2001X(GPIBInstrument):
    def __init__(self):
        super().__init__('prober_eg')
        self.z_is_up = None

    def get_id(self) -> str:
        if not self.inst:
            return ""
        try:
            resp = self.query("*IDN?")
            if resp:
                return resp
        except Exception:
            pass
        return "link up (ID query unverified)"

    def _not_implemented(self, name):
        raise NotImplementedError(
            f"Electroglas 2001X: '{name}' has no real command mapping yet. "
            f"Add it to instruments/electroglas_2001x.py once the Electroglas "
            f"command reference is available.")

    def get_prober_id(self) -> str:
        return self.get_id()

    def get_error_code(self) -> str:
        self._not_implemented("get_error_code")

    def get_error_message(self) -> str:
        self._not_implemented("get_error_message")

    def get_prober_status(self) -> str:
        return self.query("?S") or ""

    def _wait_until_not_moving(self, timeout_s: float = 30.0) -> str:
        if not self.inst:
            return ""
        start = time.time()
        status = ""
        while time.time() - start < timeout_s:
            status = (self.get_prober_status() or "").strip().lower()
            if "error" in status:
                raise RuntimeError(
                    f"Electroglas 2001CXE reported error status: {status!r}")
            if status and "moving" not in status:
                return status
            time.sleep(0.1)
        raise TimeoutError(
            f"Electroglas 2001CXE: timed out waiting for motion to complete "
            f"(last status: {status!r})")

    def get_xy_position(self) -> str:
        x = self.query("?X") or ""
        y = self.query("?Y") or ""
        return f"X={x} Y={y}"

    def get_xy_absolute(self) -> str:
        self._not_implemented("get_xy_absolute")

    def get_on_wafer_info(self) -> str:
        self._not_implemented("get_on_wafer_info")

    def get_lot_number(self) -> str:
        self._not_implemented("get_lot_number")

    def get_wafer_number(self) -> str:
        self._not_implemented("get_wafer_number")

    def get_wafer_id(self) -> str:
        self._not_implemented("get_wafer_id")

    def get_pass_fail_counts(self) -> str:
        self._not_implemented("get_pass_fail_counts")

    def get_gross_value(self) -> str:
        self._not_implemented("get_gross_value")

    def get_wafer_status(self) -> str:
        self._not_implemented("get_wafer_status")

    def get_cassette_status(self) -> str:
        self._not_implemented("get_cassette_status")

    def get_yield_data(self) -> str:
        self._not_implemented("get_yield_data")

    def get_hot_chuck_status(self) -> str:
        self._not_implemented("get_hot_chuck_status")

    def get_chuck_temperature(self) -> str:
        self._not_implemented("get_chuck_temperature")

    def get_start_die_coords(self) -> str:
        self._not_implemented("get_start_die_coords")

    def get_multisite_info(self) -> str:
        self._not_implemented("get_multisite_info")

    def buzzer_clear(self) -> str:
        self._not_implemented("buzzer_clear")

    def send_es(self):
        self._not_implemented("send_es")

    def confirm_and_clear_alarm(self) -> bool:
        self._not_implemented("confirm_and_clear_alarm")

    def read_stb_decoded(self) -> tuple:
        return 0, (self.get_prober_status() or "unknown")

    def z_up(self):
        self.write("Z")
        status = self._wait_until_not_moving()
        self.z_is_up = True
        return status

    def z_down(self):
        self.write("D")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def emergency_stop(self):
        self._not_implemented("emergency_stop")

    def unload_wafer(self):
        self.write("U")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def load_wafer(self):
        self.write("L")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def cassette_wait_for_wafer_ready(self, timeout_s=None):
        self._not_implemented("cassette_wait_for_wafer_ready")

    def cassette_next_die(self, timeout_s=None):
        self._not_implemented("cassette_next_die")

    def cassette_unload_and_load_next(self, timeout_s=None):
        self._not_implemented("cassette_unload_and_load_next")

    def next_die(self):
        self.write("J")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def index_die_alt(self):
        self.write("I")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def set_index_size(self, x_um: float, y_um: float):
        self._not_implemented("set_index_size")

    def move_xy_absolute(self, dx_um: float, dy_um: float):
        self._not_implemented("move_xy_absolute")

    def move_to_start_die(self):
        self.write("G")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_to_die_xy(self, x_die: int, y_die: int):
        self._not_implemented("move_to_die_xy")

    def move_xy_relative(self, dx_index: int, dy_index: int):
        self._not_implemented("move_xy_relative")

    def mark_current_die(self, category: str = ""):
        self._not_implemented("mark_current_die")
