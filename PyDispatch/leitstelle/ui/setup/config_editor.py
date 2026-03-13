"""
PyDispatch Leitstelle – Konfigurations-Editor.
Ermöglicht die Änderung der MySQL-Verbindungsdaten und der Leitstellen-ID.
"""

import customtkinter as ctk

from leitstelle.config.settings import (
    get_mysql_config, get_leitstellen_id, save_mysql_config, save_leitstellen_id,
)
from leitstelle.database.connection import db
from leitstelle.services.leitstellen_service import LeitstellenService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel, show_error, show_info,
)


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
        ls_id = get_leitstellen_id()

        container = StyledFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Konfiguration ändern", style="subtitle").pack(
            padx=20, pady=(20, 10)
        )

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.host_var = ctk.StringVar(value=mysql_cfg.get("host", "localhost"))
        self.port_var = ctk.StringVar(value=str(mysql_cfg.get("port", 3306)))
        self.user_var = ctk.StringVar(value=mysql_cfg.get("user", ""))
        self.pw_var = ctk.StringVar(value=mysql_cfg.get("password", ""))
        self.db_var = ctk.StringVar(value=mysql_cfg.get("database", ""))
        self.ls_id_var = ctk.StringVar(value=ls_id)

        for label, var, show in [
            ("Host", self.host_var, None),
            ("Port", self.port_var, None),
            ("DB-Benutzername", self.user_var, None),
            ("DB-Passwort", self.pw_var, "•"),
            ("Datenbankname", self.db_var, None),
            ("Leitstellen-ID", self.ls_id_var, None),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(anchor="w", pady=(10, 3))
            kw = {"master": scroll, "textvariable": var, "height": 38}
            if show:
                kw["show"] = show
            StyledEntry(**kw).pack(fill="x", pady=(0, 2))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        StyledButton(btn_frame, text="Testen", variant="warning",
                     command=self._test, width=120).pack(side="left", padx=(0, 10))
        StyledButton(btn_frame, text="Abbrechen", variant="danger",
                     command=self.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Speichern", variant="success",
                     command=self._save, width=150).pack(side="right")

        self.grab_set()

    def _test(self):
        try:
            port = int(self.port_var.get())
        except ValueError:
            show_error("Fehler", "Port muss eine Zahl sein.")
            return
        ok, msg = db.test_connection(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(),
            self.db_var.get() or None,
        )
        if ok:
            show_info("Erfolg", "Verbindung erfolgreich!")
        else:
            show_error("Fehler", msg)

    def _save(self):
        for val, name in [
            (self.host_var.get(), "Host"),
            (self.user_var.get(), "Benutzer"),
            (self.db_var.get(), "Datenbank"),
            (self.ls_id_var.get(), "Leitstellen-ID"),
        ]:
            if not val.strip():
                show_error("Fehler", f"{name} darf nicht leer sein.")
                return
        try:
            port = int(self.port_var.get())
        except ValueError:
            show_error("Fehler", "Port muss eine Zahl sein.")
            return

        save_mysql_config(
            self.host_var.get(), port,
            self.user_var.get(), self.pw_var.get(), self.db_var.get(),
        )
        save_leitstellen_id(self.ls_id_var.get().strip())
        show_info("Gespeichert", "Konfiguration wurde aktualisiert.\nBitte starten Sie die Anwendung neu.")
        if self.on_save:
            self.on_save()
        self.destroy()
