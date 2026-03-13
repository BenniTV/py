"""
PyDispatch Leitstelle – Setup-Wizard.
Zwei Schritte: MySQL-Verbindung → Leitstellen-ID.
"""

import customtkinter as ctk

from leitstelle.config.settings import save_mysql_config, save_leitstellen_id
from leitstelle.database.connection import db
from leitstelle.services.leitstellen_service import LeitstellenService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel, show_error, show_info,
)


class SetupWizard(ctk.CTkFrame):
    """Setup-Wizard für die Ersteinrichtung der Leitstelle."""

    def __init__(self, master, on_complete=None):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.on_complete = on_complete
        self.step = 1

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = StyledFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        StyledLabel(header, text="🏥 PyDispatch Leitstelle – Einrichtung", style="title").pack(
            padx=30, pady=20
        )

        # Content-Bereich
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Footer
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 30))

        self._show_step_1()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        for w in self.footer.winfo_children():
            w.destroy()

    def _show_step_1(self):
        """Schritt 1: MySQL-Verbindungsdaten."""
        self._clear_content()
        self.step = 1

        card = StyledFrame(self.content)
        card.grid(row=0, column=0, sticky="nsew", padx=50)

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)

        StyledLabel(scroll, text="Schritt 1 von 2", style="small").pack(anchor="w")
        StyledLabel(scroll, text="MySQL-Verbindung", style="subtitle").pack(
            anchor="w", pady=(5, 5)
        )
        StyledLabel(
            scroll,
            text="Geben Sie die Verbindungsdaten zum zentralen MySQL-Server ein.",
            style="normal"
        ).pack(anchor="w", pady=(0, 15))

        self.host_var = ctk.StringVar(value="localhost")
        self.port_var = ctk.StringVar(value="3306")
        self.user_var = ctk.StringVar()
        self.pw_var = ctk.StringVar()
        self.db_var = ctk.StringVar()

        for label, var, show in [
            ("Host *", self.host_var, None),
            ("Port *", self.port_var, None),
            ("Benutzername *", self.user_var, None),
            ("Passwort *", self.pw_var, "•"),
            ("Datenbankname *", self.db_var, None),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(anchor="w", pady=(10, 3))
            kw = {"master": scroll, "textvariable": var, "height": 38}
            if show:
                kw["show"] = show
            StyledEntry(**kw).pack(fill="x", pady=(0, 2))

        # Footer-Buttons
        StyledButton(
            self.footer, text="Verbindung testen", variant="warning",
            command=self._test_connection, width=180
        ).pack(side="left")
        StyledButton(
            self.footer, text="Weiter →", variant="success",
            command=self._next_step_1, width=150
        ).pack(side="right")

    def _test_connection(self):
        """Testet die MySQL-Verbindung."""
        try:
            port = int(self.port_var.get())
        except ValueError:
            show_error("Fehler", "Port muss eine Zahl sein.")
            return

        ok, msg = db.test_connection(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(),
            self.db_var.get() or None
        )
        if ok:
            show_info("Erfolg", "Verbindung erfolgreich!")
        else:
            show_error("Fehler", msg)

    def _next_step_1(self):
        """Validiert Schritt 1 und geht zu Schritt 2."""
        for name, var in [("Host", self.host_var), ("Port", self.port_var),
                          ("Benutzername", self.user_var), ("Datenbankname", self.db_var)]:
            if not var.get().strip():
                show_error("Fehler", f"{name} darf nicht leer sein.")
                return

        try:
            port = int(self.port_var.get())
        except ValueError:
            show_error("Fehler", "Port muss eine Zahl sein.")
            return

        # Verbindung testen
        ok, msg = db.test_connection(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(),
            self.db_var.get()
        )
        if not ok:
            show_error("Verbindung fehlgeschlagen", msg)
            return

        # Verbindung herstellen
        connected = db.connect(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(),
            self.db_var.get()
        )
        if not connected:
            show_error("Fehler", "Verbindung konnte nicht hergestellt werden.")
            return

        # MySQL-Daten speichern
        save_mysql_config(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(),
            self.db_var.get()
        )

        self._show_step_2()

    def _show_step_2(self):
        """Schritt 2: Leitstellen-ID eingeben."""
        self._clear_content()
        self.step = 2

        card = StyledFrame(self.content)
        card.grid(row=0, column=0, sticky="nsew", padx=50)

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=25)

        StyledLabel(scroll, text="Schritt 2 von 2", style="small").pack(anchor="w")
        StyledLabel(scroll, text="Leitstellen-ID", style="subtitle").pack(
            anchor="w", pady=(5, 5)
        )
        StyledLabel(
            scroll,
            text="Geben Sie die Leitstellen-ID ein, die in der\n"
                 "Admin-Anwendung für diese Leitstelle generiert wurde.",
            style="normal"
        ).pack(anchor="w", pady=(0, 10))

        StyledLabel(
            scroll,
            text="Die ID hat das Format: LS-XXXXXXXX",
            style="small"
        ).pack(anchor="w", pady=(0, 15))

        self.ls_id_var = ctk.StringVar()

        StyledLabel(scroll, text="Leitstellen-ID *", style="small").pack(
            anchor="w", pady=(10, 3)
        )
        StyledEntry(scroll, textvariable=self.ls_id_var, height=42,
                    font=ctk.CTkFont(size=18, weight="bold")).pack(
            fill="x", pady=(0, 20)
        )

        # Footer-Buttons
        StyledButton(
            self.footer, text="← Zurück", variant="primary",
            command=self._show_step_1, width=120
        ).pack(side="left")
        StyledButton(
            self.footer, text="Einrichtung abschließen ✓", variant="success",
            command=self._finish_setup, width=220
        ).pack(side="right")

    def _finish_setup(self):
        """Validiert die Leitstellen-ID und schließt das Setup ab."""
        ls_id = self.ls_id_var.get().strip()
        if not ls_id:
            show_error("Fehler", "Leitstellen-ID darf nicht leer sein.")
            return

        # Leitstellen-ID in DB validieren
        ok, msg, ls_data = LeitstellenService.validate_leitstellen_id(ls_id)
        if not ok:
            show_error("Fehler", msg)
            return

        # Leitstellen-ID lokal speichern
        save_leitstellen_id(ls_id)

        # Letzten Kontakt aktualisieren
        LeitstellenService.update_letzter_kontakt(ls_id)

        show_info(
            "Einrichtung abgeschlossen",
            f"Leitstelle '{ls_data['name']}' wurde erfolgreich eingerichtet.\n\n"
            "Die Software startet nun in die Leitstellen-Ansicht."
        )

        if self.on_complete:
            self.on_complete()
