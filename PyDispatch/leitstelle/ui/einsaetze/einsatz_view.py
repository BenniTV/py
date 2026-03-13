"""
PyDispatch Leitstelle – Einsatz-Übersicht.
Zeigt aktive und vergangene Einsätze.
"""

import customtkinter as ctk

from leitstelle.services.alarm_service import AlarmService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledLabel, show_info, show_confirm,
)


class EinsatzView(ctk.CTkFrame):
    """Ansicht für die Einsatz-Übersicht."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))

        StyledLabel(header, text="Einsatz-Übersicht", style="title").pack(side="left")

        StyledButton(
            header, text="🔄 Aktualisieren", variant="primary",
            command=self.refresh_data, width=160
        ).pack(side="right")

        # Content: Tabs
        self.tab_view = ctk.CTkTabview(self, fg_color=COLORS["bg_dark"])
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))

        active_tab = self.tab_view.add("Aktive Einsätze")
        self._build_active_tab(active_tab)

        history_tab = self.tab_view.add("Einsatz-Verlauf")
        self._build_history_tab(history_tab)

        self.refresh_data()

    def _build_active_tab(self, parent):
        """Baut den Tab für aktive Einsätze."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.active_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent"
        )
        self.active_scroll.grid(row=0, column=0, sticky="nsew")

    def _build_history_tab(self, parent):
        """Baut den Tab für den Einsatz-Verlauf."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.history_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent"
        )
        self.history_scroll.grid(row=0, column=0, sticky="nsew")

    def refresh_data(self):
        """Aktualisiert beide Tabs."""
        self._refresh_active()
        self._refresh_history()

    def _refresh_active(self):
        """Aktualisiert die aktiven Einsätze."""
        for w in self.active_scroll.winfo_children():
            w.destroy()

        einsaetze = AlarmService.get_active_einsaetze()

        if not einsaetze:
            StyledLabel(
                self.active_scroll,
                text="Keine aktiven Einsätze",
                style="normal"
            ).pack(pady=30)
            return

        for einsatz in einsaetze:
            self._create_active_einsatz_card(einsatz)

    def _create_active_einsatz_card(self, einsatz: dict):
        """Erstellt eine Karte für einen aktiven Einsatz."""
        card = StyledFrame(self.active_scroll)
        card.pack(fill="x", pady=6)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)
        inner.grid_columnconfigure(1, weight=1)

        # Stichwort und Standort
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        kuerzel = einsatz.get("kuerzel", "?")
        bezeichnung = einsatz.get("bezeichnung", "")
        standort = einsatz.get("standort_name") or einsatz.get("standort_text") or "—"

        StyledLabel(info_frame, text=f"🚨 {kuerzel} – {bezeichnung}", style="heading").pack(
            anchor="w"
        )
        StyledLabel(info_frame, text=f"📍 Standort: {standort}", style="normal").pack(
            anchor="w", pady=(3, 0)
        )

        # Zeitstempel
        zeit = einsatz.get("alarmiert_am", "")
        if zeit:
            zeit_str = zeit.strftime("%d.%m.%Y %H:%M:%S") if hasattr(zeit, "strftime") else str(zeit)
        else:
            zeit_str = "—"

        StyledLabel(
            info_frame, text=f"⏱ Alarmiert: {zeit_str}", style="small"
        ).pack(anchor="w", pady=(3, 0))

        # Notiz
        notiz = einsatz.get("notiz", "")
        if notiz:
            StyledLabel(
                info_frame, text=f"📝 {notiz}", style="small"
            ).pack(anchor="w", pady=(3, 0))

        # Aktions-Buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        StyledButton(
            btn_frame, text="✓ Einsatz beenden", variant="success",
            command=lambda eid=einsatz["id"]: self._end_einsatz(eid),
            width=170
        ).pack(side="left", padx=(0, 8))

        StyledButton(
            btn_frame, text="✕ Abbrechen", variant="danger",
            command=lambda eid=einsatz["id"]: self._cancel_einsatz(eid),
            width=140
        ).pack(side="left")

    def _end_einsatz(self, einsatz_id: int):
        """Beendet einen Einsatz."""
        if show_confirm("Einsatz beenden", "Möchten Sie diesen Einsatz als beendet markieren?"):
            success, msg = AlarmService.end_einsatz(einsatz_id)
            if success:
                show_info("Erledigt", "Einsatz wurde beendet.")
                self.refresh_data()

    def _cancel_einsatz(self, einsatz_id: int):
        """Bricht einen Einsatz ab."""
        if show_confirm("Einsatz abbrechen", "Möchten Sie diesen Einsatz abbrechen?"):
            success, msg = AlarmService.cancel_einsatz(einsatz_id)
            if success:
                show_info("Abgebrochen", "Einsatz wurde abgebrochen.")
                self.refresh_data()

    def _refresh_history(self):
        """Aktualisiert den Einsatz-Verlauf."""
        for w in self.history_scroll.winfo_children():
            w.destroy()

        einsaetze = AlarmService.get_einsatz_history(limit=50)

        if not einsaetze:
            StyledLabel(
                self.history_scroll,
                text="Noch keine Einsätze vorhanden",
                style="normal"
            ).pack(pady=30)
            return

        for idx, einsatz in enumerate(einsaetze):
            self._create_history_card(einsatz, idx)

    def _create_history_card(self, einsatz: dict, idx: int):
        """Erstellt eine Karte für den Einsatz-Verlauf."""
        bg = COLORS["bg_card"] if idx % 2 == 0 else COLORS["bg_dark"]
        card = ctk.CTkFrame(self.history_scroll, fg_color=bg, corner_radius=8)
        card.pack(fill="x", pady=3)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)
        inner.grid_columnconfigure(1, weight=1)

        # Status-Icon
        status = einsatz.get("status", "")
        status_map = {
            "aktiv": ("🔴", "Aktiv", COLORS["danger"]),
            "beendet": ("✅", "Beendet", COLORS["success"]),
            "abgebrochen": ("⛔", "Abgebrochen", COLORS["text_secondary"]),
        }
        icon, status_text, color = status_map.get(status, ("❓", status, COLORS["text"]))

        # Info
        kuerzel = einsatz.get("kuerzel", "?")
        bezeichnung = einsatz.get("bezeichnung", "")
        standort = einsatz.get("standort_name") or einsatz.get("standort_text") or "—"

        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w")

        StyledLabel(
            info_frame,
            text=f"{icon} {kuerzel} – {bezeichnung}  |  📍 {standort}",
            style="normal"
        ).pack(anchor="w")

        # Zeiten
        zeit_alarmiert = einsatz.get("alarmiert_am", "")
        zeit_beendet = einsatz.get("beendet_am", "")

        if zeit_alarmiert:
            z = zeit_alarmiert.strftime("%d.%m.%Y %H:%M") if hasattr(zeit_alarmiert, "strftime") else str(zeit_alarmiert)
        else:
            z = "—"

        time_text = f"Alarmiert: {z}"
        if zeit_beendet:
            zb = zeit_beendet.strftime("%H:%M") if hasattr(zeit_beendet, "strftime") else str(zeit_beendet)
            time_text += f"  →  {status_text}: {zb}"

        time_lbl = StyledLabel(info_frame, text=time_text, style="small")
        time_lbl.configure(text_color=COLORS["text_secondary"])
        time_lbl.pack(anchor="w", pady=(2, 0))
