"""
PyDispatch Leitstelle – Alarmierungs-Modul.
Schnelle Stichwort-Auswahl → Standort → Alarm auslösen.
Zeitvorgabe: max 30 Sekunden vom Öffnen bis zum Auslösen.
"""

import time
import customtkinter as ctk

from leitstelle.services.stichwort_service import StichwortService
from leitstelle.services.alarm_service import AlarmService
from leitstelle.ui.components.widgets import (
    COLORS, StyledFrame, StyledButton, StyledEntry, StyledLabel,
    StyledOptionMenu, show_error, show_info,
)


class AlarmView(ctk.CTkFrame):
    """Alarmierungs-Ansicht: Schnelle Stichwort-Auswahl und Alarm-Auslösung."""

    def __init__(self, master, leitstelle_db_id: int = None, on_done=None):
        super().__init__(master, fg_color=COLORS["bg_dark"])
        self.leitstelle_db_id = leitstelle_db_id
        self.on_done = on_done
        self.start_time = time.time()

        self.selected_stichwort = None
        self.selected_standort_id = None
        self.selected_standort_text = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header mit Timer ──
        header = ctk.CTkFrame(self, fg_color=COLORS["alarm_red"], corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        StyledLabel(header, text="🚨  ALARM AUSLÖSEN", style="subtitle").pack(
            side="left", padx=20, pady=12
        )

        self.timer_label = StyledLabel(header, text="⏱ 0s", style="heading")
        self.timer_label.pack(side="right", padx=20, pady=12)

        # ── Content ──
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # ── Footer ──
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        StyledButton(
            self.footer, text="← Abbrechen", variant="danger",
            command=self._cancel, width=150
        ).pack(side="left")

        self.send_btn = StyledButton(
            self.footer, text="🚨 ALARM SENDEN", variant="alarm",
            command=self._send_alarm, width=250,
            font=ctk.CTkFont(size=18, weight="bold"), height=50,
            state="disabled"
        )
        self.send_btn.pack(side="right")

        # Stichwörter laden und anzeigen
        self._show_stichwort_selection()

        # Timer starten
        self._update_timer()

    def _update_timer(self):
        """Aktualisiert den Timer jede Sekunde."""
        if not self.winfo_exists():
            return
        elapsed = int(time.time() - self.start_time)
        self.timer_label.configure(text=f"⏱ {elapsed}s")

        if elapsed >= 25:
            self.timer_label.configure(text_color=COLORS["alarm_red"])
        elif elapsed >= 15:
            self.timer_label.configure(text_color=COLORS["warning"])

        self.after(1000, self._update_timer)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_stichwort_selection(self):
        """Zeigt die Stichwort-Auswahl als große klickbare Buttons."""
        self._clear_content()

        StyledLabel(
            self.content, text="Stichwort auswählen:", style="subtitle"
        ).pack(anchor="w", pady=(0, 10))

        # Stichwörter laden
        stichwoerter = StichwortService.get_all_active_stichwoerter()

        if not stichwoerter:
            StyledLabel(
                self.content,
                text="Keine Stichwörter definiert.\n"
                     "Bitte in der Admin-Anwendung anlegen.",
                style="normal"
            ).pack(pady=30)
            return

        # Scrollbarer Bereich für Stichwörter
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure((0, 1), weight=1)

        # Stichwörter nach Kategorie gruppieren
        kategorien = {}
        for sw in stichwoerter:
            kat = sw.get("kategorie") or "Allgemein"
            kategorien.setdefault(kat, []).append(sw)

        row = 0
        for kat_name, sw_list in kategorien.items():
            # Kategorie-Header
            kat_label = StyledLabel(scroll, text=kat_name, style="heading")
            kat_label.configure(text_color=COLORS["text_secondary"])
            kat_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(15, 5))
            row += 1

            col = 0
            for sw in sw_list:
                # Standort-Info anzeigen
                typ = sw.get("standort_typ", "frei")
                standort_info = ""
                if typ == "fest" and sw.get("fester_standort_name"):
                    standort_info = f"\n📍 {sw['fester_standort_name']}"
                elif typ == "auswaehlbar":
                    standort_info = "\n📍 Standort wählbar"
                elif typ == "frei":
                    standort_info = "\n📍 Standort frei eintragen"

                btn_text = f"{sw['kuerzel']}\n{sw['bezeichnung']}{standort_info}"

                btn = ctk.CTkButton(
                    scroll,
                    text=btn_text,
                    fg_color=COLORS["bg_card"],
                    hover_color=COLORS["primary"],
                    corner_radius=12,
                    height=90,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text"],
                    anchor="center",
                    command=lambda s=sw: self._select_stichwort(s),
                )
                btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

                col += 1
                if col >= 2:
                    col = 0
                    row += 1

            if col != 0:
                row += 1

    def _select_stichwort(self, stichwort: dict):
        """Wird aufgerufen wenn ein Stichwort ausgewählt wurde."""
        self.selected_stichwort = stichwort
        typ = stichwort.get("standort_typ", "frei")

        if typ == "fest":
            # Fester Standort – direkt bereit zum Senden
            self.selected_standort_id = stichwort.get("fester_standort_id")
            self.selected_standort_text = stichwort.get("fester_standort_name", "")
            self._show_confirmation()

        elif typ == "auswaehlbar":
            # Standort aus Liste wählen
            self._show_standort_auswahl(stichwort)

        else:
            # Frei eintragen
            self._show_standort_frei(stichwort)

    def _show_standort_auswahl(self, stichwort: dict):
        """Zeigt die Standort-Auswahl für auswählbare Stichwörter."""
        self._clear_content()

        StyledLabel(
            self.content,
            text=f"Stichwort: {stichwort['kuerzel']} – {stichwort['bezeichnung']}",
            style="subtitle"
        ).pack(anchor="w", pady=(0, 5))

        StyledLabel(
            self.content, text="Standort auswählen:", style="heading"
        ).pack(anchor="w", pady=(5, 10))

        standorte = StichwortService.get_auswaehlbare_standorte(stichwort["id"])

        if not standorte:
            StyledLabel(
                self.content,
                text="Keine Standorte für dieses Stichwort definiert.",
                style="normal"
            ).pack(pady=20)
            StyledButton(
                self.content, text="← Zurück", variant="primary",
                command=self._show_stichwort_selection, width=120
            ).pack(anchor="w")
            return

        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for standort in standorte:
            btn = ctk.CTkButton(
                scroll,
                text=f"📍 {standort['name']}",
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["primary"],
                corner_radius=12,
                height=55,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text"],
                command=lambda s=standort: self._select_standort(s),
            )
            btn.pack(fill="x", pady=4)

        StyledButton(
            self.content, text="← Anderes Stichwort", variant="primary",
            command=self._show_stichwort_selection, width=200
        ).pack(anchor="w", pady=(10, 0))

    def _select_standort(self, standort: dict):
        """Standort aus der Auswahlliste gewählt."""
        self.selected_standort_id = standort["id"]
        self.selected_standort_text = standort["name"]
        self._show_confirmation()

    def _show_standort_frei(self, stichwort: dict):
        """Zeigt Freitext-Eingabe für den Standort."""
        self._clear_content()

        StyledLabel(
            self.content,
            text=f"Stichwort: {stichwort['kuerzel']} – {stichwort['bezeichnung']}",
            style="subtitle"
        ).pack(anchor="w", pady=(0, 5))

        StyledLabel(
            self.content, text="Standort eingeben:", style="heading"
        ).pack(anchor="w", pady=(5, 10))

        self.standort_frei_var = ctk.StringVar()
        entry = StyledEntry(
            self.content, textvariable=self.standort_frei_var,
            height=48, font=ctk.CTkFont(size=18),
            placeholder_text="z.B. Raum 204, Pausenhof, ..."
        )
        entry.pack(fill="x", pady=(0, 15))
        entry.focus_set()

        # Enter-Taste zum Bestätigen
        entry.bind("<Return>", lambda e: self._confirm_frei_standort())

        btn_row = ctk.CTkFrame(self.content, fg_color="transparent")
        btn_row.pack(fill="x")

        StyledButton(
            btn_row, text="← Anderes Stichwort", variant="primary",
            command=self._show_stichwort_selection, width=200
        ).pack(side="left")

        StyledButton(
            btn_row, text="Bestätigen →", variant="success",
            command=self._confirm_frei_standort, width=150
        ).pack(side="right")

    def _confirm_frei_standort(self):
        """Bestätigt den frei eingegebenen Standort."""
        text = self.standort_frei_var.get().strip()
        if not text:
            show_error("Fehler", "Bitte geben Sie einen Standort ein.")
            return
        self.selected_standort_id = None
        self.selected_standort_text = text
        self._show_confirmation()

    def _show_confirmation(self):
        """Zeigt die Bestätigungsansicht vor dem Senden."""
        self._clear_content()
        sw = self.selected_stichwort

        StyledLabel(
            self.content, text="Alarm bereit zum Senden", style="subtitle"
        ).pack(anchor="w", pady=(0, 15))

        # Zusammenfassung
        summary_card = StyledFrame(self.content)
        summary_card.pack(fill="x", pady=(0, 15))

        summary = ctk.CTkFrame(summary_card, fg_color="transparent")
        summary.pack(fill="x", padx=25, pady=20)

        StyledLabel(summary, text="Stichwort", style="small").pack(anchor="w", pady=(0, 2))
        StyledLabel(
            summary,
            text=f"{sw['kuerzel']} – {sw['bezeichnung']}",
            style="heading"
        ).pack(anchor="w", pady=(0, 10))

        StyledLabel(summary, text="Standort", style="small").pack(anchor="w", pady=(0, 2))
        standort = self.selected_standort_text or "—"
        StyledLabel(summary, text=f"📍 {standort}", style="heading").pack(
            anchor="w", pady=(0, 10)
        )

        # Optionale Notiz
        StyledLabel(summary, text="Notiz (optional)", style="small").pack(
            anchor="w", pady=(5, 3)
        )
        self.notiz_var = ctk.StringVar()
        StyledEntry(summary, textvariable=self.notiz_var, height=38,
                    placeholder_text="Zusätzliche Information...").pack(fill="x")

        StyledButton(
            self.content, text="← Zurück zur Stichwort-Auswahl",
            variant="primary", command=self._show_stichwort_selection,
            width=260
        ).pack(anchor="w", pady=(15, 0))

        # Alarm-Button aktivieren
        self.send_btn.configure(state="normal")

    def _send_alarm(self):
        """Sendet den Alarm."""
        if not self.selected_stichwort:
            show_error("Fehler", "Kein Stichwort ausgewählt.")
            return

        notiz = self.notiz_var.get().strip() if hasattr(self, "notiz_var") else ""

        success, msg, result = AlarmService.alarmieren(
            stichwort_id=self.selected_stichwort["id"],
            standort_text=self.selected_standort_text,
            standort_id=self.selected_standort_id,
            leitstelle_db_id=self.leitstelle_db_id,
            notiz=notiz,
        )

        if not success:
            show_error("Alarm-Fehler", msg)
            return

        # Ergebnis anzeigen
        self._show_alarm_result(result, msg)

    def _show_alarm_result(self, result: dict, message: str):
        """Zeigt das Ergebnis der Alarmierung."""
        self._clear_content()

        # Footer-Buttons anpassen
        for w in self.footer.winfo_children():
            w.destroy()

        alarm_typ = result.get("alarm_typ", "keine")

        if alarm_typ == "primaer":
            color = COLORS["success"]
            icon = "✅"
            title = "Alarm erfolgreich gesendet!"
        elif alarm_typ == "fallback":
            color = COLORS["warning"]
            icon = "⚠️"
            title = "Fallback-Alarmierung!"
        else:
            color = COLORS["danger"]
            icon = "🚫"
            title = "KEIN SANITÄTER VERFÜGBAR!"

        # Ergebnis-Anzeige
        result_card = StyledFrame(self.content)
        result_card.pack(fill="both", expand=True)

        result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
        result_inner.pack(expand=True, padx=30, pady=30)

        StyledLabel(result_inner, text=icon, style="huge").pack(pady=(0, 10))
        title_lbl = StyledLabel(result_inner, text=title, style="subtitle")
        title_lbl.configure(text_color=color)
        title_lbl.pack(pady=(0, 15))

        StyledLabel(result_inner, text=message, style="normal").pack(pady=(0, 15))

        # Alarmierte Benutzer anzeigen
        users = result.get("alarmierte_user", [])
        if users:
            StyledLabel(result_inner, text="Alarmierte Sanitäter:", style="heading").pack(
                anchor="w", pady=(10, 5)
            )
            for user in users:
                name = f"{user.get('vorname', '')} {user.get('nachname', '')}".strip()
                name = name or user["benutzername"]
                StyledLabel(result_inner, text=f"  • {name}", style="normal").pack(
                    anchor="w", pady=1
                )

        elapsed = int(time.time() - self.start_time)
        StyledLabel(
            result_inner,
            text=f"\nAlarmierung in {elapsed} Sekunden durchgeführt.",
            style="small"
        ).pack(pady=(15, 0))

        # Zurück-Button
        StyledButton(
            self.footer, text="✓ Zurück zum Dashboard", variant="success",
            command=self._done, width=250, height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="right")

    def _cancel(self):
        """Bricht die Alarmierung ab und kehrt zum Dashboard zurück."""
        if self.on_done:
            self.on_done()

    def _done(self):
        """Kehrt nach dem Alarm zum Dashboard zurück."""
        if self.on_done:
            self.on_done()
