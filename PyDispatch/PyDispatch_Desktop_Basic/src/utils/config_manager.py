import json
import os


CONFIG_FILE = "db_config_basic.json"


class ConfigManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", CONFIG_FILE)

    def config_exists(self):
        return os.path.exists(self.config_path)

    def save_config(self, host, port, user, password, database, leitstelle_id):
        data = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "leitstelle_id": leitstelle_id,
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_config(self):
        if not self.config_exists():
            return None
        with open(self.config_path, "r") as f:
            data = json.load(f)

        return {
            "host": data.get("host", ""),
            "port": data.get("port", "3306"),
            "user": data.get("user", ""),
            "password": data.get("password", ""),
            "database": data.get("database", ""),
            "leitstelle_id": data.get("leitstelle_id", ""),
        }
