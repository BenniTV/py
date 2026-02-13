import PyInstaller.__main__
import customtkinter
import os
import sys

# Ermittle den Pfad zu customtkinter, damit die Theme-Dateien etc. mitgepackt werden
ctk_path = os.path.dirname(customtkinter.__file__)

# Trennzeichen für Pfade (Semikolon für Windows, Doppelpunkt für Mac/Linux)
# Da du dieses Skript auf Windows ausführen willst, ist ';' der Standard.
# Python's os.pathsep macht das automatisch richtig, egal wo es läuft.
path_separator = os.pathsep

# Argumente für PyInstaller
args = [
    'PyDispatch_Desktop_Admin/main.py',  # Deine Hauptdatei
    '--name=PyDispatch_Admin',           # Name der EXE
    '--noconsole',                       # Kein Terminal-Fenster anzeigen (nur GUI)
    '--onefile',                         # Alles in eine einzige .exe packen
    '--clean',                           # Cache bereinigen
    # Füge customtkinter Daten hinzu: "Quellpfad_auf_Disk_Trennzeichen_Zielpfad_in_EXE"
    f'--add-data={ctk_path}{path_separator}customtkinter',
    
    # Hier fügen wir den 'src' Ordner hinzu, damit Python ihn sicher findet
    # (ist oft nicht zwingend nötig, wenn die Imports stimmen, aber sicherer)
    f'--add-data=PyDispatch_Desktop_Admin/src{path_separator}src',
]

print("Starte Build-Prozess für PyDispatch Admin...")
print(f"CustomTkinter Pfad: {ctk_path}")

# PyInstaller starten
PyInstaller.__main__.run(args)

print("\n----------------------------------------------------------------")
print("Build abgeschlossen!")
print("Du findest die .exe im Ordner 'dist'.")
print("----------------------------------------------------------------")
