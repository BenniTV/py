import customtkinter as ctk


class DevicesView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        self.user_options = ["Nicht zugewiesen"]
        self.user_name_to_id = {"Nicht zugewiesen": None}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.wrapper.grid_columnconfigure(0, weight=1)
        self.wrapper.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.wrapper, text="Geräteverwaltung", font=("Arial", 30, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(2, 12)
        )

        tools_frame = ctk.CTkFrame(self.wrapper, corner_radius=12)
        tools_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ctk.CTkButton(
            tools_frame,
            text="Neues Gerät",
            command=self.create_device,
            height=38,
            corner_radius=10,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            tools_frame,
            text="Aktualisieren",
            command=self.refresh_devices,
            height=38,
            corner_radius=10,
            font=("Arial", 13)
        ).pack(side="left", pady=8)

        self.status_label = ctk.CTkLabel(self.wrapper, text="", font=("Arial", 13))
        self.status_label.grid(row=2, column=0, sticky="nw", padx=12, pady=(0, 2))

        self.device_list_frame = ctk.CTkScrollableFrame(self.wrapper)
        self.device_list_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=(24, 8))

        self.refresh_devices()

    def _set_status(self, message, is_error=False):
        color = "#d9534f" if is_error else "#2e8b57"
        self.status_label.configure(text=message, text_color=color)

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _refresh_user_options(self):
        users = self.db_manager.get_users_basic(self.config)
        self.user_options = ["Nicht zugewiesen"]
        self.user_name_to_id = {"Nicht zugewiesen": None}
        for user in users:
            self.user_options.append(user["username"])
            self.user_name_to_id[user["username"]] = user["id"]

    def _render_devices(self, devices):
        self._clear_frame(self.device_list_frame)
        if not devices:
            ctk.CTkLabel(self.device_list_frame, text="Keine Geräte gefunden.", font=("Arial", 14)).pack(anchor="w", padx=8, pady=8)
            return

        for device in devices:
            card = ctk.CTkFrame(self.device_list_frame, corner_radius=12)
            card.pack(fill="x", padx=6, pady=6)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(10, 2))

            display_name = device.get("name") or "Ohne Name"
            ctk.CTkLabel(top, text=display_name, font=("Arial", 16, "bold")).pack(side="left")

            active_text = "Aktiv" if device["is_active"] else "Inaktiv"
            ctk.CTkLabel(top, text=f"Status: {active_text}", font=("Arial", 12)).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"Device-ID: {device['device_id']}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=12, pady=(0, 8))

            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(fill="x", padx=12, pady=(0, 10))

            assign_menu = ctk.CTkOptionMenu(controls, values=self.user_options, width=220)
            assign_menu.set(device.get("username") or "Nicht zugewiesen")
            assign_menu.pack(side="left", padx=(0, 8))

            ctk.CTkButton(
                controls,
                text="Zuweisung speichern",
                width=150,
                command=lambda device_id=device["id"], menu=assign_menu: self.save_device_assignment(
                    device_id,
                    self.user_name_to_id.get(menu.get())
                )
            ).pack(side="left", padx=(0, 8))

            toggle_text = "Deaktivieren" if device["is_active"] else "Aktivieren"
            ctk.CTkButton(
                controls,
                text=toggle_text,
                width=110,
                command=lambda device_id=device["id"], new_state=not device["is_active"]: self.toggle_device_active(
                    device_id,
                    new_state
                )
            ).pack(side="left")

    def refresh_devices(self):
        try:
            self._refresh_user_options()
            devices = self.db_manager.get_devices(self.config)
            self._render_devices(devices)
            self._set_status(f"{len(devices)} Geräte geladen")
        except Exception as exc:
            self._clear_frame(self.device_list_frame)
            ctk.CTkLabel(self.device_list_frame, text=f"Fehler beim Laden: {exc}", text_color="#d9534f").pack(anchor="w", padx=8, pady=8)
            self._set_status("Geräte konnten nicht geladen werden", is_error=True)

    def create_device(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neues Gerät")
        dialog.geometry("620x420")
        dialog.minsize(620, 420)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=14)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Gerät anlegen", font=("Arial", 24, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 18)
        )

        ctk.CTkLabel(frame, text="Gerätename:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=8)
        name_entry = ctk.CTkEntry(frame, height=40)
        name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Device-ID:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=14, pady=8)
        device_id_entry = ctk.CTkEntry(frame, height=40)
        device_id_entry.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Benutzer:", font=("Arial", 14)).grid(row=3, column=0, sticky="w", padx=14, pady=8)
        user_menu = ctk.CTkOptionMenu(frame, values=self.user_options)
        user_menu.set("Nicht zugewiesen")
        user_menu.grid(row=3, column=1, sticky="ew", padx=(0, 14), pady=8)

        status_label = ctk.CTkLabel(frame, text="", text_color="#d9534f", font=("Arial", 13))
        status_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 4))

        def submit():
            name = name_entry.get().strip()
            device_id = device_id_entry.get().strip()
            user_id = self.user_name_to_id.get(user_menu.get())

            if not name or not device_id:
                status_label.configure(text="Bitte Gerätename und Device-ID eingeben")
                return

            try:
                self.db_manager.create_device(self.config, device_id=device_id, name=name, user_id=user_id)
                dialog.destroy()
                self._set_status("Gerät erfolgreich angelegt")
                self.refresh_devices()
            except Exception as exc:
                status_label.configure(text=f"Fehler: {exc}")

        ctk.CTkButton(frame, text="Anlegen", command=submit, height=40).grid(
            row=5, column=0, columnspan=2, padx=14, pady=(10, 14), sticky="ew"
        )

    def save_device_assignment(self, device_id, user_id):
        try:
            self.db_manager.update_device(self.config, device_id=device_id, user_id=user_id, set_user=True)
            self._set_status("Gerätezuweisung gespeichert")
            self.refresh_devices()
        except Exception as exc:
            self._set_status(f"Fehler beim Speichern: {exc}", is_error=True)

    def toggle_device_active(self, device_id, is_active):
        try:
            self.db_manager.update_device(self.config, device_id=device_id, is_active=is_active)
            action = "aktiviert" if is_active else "deaktiviert"
            self._set_status(f"Gerät wurde {action}")
            self.refresh_devices()
        except Exception as exc:
            self._set_status(f"Fehler beim Aktualisieren: {exc}", is_error=True)
