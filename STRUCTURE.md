# 📂 Estructura del Proyecto

```
AI_Registros_de_Pozos/
│
├── 📄 README.md                    # Documentación original
├── 📄 README_APP.md                # Documentación de la aplicación Streamlit
├── 📄 QUICKSTART.md                # Guía de inicio rápido
├── 📄 STRUCTURE.md                 # Este archivo
│
├── 📄 requirements.txt              # Dependencias Python
├── 📄 setup.sh                      # Script setup para Linux/Mac
├── 📄 setup.bat                     # Script setup para Windows
├── 📄 run.sh                        # Script para ejecutar la app (Linux/Mac)
├── 📄 run.bat                       # Script para ejecutar la app (Windows)
│
├── 📁 app/                          # Aplicación Streamlit
│   ├── 📄 main.py                   # Aplicación principal (∼580 líneas)
│   │   ├── Interfaz Streamlit
│   │   ├── Carga de archivos LAS
│   │   ├── Procesamiento de datos
│   │   ├── Cálculos petrofísicos
│   │   ├── Visualización de registros
│   │   └── Exportación de resultados
│   │
│   └── 📁 modules/                  # Módulos reutilizables
│       ├── 📄 __init__.py           # Asegura que es un paquete Python
│       ├── 📄 petrofisica.py        # Cálculos petrofísicos (400+ líneas)
│       │   ├── PetroConfig - Configuración
│       │   ├── PetroPhysics - Cálculos
│       │   ├── LithoClassifier - Clasificación litológica
│       │   └── Funciones utilitarias
│       │
│       └── 📄 pdf_export.py         # Exportación a PDF (160+ líneas)
│           └── create_pdf_report() - Generación de reportes
│
├── 📁 .streamlit/                   # Configuración de Streamlit
│   └── 📄 config.toml               # Tema y opciones UI
│
└── 📁 venv/                         # Entorno virtual (después de setup)
    ├── bin/                         # Ejecutables (Python, pip, etc)
    └── lib/python3.x/site-packages/ # Librerías instaladas
```

## 📋 Descripción de Archivos Clave

### app/main.py (∼580 líneas)
**Aplicación Streamlit principal**

Flujo:
1. Configuración de página y sidebar
2. Upload de archivo LAS
3. Lectura e identificación de profundidad
4. Mapeo automático de curvas
5. Detección de matriz dominante
6. Cálculos petrofísicos (VSH, PHI, SW, PERM)
7. Visualización de registro de 8 tracks
8. Exportación (CSV, Excel, PDF)

Componentes principales:
- `st.sidebar` - Panel de configuración
- `st.file_uploader` - Carga de LAS
- `plt.subplots` - Gráficos matriciales
- Botones de descarga de resultados

### modules/petrofisica.py (400+ líneas)
**Lógica y cálculos petrofísicos**

Clases:
- `PetroConfig` - Configuración de parámetros
- `PetroPhysics` - Métodos de cálculo
- `LithoClassifier` - Clasificación de litología

Métodos destacados:
```python
# Cálculos petrófísicos
PetroPhysics.calc_vsh_larionov()
PetroPhysics.calc_porosity_density()
PetroPhysics.calc_porosity_neutron_density()
PetroPhysics.calc_water_saturation()
PetroPhysics.calc_permeability_kozeny()

# Clasificación
LithoClassifier.classify_advanced()

# Detección
detect_dominant_matrix()
```

### modules/pdf_export.py (160+ líneas)
**Generación de reportes PDF**

Función:
- `create_pdf_report(df, well_name, config, stats)`

Crea PDF con:
- Información del pozo
- Tabla de configuración
- Estadísticas petrofísicas
- Distribución litológica
- Zonas de paga

## 🔄 Flujo de Datos

```
┌─────────────────┐
│  Archivo LAS    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ 1. Lectura (lasio.read)     │
│ 2. Identificar DEPTH        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3. Mapeo de curvas          │
│    (GR, RHOB, NPHI, etc)    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4. Detección de matriz      │
│    (Archie params)          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 5. Cálculos petrofísicos    │
│    • VSH (Larionov)         │
│    • Porosidad              │
│    • Saturación (Archie)    │
│    • Permeabilidad          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 6. Identificar Net Pay      │
│    (Cutoffs)                │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 7. Visualización            │
│    • Registro 8 tracks      │
│    • Gráficos estadísticos  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 8. Exportación              │
│    • CSV                    │
│    • Excel                  │
│    • PDF                    │
└─────────────────────────────┘
```

## 🔧 Dependencias

| Librería | Versión | Propósito |
|----------|---------|----------|
| streamlit | ≥1.28.0 | Framework web interactivo |
| lasio | ≥0.31.0 | Lectura de archivos LAS |
| pandas | ≥2.0.0 | Manipulación de datos |
| numpy | ≥1.24.0 | Cálculos numéricos |
| scipy | ≥1.11.0 | Procesamiento científico (filtro mediana) |
| matplotlib | ≥3.7.0 | Visualización de gráficos |
| reportlab | ≥4.0.0 | Generación de PDF |
| pillow | ≥10.0.0 | Procesamiento de imágenes |
| openpyxl | ≥3.1.0 | Exportación a Excel |
| setuptools | ≥65.0.0 | Construcción de paquetes |

## 💡 Cómo Extender

### Agregar nueva curva
En `modules/petrofisica.py`, agregar a `curve_aliases`:
```python
'NUEVA_CURVA': ['ALIAS1', 'ALIAS2', 'ALIAS3'],
```

### Agregar nuevo cálculo
En `PetroPhysics`:
```python
@staticmethod
def calc_mi_parametro(valor1, valor2):
    # Tu cálculo aquí
    return resultado
```

### Modificar visualización
En `app/main.py`, sección "VISUALIZACIÓN DEL REGISTRO":
```python
# Agregar nuevo track en los subplots
axes[nuevo_track].plot(...)
```

## 🚀 Comandos Útiles

```bash
# Después de setup.sh

# Activar entorno
source venv/bin/activate

# Ejecutar aplicación
streamlit run app/main.py

# Ejecutar con puerto personalizado
streamlit run app/main.py --server.port 8502

# Ejecutar con archivo de prueba
streamlit run app/main.py -- archivo.las

# Ver versiones instaladas
pip freeze

# Actualizar una librería
pip install --upgrade streamlit

# Desactivar entorno
deactivate
```

## 📊 Estadísticas del Proyecto

- **Líneas de código**: ~1500+
- **Archivos Python**: 4
- **Dependencias**: 10
- **Funciones de cálculo**: 15+
- **Tracks de visualización**: 8
- **Formatos de exportación**: 3 (CSV, Excel, PDF)

## 🔐 Mantenibilidad

- ✅ Código modularizado (separación de responsabilidades)
- ✅ Funciones documentadas
- ✅ Nombres descriptivos de variables
- ✅ Manejo robusto de errores
- ✅ Validación de datos nulos

## 🎯 Próximas Mejoras Potenciales

- [ ] Análisis multi-pozo en batch
- [ ] Gráficos interactivos (Plotly)
- [ ] Base de datos de pozos
- [ ] Correlación entre pozos
- [ ] Modelos de machine learning
- [ ] Integración con APIs petrolíferas
- [ ] Tests unitarios
- [ ] Mobile app (Streamlit Mobile)
