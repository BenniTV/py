"""
PyDispatch Admin – Hauptfenster.
Navigiert zwischen Setup, Login und den Hauptmodulen.
"""

import customtkinter as ctk

from admin.config.settings import config_exists, get_mysql_config, get_einrichtung_name
from admin.database.connection import db
from admin.database.schema import check_tables_exist
from admin.services.auth_service import AuthService
from admin.ui.components.widgets import COLORS, StyledButton, StyledLabel
from admin.ui.setup.setup_wizard import SetupWizard
from admin.ui.auth.login import LoginView
from admin.ui.dashboard.dashboard import DashboardView
from admin.ui.users.user_management import UserManagementView
from admin.ui.users.group_management import GroupManagementView
from admin.ui.devices.device_management import DeviceManagementView
from admin.ui.keywords.keyword_management import KeywordManagementView


class AdminApp(ctk.CTk):
    """Hauptanwendungsfenster der PyDispatch Admin-Software."""

    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.title("PyDispatch – Administration")
        self.geometry("1200x750")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg_dark"])

        # Haupt-Layout
        self.grid_columnconfigure(0, weight=0)   # Sidebar
        self.grid_columnconfigure(1, weight=1)    # Content
        self.grid_rowconfigure(0, weight=1)

        # Entscheidung: Setup, Login oder Hauptansicht
        self._check_state()

    def _check_state(self):
        """Prüft den Anwendungszustand und zeigt die richtige Ansicht."""
        self._clear_window()

        if not config_exists():
            # Ersteinrichtung
            self._show_setup()
        else:
            # Verbindung herstellen
            mysql_cfg = get_mysql_config()
            success = db.connect(
                host=mysql_cfg["host"],
                port=mysql_cfg["port"],
                user=mysql_cfg["user"],
                password=mysql_cfg["password"],
                database=mysql_cfg["database"],
            )
            if success and check_tables_exist():
                self._show_login()
            else:
                # Config existiert aber Verbindung fehlgeschlagen → Setup
                self._show_setup()

    def _clear_window(self):
        """Entfernt alle Widgets aus dem Fenster."""
        for widget in self.winfo_children():
            widget.destroy()

    # ── Setup ──

    def _show_setup(self):
        """Zeigt den Setup-Wizard."""
        self._clear_window()
        setup = SetupWizard(self, on_complete=self._show_login)
        setup.pack(fill="both", expand=True)

    # ── Login ──

    def _show_login(self):
        """Zeigt den Login-Bildschirm."""
        self._clear_window()
        login = LoginView(
            self,
            on_login_success=self._on_login,
            on_setup=self._check_state,
        )
        login.pack(fill="both", expand=True)

    def _on_login(self, user: dict):
        """Callback nach erfolgreichem Login."""
        self._show_main(user)

    # ── Hauptansicht ──

    def _show_main(self, user: dict):
        """Zeigt die Hauptoberfläche mit Sidebar und Content."""
        self._clear_window()

        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Logo-Bereich
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 10))

        StyledLabel(logo_frame, text="🚑 PyDispatch", style="subtitle").pack(anchor="w")

        einrichtung = get_einrichtung_name()
        if einrichtung:
            info = StyledLabel(logo_frame, text=einrichtung, style="small")
            info.configure(text_color=COLORS["text_secondary"])
            info.pack(anchor="w", pady=(2, 0))

        # Benutzerinfo
        user_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["bg_input"], corner_radius=8)
        user_frame.pack(fill="x", padx=15, pady=(5, 15))

        name = f"{user.get('vorname', '')} {user.get('nachname', '')}".strip() or user["benutzername"]
        StyledLabel(user_frame, text=name, style="normal").pack(anchor="w", padx=10, pady=(8, 2))
        role_label = StyledLabel(user_frame, text=user["rolle"].upper(), style="small")
        role_label.configure(text_color=COLORS["primary"])
        role_label.pack(anchor="w", padx=10, pady=(0, 8))

        # Trennlinie
        ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1).pack(fill="x", padx=15, pady=5)

        # Navigations-Buttons
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        nav_items = [
            ("📊  Dashboard", self._show_dashboard),
            ("👤  Benutzer", self._show_users),
            ("👥  Gruppen", self._show_groups),
            ("📱  Geräte", self._show_devices),
            ("🏷  Stichwörter", self._show_keywords),
        ]

        self._nav_buttons = []
        for text, command in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w",
                fg_color="transparent", hover_color=COLORS["bg_input"],
                text_color=COLORS["text"], font=ctk.CTkFont(size=14),
                height=42, corner_radius=8,
                command=command,
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons.append(btn)

        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Abmelden-Button
        StyledButton(
            sidebar, text="⏻ Abmelden", variant="danger",
            command=self._logout, height=36, width=180
        ).pack(padx=15, pady=(10, 20))

        # Initial: Dashboard anzeigen
        self._show_dashboard()

    def _set_active_nav(self, index: int):
        """Markiert den aktiven Navigations-Button."""
        for i, btn in enumerate(self._nav_buttons):
            if i == index:
                btn.configure(fg_color=COLORS["primary"])
            else:
                btn.configure(fg_color="transparent")

    def _clear_content(self):
        """Leert den Content-Bereich."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_dashboard(self):
        self._clear_content()
        self._set_active_nav(0)
        view = DashboardView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _show_users(self):
        self._clear_content()
        self._set_active_nav(1)
        view = UserManagementView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _show_groups(self):
        self._clear_content()
        self._set_active_nav(2)
        view = GroupManagementView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _show_devices(self):
        self._clear_content()
        self._set_active_nav(3)
        view = DeviceManagementView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _show_keywords(self):
        self._clear_content()
        self._set_active_nav(4)
        view = KeywordManagementView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _logout(self):
        """Meldet den Benutzer ab und zeigt den Login."""
        AuthService.logout()
        db.disconnect()
        self._check_state()
