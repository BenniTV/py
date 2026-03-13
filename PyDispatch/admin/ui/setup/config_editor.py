"""
PyDispatch Admin – Konfigurations-Editor.
Ermöglicht die Änderung der MySQL-Verbindungsdaten und des Einrichtungsnamens.
"""

import customtkinter as ctk

from admin.config.settings import get_mysql_config, get_einrichtung_name, save_mysql_config, save_einrichtung_name
from admin.database.connection import db
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel, show_error, show_info,
)
from admin.utils.validators import validate_not_empty, validate_port


class ConfigEditor(ctk.CTkToplevel):
    """Dialog zur Änderung der Konfiguration."""

    def __init__(self, master, on_save=None):
        super().__init__(master)
        self.title("Konfiguration ändern")
        self.geometry("550x620")
        self.minsize(500, 550)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_dark"])
        self.on_save = on_save

        # Aktuelle Werte laden
        mysql_cfg = get_mysql_config()
        einrichtung = get_einrichtung_name()

        container = StyledFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Konfiguration ändern", style="subtitle").pack(
            padx=20, pady=(20, 10)
        )

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.host_var = ctk.StringVar(value=mysql_cfg.get("host", "localhost"))
        self.port_var = ctk.StringVar(value=str(mysql_cfg.get("port", 3306)))
        self.user_var = ctk.StringVar(value=mysql_cfg.get("user", ""))
        self.pw_var = ctk.StringVar(value=mysql_cfg.get("password", ""))
        self.db_var = ctk.StringVar(value=mysql_cfg.get("database", ""))
        self.name_var = ctk.StringVar(value=einrichtung)

        for label, var, show in [
            ("Host", self.host_var, None),
            ("Port", self.port_var, None),
            ("DB-Benutzername", self.user_var, None),
            ("DB-Passwort", self.pw_var, "•"),
            ("Datenbankname", self.db_var, None),
            ("Einrichtungsname", self.name_var, None),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(anchor="w", pady=(10, 3))
            kw = {"master": scroll, "textvariable": var, "height": 38}
            if show:
                kw["show"] = show
            StyledEntry(**kw).pack(fill="x", pady=(0, 2))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        StyledButton(btn_frame, text="Testen", variant="warning", command=self._test).pack(side="left", padx=(0, 10))
        StyledButton(btn_frame, text="Speichern", variant="success", command=self._save).pack(side="right")

        self.grab_set()

    def _test(self):
        valid, msg = validate_port(self.port_var.get())
        if not valid:
            show_error("Fehler", msg)
            return
        ok, msg = db.test_connection(
            self.host_var.get(), int(self.port_var.get()),
            self.user_var.get(), self.pw_var.get(), self.db_var.get() or None,
        )
        if ok:
            show_info("Erfolg", "Verbindung erfolgreich!")
        else:
            show_error("Fehler", msg)

    def _save(self):
        for val, name in [(self.host_var.get(), "Host"), (self.user_var.get(), "Benutzer"),
                          (self.db_var.get(), "Datenbank"), (self.name_var.get(), "Einrichtung")]:
            ok, msg = validate_not_empty(val, name)
            if not ok:
                show_error("Fehler", msg)
                return
        ok, msg = validate_port(self.port_var.get())
        if not ok:
            show_error("Fehler", msg)
            return

        save_mysql_config(
            self.host_var.get(), int(self.port_var.get()),
            self.user_var.get(), self.pw_var.get(), self.db_var.get(),
        )
        save_einrichtung_name(self.name_var.get())
        show_info("Gespeichert", "Konfiguration wurde aktualisiert.\nBitte melden Sie sich erneut an.")
        if self.on_save:
            self.on_save()
        self.destroy()
