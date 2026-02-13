## **1. Ersteinrichtung (Setup-Prozess)**

Beim ersten Start der administrativen Anwendung wird eine einmalige Einrichtung durchgeführt.
Dabei wird **nur die Verbindung zur zentralen Datenbank hergestellt**.
Es findet **keine Bindung an den lokalen PC** statt.

### **Eingaben während der Ersteinrichtung**

- **MySQL-Verbindungsdaten**
    - Host
    - Port
    - Benutzername
    - Passwort
    - Datenbankname
- **Einrichtungsname**
- **SuperAdmin-Konto**
    - Benutzername
    - Passwort

Nach Abschluss wird **ausschließlich die MySQL‑Konfiguration lokal gespeichert**, damit die Anwendung die Datenbank erreichen kann.
Alle anderen Daten (Benutzer, Gruppen, Geräte, Stichwörter, Einstellungen) liegen **zentral in der Datenbank**.

## **2. Benutzeroberfläche (UI) – Hauptmodule**

### **2.1 Dashboard**

Übersichtliche Startseite mit den wichtigsten Kennzahlen:

- Anzahl der Benutzergruppen
- Anzahl der Benutzer
- Anzahl der registrierten Einsätze
- Optional: letzte Aktivitäten, Systemstatus, Geräteübersicht

## **2.2 Benutzerverwaltung**

Zentrale Verwaltung aller Benutzer und Gruppen.

### **Funktionen**

- **Benutzergruppen anlegen, bearbeiten, löschen**
    - Jede Gruppe kann Rollen oder Berechtigungen enthalten
    - Mindestens **eine** Benutzergruppe ist erforderlich
- **Benutzer verwalten**
    - Benutzer anlegen, bearbeiten, deaktivieren
    - Benutzer einer oder mehreren Gruppen zuordnen
- **Gruppenlogik**
    - Wenn mehrere Gruppen existieren, kann definiert werden,
    wie Berechtigungen priorisiert oder kombiniert werden

## **2.3 Geräteverwaltung**

Verwaltung aller technischen Geräte, die mit dem System interagieren.

### **Leitstellen-PCs**

- Änderung der MySQL-Serverdaten
- Verwaltung der lokalen Konfiguration
- Statusanzeige (verbunden / nicht verbunden)

### **Mobile Geräte**

- Mobile Geräte registrieren
- Geräte bestimmten Personen zuordnen
- Geräte aktivieren/deaktivieren
- Übersicht über aktive Geräte

## **2.4 Stichworteinstellungen**

Hier werden alle Einsatz-Stichwörter zentral definiert.

### **Arten von Stichwörtern**

- **Stichwörter mit festem Standort**
Beispiel:
    - *R1 – Sekretariat (fester Standort)*
- **Stichwörter mit auswählbarem Standort**
Beispiel:
    - *Sport Unfall – Sporthalle (Standort wählbar: SCHULE / EXTERNE)*
- **Stichwörter ohne vordefinierten Standort**
Beispiel:
    - *R0 – Unbekannt (Standort wird in der Leitstelle manuell eingetragen)*

### **Funktionen**

- Neue Stichwörter anlegen
- Standorte definieren (fest, auswählbar, frei eintragbar)
- Kategorien oder Prioritäten vergeben
- Stichwörter aktivieren/deaktivieren

## **3. Wiederholte Einrichtung / Änderung der Konfiguration**

Falls die Ersteinrichtung bereits durchgeführt wurde, ist **kein erneutes Setup** erforderlich.

Stattdessen gibt es im Register-Fenster oder im Menü einen **Button „Konfiguration ändern“**.

### **Funktionen dieses Buttons**

- Änderung der **MySQL-Serverdaten**
- Änderung des **Einrichtungsnamens**
- Speichern der neuen Konfiguration
- Danach normaler Login mit bestehenden Benutzerdaten

### **Wichtig**

- Der SuperAdmin wird **nicht neu angelegt**
- Die Datenbank wird **nicht neu initialisiert**
- Es wird **nur die lokale Verbindungsdatei aktualisiert**

Damit bleibt das System sicher, zentralisiert und unabhängig vom jeweiligen PC.