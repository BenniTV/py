import json
import os

CONFIG_FILE = "db_config.json"

class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", CONFIG_FILE)
        
    def config_exists(self):
        return os.path.exists(self.config_path)

    def save_config(self, host, port, user, password, database, setup_name):
        data = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "setup_name": setup_name
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_config(self):
        if not self.config_exists():
            return None
        with open(self.config_path, "r") as f:
            return json.load(f)
