import pyvisa
import yaml
import sys
import os

_OPEN_TIMEOUT_MS = 1500

_VISA_BACKENDS = (None, "@py")
_rm_cache = {}


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    except Exception:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, relative_path)


def _resource_manager_for(via):
    if via not in _rm_cache:
        _rm_cache[via] = pyvisa.ResourceManager() if via is None else pyvisa.ResourceManager(via)
    return _rm_cache[via]


def open_resource(address, open_timeout=_OPEN_TIMEOUT_MS):
    errors = []
    for via in _VISA_BACKENDS:
        try:
            rm = _resource_manager_for(via)
        except Exception as e:
            errors.append(f"{via or 'default'}: {e}")
            continue
        try:
            inst = rm.open_resource(address, open_timeout=open_timeout)
            return inst, (via or "default")
        except Exception as e:
            errors.append(f"{via or 'default'}: {e}")
    raise RuntimeError(f"Could not open {address!r}. Tried: " + "; ".join(errors))


class GPIBInstrument:
    def __init__(self, config_key):
        yaml_path = get_resource_path("instruments/instruments.yaml")

        with open(yaml_path, "r") as file:
            config = yaml.safe_load(file)

        inst_data = config['instruments'].get(config_key)
        if not inst_data:
            raise ValueError(f"Instrument '{config_key}' not found in YAML.")

        self.address = inst_data['address']
        self.timeout = inst_data['timeout_ms']

        try:
            self.inst, via = open_resource(self.address)
            self.inst.timeout = self.timeout
            self.inst.encoding = "latin-1"
            print(f"[{config_key.upper()}] Connected successfully at {self.address} (via {via})")
        except Exception as e:
            print(f"[{config_key.upper()}] FAILED to connect: {e}")
            self.inst = None

    def write(self, command):
        if self.inst:
            self.inst.write(command)

    def query(self, command):
        if self.inst:
            return self.inst.query(command).strip()
        return None

    def close(self):
        if self.inst:
            self.inst.close()


def load_all_instrument_configs() -> dict:
    yaml_path = get_resource_path("instruments/instruments.yaml")
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    return config["instruments"]


def set_instrument_address(config_key: str, address: str) -> None:
    yaml_path = get_resource_path("instruments/instruments.yaml")
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    if config_key not in config["instruments"]:
        raise ValueError(f"Instrument '{config_key}' not found in YAML.")
    config["instruments"][config_key]["address"] = address
    with open(yaml_path, "w") as file:
        yaml.safe_dump(config, file, default_flow_style=False, sort_keys=False)


def ping_address(address: str, timeout_ms: int = 1000) -> tuple:
    try:
        inst, via = open_resource(address)
    except Exception as e:
        return False, str(e)
    try:
        inst.timeout = timeout_ms
        try:
            resp = inst.query("*IDN?").strip()
            return True, (resp or f"connected via {via} - empty *IDN? response")
        except Exception:
            return True, f"connected via {via} - no *IDN? response (device may not support it)"
    finally:
        try:
            inst.close()
        except Exception:
            pass


def send_raw_command(address: str, command: str, timeout_ms: int = 1000) -> str:
    inst, via = open_resource(address)
    try:
        inst.timeout = timeout_ms
        stripped = command.strip()
        if stripped.startswith("?") or stripped.endswith("?"):
            return inst.query(command).strip()
        inst.write(command)
        return f"Write sent via {via} - no response expected"
    finally:
        try:
            inst.close()
        except Exception:
            pass
