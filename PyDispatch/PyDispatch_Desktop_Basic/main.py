import customtkinter as ctk
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from database.db_manager import DBManager
from ui.dashboard_view import DashboardView
from ui.setup_view import SetupView
from utils.config_manager import ConfigManager


class BasicApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyDispatch Leitstelle")
        self.geometry("1360x860")
        self.minsize(1160, 740)

        self.config_manager = ConfigManager()
        self.db_manager = DBManager()
        self.runtime_config = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.bootstrap()

    def bootstrap(self):
        if not self.config_manager.config_exists():
            self.show_setup_view()
            return

        config = self.config_manager.load_config()
        if not config:
            self.show_setup_view()
            return

        try:
            is_valid, _ = self.db_manager.validate_leitstelle_id(config, config.get("leitstelle_id", ""))
            if not is_valid:
                self.show_setup_view()
                return

            self.runtime_config = config
            self.show_dashboard_view()
        except Exception:
            self.show_setup_view()

    def show_setup_view(self):
        self._clear_container()
        setup = SetupView(self.container, self.handle_setup_submit)
        setup.pack(fill="both", expand=True)

    def show_dashboard_view(self):
        self._clear_container()
        dashboard = DashboardView(self.container, self.runtime_config, self.db_manager)
        dashboard.pack(fill="both", expand=True)

    def handle_setup_submit(self, data):
        is_valid, message = self.db_manager.validate_leitstelle_id(data, data["leitstelle_id"])
        if not is_valid:
            raise Exception(message)

        self.config_manager.save_config(
            data["host"],
            data["port"],
            data["user"],
            data["password"],
            data["database"],
            data["leitstelle_id"],
        )
        self.runtime_config = data
        self.show_dashboard_view()

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    ctk.set_widget_scaling(1.12)
    ctk.set_window_scaling(1.05)

    app = BasicApp()
    app.mainloop()
