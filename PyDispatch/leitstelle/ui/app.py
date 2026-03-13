"""
PyDispatch Leitstelle – Hauptanwendung.
Verwaltet den Applikationsstatus und die Navigation.
"""

import customtkinter as ctk

from leitstelle.config.settings import config_exists, get_mysql_config, get_leitstellen_id
from leitstelle.database.connection import db
from leitstelle.services.leitstellen_service import LeitstellenService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledLabel, show_error,
)
from leitstelle.ui.setup.setup_wizard import SetupWizard
from leitstelle.ui.setup.config_editor import ConfigEditor
from leitstelle.ui.dashboard.dashboard import DashboardView
from leitstelle.ui.alarm.alarm_view import AlarmView
from leitstelle.ui.einsaetze.einsatz_view import EinsatzView


class LeitstelleApp(ctk.CTk):
    """Hauptfenster der Leitstellen-Anwendung."""

    def __init__(self):
        super().__init__()

        self.title("PyDispatch – Leitstelle")
        self.geometry("1280x800")
        self.minsize(1000, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg_dark"])

        self.leitstelle_db_id = None
        self.leitstelle_name = None
        self._auto_refresh_id = None

        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)

        self._check_state()

    def _check_state(self):
        """Prüft den Anwendungsstatus und zeigt die entsprechende Ansicht."""
        if not config_exists():
            self._show_setup()
            return

        # Config vorhanden → Verbinden
        cfg = get_mysql_config()
        connected = db.connect(
            cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["database"]
        )
        if not connected:
            self._show_connection_error()
            return

        # Leitstellen-ID validieren
        ls_id = get_leitstellen_id()
        if not ls_id:
            self._show_setup()
            return

        ok, msg, ls_data = LeitstellenService.validate_leitstellen_id(ls_id)
        if not ok:
            show_error("Leitstellen-Fehler", msg)
            self._show_setup()
            return

        self.leitstelle_db_id = ls_data["id"]
        self.leitstelle_name = ls_data["name"]

        # Letzten Kontakt aktualisieren
        LeitstellenService.update_letzter_kontakt(ls_id)

        self._show_main()

    def _clear_all(self):
        """Entfernt alle Widgets."""
        if self._auto_refresh_id:
            self.after_cancel(self._auto_refresh_id)
            self._auto_refresh_id = None
        for w in self.winfo_children():
            w.destroy()

    def _show_setup(self):
        """Zeigt den Setup-Wizard."""
        self._clear_all()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        wizard = SetupWizard(self, on_complete=self._check_state)
        wizard.grid(row=0, column=0, sticky="nsew")

    def _show_connection_error(self):
        """Zeigt einen Verbindungsfehler mit Konfigurations-Option."""
        self._clear_all()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        StyledLabel(frame, text="⚠️", style="huge").pack(pady=(0, 10))
        StyledLabel(
            frame, text="Verbindung zur Datenbank fehlgeschlagen",
            style="subtitle"
        ).pack(pady=(0, 10))
        StyledLabel(
            frame,
            text="Bitte prüfen Sie die MySQL-Server-Einstellungen\n"
                 "oder wenden Sie sich an den Administrator.",
            style="normal"
        ).pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack()

        StyledButton(
            btn_row, text="Konfiguration ändern", variant="warning",
            command=lambda: ConfigEditor(self, on_save=self._check_state),
            width=200
        ).pack(side="left", padx=8)

        StyledButton(
            btn_row, text="Erneut versuchen", variant="success",
            command=self._check_state, width=160
        ).pack(side="left", padx=8)

    def _show_main(self):
        """Zeigt die Hauptansicht mit Sidebar und Content."""
        self._clear_all()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        sidebar = StyledFrame(self, corner_radius=0, fg_color=COLORS["bg_card"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(5, weight=1)

        # Logo / Titel
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(20, 5))

        StyledLabel(title_frame, text="🏥", style="big").pack()
        StyledLabel(title_frame, text="Leitstelle", style="heading").pack()

        name_lbl = StyledLabel(title_frame, text=self.leitstelle_name or "—", style="small")
        name_lbl.configure(text_color=COLORS["text_secondary"])
        name_lbl.pack(pady=(2, 0))

        # Separator
        ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1).grid(
            row=1, column=0, sticky="ew", padx=15, pady=10
        )

        # Navigation Buttons
        nav_items = [
            ("🏠  Dashboard", "dashboard"),
            ("🚨  Einsätze", "einsaetze"),
        ]

        self._nav_buttons = {}
        for idx, (text, key) in enumerate(nav_items):
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w",
                fg_color="transparent", text_color=COLORS["text"],
                hover_color=COLORS["bg_input"],
                font=ctk.CTkFont(size=15), height=42,
                corner_radius=8,
                command=lambda k=key: self._navigate(k),
            )
            btn.grid(row=2 + idx, column=0, sticky="ew", padx=10, pady=3)
            self._nav_buttons[key] = btn

        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").grid(row=5, column=0, sticky="nsew")

        # Footer-Buttons
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=6, column=0, sticky="ew", padx=10, pady=(5, 10))

        StyledButton(
            footer, text="⚙ Einstellungen", variant="primary",
            command=self._open_config, width=160
        ).pack(fill="x", pady=3)

        # ── Content-Bereich ──
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._current_view = None
        self._navigate("dashboard")

        # Auto-Refresh starten (alle 15 Sekunden)
        self._start_auto_refresh()

    def _navigate(self, view_name: str):
        """Wechselt die aktive Ansicht."""
        # Highlight aktiven Nav-Button
        for key, btn in self._nav_buttons.items():
            if key == view_name:
                btn.configure(fg_color=COLORS["primary"])
            else:
                btn.configure(fg_color="transparent")

        # Content wechseln
        for w in self.content_frame.winfo_children():
            w.destroy()

        if view_name == "dashboard":
            self._current_view = DashboardView(
                self.content_frame, on_alarm=self._open_alarm
            )
            self._current_view.grid(row=0, column=0, sticky="nsew")
        elif view_name == "einsaetze":
            self._current_view = EinsatzView(self.content_frame)
            self._current_view.grid(row=0, column=0, sticky="nsew")

    def _open_alarm(self):
        """Öffnet die Alarm-Ansicht (Vollbild über Content)."""
        for w in self.content_frame.winfo_children():
            w.destroy()

        # Nav-Buttons deaktivieren (kein Highlight)
        for btn in self._nav_buttons.values():
            btn.configure(fg_color="transparent")

        alarm = AlarmView(
            self.content_frame,
            leitstelle_db_id=self.leitstelle_db_id,
            on_done=self._alarm_done,
        )
        alarm.grid(row=0, column=0, sticky="nsew")

    def _alarm_done(self):
        """Wird nach Abschluss der Alarmierung aufgerufen."""
        self._navigate("dashboard")

    def _open_config(self):
        """Öffnet den Config-Editor."""
        ConfigEditor(self, on_save=self._check_state)

    def _start_auto_refresh(self):
        """Startet den Auto-Refresh (alle 15 Sekunden)."""
        self._auto_refresh()

    def _auto_refresh(self):
        """Aktualisiert die aktuelle Ansicht periodisch."""
        if not self.winfo_exists():
            return
        try:
            if self._current_view and hasattr(self._current_view, "refresh_data"):
                self._current_view.refresh_data()
            # Letzten Kontakt aktualisieren
            ls_id = get_leitstellen_id()
            if ls_id:
                LeitstellenService.update_letzter_kontakt(ls_id)
        except Exception:
            pass
        self._auto_refresh_id = self.after(15000, self._auto_refresh)
