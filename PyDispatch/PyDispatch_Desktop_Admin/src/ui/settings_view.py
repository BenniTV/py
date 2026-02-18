import customtkinter as ctk


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager, config_manager, on_config_saved=None):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.on_config_saved = on_config_saved

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.wrapper = ctk.CTkScrollableFrame(self)
        self.wrapper.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.wrapper.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.wrapper, text="Einstellungen", font=("Arial", 30, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(2, 12)
        )

        self._build_setup_section(1)
        self._build_db_section(2)

    def _build_setup_section(self, row):
        section = ctk.CTkFrame(self.wrapper, corner_radius=14)
        section.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 12))
        section.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(section, text="Einrichtung", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 10)
        )

        ctk.CTkLabel(section, text="Einrichtungsname:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=8)
        self.setup_name_entry = ctk.CTkEntry(section, height=40, font=("Arial", 13))
        self.setup_name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=8)
        self.setup_name_entry.insert(0, self.config.get("setup_name") or "")

        self.setup_status_label = ctk.CTkLabel(section, text="", font=("Arial", 13))
        self.setup_status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 6))

        ctk.CTkButton(
            section,
            text="Einrichtungsname speichern",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.save_setup_name
        ).grid(row=3, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))

    def _build_db_section(self, row):
        section = ctk.CTkFrame(self.wrapper, corner_radius=14)
        section.grid(row=row, column=0, sticky="ew", padx=8, pady=(0, 12))
        section.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(section, text="Lokale Datenbank-Verbindung", font=("Arial", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 10)
        )

        self.host_entry = self._create_db_input(section, "Host:", self.config.get("host", ""), 1)
        self.port_entry = self._create_db_input(section, "Port:", self.config.get("port", "3306"), 2)
        self.user_entry = self._create_db_input(section, "DB Benutzer:", self.config.get("user", ""), 3)
        self.password_entry = self._create_db_input(section, "DB Passwort:", self.config.get("password", ""), 4, show="*")
        self.database_entry = self._create_db_input(section, "Datenbank:", self.config.get("database", ""), 5)

        self.db_status_label = ctk.CTkLabel(section, text="", font=("Arial", 13))
        self.db_status_label.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 6))

        ctk.CTkButton(
            section,
            text="Lokale Verbindung speichern",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.save_local_db_config
        ).grid(row=7, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))

    def _create_db_input(self, parent, label_text, value, row, show=None):
        ctk.CTkLabel(parent, text=label_text, font=("Arial", 14)).grid(row=row, column=0, sticky="w", padx=14, pady=8)
        entry = ctk.CTkEntry(parent, height=40, font=("Arial", 13), show=show)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=8)
        if value:
            entry.insert(0, value)
        return entry

    def _set_status(self, label, message, is_error=False):
        color = "#d9534f" if is_error else "#2e8b57"
        label.configure(text=message, text_color=color)

    def save_setup_name(self):
        setup_name = self.setup_name_entry.get().strip()
        if not setup_name:
            self._set_status(self.setup_status_label, "Bitte Einrichtungsname eingeben", is_error=True)
            return

        try:
            self.db_manager.set_setting(self.config, "setup_name", setup_name)
            self.config["setup_name"] = setup_name
            self._set_status(self.setup_status_label, "Einrichtungsname gespeichert")
        except Exception as exc:
            self._set_status(self.setup_status_label, f"Fehler: {exc}", is_error=True)

    def save_local_db_config(self):
        new_config = {
            "host": self.host_entry.get().strip(),
            "port": self.port_entry.get().strip(),
            "user": self.user_entry.get().strip(),
            "password": self.password_entry.get().strip(),
            "database": self.database_entry.get().strip(),
        }

        if not all([new_config["host"], new_config["port"], new_config["user"], new_config["database"]]):
            self._set_status(self.db_status_label, "Bitte alle DB-Felder ausfüllen", is_error=True)
            return

        try:
            self.config_manager.save_config(
                new_config["host"],
                new_config["port"],
                new_config["user"],
                new_config["password"],
                new_config["database"],
            )
            self.config.update(new_config)
            if callable(self.on_config_saved):
                self.on_config_saved(new_config)
            self._set_status(self.db_status_label, "Lokale Verbindungsdaten gespeichert")
        except Exception as exc:
            self._set_status(self.db_status_label, f"Fehler: {exc}", is_error=True)
