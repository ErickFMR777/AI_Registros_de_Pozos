@echo off
REM ========================================================
REM Script de Setup para Windows
REM ========================================================

echo.
echo 🚀 Iniciando setup de aplicacion Streamlit...
echo.

REM Crear entorno virtual
echo 1️⃣  Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo 2️⃣  Activando entorno virtual...
call venv\Scripts\activate

REM Actualizar pip
echo 3️⃣  Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 4️⃣  Instalando dependencias...
pip install -r requirements.txt

echo.
echo ✅ Setup completado exitosamente
echo.
echo Para ejecutar la aplicacion:
echo   1. venv\Scripts\activate
echo   2. streamlit run app/main.py
echo.
pause
