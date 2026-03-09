@echo off
REM Ejecuta la copia de columnas (para la tarea programada cada 30 min)
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python copiar_columnas_api.py
REM Opcional: registrar en un log con fecha
REM echo [%date% %time%] >> log_copia.txt 2>&1
REM python copiar_columnas_api.py >> log_copia.txt 2>&1
