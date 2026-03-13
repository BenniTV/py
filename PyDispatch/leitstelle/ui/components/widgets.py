"""
PyDispatch Leitstelle – Wiederverwendbare UI-Komponenten.
"""

import customtkinter as ctk
from tkinter import messagebox


# ── Farbschema ──
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "success": "#0d904f",
    "danger": "#d93025",
    "danger_hover": "#b5251e",
    "warning": "#f9ab00",
    "alarm_red": "#ff1744",
    "alarm_red_hover": "#d50000",
    "bg_dark": "#1e1e2e",
    "bg_card": "#2a2a3e",
    "bg_input": "#333350",
    "text": "#e0e0e0",
    "text_secondary": "#a0a0b0",
    "border": "#3a3a50",
}


class StyledFrame(ctk.CTkFrame):
    """Ein gestylter Frame als Karten-Container."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)


class StyledButton(ctk.CTkButton):
    """Ein gestylter Button."""

    def __init__(self, master, variant="primary", **kwargs):
        color_map = {
            "primary": (COLORS["primary"], COLORS["primary_hover"]),
            "success": (COLORS["success"], "#0a7a42"),
            "danger": (COLORS["danger"], COLORS["danger_hover"]),
            "warning": (COLORS["warning"], "#d99800"),
            "alarm": (COLORS["alarm_red"], COLORS["alarm_red_hover"]),
        }
        fg, hover = color_map.get(variant, color_map["primary"])
        kwargs.setdefault("fg_color", fg)
        kwargs.setdefault("hover_color", hover)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=14))
        super().__init__(master, **kwargs)


class StyledEntry(ctk.CTkEntry):
    """Ein gestyltes Eingabefeld."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_input"])
        kwargs.setdefault("border_color", COLORS["border"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=14))
        super().__init__(master, **kwargs)


class StyledLabel(ctk.CTkLabel):
    """Ein gestyltes Label."""

    def __init__(self, master, style="normal", **kwargs):
        font_map = {
            "title": ctk.CTkFont(size=24, weight="bold"),
            "subtitle": ctk.CTkFont(size=18, weight="bold"),
            "heading": ctk.CTkFont(size=16, weight="bold"),
            "normal": ctk.CTkFont(size=14),
            "small": ctk.CTkFont(size=12),
            "big": ctk.CTkFont(size=32, weight="bold"),
            "huge": ctk.CTkFont(size=48, weight="bold"),
        }
        kwargs.setdefault("font", font_map.get(style, font_map["normal"]))
        kwargs.setdefault("text_color", COLORS["text"])
        super().__init__(master, **kwargs)


class StyledOptionMenu(ctk.CTkOptionMenu):
    """Ein gestyltes Dropdown-Menü."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_input"])
        kwargs.setdefault("button_color", COLORS["primary"])
        kwargs.setdefault("button_hover_color", COLORS["primary_hover"])
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("height", 38)
        kwargs.setdefault("font", ctk.CTkFont(size=14))
        super().__init__(master, **kwargs)


class StatCard(StyledFrame):
    """Statistik-Karte für das Dashboard."""

    def __init__(self, master, title: str, value: str, icon: str = "",
                 value_color: str = None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        if icon:
            icon_label = StyledLabel(self, text=icon, style="title")
            icon_label.grid(row=0, column=0, padx=20, pady=(15, 5))

        value_label = StyledLabel(self, text=str(value), style="big")
        if value_color:
            value_label.configure(text_color=value_color)
        value_label.grid(row=1, column=0, padx=20, pady=(5, 2))

        title_label = StyledLabel(self, text=title, style="small")
        title_label.configure(text_color=COLORS["text_secondary"])
        title_label.grid(row=2, column=0, padx=20, pady=(2, 15))

        self._value_label = value_label

    def update_value(self, value: str, color: str = None):
        """Aktualisiert den angezeigten Wert."""
        self._value_label.configure(text=str(value))
        if color:
            self._value_label.configure(text_color=color)


class AlarmButton(ctk.CTkButton):
    """Großer Alarm-Button für Quick-Action."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("text", "🚨  ALARM AUSLÖSEN")
        kwargs.setdefault("fg_color", COLORS["alarm_red"])
        kwargs.setdefault("hover_color", COLORS["alarm_red_hover"])
        kwargs.setdefault("corner_radius", 16)
        kwargs.setdefault("height", 80)
        kwargs.setdefault("font", ctk.CTkFont(size=24, weight="bold"))
        super().__init__(master, **kwargs)


def show_error(title: str, message: str):
    """Zeigt eine Fehlermeldung an."""
    messagebox.showerror(title, message)


def show_info(title: str, message: str):
    """Zeigt eine Info-Meldung an."""
    messagebox.showinfo(title, message)


def show_confirm(title: str, message: str) -> bool:
    """Zeigt einen Bestätigungsdialog an."""
    return messagebox.askyesno(title, message)
