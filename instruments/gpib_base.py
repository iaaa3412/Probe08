import pyvisa
import yaml
import sys
import os

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        return os.path.join(base_path, relative_path)
    except Exception:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, relative_path)

class GPIBInstrument:
    def __init__(self, config_key):
        yaml_path = get_resource_path("config/instruments.yaml")
        
        with open(yaml_path, "r") as file:
            config = yaml.safe_load(file)
            
        inst_data = config['instruments'].get(config_key)
        if not inst_data:
            raise ValueError(f"Instrument '{config_key}' not found in YAML.")
            
        self.address = inst_data['address']
        self.timeout = inst_data['timeout_ms']
        
        try:
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource(self.address)
            self.inst.timeout = self.timeout
            self.inst.encoding = "latin-1"
            print(f"[{config_key.upper()}] Connected successfully at {self.address}")
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