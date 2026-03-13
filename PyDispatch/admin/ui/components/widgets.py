"""
PyDispatch Admin – Wiederverwendbare UI-Komponenten.
"""

import customtkinter as ctk
from tkinter import messagebox


# ── Farbschema ──
COLORS = {
    "primary": "#1a73e8",
    "primary_hover": "#1557b0",
    "success": "#0d904f",
    "danger": "#d93025",
    "warning": "#f9ab00",
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
            "danger": (COLORS["danger"], "#b5251e"),
            "warning": (COLORS["warning"], "#d99800"),
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

    def __init__(self, master, title: str, value: str, icon: str = "", **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        if icon:
            icon_label = StyledLabel(self, text=icon, style="title")
            icon_label.grid(row=0, column=0, padx=20, pady=(15, 5))

        value_label = StyledLabel(self, text=str(value), style="title")
        value_label.grid(row=1, column=0, padx=20, pady=(5, 2))

        title_label = StyledLabel(self, text=title, style="small")
        title_label.configure(text_color=COLORS["text_secondary"])
        title_label.grid(row=2, column=0, padx=20, pady=(2, 15))

        self._value_label = value_label

    def update_value(self, value: str):
        """Aktualisiert den angezeigten Wert."""
        self._value_label.configure(text=str(value))


class DataTable(ctk.CTkScrollableFrame):
    """Eine einfache Datentabelle."""

    def __init__(self, master, columns: list[dict], **kwargs):
        """
        columns: Liste von dicts mit 'key', 'header', 'width' (optional)
        """
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)

        self.columns = columns
        self._rows = []

        # Header
        header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0, height=40)
        header_frame.pack(fill="x", padx=2, pady=(2, 0))
        for i, col in enumerate(columns):
            header_frame.grid_columnconfigure(i, weight=col.get("weight", 1))
            lbl = StyledLabel(header_frame, text=col["header"], style="heading")
            lbl.grid(row=0, column=i, padx=10, pady=8, sticky="w")

        self._data_container = ctk.CTkFrame(self, fg_color="transparent")
        self._data_container.pack(fill="both", expand=True, padx=2, pady=2)

    def set_data(self, data: list[dict], on_select=None):
        """Befüllt die Tabelle mit Daten."""
        # Alte Zeilen entfernen
        for widget in self._data_container.winfo_children():
            widget.destroy()
        self._rows = []

        for idx, row_data in enumerate(data):
            bg = COLORS["bg_card"] if idx % 2 == 0 else COLORS["bg_dark"]
            row_frame = ctk.CTkFrame(self._data_container, fg_color=bg, corner_radius=0, height=40)
            row_frame.pack(fill="x", pady=1)

            for i, col in enumerate(self.columns):
                row_frame.grid_columnconfigure(i, weight=col.get("weight", 1))
                value = row_data.get(col["key"], "")
                if isinstance(value, bool):
                    value = "Ja" if value else "Nein"
                lbl = StyledLabel(row_frame, text=str(value), style="normal")
                lbl.grid(row=0, column=i, padx=10, pady=6, sticky="w")

            if on_select:
                row_frame.bind("<Button-1>", lambda e, d=row_data: on_select(d))
                for child in row_frame.winfo_children():
                    child.bind("<Button-1>", lambda e, d=row_data: on_select(d))

            self._rows.append((row_frame, row_data))


def show_error(title: str, message: str):
    """Zeigt eine Fehlermeldung an."""
    messagebox.showerror(title, message)


def show_info(title: str, message: str):
    """Zeigt eine Infomeldung an."""
    messagebox.showinfo(title, message)


def show_confirm(title: str, message: str) -> bool:
    """Zeigt eine Bestätigungsmeldung an."""
    return messagebox.askyesno(title, message)
