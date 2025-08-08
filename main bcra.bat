@echo off
REM Activar entorno virtual y ejecutar main_bcra.py

cd /d "%~dp0"
call venv\Scripts\activate.bat

python main_bcra.py

pause
