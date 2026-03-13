"""
PyDispatch Admin – Login-Bildschirm.
"""

import customtkinter as ctk

from admin.services.auth_service import AuthService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel, show_error,
)
from admin.ui.setup.config_editor import ConfigEditor


class LoginView(ctk.CTkFrame):
    """Login-Bildschirm für die Admin-Anwendung."""

    def __init__(self, master, on_login_success, on_setup=None):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.on_login_success = on_login_success
        self.on_setup = on_setup

        # Zentrierter Login-Container
        container = StyledFrame(self, width=400)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo/Titel
        StyledLabel(container, text="🚑", style="title").pack(pady=(30, 5))
        StyledLabel(container, text="PyDispatch Admin", style="title").pack(pady=(0, 5))

        subtitle = StyledLabel(container, text="Administrations-Software", style="small")
        subtitle.configure(text_color=COLORS["text_secondary"])
        subtitle.pack(pady=(0, 25))

        # Eingabefelder
        fields = ctk.CTkFrame(container, fg_color="transparent")
        fields.pack(fill="x", padx=40)

        StyledLabel(fields, text="Benutzername", style="normal").pack(anchor="w", pady=(0, 3))
        self.username_entry = StyledEntry(fields, placeholder_text="Benutzername eingeben")
        self.username_entry.pack(fill="x", pady=(0, 12))

        StyledLabel(fields, text="Passwort", style="normal").pack(anchor="w", pady=(0, 3))
        self.password_entry = StyledEntry(fields, placeholder_text="Passwort eingeben", show="•")
        self.password_entry.pack(fill="x", pady=(0, 20))

        # Login-Button
        StyledButton(
            fields, text="Anmelden", variant="primary",
            command=self._do_login, width=200
        ).pack(fill="x", pady=(0, 10))

        # Konfig-Button
        config_btn = StyledButton(
            fields, text="⚙ Konfiguration ändern", variant="warning",
            command=self._open_config, height=32
        )
        config_btn.pack(fill="x", pady=(0, 30))

        # Enter-Taste
        self.password_entry.bind("<Return>", lambda e: self._do_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            show_error("Fehler", "Bitte Benutzername und Passwort eingeben.")
            return

        success, msg, user = AuthService.login(username, password)
        if success:
            self.on_login_success(user)
        else:
            show_error("Anmeldung fehlgeschlagen", msg)

    def _open_config(self):
        ConfigEditor(self, on_save=self.on_setup)
