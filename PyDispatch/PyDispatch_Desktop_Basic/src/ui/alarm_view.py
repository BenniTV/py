import customtkinter as ctk
import time


class AlarmView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager, on_back, on_alarm_sent):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        self.on_back = on_back
        self.on_alarm_sent = on_alarm_sent
        self.keywords = []
        self.keyword_map = {}
        self.pending_alarm = None
        self.start_time = time.time()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Alarmierung", font=("Arial", 32, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(2, 8))

        self.timer_label = ctk.CTkLabel(self, text="Zeit seit Öffnen: 0s", font=("Arial", 14))
        self.timer_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 12))

        self.form = ctk.CTkFrame(self, corner_radius=14)
        self.form.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.form, text="Stichwort:", font=("Arial", 14)).grid(row=0, column=0, sticky="w", padx=14, pady=10)
        self.keyword_menu = ctk.CTkOptionMenu(self.form, values=["Lade Stichwörter..."])
        self.keyword_menu.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=10)

        ctk.CTkLabel(self.form, text="Ort:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=14, pady=10)
        self.location_fixed_label = ctk.CTkLabel(self.form, text="", font=("Arial", 13))
        self.location_selectable_menu = ctk.CTkOptionMenu(self.form, values=["-"])
        self.location_manual_entry = ctk.CTkEntry(self.form, height=38, placeholder_text="Ort manuell eingeben")

        self.location_help = ctk.CTkLabel(self.form, text="", font=("Arial", 12))
        self.location_help.grid(row=2, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8))

        self.status_label = ctk.CTkLabel(self.form, text="", font=("Arial", 13), text_color="#d9534f")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=14, pady=(0, 8))

        actions = ctk.CTkFrame(self.form, fg_color="transparent")
        actions.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(6, 14))
        actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(actions, text="Zurück", height=40, command=self.on_back).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(actions, text="Details prüfen", height=40, font=("Arial", 14, "bold"), command=self.prepare_alarm_details).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.detail_frame = ctk.CTkFrame(self, corner_radius=14)
        self.detail_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.detail_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.detail_frame, text="Alarm-Details", font=("Arial", 22, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 6)
        )

        self.detail_summary = ctk.CTkLabel(self.detail_frame, text="Bitte erst 'Details prüfen' ausführen.", font=("Arial", 13), justify="left")
        self.detail_summary.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 8))

        self.recipient_list = ctk.CTkScrollableFrame(self.detail_frame, height=160)
        self.recipient_list.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 10))
        self.recipient_list.grid_columnconfigure(0, weight=1)

        self.detail_status_label = ctk.CTkLabel(self.detail_frame, text="", font=("Arial", 13), text_color="#d9534f")
        self.detail_status_label.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 8))

        self.confirm_button = ctk.CTkButton(
            self.detail_frame,
            text="Alarm final auslösen",
            height=42,
            font=("Arial", 15, "bold"),
            state="disabled",
            command=self.confirm_and_trigger_alarm,
        )
        self.confirm_button.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 14))

        self.load_keywords()
        self._tick_timer()

    def _tick_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.configure(text=f"Zeit seit Öffnen: {elapsed}s")
        if elapsed <= 30:
            self.timer_label.configure(text_color="#2e8b57")
        else:
            self.timer_label.configure(text_color="#d9534f")
        self.after(1000, self._tick_timer)

    def load_keywords(self):
        self.keywords = self.db_manager.get_keywords(self.config)
        if not self.keywords:
            self.keyword_menu.configure(values=["Keine Stichwörter verfügbar"])
            self.keyword_menu.set("Keine Stichwörter verfügbar")
            return

        labels = [item["keyword"] for item in self.keywords]
        self.keyword_map = {item["keyword"]: item for item in self.keywords}
        self.keyword_menu.configure(values=labels, command=lambda _: self.update_location_widget())
        self.keyword_menu.set(labels[0])
        self.update_location_widget()

    def update_location_widget(self):
        self.location_fixed_label.grid_forget()
        self.location_selectable_menu.grid_forget()
        self.location_manual_entry.grid_forget()

        keyword_name = self.keyword_menu.get()
        keyword = self.keyword_map.get(keyword_name)
        if not keyword:
            return

        location_type = keyword["location_type"]
        if location_type == "fixed":
            value = keyword.get("default_location") or "(kein Standard-Ort)"
            self.location_fixed_label.configure(text=value)
            self.location_fixed_label.grid(row=1, column=1, sticky="w", padx=(0, 14), pady=10)
            self.location_help.configure(text="Fester Ort wird automatisch übernommen")
        elif location_type == "selectable":
            options = keyword.get("selectable_locations") or []
            if not options:
                options = ["Keine Orte hinterlegt"]
            self.location_selectable_menu.configure(values=options)
            self.location_selectable_menu.set(options[0])
            self.location_selectable_menu.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=10)
            self.location_help.configure(text="Ort aus der vorgegebenen Liste wählen")
        else:
            self.location_manual_entry.delete(0, "end")
            self.location_manual_entry.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=10)
            self.location_help.configure(text="Ort frei eingeben")

    def _resolve_location(self, keyword):
        location_type = keyword["location_type"]
        if location_type == "fixed":
            return (keyword.get("default_location") or "").strip()
        if location_type == "selectable":
            return self.location_selectable_menu.get().strip()
        return self.location_manual_entry.get().strip()

    def _clear_recipient_preview(self):
        for widget in self.recipient_list.winfo_children():
            widget.destroy()

    def prepare_alarm_details(self):
        self.status_label.configure(text="", text_color="#d9534f")
        self.detail_status_label.configure(text="", text_color="#d9534f")

        keyword_name = self.keyword_menu.get()
        keyword = self.keyword_map.get(keyword_name)
        if not keyword:
            self.status_label.configure(text="Kein gültiges Stichwort ausgewählt")
            self.confirm_button.configure(state="disabled")
            return

        location = self._resolve_location(keyword)
        if not location:
            self.status_label.configure(text="Bitte einen Ort setzen")
            self.confirm_button.configure(state="disabled")
            return

        recipients, fallback_used = self.db_manager.get_alert_recipients(self.config)
        if not recipients:
            self.detail_summary.configure(text="Keine Empfänger verfügbar.")
            self.detail_status_label.configure(text="Kein Sanitäter verfügbar")
            self.confirm_button.configure(state="disabled")
            self._clear_recipient_preview()
            return

        self.pending_alarm = {
            "keyword": keyword,
            "location": location,
            "recipients": recipients,
            "fallback_used": fallback_used,
        }

        fallback_text = "Ja (alle aktiven User)" if fallback_used else "Nein (aktive Gruppe)"
        self.detail_summary.configure(
            text=(
                f"Stichwort: {keyword['keyword']}\n"
                f"Ort: {location}\n"
                f"Empfänger: {len(recipients)}\n"
                f"Fallback verwendet: {fallback_text}"
            )
        )

        self._clear_recipient_preview()
        for user in recipients:
            row = ctk.CTkFrame(self.recipient_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"• {user['username']}", font=("Arial", 13)).pack(anchor="w", padx=4)

        self.detail_status_label.configure(text="Details geprüft. Du kannst jetzt final auslösen.", text_color="#2e8b57")
        self.confirm_button.configure(state="normal")

    def confirm_and_trigger_alarm(self):
        if not self.pending_alarm:
            self.detail_status_label.configure(text="Bitte zuerst Details prüfen", text_color="#d9534f")
            return

        keyword = self.pending_alarm["keyword"]
        location = self.pending_alarm["location"]
        recipients = self.pending_alarm["recipients"]
        fallback_used = self.pending_alarm["fallback_used"]

        self.db_manager.create_alarm(
            self.config,
            keyword_id=keyword["id"],
            keyword_name=keyword["keyword"],
            location_text=location,
            alerted_users=recipients,
            fallback_used=fallback_used,
        )

        fallback_info = " (Fallback: alle User)" if fallback_used else ""
        self.detail_status_label.configure(
            text=f"Alarm ausgelöst: {len(recipients)} Empfänger{fallback_info}",
            text_color="#2e8b57",
        )
        self.confirm_button.configure(state="disabled")
        self.pending_alarm = None
        if callable(self.on_alarm_sent):
            self.on_alarm_sent()
