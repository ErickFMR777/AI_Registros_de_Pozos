#!/bin/bash
# ========================================================
# Script de Setup para Linux/Mac
# ========================================================

echo "🚀 Iniciando setup de aplicación Streamlit..."
echo ""

# Crear entorno virtual
echo "1️⃣  Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "2️⃣  Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "3️⃣  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "4️⃣  Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "✅ Setup completado exitosamente"
echo ""
echo "Para ejecutar la aplicación:"
echo "  1. source venv/bin/activate"
echo "  2. streamlit run app/main.py"
echo ""
