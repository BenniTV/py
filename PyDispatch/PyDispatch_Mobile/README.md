# PyDispatch Mobile (MVP)

Dieses Verzeichnis enthält ein startbares Flutter-MVP für die Mobile-App:

- Setup mit DB-Daten + Geräte-ID
- Hauptansicht mit Schichtstatus und 3 Status-Buttons
- Realtime-Alarmstream (aktuell Mock) mit Alarm-Detailkarte
- Lokale Speicherung per `shared_preferences`

## Start

```bash
flutter pub get
flutter run
```

## Architektur-Hinweis

Aktuell ist ein `MockMobileRepository` aktiv. Für die Feinarbeiten muss es durch eine echte Realtime-Anbindung ersetzt werden (z. B. WebSocket/Gateway-Service), damit die Alarmierung ohne Polling produktiv läuft.
