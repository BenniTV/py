#!/usr/bin/env python3
"""
PyDispatch Admin – Einstiegspunkt.
Startet die administrative Desktop-Anwendung.
"""

import sys
import os

# Projekt-Root zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from admin.ui.app import AdminApp


def main():
    app = AdminApp()
    app.mainloop()


if __name__ == "__main__":
    main()
