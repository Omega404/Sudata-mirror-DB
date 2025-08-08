@echo off
REM Ejecutar actualización semanal: BCRA + réplica completa

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo Ejecutando main_bcra.py...
python main_bcra.py

echo ----------------------------------------------
echo Ejecutando main_mirror.py...
python main_mirror.py

pause