import customtkinter as ctk


class UsersView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        self.groups = []
        self.group_options = ["Keine Gruppe"]
        self.group_name_to_id = {"Keine Gruppe": None}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.wrapper.grid_columnconfigure(0, weight=1)
        self.wrapper.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.wrapper, text="Benutzerverwaltung", font=("Arial", 30, "bold")).grid(
            row=0, column=0, sticky="w", padx=8, pady=(2, 12)
        )

        self.tab_view = ctk.CTkTabview(self.wrapper)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        
        self.tab_users = self.tab_view.add("Benutzer")
        self.tab_groups = self.tab_view.add("Gruppen")
        
        self._setup_users_tab()
        self._setup_groups_tab()
        self.refresh_groups()
        self.refresh_users()
        
    def _setup_users_tab(self):
        # Tools Frame
        tools_frame = ctk.CTkFrame(self.tab_users, corner_radius=12)
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            tools_frame,
            text="Neuer Benutzer",
            command=self.create_user,
            height=38,
            corner_radius=10,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(
            tools_frame,
            text="Aktualisieren",
            command=self.refresh_users,
            height=38,
            corner_radius=10,
            font=("Arial", 13)
        ).pack(side="left", padx=0, pady=8)

        self.users_status_label = ctk.CTkLabel(self.tab_users, text="", font=("Arial", 13))
        self.users_status_label.pack(anchor="w", padx=12, pady=(0, 2))
        
        # User List (Scrollable Frame)
        self.user_list_frame = ctk.CTkScrollableFrame(self.tab_users)
        self.user_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def _setup_groups_tab(self):
         # Tools Frame
        tools_frame = ctk.CTkFrame(self.tab_groups, corner_radius=12)
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            tools_frame,
            text="Neue Gruppe",
            command=self.create_group,
            height=38,
            corner_radius=10,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=8, pady=8)
        
        # Group List
        self.group_list_frame = ctk.CTkScrollableFrame(self.tab_groups)
        self.group_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.groups_status_label = ctk.CTkLabel(self.tab_groups, text="", font=("Arial", 13))
        self.groups_status_label.pack(anchor="w", padx=12, pady=(0, 2))

    def _clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _set_users_status(self, message, is_error=False):
        color = "#d9534f" if is_error else "#2e8b57"
        self.users_status_label.configure(text=message, text_color=color)

    def _set_groups_status(self, message, is_error=False):
        color = "#d9534f" if is_error else "#2e8b57"
        self.groups_status_label.configure(text=message, text_color=color)

    def _refresh_group_options(self):
        self.group_options = ["Keine Gruppe"]
        self.group_name_to_id = {"Keine Gruppe": None}
        for group in self.groups:
            name = group["name"]
            self.group_options.append(name)
            self.group_name_to_id[name] = group["id"]

    def _render_groups(self):
        self._clear_frame(self.group_list_frame)
        if not self.groups:
            ctk.CTkLabel(self.group_list_frame, text="Noch keine Gruppen vorhanden.", font=("Arial", 14)).pack(anchor="w", padx=8, pady=8)
            return

        for group in self.groups:
            card = ctk.CTkFrame(self.group_list_frame, corner_radius=12)
            card.pack(fill="x", padx=6, pady=6)

            ctk.CTkLabel(card, text=group["name"], font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=f"Priorität: {group['priority']}", font=("Arial", 13)).pack(anchor="w", padx=12, pady=(0, 10))

    def _render_users(self, users):
        self._clear_frame(self.user_list_frame)
        if not users:
            ctk.CTkLabel(self.user_list_frame, text="Keine Benutzer gefunden.", font=("Arial", 14)).pack(anchor="w", padx=8, pady=8)
            return

        for user in users:
            card = ctk.CTkFrame(self.user_list_frame, corner_radius=12)
            card.pack(fill="x", padx=6, pady=6)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card, text=user["username"], font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

            active_text = "Aktiv" if user["is_active"] else "Inaktiv"
            ctk.CTkLabel(card, text=f"Status: {active_text}", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=8)

            role_menu = ctk.CTkOptionMenu(controls, values=["user", "admin", "superadmin"], width=140)
            role_menu.set(user["role"])
            role_menu.pack(side="left", padx=(0, 8))

            group_menu = ctk.CTkOptionMenu(controls, values=self.group_options, width=180)
            group_menu.set(user.get("group_name") or "Keine Gruppe")
            group_menu.pack(side="left", padx=(0, 8))

            ctk.CTkButton(
                controls,
                text="Speichern",
                width=110,
                command=lambda user_id=user["id"], role_menu=role_menu, group_menu=group_menu: self.save_user_changes(
                    user_id,
                    role_menu.get(),
                    self.group_name_to_id.get(group_menu.get())
                )
            ).pack(side="left", padx=(0, 8))

            toggle_text = "Deaktivieren" if user["is_active"] else "Aktivieren"
            ctk.CTkButton(
                controls,
                text=toggle_text,
                width=110,
                command=lambda user_id=user["id"], new_state=not user["is_active"]: self.toggle_user_active(user_id, new_state)
            ).pack(side="left")

    def create_user(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neuer Benutzer")
        dialog.geometry("660x460")
        dialog.minsize(660, 460)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=14)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Benutzer anlegen", font=("Arial", 26, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 18))

        ctk.CTkLabel(frame, text="Benutzername:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=8)
        username_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13))
        username_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Passwort:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=14, pady=8)
        password_entry = ctk.CTkEntry(frame, show="*", height=40, font=("Arial", 13))
        password_entry.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Rolle:", font=("Arial", 14)).grid(row=3, column=0, sticky="w", padx=14, pady=8)
        role_menu = ctk.CTkOptionMenu(frame, values=["user", "admin", "superadmin"])
        role_menu.set("user")
        role_menu.grid(row=3, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Gruppe:", font=("Arial", 14)).grid(row=4, column=0, sticky="w", padx=14, pady=8)
        group_menu = ctk.CTkOptionMenu(frame, values=self.group_options)
        group_menu.set("Keine Gruppe")
        group_menu.grid(row=4, column=1, sticky="ew", padx=(0, 14), pady=8)

        status_label = ctk.CTkLabel(frame, text="", text_color="#d9534f", font=("Arial", 13))
        status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 4))

        def submit():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_menu.get()
            group_id = self.group_name_to_id.get(group_menu.get())

            if not username or not password:
                status_label.configure(text="Bitte Benutzername und Passwort eingeben")
                return

            try:
                self.db_manager.create_user(self.config, username, password, role=role, group_id=group_id)
                dialog.destroy()
                self._set_users_status("Benutzer erfolgreich angelegt")
                self.refresh_users()
            except Exception as exc:
                status_label.configure(text=f"Fehler: {exc}")

        ctk.CTkButton(frame, text="Anlegen", command=submit, height=40, font=("Arial", 14, "bold")).grid(row=6, column=0, columnspan=2, padx=14, pady=(12, 14), sticky="ew")

    def refresh_users(self):
        try:
            users = self.db_manager.get_users(self.config)
            self._render_users(users)
            self._set_users_status(f"{len(users)} Benutzer geladen")
        except Exception as exc:
            self._clear_frame(self.user_list_frame)
            ctk.CTkLabel(self.user_list_frame, text=f"Fehler beim Laden: {exc}", text_color="#d9534f").pack(anchor="w", padx=8, pady=8)
            self._set_users_status("Benutzer konnten nicht geladen werden", is_error=True)

    def refresh_groups(self):
        try:
            self.groups = self.db_manager.get_groups(self.config)
            self._refresh_group_options()
            self._render_groups()
            self._set_groups_status(f"{len(self.groups)} Gruppen geladen")
        except Exception as exc:
            self.groups = []
            self._refresh_group_options()
            self._clear_frame(self.group_list_frame)
            ctk.CTkLabel(self.group_list_frame, text=f"Fehler beim Laden: {exc}", text_color="#d9534f").pack(anchor="w", padx=8, pady=8)
            self._set_groups_status("Gruppen konnten nicht geladen werden", is_error=True)

    def create_group(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neue Gruppe")
        dialog.geometry("620x380")
        dialog.minsize(620, 380)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=14)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Gruppe anlegen", font=("Arial", 26, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 18))

        ctk.CTkLabel(frame, text="Name:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=8)
        name_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13))
        name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=8)

        ctk.CTkLabel(frame, text="Priorität:", font=("Arial", 14)).grid(row=2, column=0, sticky="w", padx=14, pady=8)
        priority_entry = ctk.CTkEntry(frame, height=40, font=("Arial", 13), placeholder_text="0")
        priority_entry.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=8)

        status_label = ctk.CTkLabel(frame, text="", text_color="#d9534f", font=("Arial", 13))
        status_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 4))

        def submit():
            name = name_entry.get().strip()
            priority_text = priority_entry.get().strip()

            if not name:
                status_label.configure(text="Bitte Gruppennamen eingeben")
                return

            if priority_text == "":
                priority = 0
            else:
                try:
                    priority = int(priority_text)
                except ValueError:
                    status_label.configure(text="Priorität muss eine Zahl sein")
                    return

            try:
                self.db_manager.create_group(self.config, name, priority=priority)
                dialog.destroy()
                self._set_groups_status("Gruppe erfolgreich angelegt")
                self.refresh_groups()
                self.refresh_users()
            except Exception as exc:
                status_label.configure(text=f"Fehler: {exc}")

        ctk.CTkButton(frame, text="Anlegen", command=submit, height=40, font=("Arial", 14, "bold")).grid(row=4, column=0, columnspan=2, padx=14, pady=(12, 14), sticky="ew")

    def save_user_changes(self, user_id, role, group_id):
        try:
            self.db_manager.update_user(self.config, user_id, role=role, group_id=group_id, set_group=True)
            self._set_users_status("Benutzer aktualisiert")
            self.refresh_users()
        except Exception as exc:
            self._set_users_status(f"Fehler beim Speichern: {exc}", is_error=True)

    def toggle_user_active(self, user_id, is_active):
        try:
            self.db_manager.update_user(self.config, user_id, is_active=is_active)
            action = "aktiviert" if is_active else "deaktiviert"
            self._set_users_status(f"Benutzer wurde {action}")
            self.refresh_users()
        except Exception as exc:
            self._set_users_status(f"Fehler beim Aktualisieren: {exc}", is_error=True)
