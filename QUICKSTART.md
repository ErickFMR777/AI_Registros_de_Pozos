# ⚡ Inicio Rápido

## Opción 1: Script Automático (Recomendado)

### En Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
streamlit run app/main.py
```

### En Windows:
```cmd
setup.bat
streamlit run app/main.py
```

---

## Opción 2: Manual

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar entorno
**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación
```bash
streamlit run app/main.py
```

---

## 📱 Usar la Aplicación

1. Se abrirá automáticamente en `http://localhost:8501`
2. Carga un archivo LAS con el botón "Upload"
3. Ajusta parámetros en el panel lateral si es necesario
4. Visualiza los resultados
5. Descarga el análisis en PDF, Excel o CSV

---

## 🛑 Detener la Aplicación

Presiona `Ctrl + C` en la terminal

---

## ✅ Verificar Instalación

Si algo falla, prueba:

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Instalar nuevamente dependencias
pip install --upgrade -r requirements.txt

# Verificar lasio
python -c "import lasio; print('✓ lasio OK')"

# Verificar streamlit
streamlit --version
```

---

## 📂 Archivos Importantes

- `app/main.py` - Aplicación principal
- `app/modules/petrofisica.py` - Cálculos petrofísicos
- `app/modules/pdf_export.py` - Exportación a PDF
- `requirements.txt` - Dependencias
- `.streamlit/config.toml` - Configuración UI

---

¡Listo! Disfruta analizando tus registros de pozos 🪨
