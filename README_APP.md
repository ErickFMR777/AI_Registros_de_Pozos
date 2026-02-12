# 🪨 Análisis Petrofísico - Aplicación Streamlit

Aplicación profesional para análisis petrofísico de registros de pozos (archivos LAS) con exportación a PDF, Excel y CSV.

## ✨ Características

- ✅ **Lectura automática de archivos LAS** - Detecta automáticamente profundidad y curvas
- ✅ **Mapeo flexible de curvas** - Maneja múltiples nombres de alias según estándares industria
- ✅ **Detección inteligente de matriz** - Identifica ARENISCA, CALIZA o DOLOMITA automáticamente
- ✅ **Cálculos petrofísicos completos**:
  - Volumen de arcilla (VSH) - Método Larionov
  - Porosidad total y efectiva
  - Saturación de agua - Ecuación de Archie
  - Permeabilidad - Modelo Kozeny-Carman
- ✅ **Identificación de Net Pay** - Criterios multi-parámetro configurables
- ✅ **Visualización profesional** - Registro de 8 tracks similar a software comercial
- ✅ **Exportación múltiple**:
  - CSV para análisis adicional
  - Excel con formato
  - PDF con tablas de resumen
- ✅ **Parámetros configurables** - Ajusta Archie, Rw y cutoffs en tiempo real

## 🚀 Instalación Rápida

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

## 📋 Instalación Manual

Si prefieres instalar manualmente:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app/main.py
```

## 📖 Uso

1. **Ejecuta la aplicación**:
```bash
streamlit run app/main.py
```

2. **Carga un archivo LAS** con el uploader en la interfaz

3. **Configura parámetros** en el panel lateral:
   - Parámetros de Archie (A, M, N)
   - Resistividad del agua (Rw)
   - Cutoffs para Net Pay

4. **Visualiza resultados**:
   - Gráfico del registro de 8 tracks
   - Estadísticas petrofísicas
   - Distribución litológica

5. **Exporta resultados** en tu formato preferido:
   - 📥 CSV
   - 📊 Excel
   - 📄 PDF

## 🔧 Estructura de Carpetas

```
AI_Registros_de_Pozos/
├── app/
│   ├── main.py                 # Aplicación principal Streamlit
│   └── modules/
│       ├── petrofisica.py      # Lógica de cálculos petrofísicos
│       └── pdf_export.py       # Generación de reportes PDF
├── .streamlit/
│   └── config.toml             # Configuración de Streamlit
├── requirements.txt            # Dependencias Python
├── setup.sh                    # Script setup para Linux/Mac
├── setup.bat                   # Script setup para Windows
└── README.md                   # Este archivo
```

## 📦 Dependencias

- **streamlit** - Framework web interactivo
- **lasio** - Lectura de archivos LAS
- **pandas** - Manipulación de datos
- **numpy** - Cálculos numéricos
- **scipy** - Procesamiento científico
- **matplotlib** - Visualización
- **reportlab** - Generación de PDF
- **pillow** - Procesamiento de imágenes
- **openpyxl** - Exportación Excel

Ver `requirements.txt` para versiones específicas.

## ⚙️ Parámetros Configurables

### Parámetros de Archie
- **A** (0.1 - 2.0): Factor de cementación
- **M** (1.5 - 3.0): Exponente de porosidad
- **N** (1.5 - 3.0): Exponente de saturación
- **Rw** (0.01 - 1.0 ohm-m): Resistividad del agua

### Cutoffs para Net Pay
- **Porosidad mínima**: 0.1% - 20%
- **VSH máximo**: 10% - 80%
- **Sw máximo**: 30% - 100%

## 📊 Formato de Archivo LAS

La aplicación acepta archivos LAS (Log ASCII Standard). Debe contener como mínimo:
- **Columna de profundidad**: DEPTH, DEPT, MD, TVD, etc.

Curvas opcionales (detectadas automáticamente):
- GR, SP, RT, RXOS, RHOB, NPHI, PEF, DT, VSH, SW, CALI, etc.

## 🎯 Casos de Uso

- Evaluación rápida de pozos
- Interpretación petrofísica automatizada
- Generación de reportes profesionales
- Análisis multi-pozo
- Capacitación en petrofísica

## 💡 Tips de Uso

1. **Detecta matriz automáticamente** - La app identifica si es arenisca, caliza o dolomita
2. **Ajusta parámetros de Archie** - Cambian según matriz dominante
3. **Verifica cobertura de datos** - En el resumen inicial
4. **Analiza distribución litológica** - Gráfico pie integrado
5. **Personaliza cutoffs** - Ajusta según criterios locales

## 🐛 Solución de Problemas

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
# Asegúrate de activar el entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instala dependencias
pip install -r requirements.txt
```

### "Error al leer archivo LAS"
- Verifica que el archivo sea válido
- Intenta abrirlo con `lasio.read(filename)` en Python
- Asegúrate que tenga extensión .las

### "Visualización lenta con muchas muestras"
- Normal con >10,000 muestras
- Los gráficos de Matplotlib pueden ser lentos
- Espera a que se complete

## 📝 Licencia

Este proyecto es de código abierto.

## 👨‍💻 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📧 Soporte

Para reportar bugs o sugerencias, abre un issue en el repositorio.

---

**Versión**: 1.0.0  
**Última actualización**: 2026-02-12
