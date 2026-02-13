@echo off
echo ==========================================
echo PyDispatch Admin - Windows Build Script
echo ==========================================

REM Prüfen, ob Python verfügbar ist
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [FEHLER] Python wurde nicht gefunden!
    echo Bitte installiere Python und füge es zum PATH hinzu.
    echo Oder nutze eine portable Python-Version.
    pause
    exit /b
)

echo.
echo [1/4] Erstelle virtuelle Umgebung (.venv_win)...
if not exist .venv_win (
    python -m venv .venv_win
)

echo.
echo [2/4] Aktiviere virtuelle Umgebung...
call .venv_win\Scripts\activate

echo.
echo [3/4] Installiere Bibliotheken (Requirements & PyInstaller)...
pip install --upgrade pip
pip install -r PyDispatch_Desktop_Admin/requirements.txt
pip install pyinstaller

echo.
echo [4/4] Starte Build-Prozess (build_admin.py)...
python build_admin.py

echo.
if exist dist\PyDispatch_Admin.exe (
    echo ==========================================
    echo [ERFOLG] Build abgeschlossen!
    echo Die Datei liegt unter: dist\PyDispatch_Admin.exe
    echo ==========================================
) else (
    echo [FEHLER] Irgendetwas ist schiefgelaufen. Keine .exe gefunden.
)

pause
