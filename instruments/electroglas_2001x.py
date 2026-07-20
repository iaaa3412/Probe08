import datetime
import time

from instruments.gpib_base import GPIBInstrument


def _fmt6(value) -> str:
    return f"{float(value):07.3f}"


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
        self.write("ZU")
        status = self._wait_until_not_moving()
        self.z_is_up = True
        return status

    def z_down(self):
        self.write("ZD")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_z_absolute(self, z):
        self.write(f"ZM{int(z)}")
        status = self._wait_until_not_moving()
        self.z_is_up = None
        return status

    def move_z_relative(self, dz):
        self.write(f"ZR{int(dz)}")
        status = self._wait_until_not_moving()
        self.z_is_up = None
        return status

    def move_theta_relative(self, dtheta):
        self.write(f"MT{int(dtheta)}")
        return self._wait_until_not_moving()

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
        self.write("MF")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_to_home(self):
        self.write("HO")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_to_die_xy(self, x_die: int, y_die: int):
        self._not_implemented("move_to_die_xy")

    def move_absolute_die(self, x_die, y_die):
        self.write(f"MOX{int(x_die)}Y{int(y_die)}")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_relative_die(self, dx_die, dy_die):
        self.write(f"MDX{int(dx_die)}Y{int(dy_die)}")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_absolute_m(self, x, y):
        self.write(f"MAX{int(x)}Y{int(y)}")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_relative_m(self, dx, dy):
        self.write(f"MMX{int(dx)}Y{int(dy)}")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_micro(self, dx, dy):
        self.write(f"FMX{int(dx)}Y{int(dy)}")
        status = self._wait_until_not_moving()
        self.z_is_up = False
        return status

    def move_xy_relative(self, dx_index: int, dy_index: int):
        self._not_implemented("move_xy_relative")

    def mark_current_die(self, category: str = ""):
        self._not_implemented("mark_current_die")

    def set_die_size(self, x, y):
        self.write(f"SP1X{int(x)}Y{int(y)}")

    def set_die_size_precise_mm(self, x_mm, y_mm):
        self.write(f"SP29X{_fmt6(x_mm)}Y{_fmt6(y_mm)}")

    def set_wafer_diameter(self, diameter):
        self.write(f"SP4D{int(diameter)}")

    def set_coordinate_quadrant(self, quadrant):
        self.write(f"SM11Q{int(quadrant)}")

    def set_count_pulse_width(self, width):
        self.write(f"SM32P{int(width)}")

    def set_current_cassette(self, cassette):
        self.write(f"SM70C{int(cassette)}")

    def set_date_time(self, when=None):
        when = when or datetime.datetime.now()
        self.write(f"TI{when.hour:02d}:{when.minute:02d}")

    def set_first_die(self):
        self.write("FD")

    def set_flat_orientation(self, orientation):
        self.write(f"SM3F{int(orientation)}")

    def set_probe_clean_count(self, count, w):
        self.write(f"SM12C{int(count)}W{int(w)}")

    def set_probe_quadrant(self, quadrant):
        self.write(f"SM2Q{int(quadrant)}")

    def set_profiler_retry_count(self, retries):
        self.write(f"SM42R{int(retries)}")

    def set_reference_die_coordinate(self, x, y):
        self.write(f"SP2X{int(x)}Y{int(y)}")

    def set_reprobe_count(self, count):
        self.write(f"SP14R{int(count)}")

    def set_starting_wafer_number(self, number):
        self.write(f"SM16N{int(number)}")

    def set_touchdown_counter(self, count):
        self.write(f"SP19C{int(count)}")

    def set_units(self, unit):
        self.write(f"SM1U{int(unit)}")

    def set_yield_to_pass_wafer(self, yield_pct):
        self.write(f"SP33Y{int(yield_pct)}")

    def set_z_autoalign_height(self, z):
        self.write(f"SP9Z{int(z)}")

    def set_z_clearance(self, z):
        self.write(f"SP6Z{int(z)}")

    def set_z_down_limit(self, z):
        self.write(f"SP8Z{int(z)}")

    def set_z_overtravel(self, z):
        self.write(f"SP5Z{int(z)}")

    def set_z_undertravel(self, z):
        self.write(f"SP10Z{int(z)}")

    def set_z_up_limit(self, z):
        self.write(f"SP7Z{int(z)}")

    def set_zprofile_height(self):
        self.write("PH")

    def set_wafer_x_expansion(self, coefficient):
        self.write(f"SX4C{int(coefficient)}")

    def set_wafer_y_expansion(self, coefficient):
        self.write(f"SX5C{int(coefficient)}")

    def set_die_size_mm(self, x_mm, y_mm):
        self.set_die_size(round(x_mm * 1000), round(y_mm * 1000))

    def set_die_size_mil(self, x_mil, y_mil):
        self.set_die_size(round(x_mil * 10), round(y_mil * 10))
