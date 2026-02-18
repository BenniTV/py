import customtkinter as ctk


class SetupView(ctk.CTkFrame):
    def __init__(self, master, on_submit_callback):
        super().__init__(master)
        self.on_submit_callback = on_submit_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        wrapper = ctk.CTkFrame(self, corner_radius=18)
        wrapper.grid(row=0, column=0, padx=28, pady=28, sticky="n")
        wrapper.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(wrapper, text="Leitstelle einrichten", font=("Arial", 30, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 6)
        )
        ctk.CTkLabel(
            wrapper,
            text="Verbinde die Basic-App mit der zentralen Datenbank und bestätige die Leitstellen-ID.",
            font=("Arial", 14),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 18))

        self.entry_host = self._create_input(wrapper, "Host:", "135.125.201.14", 2)
        self.entry_port = self._create_input(wrapper, "Port:", "3306", 3)
        self.entry_user = self._create_input(wrapper, "DB Benutzer:", "pydispatch_admin", 4)
        self.entry_password = self._create_input(wrapper, "DB Passwort:", "", 5, show="*")
        self.entry_database = self._create_input(wrapper, "Datenbank:", "pydispatch_admin", 6)
        self.entry_leitstelle_id = self._create_input(wrapper, "Leitstellen-ID:", "leitstelle-001", 7)

        self.status_label = ctk.CTkLabel(wrapper, text="", font=("Arial", 13), text_color="#d9534f")
        self.status_label.grid(row=8, column=0, columnspan=2, sticky="w", padx=20, pady=(8, 6))

        ctk.CTkButton(
            wrapper,
            text="Verbindung prüfen & starten",
            height=42,
            font=("Arial", 15, "bold"),
            command=self.submit,
        ).grid(row=9, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 18))

    def _create_input(self, parent, label, placeholder, row, show=None):
        ctk.CTkLabel(parent, text=label, font=("Arial", 14)).grid(row=row, column=0, sticky="w", padx=20, pady=8)
        entry = ctk.CTkEntry(parent, height=40, font=("Arial", 13), show=show, placeholder_text=placeholder)
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=8)
        return entry

    def set_status(self, message, is_error=True):
        color = "#d9534f" if is_error else "#2e8b57"
        self.status_label.configure(text=message, text_color=color)

    def submit(self):
        data = {
            "host": self.entry_host.get().strip(),
            "port": self.entry_port.get().strip() or "3306",
            "user": self.entry_user.get().strip(),
            "password": self.entry_password.get().strip(),
            "database": self.entry_database.get().strip(),
            "leitstelle_id": self.entry_leitstelle_id.get().strip(),
        }

        if not all([data["host"], data["port"], data["user"], data["database"], data["leitstelle_id"]]):
            self.set_status("Bitte alle Pflichtfelder ausfüllen")
            return

        try:
            self.on_submit_callback(data)
        except Exception as exc:
            self.set_status(f"Fehler: {exc}")
