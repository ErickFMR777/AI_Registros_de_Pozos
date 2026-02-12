@echo off
REM ========================================================
REM Script para ejecutar la aplicacion Streamlit en Windows
REM ========================================================

REM Activar entorno virtual
call venv\Scripts\activate

REM Ejecutar streamlit
echo.
echo 🚀 Iniciando aplicacion Streamlit...
echo 📱 Abriendo en http://localhost:8501
echo.
echo Presiona Ctrl+C para detener
echo.

streamlit run app/main.py

pause
