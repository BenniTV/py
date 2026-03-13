#!/usr/bin/env python3
"""
PyDispatch Leitstelle – Einstiegspunkt.
Startet die Leitstellen-Anwendung.
"""

import sys
import os

# Projekt-Root zum Suchpfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from leitstelle.ui.app import LeitstelleApp


def main():
    app = LeitstelleApp()
    app.mainloop()


if __name__ == "__main__":
    main()
