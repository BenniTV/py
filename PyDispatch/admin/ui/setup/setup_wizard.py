"""
PyDispatch Admin – Setup-Wizard.
Ersteinrichtung: MySQL-Verbindung, Einrichtungsname, SuperAdmin.
"""

import customtkinter as ctk

from admin.config.settings import config_exists, save_mysql_config, save_einrichtung_name
from admin.database.connection import db
from admin.database.schema import initialize_database, check_tables_exist
from admin.services.user_service import UserService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel, show_error, show_info,
)
from admin.utils.validators import validate_not_empty, validate_port, validate_username, validate_password


class SetupWizard(ctk.CTkFrame):
    """Setup-Wizard für die Ersteinrichtung."""

    def __init__(self, master, on_complete):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.on_complete = on_complete
        self.current_step = 0

        # Haupt-Container
        self.container = StyledFrame(self, width=500)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Titel
        self.title_label = StyledLabel(
            self.container, text="PyDispatch – Ersteinrichtung", style="title"
        )
        self.title_label.pack(padx=40, pady=(30, 5))

        self.step_label = StyledLabel(
            self.container, text="Schritt 1 von 3: MySQL-Verbindung", style="small"
        )
        self.step_label.configure(text_color=COLORS["text_secondary"])
        self.step_label.pack(padx=40, pady=(0, 20))

        # Content-Bereich
        self.content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Button-Bereich
        self.button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=40, pady=(10, 30))

        # Variablen für MySQL
        self.mysql_host = ctk.StringVar(value="localhost")
        self.mysql_port = ctk.StringVar(value="3306")
        self.mysql_user = ctk.StringVar()
        self.mysql_password = ctk.StringVar()
        self.mysql_database = ctk.StringVar()

        # Variablen für Einrichtung
        self.einrichtung_name = ctk.StringVar()

        # Variablen für SuperAdmin
        self.admin_username = ctk.StringVar()
        self.admin_password = ctk.StringVar()
        self.admin_password_confirm = ctk.StringVar()

        self._show_step(0)

    def _clear_content(self):
        """Leert den Content-Bereich."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def _show_step(self, step: int):
        """Zeigt den aktuellen Schritt an."""
        self.current_step = step
        self._clear_content()

        steps = [self._step_mysql, self._step_einrichtung, self._step_superadmin]
        step_labels = [
            "Schritt 1 von 3: MySQL-Verbindung",
            "Schritt 2 von 3: Einrichtungsname",
            "Schritt 3 von 3: SuperAdmin-Konto",
        ]
        self.step_label.configure(text=step_labels[step])
        steps[step]()

    def _add_field(self, label: str, variable: ctk.StringVar, show: str = None):
        """Fügt ein Eingabefeld hinzu."""
        StyledLabel(self.content_frame, text=label, style="normal").pack(
            anchor="w", pady=(10, 3)
        )
        entry_kwargs = {"master": self.content_frame, "textvariable": variable}
        if show:
            entry_kwargs["show"] = show
        entry = StyledEntry(**entry_kwargs)
        entry.pack(fill="x", pady=(0, 5))
        return entry

    # ── Schritt 1: MySQL-Verbindung ──

    def _step_mysql(self):
        self._add_field("Host", self.mysql_host)
        self._add_field("Port", self.mysql_port)
        self._add_field("Benutzername", self.mysql_user)
        self._add_field("Passwort", self.mysql_password, show="•")
        self._add_field("Datenbankname", self.mysql_database)

        # Buttons
        test_btn = StyledButton(
            self.button_frame, text="Verbindung testen", variant="warning",
            command=self._test_connection
        )
        test_btn.pack(side="left", padx=(0, 10))

        next_btn = StyledButton(
            self.button_frame, text="Weiter →", command=self._next_mysql
        )
        next_btn.pack(side="right")

    def _test_connection(self):
        """Testet die MySQL-Verbindung."""
        valid, msg = validate_port(self.mysql_port.get())
        if not valid:
            show_error("Fehler", msg)
            return

        success, msg = db.test_connection(
            host=self.mysql_host.get(),
            port=int(self.mysql_port.get()),
            user=self.mysql_user.get(),
            password=self.mysql_password.get(),
            database=self.mysql_database.get() or None,
        )
        if success:
            show_info("Erfolg", "Verbindung erfolgreich!")
        else:
            show_error("Verbindungsfehler", msg)

    def _next_mysql(self):
        """Validiert MySQL-Daten und geht zum nächsten Schritt."""
        fields = [
            (self.mysql_host.get(), "Host"),
            (self.mysql_user.get(), "Benutzername"),
            (self.mysql_database.get(), "Datenbankname"),
        ]
        for value, name in fields:
            valid, msg = validate_not_empty(value, name)
            if not valid:
                show_error("Fehler", msg)
                return

        valid, msg = validate_port(self.mysql_port.get())
        if not valid:
            show_error("Fehler", msg)
            return

        # Verbindung herstellen
        success = db.connect(
            host=self.mysql_host.get(),
            port=int(self.mysql_port.get()),
            user=self.mysql_user.get(),
            password=self.mysql_password.get(),
            database=self.mysql_database.get(),
        )
        if not success:
            show_error("Fehler", "Verbindung zur Datenbank konnte nicht hergestellt werden.")
            return

        # MySQL-Config sofort speichern, damit der Login direkt darauf zugreifen kann
        save_mysql_config(
            host=self.mysql_host.get(),
            port=int(self.mysql_port.get()),
            user=self.mysql_user.get(),
            password=self.mysql_password.get(),
            database=self.mysql_database.get(),
        )

        # Sicherstellen, dass die Tabellen vorhanden sind (bei leerer/neuer DB)
        if not check_tables_exist():
            init_success, init_msg = initialize_database()
            if not init_success:
                show_error("Fehler", init_msg)
                return

        # Prüfen, ob bereits eine Einrichtung existiert
        try:
            result = db.execute("SELECT name FROM einrichtung ORDER BY id ASC LIMIT 1")
            if result and result[0].get("name"):
                einrichtungsname = result[0]["name"]
                save_einrichtung_name(einrichtungsname)
                show_info(
                    "Einrichtung erkannt",
                    "Diese Datenbank ist bereits eingerichtet.\n"
                    "Sie werden direkt zur Anmeldung weitergeleitet.",
                )
                self.on_complete()
                return
        except Exception:
            # Falls die Prüfung fehlschlägt, normal mit Setup fortfahren
            pass

        self._show_step(1)

    # ── Schritt 2: Einrichtungsname ──

    def _step_einrichtung(self):
        StyledLabel(
            self.content_frame,
            text="Geben Sie den Namen Ihrer Einrichtung ein.\n"
                 "Dieser wird zentral in der Datenbank gespeichert.",
            style="normal",
        ).pack(anchor="w", pady=(10, 10))
        self._add_field("Einrichtungsname", self.einrichtung_name)

        back_btn = StyledButton(
            self.button_frame, text="← Zurück", variant="warning",
            command=lambda: self._show_step(0)
        )
        back_btn.pack(side="left")

        next_btn = StyledButton(
            self.button_frame, text="Weiter →", command=self._next_einrichtung
        )
        next_btn.pack(side="right")

    def _next_einrichtung(self):
        valid, msg = validate_not_empty(self.einrichtung_name.get(), "Einrichtungsname")
        if not valid:
            show_error("Fehler", msg)
            return
        self._show_step(2)

    # ── Schritt 3: SuperAdmin ──

    def _step_superadmin(self):
        StyledLabel(
            self.content_frame,
            text="Erstellen Sie das SuperAdmin-Konto.\nDieser Account hat vollständige Kontrolle.",
            style="normal",
        ).pack(anchor="w", pady=(10, 10))

        self._add_field("Benutzername", self.admin_username)
        self._add_field("Passwort", self.admin_password, show="•")
        self._add_field("Passwort wiederholen", self.admin_password_confirm, show="•")

        back_btn = StyledButton(
            self.button_frame, text="← Zurück", variant="warning",
            command=lambda: self._show_step(1)
        )
        back_btn.pack(side="left")

        finish_btn = StyledButton(
            self.button_frame, text="Einrichtung abschließen ✓", variant="success",
            command=self._finish_setup
        )
        finish_btn.pack(side="right")

    def _finish_setup(self):
        """Schließt die Einrichtung ab."""
        # Validierung
        valid, msg = validate_username(self.admin_username.get())
        if not valid:
            show_error("Fehler", msg)
            return

        valid, msg = validate_password(self.admin_password.get())
        if not valid:
            show_error("Fehler", msg)
            return

        if self.admin_password.get() != self.admin_password_confirm.get():
            show_error("Fehler", "Passwörter stimmen nicht überein.")
            return

        # Datenbank initialisieren
        success, msg = initialize_database()
        if not success:
            show_error("Fehler", msg)
            return

        # Einrichtung speichern
        try:
            db.execute_modify("DELETE FROM einrichtung")
            db.execute_insert(
                "INSERT INTO einrichtung (name) VALUES (%s)",
                (self.einrichtung_name.get(),)
            )
        except Exception as e:
            show_error("Fehler", f"Einrichtung konnte nicht gespeichert werden: {e}")
            return

        # SuperAdmin erstellen
        success, msg, _ = UserService.create_user(
            benutzername=self.admin_username.get(),
            passwort=self.admin_password.get(),
            vorname="Super",
            nachname="Admin",
            rolle="superadmin",
        )
        if not success:
            show_error("Fehler", msg)
            return

        # MySQL-Config lokal speichern
        save_mysql_config(
            host=self.mysql_host.get(),
            port=int(self.mysql_port.get()),
            user=self.mysql_user.get(),
            password=self.mysql_password.get(),
            database=self.mysql_database.get(),
        )
        save_einrichtung_name(self.einrichtung_name.get())

        show_info("Erfolg", "Einrichtung erfolgreich abgeschlossen!\nSie können sich jetzt anmelden.")
        self.on_complete()
