@echo off
REM ════════════════════════════════════════════════════
REM  iniciar_club.bat — Inicializa o Club (porta 5001)
REM  Coloque este arquivo na pasta CLUB/
REM ════════════════════════════════════════════════════

cd /d "%~dp0"

powershell -NoExit -Command "& '.\venv\Scripts\Activate.ps1'; python app.py"