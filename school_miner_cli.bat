@echo off
title Schul-Scanner Pro (Terminal)
echo =========================================
echo  🏫 Schul-Scanner Pro - Terminal Version
echo =========================================
echo.
cd /d "%~dp0"

REM 1. Pruefen, ob Python installiert ist
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python wurde nicht gefunden!
    echo Bitte installiere Python von python.org und setze den Haken bei "Add Python to PATH".
    pause
    exit
)

REM 2. Virtuelle Umgebung erstellen
IF NOT EXIST "venv" (
    echo [1/3] Richte Programm zum ersten Mal ein...
    python -m venv venv
)

REM 3. Umgebung aktivieren
call venv\Scripts\activate

REM 4. Pakete aktualisieren/installieren
echo [2/3] Pruefe auf Updates fuer benoetigte Pakete...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

REM 5. Skript starten (Ersetze 'main.py' mit dem Namen deiner Konsolen-Datei!)
echo [3/3] Starte Skript...
echo.
python school_miner.py

pause
