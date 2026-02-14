# AI_WELL_LOG

**Advanced Well Log Analysis - Interpretación Automatizada de Registros de Pozos**

Una aplicación de análisis petrofísico automatizado para la interpretación de registros de pozos con soporte multiidioma (Español, Inglés, Francés).

🌐 **Disponible en:** aiwelllog.streamlit.app

## Características

- 📊 **Análisis Petrofísico Avanzado**: Porosidad, saturación de agua, arcillosidad, net pay
- 🎯 **Procesamiento Automático**: Análisis automático de registros de pozos (LAS)
- 🗺️ **Visualización en 8 Tracks**: Representación gráfica completa de registros
- 📈 **Clasificación Litológica**: Identificación automática de formaciones
- 📄 **Exportación de Reportes**: PDF, Excel y CSV individuales y consolidados
- 🌍 **Soporte Multiidioma**: Español, English, Français
- 🎨 **Interfaz Intuitiva**: Diseño limpio y moderno con Streamlit

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/ErickFMR777/AI_Registros_de_Pozos.git
cd AI_Registros_de_Pozos

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar la aplicación
streamlit run app/main.py
```

La aplicación se abrirá en `http://localhost:8501`

## Requisitos

- Python >= 3.8
- Streamlit >= 1.28.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.11.0
- matplotlib >= 3.7.0
- reportlab >= 4.0.0
- lasio >= 0.31.0
- openpyxl >= 3.1.0

## Estructura del Proyecto

```
├── app/
│   ├── main.py                 # Aplicación principal
│   └── modules/
│       ├── petrofisica.py      # Lógica petrofísica
│       ├── pdf_export.py       # Generación de PDFs individuales
│       └── pdf_batch_export.py # Generación de PDFs consolidados
├── .streamlit/
│   └── config.toml             # Configuración de Streamlit
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## Idiomas Soportados

- 🇪🇸 Español (es)
- 🇺🇸 English (en)
- 🇫🇷 Français (fr)

Selecciona tu idioma desde la barra lateral de la aplicación.

## Autor

Erick FM Rodríguez (ErickFMR777)

## Licencia

Todos los derechos reservados © 2026
