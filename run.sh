#!/bin/bash
# ========================================================
# Script para ejecutar la aplicación Streamlit
# ========================================================

cd "$(dirname "$0")"

# Activar entorno virtual
source venv/bin/activate

# Ejecutar streamlit
echo "🚀 Iniciando aplicación Streamlit..."
echo "📱 Abriendo en http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

streamlit run app/main.py
