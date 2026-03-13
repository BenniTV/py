"""
PyDispatch Leitstelle – Dashboard.
Zeigt Echtzeit-Übersicht: aktive Gruppe, verfügbare Sanitäter, aktive Einsätze.
"""

import customtkinter as ctk

from leitstelle.services.status_service import StatusService
from leitstelle.services.alarm_service import AlarmService
from leitstelle.services.leitstellen_service import LeitstellenService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledLabel, StatCard, AlarmButton,
)


class DashboardView(ctk.CTkFrame):
    """Dashboard-Ansicht der Leitstelle."""

    def __init__(self, master, on_alarm=None):
        super().__init__(master, fg_color="transparent")
        self.on_alarm = on_alarm

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))

        einrichtung = LeitstellenService.get_einrichtung_name()
        StyledLabel(header, text=f"🏥 {einrichtung} – Leitstelle", style="title").pack(
            side="left"
        )

        # ── Alarm-Button (prominent) ──
        alarm_frame = ctk.CTkFrame(self, fg_color="transparent")
        alarm_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(5, 15))

        self.alarm_btn = AlarmButton(alarm_frame, command=self._trigger_alarm)
        self.alarm_btn.pack(fill="x")

        # ── Content ──
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 20))
        content.grid_columnconfigure((0, 1, 2), weight=1)

        # Stat-Cards
        self.card_gruppe = StatCard(content, title="Aktive Gruppe", value="—", icon="👥")
        self.card_gruppe.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.card_verfuegbar = StatCard(
            content, title="Verfügbare Sanitäter", value="0", icon="🩺",
            value_color=COLORS["success"]
        )
        self.card_verfuegbar.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self.card_einsaetze = StatCard(
            content, title="Aktive Einsätze", value="0", icon="🚨"
        )
        self.card_einsaetze.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)

        # ── Sanitäter-Liste ──
        sani_card = StyledFrame(content)
        sani_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        StyledLabel(sani_card, text="Verfügbare Sanitäter (aktive Gruppe)", style="heading").pack(
            anchor="w", padx=20, pady=(15, 10)
        )

        self.sani_list_frame = ctk.CTkFrame(sani_card, fg_color="transparent")
        self.sani_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # ── Aktive Einsätze ──
        einsatz_card = StyledFrame(content)
        einsatz_card.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)

        StyledLabel(einsatz_card, text="Aktive Einsätze", style="heading").pack(
            anchor="w", padx=20, pady=(15, 10)
        )

        self.einsatz_list_frame = ctk.CTkFrame(einsatz_card, fg_color="transparent")
        self.einsatz_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Initiales Laden
        self.refresh_data()

    def refresh_data(self):
        """Aktualisiert alle Dashboard-Daten."""
        # Aktive Gruppe
        group = StatusService.get_active_group()
        if group:
            self.card_gruppe.update_value(group["name"])
        else:
            self.card_gruppe.update_value("Keine", color=COLORS["danger"])

        # Verfügbare Sanitäter
        available = StatusService.get_available_sanitaeter()
        count = len(available)
        if count > 0:
            self.card_verfuegbar.update_value(str(count), color=COLORS["success"])
        else:
            self.card_verfuegbar.update_value("0", color=COLORS["danger"])

        # Sanitäter-Liste aktualisieren
        for w in self.sani_list_frame.winfo_children():
            w.destroy()

        all_members = StatusService.get_all_group_members()
        if all_members:
            for member in all_members:
                name = f"{member.get('vorname', '')} {member.get('nachname', '')}".strip()
                name = name or member["benutzername"]
                is_available = member.get("status") == "in_der_schule"

                row = ctk.CTkFrame(self.sani_list_frame, fg_color="transparent", height=30)
                row.pack(fill="x", pady=2)

                status_icon = "🟢" if is_available else "🔴"
                status_text = "In der Schule" if is_available else "Nicht verfügbar"

                StyledLabel(row, text=f"{status_icon}  {name}", style="normal").pack(
                    side="left"
                )
                lbl = StyledLabel(row, text=status_text, style="small")
                lbl.configure(text_color=COLORS["success"] if is_available else COLORS["text_secondary"])
                lbl.pack(side="right")
        else:
            StyledLabel(
                self.sani_list_frame,
                text="Keine Mitglieder in der\naktiven Gruppe",
                style="small"
            ).pack(pady=10)

        # Aktive Einsätze
        active_einsaetze = AlarmService.get_active_einsaetze()
        self.card_einsaetze.update_value(str(len(active_einsaetze)))

        for w in self.einsatz_list_frame.winfo_children():
            w.destroy()

        if active_einsaetze:
            for einsatz in active_einsaetze:
                standort = einsatz.get("standort_name") or einsatz.get("standort_text") or "—"
                text = f"🚨 {einsatz['kuerzel']} – {standort}"
                StyledLabel(self.einsatz_list_frame, text=text, style="small").pack(
                    anchor="w", pady=2
                )
        else:
            lbl = StyledLabel(
                self.einsatz_list_frame,
                text="Keine aktiven Einsätze",
                style="small"
            )
            lbl.configure(text_color=COLORS["text_secondary"])
            lbl.pack(pady=10)

    def _trigger_alarm(self):
        """Öffnet die Alarmierungsübersicht."""
        if self.on_alarm:
            self.on_alarm()
