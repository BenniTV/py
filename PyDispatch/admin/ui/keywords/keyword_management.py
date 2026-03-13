"""
PyDispatch Admin – Stichwort- und Standortverwaltung.
"""

import customtkinter as ctk

from admin.services.keyword_service import KeywordService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel,
    StyledOptionMenu, DataTable, show_error, show_info, show_confirm,
)
from admin.utils.validators import validate_not_empty


class KeywordManagementView(ctk.CTkFrame):
    """Ansicht für die Stichwort- und Standortverwaltung."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        StyledLabel(header, text="Stichworteinstellungen", style="title").pack(side="left")

        # Tabs
        self.tab_view = ctk.CTkTabview(self, fg_color=COLORS["bg_dark"])
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        sw_tab = self.tab_view.add("Stichwörter")
        self._build_stichwort_tab(sw_tab)

        so_tab = self.tab_view.add("Standorte")
        self._build_standort_tab(so_tab)

    # ── Stichwörter ──

    def _build_stichwort_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        StyledButton(
            header, text="+ Neues Stichwort", variant="success",
            command=self._create_stichwort, width=170
        ).pack(side="right")

        self.sw_table = DataTable(
            parent,
            columns=[
                {"key": "kuerzel", "header": "Kürzel", "weight": 1},
                {"key": "bezeichnung", "header": "Bezeichnung", "weight": 2},
                {"key": "standort_typ", "header": "Standort-Typ", "weight": 1},
                {"key": "fester_standort_name", "header": "Fester Standort", "weight": 2},
                {"key": "kategorie", "header": "Kategorie", "weight": 1},
                {"key": "prioritaet", "header": "Priorität", "weight": 1},
                {"key": "ist_aktiv", "header": "Aktiv", "weight": 1},
            ],
        )
        self.sw_table.grid(row=1, column=0, sticky="nsew")
        self._refresh_stichwoerter()

    def _refresh_stichwoerter(self):
        data = KeywordService.get_all_stichwoerter()
        # Standort-Typ Labels anpassen
        for row in data:
            typ_map = {"fest": "Fest", "auswaehlbar": "Auswählbar", "frei": "Frei"}
            row["standort_typ"] = typ_map.get(row.get("standort_typ", ""), row.get("standort_typ", ""))
        self.sw_table.set_data(data, on_select=self._edit_stichwort)

    def _create_stichwort(self):
        StichwortDialog(self, on_save=self._refresh_stichwoerter)

    def _edit_stichwort(self, data: dict):
        StichwortDialog(self, edit_data=data, on_save=self._refresh_stichwoerter)

    # ── Standorte ──

    def _build_standort_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 10))

        StyledButton(
            header, text="+ Neuer Standort", variant="success",
            command=self._create_standort, width=160
        ).pack(side="right")

        self.so_table = DataTable(
            parent,
            columns=[
                {"key": "name", "header": "Name", "weight": 2},
                {"key": "beschreibung", "header": "Beschreibung", "weight": 3},
                {"key": "ist_aktiv", "header": "Aktiv", "weight": 1},
            ],
        )
        self.so_table.grid(row=1, column=0, sticky="nsew")
        self._refresh_standorte()

    def _refresh_standorte(self):
        data = KeywordService.get_all_standorte()
        self.so_table.set_data(data, on_select=self._edit_standort)

    def _create_standort(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neuer Standort")
        dialog.geometry("520x420")
        dialog.minsize(450, 350)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neuer Standort", style="subtitle").pack(padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        name_var = ctk.StringVar()

        StyledLabel(scroll, text="Name *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 5))

        StyledLabel(scroll, text="Beschreibung", style="small").pack(anchor="w", pady=(10, 3))
        desc_textbox = ctk.CTkTextbox(
            scroll, height=100,
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
            success, msg, _ = KeywordService.create_standort(name_var.get(), beschreibung)
            if success:
                show_info("Erfolg", "Standort erstellt.")
                dialog.destroy()
                self._refresh_standorte()
            else:
                show_error("Fehler", msg)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        StyledButton(btn_frame, text="Abbrechen", variant="danger", command=dialog.destroy, width=120).pack(side="left")
        StyledButton(btn_frame, text="Erstellen", variant="success", command=create, width=150).pack(side="right")

    def _edit_standort(self, data: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Standort – {data.get('name', '')}")
        dialog.geometry("520x480")
        dialog.minsize(450, 400)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Standort bearbeiten", style="subtitle").pack(padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        name_var = ctk.StringVar(value=data.get("name", ""))
        aktiv_var = ctk.BooleanVar(value=data.get("ist_aktiv", True))

        StyledLabel(scroll, text="Name *", style="small").pack(anchor="w", pady=(10, 3))
        StyledEntry(scroll, textvariable=name_var, height=38).pack(fill="x", pady=(0, 5))

        StyledLabel(scroll, text="Beschreibung", style="small").pack(anchor="w", pady=(10, 3))
        desc_textbox = ctk.CTkTextbox(
            scroll, height=100,
            fg_color=COLORS["bg_input"], text_color=COLORS["text"],
            border_color=COLORS["border"], border_width=1,
            corner_radius=8
        )
        desc_textbox.pack(fill="x", pady=(0, 5))
        if data.get("beschreibung"):
            desc_textbox.insert("1.0", data["beschreibung"])

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=aktiv_var,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(15, 10))

        # Button-Leiste
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        def save():
            beschreibung = desc_textbox.get("1.0", "end").strip()
            KeywordService.update_standort(data["id"], name_var.get(), beschreibung, aktiv_var.get())
            show_info("Gespeichert", "Standort aktualisiert.")
            dialog.destroy()
            self._refresh_standorte()

        def delete():
            if show_confirm("Löschen", "Standort wirklich löschen?"):
                KeywordService.delete_standort(data["id"])
                dialog.destroy()
                self._refresh_standorte()

        StyledButton(btn_frame, text="Löschen", variant="danger", command=delete, width=120).pack(side="left")
        StyledButton(btn_frame, text="Speichern", variant="success", command=save, width=150).pack(side="right")


class StichwortDialog(ctk.CTkToplevel):
    """Dialog zum Erstellen/Bearbeiten eines Stichworts."""

    def __init__(self, master, edit_data: dict = None, on_save=None):
        super().__init__(master)
        self.edit_data = edit_data
        self.on_save = on_save
        self.is_edit = edit_data is not None

        self.title("Stichwort bearbeiten" if self.is_edit else "Neues Stichwort")
        self.geometry("600x720")
        self.minsize(550, 600)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_dark"])

        container = StyledFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        StyledLabel(
            scroll,
            text="Stichwort bearbeiten" if self.is_edit else "Neues Stichwort",
            style="subtitle"
        ).pack(anchor="w", pady=(0, 15))

        # Felder
        self.kuerzel_var = ctk.StringVar(value=edit_data.get("kuerzel", "") if edit_data else "")
        self.bez_var = ctk.StringVar(value=edit_data.get("bezeichnung", "") if edit_data else "")
        self.kategorie_var = ctk.StringVar(value=edit_data.get("kategorie", "") if edit_data else "")
        self.prio_var = ctk.StringVar(value=str(edit_data.get("prioritaet", 0)) if edit_data else "0")

        # Standort-Typ zurückmappen
        typ_reverse = {"Fest": "fest", "Auswählbar": "auswaehlbar", "Frei": "frei"}
        edit_typ = edit_data.get("standort_typ", "frei") if edit_data else "frei"
        edit_typ = typ_reverse.get(edit_typ, edit_typ)

        typ_display_map = {"fest": "Fest", "auswaehlbar": "Auswählbar", "frei": "Frei"}
        self.typ_var = ctk.StringVar(value=typ_display_map.get(edit_typ, "Frei"))

        aktiv_val = edit_data.get("ist_aktiv", True) if edit_data else True
        self.aktiv_var = ctk.BooleanVar(value=aktiv_val)

        for label, var in [
            ("Kürzel (z.B. R1) *", self.kuerzel_var),
            ("Bezeichnung *", self.bez_var),
            ("Kategorie", self.kategorie_var),
            ("Priorität (0 = niedrig)", self.prio_var),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(anchor="w", pady=(10, 3))
            StyledEntry(scroll, textvariable=var, height=38).pack(fill="x", pady=(0, 2))

        StyledLabel(scroll, text="Standort-Typ", style="small").pack(anchor="w", pady=(10, 3))
        self.typ_menu = StyledOptionMenu(
            scroll, variable=self.typ_var,
            values=["Fest", "Auswählbar", "Frei"],
            command=self._on_typ_change
        )
        self.typ_menu.pack(fill="x", pady=(0, 5))

        # Standort-Auswahl-Bereich
        self.standort_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.standort_frame.pack(fill="x", pady=5)

        self.standorte = KeywordService.get_all_standorte()
        self.standort_vars = {}

        # Initial anzeigen
        self._on_typ_change(self.typ_var.get())

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=self.aktiv_var,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(10, 15))

        # Buttons
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))

        if self.is_edit:
            StyledButton(
                btn_frame, text="Löschen", variant="danger",
                command=self._delete, width=100
            ).pack(side="left")

        StyledButton(
            btn_frame, text="Speichern" if self.is_edit else "Erstellen",
            variant="success", command=self._save, width=120
        ).pack(side="right")

        self.grab_set()

    def _on_typ_change(self, value: str):
        """Aktualisiert die Standort-Auswahl je nach Typ."""
        for w in self.standort_frame.winfo_children():
            w.destroy()
        self.standort_vars = {}

        typ_map = {"Fest": "fest", "Auswählbar": "auswaehlbar", "Frei": "frei"}
        typ = typ_map.get(value, "frei")

        if typ == "fest" and self.standorte:
            StyledLabel(self.standort_frame, text="Fester Standort", style="small").pack(anchor="w", pady=(5, 2))
            names = [s["name"] for s in self.standorte]
            current_id = self.edit_data.get("fester_standort_id") if self.edit_data else None
            current_name = ""
            if current_id:
                for s in self.standorte:
                    if s["id"] == current_id:
                        current_name = s["name"]
                        break
            self.fest_standort_var = ctk.StringVar(value=current_name or (names[0] if names else ""))
            StyledOptionMenu(
                self.standort_frame, variable=self.fest_standort_var, values=names
            ).pack(fill="x")

        elif typ == "auswaehlbar" and self.standorte:
            StyledLabel(self.standort_frame, text="Auswählbare Standorte", style="small").pack(anchor="w", pady=(5, 2))
            # Bestehende Zuordnungen laden
            existing_ids = set()
            if self.edit_data:
                existing = KeywordService.get_stichwort_standorte(self.edit_data["id"])
                existing_ids = {s["id"] for s in existing}

            for s in self.standorte:
                var = ctk.BooleanVar(value=s["id"] in existing_ids)
                self.standort_vars[s["id"]] = var
                ctk.CTkCheckBox(
                    self.standort_frame, text=s["name"], variable=var,
                    fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
                ).pack(anchor="w", pady=2)

        elif typ == "frei":
            StyledLabel(
                self.standort_frame,
                text="Standort wird in der Leitstelle frei eingetragen.",
                style="small"
            ).pack(anchor="w", pady=5)

    def _save(self):
        ok, msg = validate_not_empty(self.kuerzel_var.get(), "Kürzel")
        if not ok:
            show_error("Fehler", msg)
            return
        ok, msg = validate_not_empty(self.bez_var.get(), "Bezeichnung")
        if not ok:
            show_error("Fehler", msg)
            return

        typ_map = {"Fest": "fest", "Auswählbar": "auswaehlbar", "Frei": "frei"}
        standort_typ = typ_map.get(self.typ_var.get(), "frei")

        try:
            prio = int(self.prio_var.get())
        except ValueError:
            prio = 0

        fester_standort_id = None
        standort_ids = None

        if standort_typ == "fest" and hasattr(self, "fest_standort_var"):
            name = self.fest_standort_var.get()
            for s in self.standorte:
                if s["name"] == name:
                    fester_standort_id = s["id"]
                    break

        elif standort_typ == "auswaehlbar":
            standort_ids = [sid for sid, var in self.standort_vars.items() if var.get()]

        if self.is_edit:
            success, msg = KeywordService.update_stichwort(
                self.edit_data["id"],
                kuerzel=self.kuerzel_var.get(),
                bezeichnung=self.bez_var.get(),
                standort_typ=standort_typ,
                fester_standort_id=fester_standort_id or 0,
                prioritaet=prio,
                kategorie=self.kategorie_var.get(),
                ist_aktiv=self.aktiv_var.get(),
                standort_ids=standort_ids,
            )
        else:
            success, msg, _ = KeywordService.create_stichwort(
                kuerzel=self.kuerzel_var.get(),
                bezeichnung=self.bez_var.get(),
                standort_typ=standort_typ,
                fester_standort_id=fester_standort_id,
                prioritaet=prio,
                kategorie=self.kategorie_var.get(),
                standort_ids=standort_ids,
            )

        if success:
            show_info("Erfolg", "Stichwort gespeichert.")
            if self.on_save:
                self.on_save()
            self.destroy()
        else:
            show_error("Fehler", msg)

    def _delete(self):
        if self.is_edit and show_confirm("Löschen", "Stichwort wirklich löschen?"):
            success, msg = KeywordService.delete_stichwort(self.edit_data["id"])
            if success:
                if self.on_save:
                    self.on_save()
                self.destroy()
            else:
                show_error("Fehler", msg)
