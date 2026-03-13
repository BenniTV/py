"""
PyDispatch Admin – Benutzerverwaltung.
"""

import customtkinter as ctk

from admin.services.user_service import UserService
from admin.services.group_service import GroupService
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel,
    StyledOptionMenu, DataTable, show_error, show_info, show_confirm,
)
from admin.utils.validators import validate_username, validate_password, validate_not_empty


class UserManagementView(ctk.CTkFrame):
    """Ansicht für die Benutzerverwaltung."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        StyledLabel(header, text="Benutzerverwaltung", style="title").pack(side="left")

        StyledButton(
            header, text="+ Neuer Benutzer", variant="success",
            command=self._open_create_dialog, width=160
        ).pack(side="right")

        # Content: links Tabelle, rechts Detail
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # Tabelle
        self.table = DataTable(
            content,
            columns=[
                {"key": "benutzername", "header": "Benutzername", "weight": 2},
                {"key": "vorname", "header": "Vorname", "weight": 1},
                {"key": "nachname", "header": "Nachname", "weight": 1},
                {"key": "rolle", "header": "Rolle", "weight": 1},
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
        """Zeigt den leeren Zustand im Detail-Panel."""
        for w in self.detail_panel.winfo_children():
            w.destroy()
        StyledLabel(
            self.detail_panel, text="Benutzer auswählen\noder neuen erstellen",
            style="normal"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _show_user_detail(self, user_data):
        """Zeigt die Details eines Benutzers."""
        for w in self.detail_panel.winfo_children():
            w.destroy()

        user = UserService.get_user_by_id(user_data["id"])
        if not user:
            return

        scroll = ctk.CTkScrollableFrame(self.detail_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)

        StyledLabel(scroll, text="Benutzer bearbeiten", style="subtitle").pack(
            anchor="w", pady=(0, 15)
        )

        # Felder
        self._detail_vorname = ctk.StringVar(value=user.get("vorname", ""))
        self._detail_nachname = ctk.StringVar(value=user.get("nachname", ""))
        self._detail_rolle = ctk.StringVar(value=user.get("rolle", "benutzer"))
        self._detail_aktiv = ctk.BooleanVar(value=user.get("ist_aktiv", True))
        self._detail_user_id = user["id"]

        for label, var in [
            ("Vorname", self._detail_vorname),
            ("Nachname", self._detail_nachname),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(anchor="w", pady=(8, 2))
            StyledEntry(scroll, textvariable=var).pack(fill="x", pady=(0, 2))

        StyledLabel(scroll, text="Rolle", style="small").pack(anchor="w", pady=(8, 2))
        StyledOptionMenu(
            scroll, variable=self._detail_rolle,
            values=["superadmin", "admin", "benutzer"]
        ).pack(fill="x", pady=(0, 2))

        ctk.CTkCheckBox(
            scroll, text="Aktiv", variable=self._detail_aktiv,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
        ).pack(anchor="w", pady=(10, 5))

        # Gruppen
        StyledLabel(scroll, text="Gruppen", style="heading").pack(
            anchor="w", pady=(15, 5)
        )
        user_groups = UserService.get_user_groups(user["id"])
        all_groups = GroupService.get_all_groups()

        self._group_vars = {}
        user_group_ids = {g["id"] for g in user_groups}
        for group in all_groups:
            var = ctk.BooleanVar(value=group["id"] in user_group_ids)
            self._group_vars[group["id"]] = var
            ctk.CTkCheckBox(
                scroll, text=group["name"], variable=var,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
            ).pack(anchor="w", pady=2)

        if not all_groups:
            StyledLabel(
                scroll, text="Keine Gruppen vorhanden", style="small"
            ).pack(anchor="w")

        # Buttons
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 5))

        StyledButton(
            btn_frame, text="Speichern", variant="success",
            command=self._save_user, width=120
        ).pack(side="left", padx=(0, 8))

        StyledButton(
            btn_frame, text="Passwort ändern", variant="warning",
            command=lambda uid=user["id"]: self._open_password_dialog(uid),
            width=140
        ).pack(side="left", padx=(0, 8))

        StyledButton(
            btn_frame, text="Löschen", variant="danger",
            command=lambda uid=user["id"]: self._delete_user(uid),
            width=100
        ).pack(side="right")

    def _save_user(self):
        """Speichert die Benutzeränderungen."""
        success, msg = UserService.update_user(
            self._detail_user_id,
            vorname=self._detail_vorname.get(),
            nachname=self._detail_nachname.get(),
            rolle=self._detail_rolle.get(),
            ist_aktiv=self._detail_aktiv.get(),
        )
        if success:
            selected_groups = [
                gid for gid, var in self._group_vars.items() if var.get()
            ]
            UserService.assign_groups(self._detail_user_id, selected_groups)
            show_info("Erfolg", "Benutzer aktualisiert.")
            self.refresh_data()
        else:
            show_error("Fehler", msg)

    def _delete_user(self, user_id):
        """Löscht einen Benutzer nach Bestätigung."""
        if show_confirm(
            "Benutzer löschen",
            "Möchten Sie diesen Benutzer wirklich löschen?"
        ):
            success, msg = UserService.delete_user(user_id)
            if success:
                show_info("Gelöscht", "Benutzer wurde gelöscht.")
                self._show_no_selection()
                self.refresh_data()
            else:
                show_error("Fehler", msg)

    def _open_create_dialog(self):
        """Öffnet den Dialog zum Erstellen eines neuen Benutzers."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neuer Benutzer")
        dialog.geometry("550x600")
        dialog.minsize(500, 500)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neuer Benutzer", style="subtitle").pack(
            padx=20, pady=(20, 10)
        )

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        username_var = ctk.StringVar()
        pw_var = ctk.StringVar()
        pw2_var = ctk.StringVar()
        vorname_var = ctk.StringVar()
        nachname_var = ctk.StringVar()
        rolle_var = ctk.StringVar(value="benutzer")

        for label, var, show in [
            ("Benutzername *", username_var, None),
            ("Passwort *", pw_var, "\u2022"),
            ("Passwort wiederholen *", pw2_var, "\u2022"),
            ("Vorname", vorname_var, None),
            ("Nachname", nachname_var, None),
        ]:
            StyledLabel(scroll, text=label, style="small").pack(
                anchor="w", pady=(10, 3)
            )
            kw = {"master": scroll, "textvariable": var, "height": 38}
            if show:
                kw["show"] = show
            StyledEntry(**kw).pack(fill="x", pady=(0, 2))

        StyledLabel(scroll, text="Rolle", style="small").pack(
            anchor="w", pady=(10, 3)
        )
        StyledOptionMenu(
            scroll, variable=rolle_var, values=["admin", "benutzer"]
        ).pack(fill="x", pady=(0, 5))

        # Gruppen direkt beim Erstellen zuweisen
        StyledLabel(scroll, text="Gruppen zuweisen", style="heading").pack(
            anchor="w", pady=(15, 5)
        )
        all_groups = GroupService.get_all_groups()
        group_vars = {}
        if all_groups:
            for group in all_groups:
                var = ctk.BooleanVar(value=False)
                group_vars[group["id"]] = var
                ctk.CTkCheckBox(
                    scroll, text=group["name"], variable=var,
                    fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
                ).pack(anchor="w", pady=2)
        else:
            StyledLabel(scroll, text="Keine Gruppen vorhanden", style="small").pack(anchor="w")

        def create():
            ok, msg = validate_username(username_var.get())
            if not ok:
                show_error("Fehler", msg)
                return
            ok, msg = validate_password(pw_var.get())
            if not ok:
                show_error("Fehler", msg)
                return
            if pw_var.get() != pw2_var.get():
                show_error("Fehler", "Passwörter stimmen nicht überein.")
                return
            success, msg2, new_id = UserService.create_user(
                benutzername=username_var.get(),
                passwort=pw_var.get(),
                vorname=vorname_var.get(),
                nachname=nachname_var.get(),
                rolle=rolle_var.get(),
            )
            if success:
                # Gruppen zuweisen
                selected_groups = [gid for gid, var in group_vars.items() if var.get()]
                if selected_groups and new_id:
                    UserService.assign_groups(new_id, selected_groups)
                show_info("Erfolg", "Benutzer erstellt.")
                dialog.destroy()
                self.refresh_data()
            else:
                show_error("Fehler", msg2)

        # Button-Leiste am unteren Rand
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        StyledButton(
            btn_frame, text="Abbrechen", variant="danger",
            command=dialog.destroy, width=120
        ).pack(side="left")
        StyledButton(
            btn_frame, text="Erstellen", variant="success",
            command=create, width=150
        ).pack(side="right")

    def _open_password_dialog(self, user_id):
        """Dialog zum Ändern des Passworts."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Passwort ändern")
        dialog.geometry("450x340")
        dialog.minsize(400, 300)
        dialog.resizable(True, True)
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.grab_set()

        container = StyledFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        StyledLabel(container, text="Neues Passwort", style="subtitle").pack(
            padx=20, pady=(20, 15)
        )

        pw_var = ctk.StringVar()
        pw2_var = ctk.StringVar()

        fields = ctk.CTkFrame(container, fg_color="transparent")
        fields.pack(fill="x", padx=20)

        StyledLabel(fields, text="Neues Passwort", style="small").pack(
            anchor="w", pady=(10, 3)
        )
        StyledEntry(fields, textvariable=pw_var, show="\u2022", height=38).pack(
            fill="x", pady=(0, 5)
        )
        StyledLabel(fields, text="Passwort wiederholen", style="small").pack(
            anchor="w", pady=(10, 3)
        )
        StyledEntry(fields, textvariable=pw2_var, show="\u2022", height=38).pack(
            fill="x", pady=(0, 15)
        )

        def change():
            if pw_var.get() != pw2_var.get():
                show_error("Fehler", "Passwörter stimmen nicht überein.")
                return
            ok, msg = validate_password(pw_var.get())
            if not ok:
                show_error("Fehler", msg)
                return
            success, msg2 = UserService.change_password(user_id, pw_var.get())
            if success:
                show_info("Erfolg", "Passwort geändert.")
                dialog.destroy()
            else:
                show_error("Fehler", msg2)

        btn_frame = ctk.CTkFrame(fields, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 0))
        StyledButton(
            btn_frame, text="Abbrechen", variant="danger",
            command=dialog.destroy, width=120
        ).pack(side="left")
        StyledButton(
            btn_frame, text="Ändern", variant="success",
            command=change, width=120
        ).pack(side="right")

    def refresh_data(self):
        """Aktualisiert die Tabelle."""
        users = UserService.get_all_users()
        self.table.set_data(users, on_select=self._show_user_detail)
