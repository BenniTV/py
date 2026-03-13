"""
PyDispatch Admin – Dashboard-Ansicht.
Zeigt Übersichtskennzahlen und wichtige Informationen.
"""

import customtkinter as ctk

from admin.services.user_service import UserService
from admin.services.group_service import GroupService
from admin.services.device_service import DeviceService
from admin.services.keyword_service import KeywordService
from admin.config.settings import get_einrichtung_name
from admin.ui.components.widgets import (
    COLORS, StyledFrame, StyledLabel, StyledButton, StatCard,
)


class DashboardView(ctk.CTkFrame):
    """Dashboard-Ansicht mit Kennzahlen."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        einrichtung = get_einrichtung_name() or "PyDispatch"
        StyledLabel(header, text=f"Dashboard – {einrichtung}", style="title").pack(
            side="left"
        )

        refresh_btn = StyledButton(
            header, text="↻ Aktualisieren", variant="primary",
            command=self.refresh_data, width=150
        )
        refresh_btn.pack(side="right")

        # Statistik-Karten
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="new", padx=20, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_groups = StatCard(cards_frame, title="Benutzergruppen", value="0", icon="👥")
        self.card_groups.grid(row=0, column=0, padx=8, pady=8, sticky="ew")

        self.card_users = StatCard(cards_frame, title="Benutzer", value="0", icon="👤")
        self.card_users.grid(row=0, column=1, padx=8, pady=8, sticky="ew")

        self.card_einsaetze = StatCard(cards_frame, title="Einsätze", value="0", icon="🚨")
        self.card_einsaetze.grid(row=0, column=2, padx=8, pady=8, sticky="ew")

        self.card_devices = StatCard(cards_frame, title="Geräte", value="0", icon="📱")
        self.card_devices.grid(row=0, column=3, padx=8, pady=8, sticky="ew")

        # Zweite Reihe: Weitere Infos
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="new", padx=20, pady=10)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        # Aktive Gruppe
        self.active_group_card = StyledFrame(info_frame)
        self.active_group_card.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        StyledLabel(self.active_group_card, text="Aktive Benutzergruppe", style="heading").pack(
            anchor="w", padx=20, pady=(15, 5)
        )
        self.active_group_label = StyledLabel(
            self.active_group_card, text="Keine Gruppe gesetzt", style="normal"
        )
        self.active_group_label.configure(text_color=COLORS["text_secondary"])
        self.active_group_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Systemstatus
        self.status_card = StyledFrame(info_frame)
        self.status_card.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        StyledLabel(self.status_card, text="Systemstatus", style="heading").pack(
            anchor="w", padx=20, pady=(15, 5)
        )
        self.status_label = StyledLabel(self.status_card, text="Verbunden ✓", style="normal")
        self.status_label.configure(text_color=COLORS["success"])
        self.status_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Stichwörter-Übersicht
        self.keywords_card = StyledFrame(info_frame)
        self.keywords_card.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        StyledLabel(self.keywords_card, text="Stichwörter", style="heading").pack(
            anchor="w", padx=20, pady=(15, 5)
        )
        self.keywords_label = StyledLabel(
            self.keywords_card, text="0 Stichwörter definiert", style="normal"
        )
        self.keywords_label.configure(text_color=COLORS["text_secondary"])
        self.keywords_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Daten laden
        self.refresh_data()

    def refresh_data(self):
        """Aktualisiert alle Dashboard-Daten."""
        try:
            self.card_groups.update_value(str(GroupService.get_group_count()))
            self.card_users.update_value(str(UserService.get_user_count()))
            self.card_einsaetze.update_value(str(KeywordService.get_einsatz_count()))

            device_count = DeviceService.get_leitstellen_count() + DeviceService.get_mobile_device_count()
            self.card_devices.update_value(str(device_count))

            active_group = GroupService.get_active_group()
            if active_group:
                self.active_group_label.configure(
                    text=active_group["name"],
                    text_color=COLORS["primary"]
                )
            else:
                self.active_group_label.configure(
                    text="Keine Gruppe gesetzt",
                    text_color=COLORS["text_secondary"]
                )

            sw_count = KeywordService.get_stichwort_count()
            self.keywords_label.configure(text=f"{sw_count} Stichwörter definiert")
        except Exception:
            pass
