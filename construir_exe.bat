@echo off
REM Genera dist\MundoWumpus.exe (un solo archivo, sin consola).
REM Requiere: pip install -r requirements.txt pyinstaller
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name MundoWumpus ^
    --paths src --paths . ^
    --icon assets\icono.ico ^
    src\main.py
