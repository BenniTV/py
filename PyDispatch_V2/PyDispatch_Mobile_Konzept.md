# **Konzept – Mobile App (Android & iOS)**

## **1. Plattformen**

- Verfügbar für **Android**
- Verfügbar für **iOS**
- Native oder Cross‑Platform (z. B. Flutter), je nach Projektentscheidung
- Fokus auf **extrem niedrigen Ressourcenverbrauch**
- Push‑ähnliche Alarmierung ohne Verzögerung (0 Sekunden Delay)

# **2. Einrichtung der App**

Beim ersten Start wird ein kurzer Setup‑Prozess durchgeführt.

### **Eingaben**

- **MySQL‑Verbindungsdaten**
    - Host
    - Port
    - Benutzername
    - Passwort
    - Datenbankname
- **Geräte‑ID**
    - Wird in der **Admin‑Software generiert**
    - Identifiziert das Gerät eindeutig
    - Ordnet automatisch:
        - Benutzer
        - Benutzergruppe
        - Berechtigungen

### **Wichtig**

- **Kein Login nötig**
- **Keine Passwörter lokal**
- **Keine Benutzerverwaltung in der App**
- Nach der Einrichtung läuft die App komplett automatisch

# **3. Hauptübersicht der App**

Die Startseite zeigt dem Nutzer:

### **3.1 Schichtstatus**

- Ob man **diese Woche** mit der Schicht dran ist
- Welche Gruppe aktuell aktiv ist
- Mit welchen Personen man gemeinsam Dienst hat

### **3.2 Status‑Buttons**

Der Nutzer hat drei große Buttons:

1. **In der Schule**
2. **Nicht in der Schule**
3. **Klassenarbeits‑Modus**

Der Status wird sofort an die Datenbank übertragen.

# **4. Alarmverhalten der App**

## **4.1 Status: „In der Schule“**

Wenn ein Alarm eingeht:

- Handy löst **10 Sekunden Alarm** aus
- **Taschenlampe blinkt SOS‑Muster**
- **Vibration aktiv**
- **Ton auf maximaler Lautstärke**
- Alarm stoppt nach 10 Sekunden automatisch
- Die Einsatzmeldung bleibt sichtbar, bis der Nutzer sie **per Swipe (oben → unten)** wegwischt

### **Datenschutz**

- Keine Rückmeldung, ob der Einsatz angenommen wurde
- Keine Standortübertragung des Nutzers

## **4.2 Status: „Nicht in der Schule“**

- **Keine Alarmierung**
- Nutzer wird komplett ignoriert
- Keine Benachrichtigungen

## **4.3 Klassenarbeits‑Modus**

Für Prüfungen, Klausuren, Tests.

Alarmverhalten:

- **Nur Taschenlampe (SOS)**
- **Keine Vibration**
- **Kein Ton**
- Alarm verschwindet automatisch nach **10 Minuten**
- Keine Interaktion nötig

### **Datenschutz**

- Keine sichtbare Einsatzmeldung
- Nur Lichtsignal
- Keine Logs auf dem Gerät

# **5. Backend‑Logik für die Mobile App**

### **5.1 Geräte‑Identifikation**

- Die Geräte‑ID aus der Admin‑Software verknüpft:
    - Benutzer
    - Gruppe
    - Berechtigungen
    - Status

### **5.2 Keine Benutzerkonten**

- Kein Login
- Keine Passwörter
- Keine Sessions
- Gerät = Identität

### **5.3 Minimaler Speicherverbrauch**

- App speichert nur:
    - MySQL‑Verbindungsdaten
    - Geräte‑ID
    - Aktuellen Status (in der Schule / nicht / Klassenarbeit)

### **5.4 Sofortige Alarmierung**

- Alarm wird **direkt** aus der Datenbank gelesen
- Keine Verzögerung
- Keine Polling‑Intervalle
- Push‑ähnliches Verhalten durch:
    - Websocket
    - Long‑Polling
    - Realtime‑DB‑Trigger