import customtkinter as ctk

from ui.devices_view import DevicesView
from ui.keywords_view import KeywordsView
from ui.settings_view import SettingsView
from ui.users_view import UsersView


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, config, user_data, db_manager, config_manager=None):
        super().__init__(master)
        self.config = config
        self.user_data = user_data
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.nav_buttons = {}
        
        # Grid layout for sidebar + main content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()
        self.show_page("Dashboard")
        
    def set_db_manager(self, db_manager):
        # Deprecated
        pass
        
    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="PyDispatch Admin", font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=(26, 20))

        nav_items = ["Dashboard", "Benutzer", "Geräte", "Stichwörter", "Einstellungen"]
        for index, item in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=item,
                height=40,
                corner_radius=10,
                font=("Arial", 14),
                command=lambda page=item: self.show_page(page)
            )
            btn.grid(row=index, column=0, padx=20, pady=8, sticky="ew")
            self.nav_buttons[item] = btn

        role = self.user_data.get("role", "user")
        ctk.CTkLabel(self.sidebar, text=f"User: {self.user_data['username']}", font=("Arial", 13)).grid(row=8, column=0, padx=20, pady=(10, 4))
        ctk.CTkLabel(self.sidebar, text=f"Rolle: {role}", font=("Arial", 13)).grid(row=9, column=0, padx=20, pady=(0, 18))

    def _create_main_content(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _highlight_nav(self, active_name):
        for name, btn in self.nav_buttons.items():
            if name == active_name:
                btn.configure(state="disabled")
            else:
                btn.configure(state="normal")

    def _create_stat_card(self, master, title, value):
        card = ctk.CTkFrame(master, corner_radius=14)
        ctk.CTkLabel(card, text=title, font=("Arial", 13)).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(card, text=str(value), font=("Arial", 32, "bold")).pack(anchor="w", padx=16, pady=(0, 14))
        return card

    def _create_module_card(self, master, title, status_text):
        card = ctk.CTkFrame(master, corner_radius=14)
        ctk.CTkLabel(card, text=title, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(card, text=status_text, font=("Arial", 13)).pack(anchor="w", padx=16, pady=(0, 14))
        return card

    def _show_dashboard_page(self):
        wrapper = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)
        wrapper.grid_columnconfigure((0, 1), weight=1)

        setup_name = self.config.get("setup_name") or "PyDispatch Schule"
        ctk.CTkLabel(wrapper, text=setup_name, font=("Arial", 16)).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(2, 0)
        )
        ctk.CTkLabel(wrapper, text="Dashboard", font=("Arial", 34, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 18)
        )

        stats = self.db_manager.get_dashboard_stats(self.config)
        stats_cards = [
            ("Benutzer gesamt", stats.get("users_total", 0)),
            ("Benutzer aktiv", stats.get("users_active", 0)),
            ("Gruppen", stats.get("groups_total", 0)),
            ("Geräte", stats.get("devices_total", 0)),
            ("Stichwörter", stats.get("keywords_total", 0)),
        ]

        stats_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8)
        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        for idx, (title, value) in enumerate(stats_cards):
            card = self._create_stat_card(stats_frame, title, value)
            card.grid(row=0, column=idx, padx=5, sticky="nsew")

        ctk.CTkLabel(wrapper, text="Module", font=("Arial", 18, "bold")).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(20, 10)
        )

        module_frame = ctk.CTkFrame(wrapper, fg_color="transparent")
        module_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8)
        module_frame.grid_columnconfigure((0, 1), weight=1)

        modules = [
            ("Benutzerverwaltung", "Grundfunktionen vorhanden, Ausbau möglich"),
            ("Geräte", "Geräteverwaltung vorhanden, Ausbau möglich"),
            ("Stichwörter", "Stichwortverwaltung vorhanden, Ausbau möglich"),
            ("Einstellungen", "Setup- und Verbindungsdaten verwalten"),
        ]

        for idx, (title, text) in enumerate(modules):
            row = idx // 2
            col = idx % 2
            card = self._create_module_card(module_frame, title, text)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _show_placeholder_page(self, title, description):
        wrapper = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        ctk.CTkLabel(wrapper, text=title, font=("Arial", 34, "bold")).pack(anchor="w", pady=(4, 8))
        ctk.CTkLabel(wrapper, text=description, font=("Arial", 15)).pack(anchor="w", pady=(0, 14))

        info_box = ctk.CTkFrame(wrapper, corner_radius=14)
        info_box.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(info_box, text="Status: Platzhalter", font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(info_box, text="Hier entsteht als nächstes die vollständige Verwaltung.", font=("Arial", 13)).pack(anchor="w", padx=16, pady=(0, 12))

        actions = ctk.CTkFrame(wrapper, fg_color="transparent")
        actions.pack(fill="x")
        ctk.CTkButton(actions, text="Aktualisieren", height=40, corner_radius=10, font=("Arial", 14), command=lambda: self.show_page(title)).pack(side="left", padx=(0, 8), pady=4)
        ctk.CTkButton(actions, text="Zurück zum Dashboard", height=40, corner_radius=10, font=("Arial", 14), command=lambda: self.show_page("Dashboard")).pack(side="left", pady=4)
        
    def show_page(self, name):
        self._clear_content()
        self._highlight_nav(name)

        if name == "Dashboard":
            self._show_dashboard_page()
        elif name == "Benutzer":
            view = UsersView(self.content_frame, self.config, self.db_manager)
            view.pack(fill="both", expand=True)
        elif name == "Geräte":
            view = DevicesView(self.content_frame, self.config, self.db_manager)
            view.pack(fill="both", expand=True)
        elif name == "Stichwörter":
            view = KeywordsView(self.content_frame, self.config, self.db_manager)
            view.pack(fill="both", expand=True)
        elif name == "Einstellungen":
            view = SettingsView(
                self.content_frame,
                self.config,
                self.db_manager,
                self.config_manager,
                on_config_saved=self._on_config_saved
            )
            view.pack(fill="both", expand=True)
        else:
            self._show_placeholder_page(name, "Modul ist in Vorbereitung")

    def _on_config_saved(self, new_config):
        self.config.update(new_config)
