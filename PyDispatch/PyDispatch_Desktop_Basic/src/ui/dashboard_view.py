import customtkinter as ctk
from datetime import datetime

from ui.alarm_view import AlarmView


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        self._refresh_job = None
        self._refresh_interval_ms = 5000

        self.active_group_value_label = None
        self.available_count_value_label = None
        self.history_container = None
        self.last_update_label = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)

        self.show_dashboard()

    def _clear_content(self):
        self._cancel_auto_refresh()
        for widget in self.content.winfo_children():
            widget.destroy()

    def _cancel_auto_refresh(self):
        if self._refresh_job is not None:
            try:
                self.after_cancel(self._refresh_job)
            except Exception:
                pass
            self._refresh_job = None

    def _schedule_auto_refresh(self):
        self._cancel_auto_refresh()
        self._refresh_job = self.after(self._refresh_interval_ms, self._refresh_dashboard_data)

    def _refresh_dashboard_data(self):
        try:
            data = self.db_manager.get_dashboard_data(self.config)
            active_group = data.get("active_group")
            active_group_name = active_group["name"] if active_group else "Keine Gruppe"
            available_count = str(data.get("available_count", 0))

            if self.active_group_value_label is not None and self.active_group_value_label.winfo_exists():
                self.active_group_value_label.configure(text=active_group_name)

            if self.available_count_value_label is not None and self.available_count_value_label.winfo_exists():
                self.available_count_value_label.configure(text=available_count)

            recent_alarms = self.db_manager.get_recent_alarms(self.config, limit=5)
            self._render_alarm_history(recent_alarms)

            if self.last_update_label is not None and self.last_update_label.winfo_exists():
                self.last_update_label.configure(text=f"Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            if self.last_update_label is not None and self.last_update_label.winfo_exists():
                self.last_update_label.configure(text="Aktualisierung fehlgeschlagen")
        finally:
            self._schedule_auto_refresh()

    def _render_alarm_history(self, recent_alarms):
        if self.history_container is None or not self.history_container.winfo_exists():
            return

        for widget in self.history_container.winfo_children():
            widget.destroy()

        if not recent_alarms:
            ctk.CTkLabel(self.history_container, text="Noch keine Alarme vorhanden.", font=("Arial", 13)).pack(
                anchor="w", padx=2, pady=(0, 6)
            )
            return

        for alarm in recent_alarms:
            row = ctk.CTkFrame(self.history_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            fallback_text = "Fallback" if alarm.get("fallback_used") else "Gruppe"
            time_text = str(alarm.get("created_at") or "")
            line = (
                f"{time_text} | {alarm.get('keyword_name')} @ {alarm.get('location_text')} | "
                f"Empfänger: {alarm.get('recipient_count', 0)} | {fallback_text}"
            )
            ctk.CTkLabel(row, text=line, font=("Arial", 12), justify="left", wraplength=980).pack(anchor="w")

    def show_dashboard(self):
        self._clear_content()
        self.content.grid_columnconfigure((0, 1), weight=1)
        self.content.grid_rowconfigure(4, weight=1)

        setup_name = self.db_manager.get_setting(self.config, "setup_name") or "PyDispatch"
        ctk.CTkLabel(self.content, text=f"{setup_name} – Leitstelle", font=("Arial", 16)).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 2)
        )
        ctk.CTkLabel(self.content, text="Dashboard", font=("Arial", 34, "bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 16)
        )

        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.grid(row=1, column=1, sticky="e", padx=8, pady=(0, 16))

        ctk.CTkButton(
            toolbar,
            text="Jetzt aktualisieren",
            width=150,
            height=36,
            command=self._refresh_dashboard_data,
        ).pack(side="right", padx=(8, 0))

        self.last_update_label = ctk.CTkLabel(toolbar, text="Noch nicht aktualisiert", font=("Arial", 12))
        self.last_update_label.pack(side="right")

        card_group = ctk.CTkFrame(self.content, corner_radius=14)
        card_group.grid(row=2, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))
        ctk.CTkLabel(card_group, text="Aktive Benutzergruppe", font=("Arial", 14)).pack(anchor="w", padx=14, pady=(12, 4))
        self.active_group_value_label = ctk.CTkLabel(card_group, text="—", font=("Arial", 26, "bold"))
        self.active_group_value_label.pack(anchor="w", padx=14, pady=(0, 14))

        card_available = ctk.CTkFrame(self.content, corner_radius=14)
        card_available.grid(row=2, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        ctk.CTkLabel(card_available, text="Verfügbare Schulsanitäter", font=("Arial", 14)).pack(anchor="w", padx=14, pady=(12, 4))
        self.available_count_value_label = ctk.CTkLabel(card_available, text="0", font=("Arial", 34, "bold"))
        self.available_count_value_label.pack(anchor="w", padx=14, pady=(0, 14))

        action = ctk.CTkFrame(self.content, corner_radius=14)
        action.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 6))
        ctk.CTkLabel(action, text="Alarmierung", font=("Arial", 18, "bold")).pack(anchor="w", padx=14, pady=(12, 6))
        ctk.CTkLabel(
            action,
            text="Starte die Alarmierung mit einem Klick und bleibe innerhalb der 30-Sekunden-Vorgabe.",
            font=("Arial", 13),
        ).pack(anchor="w", padx=14, pady=(0, 10))

        ctk.CTkButton(
            action,
            text="ALARM AUSLÖSEN",
            height=52,
            font=("Arial", 18, "bold"),
            command=self.show_alarm_view,
        ).pack(fill="x", padx=14, pady=(0, 14))

        history = ctk.CTkFrame(self.content, corner_radius=14)
        history.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=(8, 6))
        history.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(history, text="Letzte Alarme", font=("Arial", 18, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 6)
        )

        self.history_container = ctk.CTkScrollableFrame(history, height=180)
        self.history_container.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))
        self.history_container.grid_columnconfigure(0, weight=1)

        self._refresh_dashboard_data()

    def show_alarm_view(self):
        self._clear_content()
        alarm_view = AlarmView(
            self.content,
            self.config,
            self.db_manager,
            on_back=self.show_dashboard,
            on_alarm_sent=self.show_dashboard,
        )
        alarm_view.pack(fill="both", expand=True)
