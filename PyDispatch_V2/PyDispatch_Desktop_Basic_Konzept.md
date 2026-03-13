# Leitstelle

## **1. Einrichtung der Leitstellen‑Software**

Beim ersten Start der Leitstellen‑Software wird ein kurzer Setup‑Prozess durchgeführt.

### **Eingaben während des Setups**

- **MySQL‑Serverdaten**
    - Host
    - Port
    - Benutzername
    - Passwort
    - Datenbankname
- **Leitstellen‑ID**
    - Diese ID wird **in der Admin‑Anwendung generiert**
    - Dient zur Zuordnung der Leitstelle zur jeweiligen Einrichtung

Nach erfolgreicher Verbindung zur Datenbank und Validierung der Leitstellen‑ID startet die Software direkt in die Leitstellen‑Ansicht.

# **2. Dashboard‑Ansicht**

Die Dashboard‑Ansicht zeigt alle relevanten Informationen für die Einsatzleitung in Echtzeit.

### **Angezeigte Informationen**

- **Aktive Benutzergruppe**
    - Welche Gruppe aktuell „dran“ ist (z. B. Gruppe A, Gruppe B)
- **Anzahl der verfügbaren Schulsanitäter**
    - Nur Nutzer, die ihren Status auf „in der Schule“ gesetzt haben

# **3. Alarmierungs‑Modul**

Das Herzstück der Leitstellen‑Software ist die Alarmierung.

## **3.1 Quick‑Action‑Button „Alarm auslösen“**

Ein großer, klar erkennbarer Button, der sofort in die Alarmierungsübersicht führt.

## **3.2 Alarmierungsübersicht**

Hier wird der Alarm vorbereitet.

### **Auswahl des Stichworts**

- Es werden alle Stichwörter angezeigt, die in der Admin‑Anwendung definiert wurden.
- Je nach Stichwort gelten unterschiedliche Standortregeln:

### **a) Stichwort mit festem Standort**

- Standort ist **vordefiniert**
- Kann **nicht geändert** werden
- Beispiel:
    - *R1 – Sekretariat (fester Standort)*

### **b) Stichwort mit auswählbarem Standort**

- Benutzer kann aus einer Liste wählen
- Beispiel:
    - *Sport Unfall – Sporthalle (Standort wählbar: SCHULE / EXTERNE)*
    - Bei mehreren Sporthallen → Auswahlmenü

### **c) Stichwort ohne vordefinierten Standort**

- Standort wird **frei eingetragen**
- Beispiel:
    - *R0 – Unbekannt*

### **Zeitkritische Vorgabe**

Vom Öffnen der Alarmierungsübersicht bis zum Auslösen des Alarms dürfen **maximal 30 Sekunden** vergehen.
→ UI muss extrem schnell und klar sein.

# **4. Backend‑Logik der Alarmierung**

Die Alarmierungslogik folgt festen Regeln:

## **4.1 Primäre Alarmierung**

- Es wird **zuerst die aktuelle Benutzergruppe** alarmiert
- Nur Nutzer, die ihren Status auf „in der Schule“ gesetzt haben, werden berücksichtigt

## **4.2 Fallback‑Alarmierung**

Wenn **kein einziger Schulsanitäter** der aktuellen Gruppe verfügbar ist:

- Werden **alle angelegten User** alarmiert
- Unabhängig von Gruppe oder Status

## **4.3 Keine Rückmeldung erforderlich**

- Nutzer müssen **nicht bestätigen**, ob sie den Einsatz annehmen
- Die App zeigt nur an, dass ein Alarm eingegangen ist

## **4.4 Keiner Verfügbar**

- Wenn keiner verfügar sendet nachricht an Leitstelle per Push und sound Kein sanitäter verfügbar

# **5. Status‑Reset der Benutzer**

Jeder Benutzer hat einen Status:

- „In der Schule“
- „Nicht in der Schule“

Dieser Status wird **täglich um 17:00 Uhr automatisch zurückgesetzt**.

Zweck:

- Sicherstellen, dass nur tatsächlich anwesende Sanitäter alarmiert werden
- Verhindern, dass alte Statuswerte zu Fehlalarmierungen führen