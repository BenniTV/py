import customtkinter as ctk
import sys
import os

# Add src to path so imports work cleanly
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.config_manager import ConfigManager
from ui.setup_view import SetupView
from ui.login_view import LoginView
from ui.dashboard_view import DashboardView
from database.db_manager import DBManager

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyDispatch Admin")
        self.geometry("1360x860")
        self.minsize(1180, 760)
        
        # Initialize Config Manager
        self.config_manager = ConfigManager()
        self.db_manager = DBManager()

        # Build Main UI Container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.check_initial_setup()

    def check_initial_setup(self):
        if not self.config_manager.config_exists():
            self.show_setup_view()
        else:
            self.show_login_view()

    def show_setup_view(self):
        self._clear_container()
        setup_view = SetupView(self.container, self.handle_setup_complete)
        setup_view.pack(fill="both", expand=True)

    def show_login_view(self):
        self._clear_container()
        login_view = LoginView(self.container, self.handle_login)
        login_view.pack(fill="both", expand=True)

    def handle_login(self, username, password, error_callback):
        try:
            config = self.config_manager.load_config()
            if not config:
                error_callback("Keine Datenbank-Konfiguration gefunden")
                return

            setup_name = self.db_manager.get_setup_name(config)
            if setup_name:
                config["setup_name"] = setup_name

            user = self.db_manager.authenticate_user(config, username, password)
            if user:
                print(f"Login successful: {username}")
                self.show_dashboard_view(config, user)
            else:
                error_callback("Ungültiger Benutzername oder Passwort")
        except Exception as e:
            print(f"Login error: {e}")
            error_callback(f"Verbindungsfehler: {str(e)}")

    def show_dashboard_view(self, config, user):
        self._clear_container()
        dashboard = DashboardView(self.container, config, user, self.db_manager, self.config_manager)
        dashboard.pack(fill="both", expand=True)

    def handle_setup_complete(self, data):
        try:
            mode = data.get("mode", "Neu einrichten")

            if mode == "Neu einrichten":
                # Initialize Database
                self.db_manager.initialize_database(data, data)

                # Save Config locally
                self.config_manager.save_config(
                    data["host"], data["port"], data["user"],
                    data["password"], data["database"]
                )
                print("Config saved. Switching to Login.")
                self.show_login_view()
                return

            config = {
                "host": data["host"],
                "port": data["port"],
                "user": data["user"],
                "password": data["password"],
                "database": data["database"]
            }

            user = self.db_manager.authenticate_user(
                config,
                data["existing_user"],
                data["existing_pass"]
            )
            if not user:
                raise Exception("Ungültige Admin-Zugangsdaten")

            if user.get("role") not in ("admin", "superadmin"):
                raise Exception("Nur Admin oder SuperAdmin können ein Admin-Notebook verbinden")

            setup_name = self.db_manager.get_setup_name(config)
            if setup_name:
                config["setup_name"] = setup_name

            self.config_manager.save_config(
                config["host"], config["port"], config["user"],
                config["password"], config["database"]
            )
            print("Existing setup connected. Opening dashboard.")
            self.show_dashboard_view(config, user)
        except Exception as e:
            print(f"Error during setup: {e}")
            self._clear_container()
            ctk.CTkLabel(self.container, text=f"Fehler: {e}", text_color="red").pack(pady=50)
            ctk.CTkButton(self.container, text="Zurück", command=self.show_setup_view).pack()

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    ctk.set_widget_scaling(1.12)
    ctk.set_window_scaling(1.06)
    
    app = AdminApp()
    app.mainloop()
