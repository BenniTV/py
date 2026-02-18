import customtkinter as ctk

DEFAULT_DB_PORT = "3306"
DEFAULT_DB_USER = "pydispatch_admin"
DEFAULT_DB_PASSWORD = "pydispatch_admin2026!"
DEFAULT_DB_NAME = "pydispatch_admin"

class SetupView(ctk.CTkFrame):
    def __init__(self, master, on_setup_complete_callback):
        super().__init__(master)
        self.on_setup_complete_callback = on_setup_complete_callback
        self.input_rows = {}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.form_frame = ctk.CTkFrame(self.main_frame, corner_radius=18)
        self.form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.form_frame.grid_columnconfigure(0, minsize=190)
        self.form_frame.grid_columnconfigure(1, weight=1, minsize=500)

        # Title
        self.label_title = ctk.CTkLabel(self.form_frame, text="Ersteinrichtung PyDispatch Admin", font=("Arial", 32, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=(24, 6), padx=24)

        self.label_subtitle = ctk.CTkLabel(
            self.form_frame,
            text="Verbinde das Admin-Notebook mit der zentralen Schul-Datenbank",
            font=("Arial", 14)
        )
        self.label_subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 22), padx=24)

        # Mode Switch
        self.mode_selector = ctk.CTkSegmentedButton(
            self.form_frame,
            values=["Neu einrichten", "Bestehende Schule verbinden"],
            command=self.on_mode_change
        )
        self.mode_selector.grid(row=2, column=0, columnspan=2, padx=24, pady=(0, 22), sticky="ew")
        self.mode_selector.set("Neu einrichten")

        # Database Configuration
        self._create_section("Datenbank Verbindung", 3)
        
        self.entry_host = self._create_input("host", "Host:", "135.125.201.14", 4)
        self.entry_port = self._create_input("port", "Port:", DEFAULT_DB_PORT, 5)
        self.entry_user = self._create_input("db_user", "DB Benutzer:", DEFAULT_DB_USER, 6)
        self.entry_password = self._create_input("db_password", "DB Passwort:", DEFAULT_DB_PASSWORD, 7, show="*")
        self.entry_database = self._create_input("database", "Datenbank Name:", DEFAULT_DB_NAME, 8)

        # General Configuration
        self.section_general = self._create_section("Allgemeine Einstellungen", 9)
        self.entry_setup_name = self._create_input("setup_name", "Einrichtungsname:", "Hauptschule Musterstadt", 10)

        # SuperAdmin
        self.section_superadmin = self._create_section("SuperAdmin Konto erstellen", 11)
        self.entry_admin_user = self._create_input("admin_user", "Admin Benutzername:", "admin", 12)
        self.entry_admin_pass = self._create_input("admin_pass", "Admin Passwort:", "", 13, show="*")

        # Existing School Login
        self.section_existing = self._create_section("Bestehenden Admin anmelden", 14)
        self.entry_existing_user = self._create_input("existing_user", "Admin Benutzername:", "admin", 15)
        self.entry_existing_pass = self._create_input("existing_pass", "Admin Passwort:", "", 16, show="*")

        # Submit Button
        self.btn_submit = ctk.CTkButton(
            self.form_frame,
            text="Einrichtung abschließen",
            command=self.on_submit,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold")
        )
        self.btn_submit.grid(row=17, column=0, columnspan=2, padx=24, pady=(24, 16), sticky="ew")

        # Status Label
        self.label_status = ctk.CTkLabel(self.form_frame, text="", text_color="#d9534f", font=("Arial", 13))
        self.label_status.grid(row=18, column=0, columnspan=2, pady=(0, 20), padx=24)

        self.on_mode_change("Neu einrichten")

    def _create_section(self, text, row):
        label = ctk.CTkLabel(self.form_frame, text=text, font=("Arial", 15, "bold"), anchor="w")
        label.grid(row=row, column=0, columnspan=2, pady=(16, 8), padx=24, sticky="w")
        return label

    def _create_input(self, key, label_text, placeholder, row, show=None):
        label = ctk.CTkLabel(self.form_frame, text=label_text, anchor="w", font=("Arial", 13))
        label.grid(row=row, column=0, padx=(24, 8), pady=6, sticky="w")
        
        entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text=placeholder,
            show=show,
            height=40,
            corner_radius=10,
            font=("Arial", 13)
        )
        entry.grid(row=row, column=1, padx=(0, 24), pady=6, sticky="ew")
        self.input_rows[key] = (label, entry)
        return entry

    def _show_row(self, key):
        label, entry = self.input_rows[key]
        label.grid()
        entry.grid()

    def _hide_row(self, key):
        label, entry = self.input_rows[key]
        label.grid_remove()
        entry.grid_remove()

    def on_mode_change(self, mode):
        is_setup_mode = mode == "Neu einrichten"

        if is_setup_mode:
            self.label_title.configure(text="Ersteinrichtung PyDispatch Admin")
            self.btn_submit.configure(text="Einrichtung abschließen")
            self.section_general.grid()
            self._show_row("setup_name")
            self.section_superadmin.grid()
            self._show_row("admin_user")
            self._show_row("admin_pass")
            self.section_existing.grid_remove()
            self._hide_row("existing_user")
            self._hide_row("existing_pass")
        else:
            self.label_title.configure(text="Mit bestehender Schule verbinden")
            self.btn_submit.configure(text="Verbinden und anmelden")
            self.section_general.grid_remove()
            self._hide_row("setup_name")
            self.section_superadmin.grid_remove()
            self._hide_row("admin_user")
            self._hide_row("admin_pass")
            self.section_existing.grid()
            self._show_row("existing_user")
            self._show_row("existing_pass")

        self.label_status.configure(text="")

    def on_submit(self):
        mode = self.mode_selector.get()

        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip() or DEFAULT_DB_PORT
        db_user = self.entry_user.get().strip() or DEFAULT_DB_USER
        db_password = self.entry_password.get().strip() or DEFAULT_DB_PASSWORD
        database = self.entry_database.get().strip() or DEFAULT_DB_NAME

        # Gather data
        data = {
            "mode": mode,
            "host": host,
            "port": port,
            "user": db_user,
            "password": db_password,
            "database": database,
            "setup_name": self.entry_setup_name.get(),
            "admin_user": self.entry_admin_user.get(),
            "admin_pass": self.entry_admin_pass.get(),
            "existing_user": self.entry_existing_user.get(),
            "existing_pass": self.entry_existing_pass.get()
        }

        # Basic Validation
        if not data["host"]:
            self.label_status.configure(text="Bitte alle Felder ausfüllen!", text_color="red")
            return

        if mode == "Neu einrichten":
            db_fields_valid = all([data["port"], data["user"], data["database"]])
            if not db_fields_valid:
                self.label_status.configure(text="Bitte alle Felder ausfüllen!", text_color="red")
                return
            if not all([data["setup_name"], data["admin_user"], data["admin_pass"]]):
                self.label_status.configure(text="Bitte alle Felder ausfüllen!", text_color="red")
                return
        else:
            if not all([data["existing_user"], data["existing_pass"]]):
                self.label_status.configure(text="Bitte bestehende Admin-Zugangsdaten eingeben!", text_color="red")
                return

        # Callback to logic handler
        try:
            self.on_setup_complete_callback(data)
        except Exception as e:
            self.label_status.configure(text=f"Fehler: {str(e)}", text_color="red")
