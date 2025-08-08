@echo off
REM Activar entorno virtual y ejecutar main_mirror.py

cd /d "%~dp0"
call venv\Scripts\activate.bat

python main_mirror.py

pause
