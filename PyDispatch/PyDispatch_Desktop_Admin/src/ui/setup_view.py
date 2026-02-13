import customtkinter as ctk

class SetupView(ctk.CTkFrame):
    def __init__(self, master, on_setup_complete_callback):
        super().__init__(master)
        self.on_setup_complete_callback = on_setup_complete_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self.main_frame, text="Ersteinrichtung PyDispatch Admin", font=("Arial", 20, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # Database Configuration
        self._create_section("Datenbank Verbindung", 1)
        
        self.entry_host = self._create_input("Host:", "135.125.201.14", 2)
        self.entry_port = self._create_input("Port:", "3306", 3)
        self.entry_db_user = self._create_input("DB Benutzer:", "pydispatch_admin", 4)
        self.entry_db_pass = self._create_input("DB Passwort:", "pydispatch_admin2026!", 5, show="*")
        self.entry_db_name = self._create_input("Datenbank Name:", "pydispatch_admin", 6)

        # General Configuration
        self._create_section("Allgemeine Einstellungen", 7)
        self.entry_setup_name = self._create_input("Einrichtungsname:", "Hauptschule Musterstadt", 8)

        # SuperAdmin
        self._create_section("SuperAdmin Konto erstellen", 9)
        self.entry_admin_user = self._create_input("Admin Benutzername:", "admin", 10)
        self.entry_admin_pass = self._create_input("Admin Passwort:", "", 11, show="*")

        # Submit Button
        self.btn_submit = ctk.CTkButton(self.main_frame, text="Einrichtung abschließen", command=self.on_submit, height=40)
        self.btn_submit.grid(row=12, column=0, columnspan=2, pady=30, padx=20, sticky="ew")

        # Status Label
        self.label_status = ctk.CTkLabel(self.main_frame, text="", text_color="red")
        self.label_status.grid(row=13, column=0, columnspan=2, pady=(0, 20))

    def _create_section(self, text, row):
        label = ctk.CTkLabel(self.main_frame, text=text, font=("Arial", 14, "bold"), anchor="w")
        label.grid(row=row, column=0, columnspan=2, pady=(15, 5), padx=20, sticky="w")

    def _create_input(self, label_text, placeholder, row, show=None):
        label = ctk.CTkLabel(self.main_frame, text=label_text, anchor="w")
        label.grid(row=row, column=0, padx=20, pady=5, sticky="w")
        
        entry = ctk.CTkEntry(self.main_frame, placeholder_text=placeholder, show=show)
        entry.grid(row=row, column=1, padx=20, pady=5, sticky="ew")
        return entry

    def on_submit(self):
        # Gather data
        data = {
            "host": self.entry_host.get(),
            "port": self.entry_port.get(),
            "db_user": self.entry_db_user.get(),
            "db_pass": self.entry_db_pass.get(),
            "db_name": self.entry_db_name.get(),
            "setup_name": self.entry_setup_name.get(),
            "admin_user": self.entry_admin_user.get(),
            "admin_pass": self.entry_admin_pass.get()
        }

        # Basic Validation
        if not all([data["host"], data["port"], data["db_user"], data["db_name"], data["setup_name"], data["admin_user"], data["admin_pass"]]):
            self.label_status.configure(text="Bitte alle Felder ausfüllen!", text_color="red")
            return

        # Callback to logic handler
        try:
            self.on_setup_complete_callback(data)
        except Exception as e:
            self.label_status.configure(text=f"Fehler: {str(e)}", text_color="red")
