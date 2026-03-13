"""
PyDispatch Admin – Gruppenverwaltung.
"""

import customtkinter as ctk

from admin.services.group_service import GroupService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel,
    StyledOptionMenu, DataTable, show_error, show_info, show_confirm,
)
from admin.utils.validators import validate_not_empty


class GroupManagementView(ctk.CTkFrame):
    """Ansicht für die Gruppenverwaltung."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        StyledLabel(header, text="Gruppenverwaltung", style="title").pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        StyledButton(
            btn_frame, text="+ Neue Gruppe", variant="success",
            command=self._open_create_dialog, width=150
        ).pack(side="left", padx=(0, 8))

        # ── Aktive-Gruppe Banner ──
        self._banner_frame = ctk.CTkFrame(self, corner_radius=10, height=60)
        self._banner_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        self._banner_frame.grid_columnconfigure(1, weight=1)

        self._banner_icon = ctk.CTkLabel(
            self._banner_frame, text="", font=("Segoe UI", 22, "bold"), width=40
        )
        self._banner_icon.grid(row=0, column=0, padx=(15, 5), pady=12)

        self._banner_text = ctk.CTkLabel(
            self._banner_frame, text="", font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        self._banner_text.grid(row=0, column=1, sticky="w", pady=12)

        self._banner_btn = StyledButton(
            self._banner_frame, text="⚡ Aktive Gruppe setzen",
            variant="warning", command=self._set_active_group_dialog,
            width=220, height=38, font=("Segoe UI", 14, "bold")
        )
        self._banner_btn.grid(row=0, column=2, padx=(10, 15), pady=12)

        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # Tabelle
        self.table = DataTable(
            content,
            columns=[
                {"key": "name", "header": "Name", "weight": 2},
                {"key": "beschreibung", "header": "Beschreibung", "weight": 2},
                {"key": "mitglieder_anzahl", "header": "Mitglieder", "weight": 1},
                {"key": "ist_aktiv", "header": "Aktiv", "weight": 1},
            ],
        )
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Detail-Panel
        self.detail_panel = StyledFrame(content)
        self.detail_panel.grid(row=0, column=1, sticky="nsew")
        self._show_no_selection()

        self.refresh_data()

    def _show_no_selection(self):
        for w in self.detail_panel.winfo_children():
            w.destroy()
        StyledLabel(
            self.detail_panel, text="Gruppe auswählen", style="normal"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _show_group_detail(self, group_data: dict):
        """Zeigt Gruppendetails."""
        for w in self.detail_panel.winfo_children():
            w.destroy()

        group = GroupService.get_group_by_id(group_data["id"])
        if not group:
            return

        scroll = ctk.CTkScrollableFrame(self.detail_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        StyledLabel(scroll, text="Gruppe bearbeiten", style="subtitle").pack(anchor="w", pady=(0, 15))

        self._detail_name = ctk.StringVar(value=group.get("name", ""))
        self._detail_aktiv = ctk.BooleanVar(value=group.get("ist_aktiv", True))
        self._detail_group_id = group["id"]

        StyledLabel(scroll, text="Name", style="small").pack(anchor="w", pady=(8, 2))
        StyledEntry(scroll, textvariable=self._detail_name).pack(fill="x", pady=(0, 2))

        StyledLabel(scroll, text="Beschreibung", style="small").pack(anchor="w", pady=(8, 2))
        self._detail_beschreibung_box = ctk.CTkTextbox(
            scroll, height=80,
            fg_color=COLORS["bg_input"], text_color=COLORS["text"],
            border_color=COLORS["border"], border_width=1,
            corner_radius=8
        )
        self._detail_beschreibung_box.pack(fill="x", pady=(0, 2))
        if group.get("beschreibung"):
            self._detail_beschreibung_box.insert("1.0", group["beschreibung"])

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=self._detail_aktiv,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(10, 5))

        # Mitglieder anzeigen
        StyledLabel(scroll, text="Mitglieder", style="heading").pack(anchor="w", pady=(15, 5))
        members = GroupService.get_group_members(group["id"])
        if members:
            for m in members:
                name = f"{m.get('vorname', '')} {m.get('nachname', '')}".strip() or m["benutzername"]
                status_icon = "🟢" if m.get("ist_aktiv") else "🔴"
                StyledLabel(scroll, text=f"{status_icon} {name} ({m['benutzername']})", style="small").pack(
                    anchor="w", pady=1
                )
        else:
            StyledLabel(scroll, text="Keine Mitglieder", style="small").pack(anchor="w")

        # Buttons
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 5))

        StyledButton(
            btn_frame, text="Speichern", variant="success",
            command=self._save_group, width=120
        ).pack(side="left", padx=(0, 8))

        StyledButton(
            btn_frame, text="Löschen", variant="danger",
            command=lambda: self._delete_group(group["id"]), width=100
        ).pack(side="right")

    def _save_group(self):
        ok, msg = validate_not_empty(self._detail_name.get(), "Name")
        if not ok:
            show_error("Fehler", msg)
            return

        success, msg = GroupService.update_group(
            self._detail_group_id,
            name=self._detail_name.get(),
            beschreibung=self._detail_beschreibung_box.get("1.0", "end").strip(),
            ist_aktiv=self._detail_aktiv.get(),
        )
        if success:
            show_info("Erfolg", "Gruppe aktualisiert.")
            self.refresh_data()
        else:
            show_error("Fehler", msg)

    def _delete_group(self, group_id: int):
        if show_confirm("Gruppe löschen", "Möchten Sie diese Gruppe wirklich löschen?\nAlle Mitgliederzuordnungen werden entfernt."):
            success, msg = GroupService.delete_group(group_id)
            if success:
                show_info("Gelöscht", msg)
                self._show_no_selection()
                self.refresh_data()
            else:
                show_error("Fehler", msg)

    def _open_create_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neue Gruppe")
        dialog.geometry("520x420")
        dialog.minsize(450, 350)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neue Gruppe", style="subtitle").pack(padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        name_var = ctk.StringVar()
        desc_var = ctk.StringVar()

        StyledLabel(scroll, text="Name *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 2))

        StyledLabel(scroll, text="Beschreibung", style="small").pack(anchor="w", pady=(10, 3))
        desc_textbox = ctk.CTkTextbox(
            scroll, height=80,
            fg_color=COLORS["bg_input"], text_color=COLORS["text"],
            border_color=COLORS["border"], border_width=1,
            corner_radius=8
        )
        desc_textbox.pack(fill="x", pady=(0, 10))

        def create():
            ok, msg = validate_not_empty(name_var.get(), "Name")
            if not ok:
                show_error("Fehler", msg)
                return
            beschreibung = desc_textbox.get("1.0", "end").strip()
            success, msg, _ = GroupService.create_group(name_var.get(), beschreibung)
            if success:
                show_info("Erfolg", "Gruppe erstellt.")
                dialog.destroy()
                self.refresh_data()
            else:
                show_error("Fehler", msg)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        StyledButton(btn_frame, text="Abbrechen", variant="danger", command=dialog.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Erstellen", variant="success", command=create, width=150).pack(side="right")

    def _set_active_group_dialog(self):
        """Dialog zum Setzen der aktiven Benutzergruppe."""
        groups = GroupService.get_all_groups()
        if not groups:
            show_error("Fehler", "Keine Gruppen vorhanden.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Aktive Gruppe setzen")
        dialog.geometry("480x320")
        dialog.minsize(400, 280)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Aktive Gruppe wählen", style="subtitle").pack(padx=20, pady=(20, 10))

        StyledLabel(
            container,
            text="Die aktive Gruppe bestimmt, welche Benutzer\nbeim nächsten Einsatz alarmiert werden.",
            style="small"
        ).pack(padx=20, pady=(0, 15))

        # Aktuelle aktive Gruppe anzeigen
        current_active = GroupService.get_active_group()
        if current_active:
            StyledLabel(
                container,
                text=f"Aktuell aktiv: {current_active.get('name', 'Unbekannt')}",
                style="heading"
            ).pack(padx=20, pady=(0, 10))

        group_names = [g["name"] for g in groups]
        selected = ctk.StringVar(value=group_names[0])

        StyledOptionMenu(container, variable=selected, values=group_names).pack(
            fill="x", padx=20, pady=(0, 20)
        )

        def set_group():
            name = selected.get()
            group = next((g for g in groups if g["name"] == name), None)
            if group:
                success, msg = GroupService.set_active_group(group["id"])
                if success:
                    show_info("Erfolg", f"Aktive Gruppe: {name}")
                    dialog.destroy()
                    self.refresh_data()
                else:
                    show_error("Fehler", msg)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        StyledButton(btn_frame, text="Abbrechen", variant="danger", command=dialog.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Setzen", variant="success", command=set_group, width=150).pack(side="right")

    def _update_banner(self):
        """Aktualisiert das Banner je nach aktiver Gruppe."""
        active = GroupService.get_active_group()
        if active:
            name = active.get("name", "Unbekannt")
            self._banner_frame.configure(fg_color="#1a3d1a", border_color="#0d904f", border_width=2)
            self._banner_icon.configure(text="✅", text_color="#0d904f")
            self._banner_text.configure(
                text=f"Aktive Gruppe: {name}",
                text_color="#4ade80"
            )
            self._banner_btn.configure(text="🔄 Aktive Gruppe ändern")
        else:
            self._banner_frame.configure(fg_color="#3d2a00", border_color="#f9ab00", border_width=2)
            self._banner_icon.configure(text="⚠️", text_color="#f9ab00")
            self._banner_text.configure(
                text="Keine aktive Gruppe gesetzt! Alarme können nicht zugestellt werden.",
                text_color="#fbbf24"
            )
            self._banner_btn.configure(text="⚡ Aktive Gruppe setzen")

    def refresh_data(self):
        groups = GroupService.get_all_groups()
        self.table.set_data(groups, on_select=self._show_group_detail)
        self._update_banner()
