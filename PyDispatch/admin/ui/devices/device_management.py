"""
PyDispatch Admin – Geräteverwaltung.
Leitstellen-PCs und mobile Geräte verwalten.
"""

import customtkinter as ctk

from admin.services.device_service import DeviceService
from admin.services.user_service import UserService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel,
    StyledOptionMenu, DataTable, show_error, show_info, show_confirm,
)
from admin.utils.validators import validate_not_empty


class DeviceManagementView(ctk.CTkFrame):
    """Ansicht für die Geräteverwaltung – Leitstellen und mobile Geräte."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        StyledLabel(header, text="Geräteverwaltung", style="title").pack(side="left")

        # Tabs
        self.tab_view = ctk.CTkTabview(self, fg_color=COLORS["bg_dark"])
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Tab: Leitstellen
        ls_tab = self.tab_view.add("Leitstellen-PCs")
        self._build_leitstellen_tab(ls_tab)

        # Tab: Mobile Geräte
        mg_tab = self.tab_view.add("Mobile Geräte")
        self._build_mobile_tab(mg_tab)

    def _build_leitstellen_tab(self, parent):
        """Baut den Leitstellen-Tab auf."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        StyledButton(
            header, text="+ Neue Leitstelle", variant="success",
            command=self._create_leitstelle, width=170
        ).pack(side="right")

        # Tabelle
        self.ls_table = DataTable(
            parent,
            columns=[
                {"key": "leitstellen_id", "header": "Leitstellen-ID", "weight": 2},
                {"key": "name", "header": "Name", "weight": 2},
                {"key": "ist_aktiv", "header": "Aktiv", "weight": 1},
                {"key": "letzter_kontakt", "header": "Letzter Kontakt", "weight": 2},
            ],
        )
        self.ls_table.grid(row=1, column=0, sticky="nsew")

        self._refresh_leitstellen()

    def _build_mobile_tab(self, parent):
        """Baut den Mobile-Geräte-Tab auf."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        StyledButton(
            header, text="+ Neues Gerät", variant="success",
            command=self._create_mobile_device, width=150
        ).pack(side="right")

        self.mg_table = DataTable(
            parent,
            columns=[
                {"key": "geraete_id", "header": "Geräte-ID", "weight": 2},
                {"key": "name", "header": "Name", "weight": 2},
                {"key": "benutzername", "header": "Benutzer", "weight": 2},
                {"key": "ist_aktiv", "header": "Aktiv", "weight": 1},
                {"key": "letzter_kontakt", "header": "Letzter Kontakt", "weight": 2},
            ],
        )
        self.mg_table.grid(row=1, column=0, sticky="nsew")

        self._refresh_mobile_devices()

    # ── Leitstellen ──

    def _refresh_leitstellen(self):
        data = DeviceService.get_all_leitstellen()
        self.ls_table.set_data(data, on_select=self._edit_leitstelle)

    def _create_leitstelle(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neue Leitstelle")
        dialog.geometry("520x340")
        dialog.minsize(450, 300)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neue Leitstelle registrieren", style="subtitle").pack(padx=20, pady=(20, 10))

        StyledLabel(
            container,
            text="Die Leitstellen-ID wird automatisch generiert\nund muss am Leitstellen-PC eingetragen werden.",
            style="small"
        ).pack(padx=20, pady=(0, 10))

        fields = ctk.CTkFrame(container, fg_color="transparent")
        fields.pack(fill="x", padx=20)

        name_var = ctk.StringVar()
        StyledLabel(fields, text="Name der Leitstelle *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(fields, textvariable=name_var, height=38).pack(fill="x", pady=(0, 15))

        def create():
            ok, msg = validate_not_empty(name_var.get(), "Name")
            if not ok:
                show_error("Fehler", msg)
                return
            success, msg, ls_id = DeviceService.create_leitstelle(name_var.get())
            if success:
                show_info("Leitstelle erstellt", f"Die Leitstellen-ID lautet:\n\n{ls_id}\n\nBitte notieren Sie sich diese ID!")
                dialog.destroy()
                self._refresh_leitstellen()
            else:
                show_error("Fehler", msg)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        StyledButton(btn_frame, text="Abbrechen", variant="danger", command=dialog.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Erstellen", variant="success", command=create, width=150).pack(side="right")

    def _edit_leitstelle(self, data: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Leitstelle – {data.get('name', '')}")
        dialog.geometry("520x420")
        dialog.minsize(450, 360)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Leitstelle bearbeiten", style="subtitle").pack(padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        StyledLabel(scroll, text=f"Leitstellen-ID: {data.get('leitstellen_id', '')}", style="heading").pack(
            anchor="w", pady=(5, 10)
        )

        name_var = ctk.StringVar(value=data.get("name", ""))
        aktiv_var = ctk.BooleanVar(value=data.get("ist_aktiv", True))

        StyledLabel(scroll, text="Name *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 5))

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=aktiv_var,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(15, 10))

        # Letzter Kontakt
        kontakt = data.get("letzter_kontakt", "Nie")
        StyledLabel(scroll, text=f"Letzter Kontakt: {kontakt or 'Nie'}", style="small").pack(
            anchor="w", pady=(10, 5)
        )

        # Button-Leiste
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        def save():
            DeviceService.update_leitstelle(data["id"], name=name_var.get(), ist_aktiv=aktiv_var.get())
            show_info("Gespeichert", "Leitstelle aktualisiert.")
            dialog.destroy()
            self._refresh_leitstellen()

        def delete():
            if show_confirm("Löschen", "Leitstelle wirklich löschen?"):
                DeviceService.delete_leitstelle(data["id"])
                dialog.destroy()
                self._refresh_leitstellen()

        StyledButton(btn_frame, text="Löschen", variant="danger", command=delete, width=120).pack(side="left")
        StyledButton(btn_frame, text="Speichern", variant="success", command=save, width=150).pack(side="right")

    # ── Mobile Geräte ──

    def _refresh_mobile_devices(self):
        data = DeviceService.get_all_mobile_devices()
        self.mg_table.set_data(data, on_select=self._edit_mobile_device)

    def _create_mobile_device(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neues Gerät")
        dialog.geometry("520x450")
        dialog.minsize(450, 380)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neues mobiles Gerät", style="subtitle").pack(padx=20, pady=(20, 10))

        StyledLabel(
            container,
            text="Die Geräte-ID wird automatisch generiert\nund muss auf dem Gerät eingetragen werden.",
            style="small"
        ).pack(padx=20, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        name_var = ctk.StringVar()
        StyledLabel(scroll, text="Gerätename *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 5))

        # Benutzer-Zuordnung
        users = UserService.get_all_users()
        user_map = {f"{u['vorname']} {u['nachname']} ({u['benutzername']})": u["id"] for u in users}
        user_options = ["-- Kein Benutzer --"] + list(user_map.keys())
        user_var = ctk.StringVar(value="-- Kein Benutzer --")

        StyledLabel(scroll, text="Benutzer zuordnen", style="small").pack(anchor="w", pady=(10, 3))
        StyledOptionMenu(scroll, variable=user_var, values=user_options).pack(fill="x", pady=(0, 10))

        def create():
            ok, msg = validate_not_empty(name_var.get(), "Gerätename")
            if not ok:
                show_error("Fehler", msg)
                return
            uid = user_map.get(user_var.get())
            success, msg, mg_id = DeviceService.create_mobile_device(name_var.get(), uid)
            if success:
                show_info("Gerät erstellt", f"Die Geräte-ID lautet:\n\n{mg_id}\n\nBitte notieren Sie sich diese ID!")
                dialog.destroy()
                self._refresh_mobile_devices()
            else:
                show_error("Fehler", msg)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        StyledButton(btn_frame, text="Abbrechen", variant="danger", command=dialog.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Erstellen", variant="success", command=create, width=150).pack(side="right")

    def _edit_mobile_device(self, data: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Gerät – {data.get('name', '')}")
        dialog.geometry("520x520")
        dialog.minsize(450, 420)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Gerät bearbeiten", style="subtitle").pack(padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        StyledLabel(scroll, text=f"Geräte-ID: {data.get('geraete_id', '')}", style="heading").pack(
            anchor="w", pady=(5, 10)
        )

        name_var = ctk.StringVar(value=data.get("name", ""))
        aktiv_var = ctk.BooleanVar(value=data.get("ist_aktiv", True))

        StyledLabel(scroll, text="Gerätename *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 5))

        # Benutzer-Zuordnung
        users = UserService.get_all_users()
        user_map = {f"{u['vorname']} {u['nachname']} ({u['benutzername']})": u["id"] for u in users}
        user_options = ["-- Kein Benutzer --"] + list(user_map.keys())

        current_user = "-- Kein Benutzer --"
        if data.get("benutzername"):
            for key in user_map:
                if data["benutzername"] in key:
                    current_user = key
                    break

        user_var = ctk.StringVar(value=current_user)
        StyledLabel(scroll, text="Benutzer zuordnen", style="small").pack(anchor="w", pady=(10, 3))
        StyledOptionMenu(scroll, variable=user_var, values=user_options).pack(fill="x", pady=(0, 5))

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=aktiv_var,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(15, 10))

        # Letzter Kontakt
        kontakt = data.get("letzter_kontakt", "Nie")
        StyledLabel(scroll, text=f"Letzter Kontakt: {kontakt or 'Nie'}", style="small").pack(
            anchor="w", pady=(10, 5)
        )

        # Button-Leiste
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        def save():
            uid = user_map.get(user_var.get(), 0)
            DeviceService.update_mobile_device(
                data["id"], name=name_var.get(), benutzer_id=uid, ist_aktiv=aktiv_var.get()
            )
            show_info("Gespeichert", "Gerät aktualisiert.")
            dialog.destroy()
            self._refresh_mobile_devices()

        def delete():
            if show_confirm("Löschen", "Gerät wirklich löschen?"):
                DeviceService.delete_mobile_device(data["id"])
                dialog.destroy()
                self._refresh_mobile_devices()

        StyledButton(btn_frame, text="Löschen", variant="danger", command=delete, width=120).pack(side="left")
        StyledButton(btn_frame, text="Speichern", variant="success", command=save, width=150).pack(side="right")
