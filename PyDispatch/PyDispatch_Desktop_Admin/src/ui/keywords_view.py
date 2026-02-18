import customtkinter as ctk


LOCATION_TYPES = ["fixed", "selectable", "none"]
LOCATION_TYPE_LABELS = {
    "fixed": "Fester Ort (fixed)",
    "selectable": "Ort auswählbar (selectable)",
    "none": "Kein Ort (none)",
}
LOCATION_TYPE_VALUES = {label: value for value, label in LOCATION_TYPE_LABELS.items()}
LOCATION_TYPE_HELP = {
    "fixed": "Nutzer sendet immer an genau diesen Ort.",
    "selectable": "Nutzer wählt den Ort beim Senden selbst aus.",
    "none": "Für dieses Stichwort wird kein Ort benötigt.",
}


class KeywordsView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.wrapper.grid_columnconfigure(0, weight=1)
        self.wrapper.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.wrapper, text="Stichwortverwaltung", font=("Arial", 30, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(2, 12)
        )

        tools_frame = ctk.CTkFrame(self.wrapper, corner_radius=12)
        tools_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ctk.CTkButton(
            tools_frame,
            text="Neues Stichwort",
            command=self.create_keyword,
            height=38,
            corner_radius=10,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            tools_frame,
            text="Aktualisieren",
            command=self.refresh_keywords,
            height=38,
            corner_radius=10,
            font=("Arial", 13)
        ).pack(side="left", pady=8)

        self.status_label = ctk.CTkLabel(self.wrapper, text="", font=("Arial", 13))
        self.status_label.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 6))

        self.keyword_list_frame = ctk.CTkScrollableFrame(self.wrapper)
        self.keyword_list_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))

        self.refresh_keywords()

    def _set_status(self, message, is_error=False):
        color = "#d9534f" if is_error else "#2e8b57"
        self.status_label.configure(text=message, text_color=color)

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _normalize_location(self, location_type, default_location):
        value = (default_location or "").strip()
        if location_type == "fixed":
            return value or None
        return None

    def _parse_selectable_locations(self, text_value):
        return [part.strip() for part in (text_value or "").split(",") if part.strip()]

    def _on_location_type_change(self, location_type, fixed_entry, selectable_entry, help_label=None):
        if location_type == "fixed":
            fixed_entry.configure(state="normal")
            selectable_entry.delete(0, "end")
            selectable_entry.configure(state="disabled")
        elif location_type == "selectable":
            fixed_entry.delete(0, "end")
            fixed_entry.configure(state="disabled")
            selectable_entry.configure(state="normal")
        else:
            fixed_entry.delete(0, "end")
            fixed_entry.configure(state="disabled")
            selectable_entry.delete(0, "end")
            selectable_entry.configure(state="disabled")

        if help_label is not None:
            help_label.configure(text=LOCATION_TYPE_HELP.get(location_type, ""))

    def _render_keywords(self, keywords):
        self._clear_frame(self.keyword_list_frame)
        if not keywords:
            ctk.CTkLabel(self.keyword_list_frame, text="Keine Stichwörter gefunden.", font=("Arial", 14)).pack(anchor="w", padx=8, pady=8)
            return

        for keyword in keywords:
            card = ctk.CTkFrame(self.keyword_list_frame, corner_radius=12)
            card.pack(fill="x", padx=6, pady=6)
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(top, text=keyword["keyword"], font=("Arial", 16, "bold")).pack(side="left")

            active_text = "Aktiv" if keyword["is_active"] else "Inaktiv"
            ctk.CTkLabel(top, text=f"Status: {active_text}", font=("Arial", 12)).pack(side="right")

            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(fill="x", padx=12, pady=(4, 10))
            controls.grid_columnconfigure(0, weight=1)
            controls.grid_columnconfigure(1, weight=1)
            controls.grid_columnconfigure(2, weight=1)
            controls.grid_columnconfigure(3, weight=0)
            controls.grid_columnconfigure(4, weight=0)

            location_type_menu = ctk.CTkOptionMenu(controls, values=list(LOCATION_TYPE_VALUES.keys()), width=240)
            location_type_menu.set(LOCATION_TYPE_LABELS[keyword["location_type"]])
            location_type_menu.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="ew")

            location_entry = ctk.CTkEntry(controls, width=220, placeholder_text="Standard-Ort (nur fixed)")
            location_entry.grid(row=0, column=1, padx=(0, 8), pady=(0, 8), sticky="ew")
            if keyword.get("default_location"):
                location_entry.insert(0, keyword["default_location"])

            selectable_entry = ctk.CTkEntry(controls, width=260, placeholder_text="Auswahl-Orte (kommagetrennt)")
            selectable_entry.grid(row=0, column=2, padx=(0, 8), pady=(0, 8), sticky="ew")
            selectable_values = keyword.get("selectable_locations") or []
            if selectable_values:
                selectable_entry.insert(0, ", ".join(selectable_values))

            location_type_menu.configure(
                command=lambda value, fixed=location_entry, selectable=selectable_entry: self._on_location_type_change(
                    LOCATION_TYPE_VALUES[value],
                    fixed,
                    selectable
                )
            )
            self._on_location_type_change(keyword["location_type"], location_entry, selectable_entry)

            ctk.CTkButton(
                controls,
                text="Speichern",
                width=120,
                command=lambda keyword_id=keyword["id"], type_menu=location_type_menu, fixed_entry=location_entry, selectable_text=selectable_entry: self.save_keyword_changes(
                    keyword_id,
                    LOCATION_TYPE_VALUES[type_menu.get()],
                    fixed_entry.get() if str(fixed_entry.cget("state")) == "normal" else None,
                    selectable_text.get() if str(selectable_text.cget("state")) == "normal" else ""
                )
            ).grid(row=0, column=3, padx=(0, 8), pady=(0, 8), sticky="e")

            toggle_text = "Deaktivieren" if keyword["is_active"] else "Aktivieren"
            ctk.CTkButton(
                controls,
                text=toggle_text,
                width=110,
                command=lambda keyword_id=keyword["id"], new_state=not keyword["is_active"]: self.toggle_keyword_active(
                    keyword_id,
                    new_state
                )
            ).grid(row=0, column=4, pady=(0, 8), sticky="e")

    def refresh_keywords(self):
        try:
            keywords = self.db_manager.get_keywords(self.config)
            self._render_keywords(keywords)
            self._set_status(f"{len(keywords)} Stichwörter geladen")
        except Exception as exc:
            self._clear_frame(self.keyword_list_frame)
            ctk.CTkLabel(self.keyword_list_frame, text=f"Fehler beim Laden: {exc}", text_color="#d9534f").pack(anchor="w", padx=8, pady=8)
            self._set_status("Stichwörter konnten nicht geladen werden", is_error=True)

    def create_keyword(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neues Stichwort")
        dialog.geometry("640x440")
        dialog.minsize(640, 440)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=14)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Stichwort anlegen", font=("Arial", 26, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 18)
        )

        ctk.CTkLabel(frame, text="Stichwort:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=8)
        keyword_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13))
        keyword_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Ort-Typ:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=14, pady=8)
        location_type_menu = ctk.CTkOptionMenu(frame, values=list(LOCATION_TYPE_VALUES.keys()))
        location_type_menu.set(LOCATION_TYPE_LABELS["selectable"])
        location_type_menu.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=8)

        type_help_label = ctk.CTkLabel(frame, text=LOCATION_TYPE_HELP["selectable"], font=("Arial", 12))
        type_help_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 4))

        ctk.CTkLabel(frame, text="Standard-Ort:", font=("Arial", 14)).grid(row=4, column=0, sticky="w", padx=14, pady=8)
        location_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13), placeholder_text="Nur für fixed")
        location_entry.grid(row=4, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Auswahl-Orte:", font=("Arial", 14)).grid(row=5, column=0, sticky="w", padx=14, pady=8)
        selectable_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13), placeholder_text="z. B. SCHULE, EXTERNE, SPORTHALLE")
        selectable_entry.grid(row=5, column=1, sticky="ew", padx=(0, 14), pady=8)

        location_type_menu.configure(
            command=lambda value: self._on_location_type_change(
                LOCATION_TYPE_VALUES[value],
                location_entry,
                selectable_entry,
                type_help_label
            )
        )
        self._on_location_type_change("selectable", location_entry, selectable_entry, type_help_label)

        status_label = ctk.CTkLabel(frame, text="", text_color="#d9534f", font=("Arial", 13))
        status_label.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 4))

        def submit():
            keyword = keyword_entry.get().strip()
            location_type = LOCATION_TYPE_VALUES[location_type_menu.get()]
            default_location = location_entry.get().strip() if str(location_entry.cget("state")) == "normal" else None
            selectable_text = selectable_entry.get().strip() if str(selectable_entry.cget("state")) == "normal" else ""
            selectable_locations = self._parse_selectable_locations(selectable_text)

            if not keyword:
                status_label.configure(text="Bitte ein Stichwort eingeben")
                return

            normalized_location = self._normalize_location(location_type, default_location)
            if location_type == "fixed" and not normalized_location:
                status_label.configure(text="Für fixed muss ein Standard-Ort gesetzt sein")
                return
            if location_type == "selectable" and not selectable_locations:
                status_label.configure(text="Für selectable bitte mindestens einen Auswahl-Ort eingeben")
                return

            try:
                self.db_manager.create_keyword(
                    self.config,
                    keyword=keyword,
                    location_type=location_type,
                    default_location=normalized_location,
                    selectable_locations=selectable_locations
                )
                dialog.destroy()
                self._set_status("Stichwort erfolgreich angelegt")
                self.refresh_keywords()
            except Exception as exc:
                status_label.configure(text=f"Fehler: {exc}")

        ctk.CTkButton(frame, text="Anlegen", command=submit, height=40, font=("Arial", 14, "bold")).grid(
            row=7, column=0, columnspan=2, padx=14, pady=(12, 14), sticky="ew"
        )

    def save_keyword_changes(self, keyword_id, location_type, default_location, selectable_text):
        normalized_location = self._normalize_location(location_type, default_location)
        selectable_locations = self._parse_selectable_locations(selectable_text)
        if location_type == "fixed" and not normalized_location:
            self._set_status("Für fixed muss ein Standard-Ort gesetzt sein", is_error=True)
            return
        if location_type == "selectable" and not selectable_locations:
            self._set_status("Für selectable bitte mindestens einen Auswahl-Ort eingeben", is_error=True)
            return

        try:
            self.db_manager.update_keyword(
                self.config,
                keyword_id=keyword_id,
                location_type=location_type,
                default_location=normalized_location,
                set_default_location=True,
                selectable_locations=selectable_locations,
                set_selectable_locations=True
            )
            self._set_status("Stichwort aktualisiert")
            self.refresh_keywords()
        except Exception as exc:
            self._set_status(f"Fehler beim Speichern: {exc}", is_error=True)

    def toggle_keyword_active(self, keyword_id, is_active):
        try:
            self.db_manager.update_keyword(
                self.config,
                keyword_id=keyword_id,
                is_active=is_active
            )
            action = "aktiviert" if is_active else "deaktiviert"
            self._set_status(f"Stichwort wurde {action}")
            self.refresh_keywords()
        except Exception as exc:
            self._set_status(f"Fehler beim Aktualisieren: {exc}", is_error=True)
