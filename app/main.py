# ==========================================================
# APLICACIÓN STREAMLIT: ANÁLISIS PETROFÍSICO
# ==========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import lasio
import io
import warnings
warnings.filterwarnings('ignore')

from modules.petrofisica import (
    PetroConfig, PetroPhysics, LithoClassifier, LITHO_COLORS,
    smooth_curve, flag_bad_data, clean_depth_data, 
    detect_dominant_matrix, get_valid_data_range
)
from modules.pdf_export import create_pdf_report
from modules.pdf_batch_export import create_pdf_batch_report

# ==========================================================
# CONFIGURACIÓN DE STREAMLIT
# ==========================================================
st.set_page_config(
    page_title="Análisis Petrofísico Preliminar Automatizado",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 2rem; }
    h1 { color: #1f77b4; }
    h2 { color: #1f77b4; margin-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR - CONFIGURACIÓN
# ==========================================================
st.sidebar.title("⚙️ Configuración")

st.sidebar.markdown("""
### 📋 Parámetros Ajustables

Ajusta los siguientes parámetros según tus necesidades de análisis:

- **Cutoffs**: Umbrales mínimos y máximos para identificar zonas productivas
- **Archie**: Parámetros de la ecuación de Archie para cálculo de saturación
""")

st.sidebar.subheader("Cutoffs para Net Pay")
phi_cutoff = st.sidebar.slider("Porosidad mínima (%)", 0.1, 20.0, 6.0, step=0.1) / 100
vsh_cutoff = st.sidebar.slider("VSH máximo (%)", 10.0, 80.0, 50.0, step=5.0) / 100
sw_cutoff = st.sidebar.slider("Sw máximo (%)", 30.0, 100.0, 70.0, step=5.0) / 100

st.sidebar.subheader("Parámetros de Archie")
config_a = st.sidebar.slider("Parámetro A", 0.5, 2.0, 1.0, step=0.05)
config_m = st.sidebar.slider("Parámetro M (cementación)", 1.8, 2.5, 2.0, step=0.05)
config_n = st.sidebar.slider("Parámetro N (saturación)", 1.8, 2.5, 2.0, step=0.05)
config_rw = st.sidebar.slider("Resistividad agua (Rw) [ohm-m]", 0.01, 0.5, 0.05, step=0.01)

# Actualizar configuración global
PetroConfig.A = config_a
PetroConfig.M = config_m
PetroConfig.N = config_n
PetroConfig.RW = config_rw
PetroConfig.PHI_CUTOFF = phi_cutoff
PetroConfig.VSH_CUTOFF = vsh_cutoff
PetroConfig.SW_CUTOFF = sw_cutoff

# ==========================================================
# FUNCIONES DE APOYO
# ==========================================================

def display_las_viewer(df, file_index):
    """Muestra un explorador de datos interactivo del archivo LAS"""
    with st.expander("📊 Explorador de Datos del Archivo LAS", expanded=False):
        st.subheader("Columnas disponibles")
        
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Selecciona columnas para visualizar",
            all_columns,
            default=all_columns[:min(8, len(all_columns))],
            key=f"col_selector_{file_index}"
        )
        
        if selected_columns:
            # Tabla de datos
            st.subheader("Primeras 100 muestras")
            st.dataframe(
                df[selected_columns].head(100),
                use_container_width=True,
                height=400
            )
            
            # Estadísticas
            st.subheader("Estadísticas de Columnas")
            stats_display = df[selected_columns].describe().T
            st.dataframe(stats_display, use_container_width=True)
            
            # Info de columnas
            st.subheader("Información Detallada")
            col_info_list = []
            for col in selected_columns:
                col_info_list.append({
                    'Columna': col,
                    'Tipo': str(df[col].dtype),
                    'No-nulos': df[col].notna().sum(),
                    'Nulos': df[col].isna().sum(),
                    'Min': f"{df[col].min():.4f}" if pd.api.types.is_numeric_dtype(df[col]) else '-',
                    'Max': f"{df[col].max():.4f}" if pd.api.types.is_numeric_dtype(df[col]) else '-',
                })
            
            col_info_df = pd.DataFrame(col_info_list)
            st.dataframe(col_info_df, use_container_width=True)

# ==========================================================
# MAIN
# ==========================================================
# Interfaz inicial profesional - Rediseño limpio
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0 2.5rem 0;">
    <h1 style="color: #1f77b4; font-size: 2.5em; margin: 0; font-weight: 700;">🪨 ANÁLISIS PETROFÍSICO</h1>
    <p style="color: #666; font-size: 1.05em; margin: 0.5rem 0 0 0; font-weight: 300;">Registros de Pozos - Procesamiento Profesional</p>
</div>
""", unsafe_allow_html=True)

# Características en fila compacta
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid #667eea; text-align: center;">
    <p style="margin: 0; font-size: 0.9em;"><b>8 Tracks</b><br/>Visualización profesional</p>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid #667eea; text-align: center;">
    <p style="margin: 0; font-size: 0.9em;"><b>Multi-pozo</b><br/>Procesamiento lote</p>
    </div>
    """, unsafe_allow_html=True)
    
with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid #667eea; text-align: center;">
    <p style="margin: 0; font-size: 0.9em;"><b>3 Formatos</b><br/>PDF, Excel, CSV</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# Upload de múltiples archivos
uploaded_files = st.file_uploader("📤 Carga uno o más archivos LAS (.las)", type=['las'], accept_multiple_files=True, key='las_files', label_visibility="visible")

if uploaded_files:
    total_files = len(uploaded_files)
    st.info(f"📊 {total_files} archivo(s) para procesar")
    
    # Almacenar datos de todos los pozos
    all_wells_data = []
    for file_idx, uploaded_file in enumerate(uploaded_files, 1):
        st.markdown("---")
        
        try:
            # ======================================================
            # LECTURA Y LIMPIEZA DE DATOS
            # ======================================================
            st.info(f"📖 Procesando: {uploaded_file.name} ({file_idx}/{total_files})...")
            
            # Guardar archivo temporal
            temp_path = f'/tmp/temp_well_{file_idx}.las'
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            las = lasio.read(temp_path, ignore_header_errors=True)
            df = las.df().reset_index()
            
            well_name = uploaded_file.name.replace('.las', '').upper()
            
            st.success(f"✓ {well_name}: {len(df.columns)} columnas, {len(df)} muestras")
            
            # ======================================================
            # EXPLORADOR DE DATOS
            # ======================================================
            display_las_viewer(df, file_idx)
            
            # ======================================================
            # PASO 1: IDENTIFICAR PROFUNDIDAD
            # ======================================================
            st.subheader(f"1️⃣ Identificación de Profundidad")
            
            depth_aliases = ['DEPTH', 'DEPT', 'MD', 'MEASURED_DEPTH', 'TVD', 'TVDSS', 
                            'TDEP', 'MD_FT', 'DEPTM', 'INDEX']
            depth_col = None
            
            for alias in depth_aliases:
                if alias in df.columns:
                    depth_col = alias
                    break
            
            if depth_col is None:
                depth_col = df.columns[0]
            
            df.rename(columns={depth_col: 'DEPTH_FT'}, inplace=True)
            df = clean_depth_data(df)
            df['DEPTH'] = df['DEPTH_FT'] * 0.3048
            
            depth_ft_min = df['DEPTH_FT'].min()
            depth_ft_max = df['DEPTH_FT'].max()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Profundidad Inicial (ft)", f"{depth_ft_min:.1f}")
            with col2:
                st.metric("Profundidad Final (ft)", f"{depth_ft_max:.1f}")
            with col3:
                st.metric("Intervalo (ft)", f"{depth_ft_max - depth_ft_min:.1f}")
            
            # ======================================================
            # PASO 2: MAPEO DE CURVAS
            # ======================================================
            st.subheader("2️⃣ Mapeo de Curvas Disponibles")
            
            curve_aliases = {
                'CALI': ['CALI', 'CAL', 'CAL1', 'CALIPER'],
                'BS': ['BS', 'BIT_SIZE'],
                'GR': ['GR', 'GAM', 'HGR', 'GAMMA'],
                'SP': ['SP', 'SSP'],
                'RT': ['RT', 'RTRUE', 'RESD', 'RDEP', 'ILD', 'LLD', 'RILD', 'RD', 'AT90', 'AIT90', 'AT60', 'AIT60', 'RLA4', 'HRLA4'],
                'RM_RES': ['RESM', 'LLM', 'ILM', 'AT30', 'AIT30', 'AT20', 'AIT20', 'RLA3', 'HRLA3', 'RLA2', 'HRLA2'],
                'RXOS': ['RXOS', 'RESS', 'LLS', 'SFL', 'MSFL', 'RXO', 'AT10', 'AIT10', 'RLA1', 'HRLA1'],
                'RMC': ['RMC', 'RMCAKE', 'MUDCAKE'],
                'RMUD': ['RMUD', 'MUD_RES'],
                'RW': ['RW', 'RWA', 'WATER_RES'],
                'RHOB': ['RHOB', 'DEN', 'DENS', 'RHOZ', 'DENSITY'],
                'NPHI': ['NPHI', 'NPL', 'NPOS', 'NEUT'],
                'PEF': ['PEF', 'PE', 'PHOTO'],
                'DT': ['DT', 'AC', 'SONIC'],
                'VSH': ['VSH', 'VCL', 'VSHALE'],
                'SW': ['SW', 'SWE', 'SWAT'],
                'PHIT': ['PHIT', 'PHI_T', 'PHIE', 'PHI'],
            }
            
            available_curves = {}
            for standard_name, aliases in curve_aliases.items():
                for alias in aliases:
                    if alias in df.columns:
                        df[standard_name] = df[alias].copy()
                        available_curves[standard_name] = alias
                        break
                if standard_name not in available_curves:
                    df[standard_name] = np.nan
            
            available_str = ", ".join([f"{k} ({v})" for k, v in available_curves.items()])
            st.write(f"✓ Curvas mapeadas: {available_str}")
            
            # ======================================================
            # PASO 3: DETECCIÓN DE MATRIZ
            # ======================================================
            st.subheader("3️⃣ Detección de Matriz Dominante")
            
            dominant_matrix, dominant_rho = detect_dominant_matrix(df)
            PetroConfig.DOMINANT_MATRIX = dominant_matrix
            PetroConfig.DOMINANT_RHO = dominant_rho
            
            if dominant_matrix in PetroConfig.ARCHIE_PARAMS:
                params = PetroConfig.ARCHIE_PARAMS[dominant_matrix]
                PetroConfig.A = params['A']
                PetroConfig.M = params['M']
                PetroConfig.N = params['N']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Matriz Dominante", dominant_matrix)
            with col2:
                st.metric("Densidad (g/cc)", f"{dominant_rho:.3f}")
            
            # ======================================================
            # PASO 4: CÁLCULOS PETROFÍSICOS
            # ======================================================
            st.subheader("4️⃣ Cálculos Petrofísicos")
            
            progress = st.progress(0)
            
            # Suavizado
            for col in ['GR', 'RHOB', 'NPHI']:
                if col in df.columns and df[col].notna().sum() > 10:
                    df[col] = smooth_curve(df[col], window=5)
            
            progress.progress(20)
            
            # VSH
            if df['VSH'].notna().any():
                st.write("✓ VSH: valores pre-calculados")
            elif df['GR'].notna().any():
                gr_valid = df['GR'].dropna()
                gr_min = gr_valid.quantile(0.02)
                gr_max = gr_valid.quantile(0.98)
                df['VSH'] = df['GR'].apply(
                    lambda x: PetroPhysics.calc_vsh_larionov(x, gr_min, gr_max)
                )
                st.write(f"✓ VSH: calculado (Larionov)")
            else:
                df['VSH'] = np.nan
                st.warning("⚠️ VSH: No se puede calcular sin GR")
            
            progress.progress(40)
            
            # Litología
            litho_list = []
            rho_matrix_list = []
            
            for idx, row in df.iterrows():
                lith = LithoClassifier.classify_advanced(
                    row['VSH'], 0, row['RHOB'], row['NPHI'], 
                    row['PEF'], dominant_matrix
                )
                litho_list.append(lith)
                
                if 'DOLOMITA' in lith:
                    rho_ma = 2.87
                elif 'CALIZA' in lith or 'CARBONATO' in lith:
                    rho_ma = 2.71
                elif 'LUTITA' in lith:
                    rho_ma = 2.70
                else:
                    rho_ma = dominant_rho
                
                rho_matrix_list.append(rho_ma)
            
            df['LITOLOGIA'] = litho_list
            df['RHO_MATRIX'] = rho_matrix_list
            
            progress.progress(60)
            
            # Porosidad
            df['PHI_T'] = np.nan
            df['PHI_E'] = np.nan
            
            if df['PHIT'].notna().any():
                df['PHI_T'] = df['PHIT'].copy()
                st.write("✓ Porosidad: valores pre-calculados")
            elif df['RHOB'].notna().any():
                for idx, row in df.iterrows():
                    if pd.notna(row['RHOB']):
                        if pd.notna(row['NPHI']):
                            phi_t = PetroPhysics.calc_porosity_neutron_density(
                                row['NPHI'], row['RHOB'], row['RHO_MATRIX'], 
                                PetroConfig.RHO_FLUID, row['VSH']
                            )
                        else:
                            phi_t = PetroPhysics.calc_porosity_density(
                                row['RHOB'], row['RHO_MATRIX'], 
                                PetroConfig.RHO_FLUID, row['VSH']
                            )
                        df.loc[idx, 'PHI_T'] = phi_t
                
                st.write(f"✓ Porosidad: calculada para {df['PHI_T'].notna().sum()} muestras")
            else:
                st.warning("⚠️ Porosidad: No se puede calcular sin RHOB")
            
            # Porosidad efectiva
            for idx, row in df.iterrows():
                if pd.notna(row['PHI_T']) and pd.notna(row['VSH']):
                    phi_e = PetroPhysics.calc_effective_porosity(row['PHI_T'], row['VSH'])
                    df.loc[idx, 'PHI_E'] = phi_e
            
            progress.progress(80)
            
            # Saturación
            df['SW'] = np.nan
            if df['SW'].notna().any():
                st.write("✓ Saturación: valores pre-calculados")
            elif df['RT'].notna().any():
                for idx, row in df.iterrows():
                    sw = PetroPhysics.calc_water_saturation(
                        row['PHI_E'], row['RT'], 
                        PetroConfig.A, PetroConfig.M, 
                        PetroConfig.N, PetroConfig.RW
                    )
                    df.loc[idx, 'SW'] = sw
                st.write(f"✓ Saturación: calculada para {df['SW'].notna().sum()} muestras")
            else:
                st.warning("⚠️ Saturación: No se puede calcular sin RT")
            
            # Permeabilidad
            df['PERM'] = np.nan
            for idx, row in df.iterrows():
                perm = PetroPhysics.calc_permeability_kozeny(row['PHI_E'], row['VSH'])
                df.loc[idx, 'PERM'] = perm
            
            progress.progress(90)
            
            # Net Pay
            phi_ok = df['PHI_E'].fillna(0) >= PetroConfig.PHI_CUTOFF
            vsh_ok = df['VSH'].fillna(1) <= PetroConfig.VSH_CUTOFF
            sw_ok = df['SW'].fillna(1) <= PetroConfig.SW_CUTOFF
            
            if not df['RT'].notna().any():
                df['IS_PAY'] = phi_ok & vsh_ok
            else:
                df['IS_PAY'] = phi_ok & vsh_ok & sw_ok
            
            net_pay = df['IS_PAY'].sum()
            
            progress.progress(100)
            st.write(f"✓ Net pay: {net_pay} muestras ({100*net_pay/len(df):.1f}%)")
            
            # ======================================================
            # RESUMEN ESTADÍSTICO
            # ======================================================
            st.subheader("📊 Resumen Estadístico")
            # ======================================================
            # RESUMEN ESTADÍSTICO
            # ======================================================
            st.subheader("📊 Resumen Estadístico")
            
            stats_dict = {}
            
            for col, label in [('PHI_E', 'Porosidad Efectiva'), 
                               ('VSH', 'Volumen de Arcilla'),
                               ('SW', 'Saturación de Agua'),
                               ('PERM', 'Permeabilidad')]:
                if df[col].notna().any():
                    valid_data = df[df[col] > 0][col] if col == 'PERM' else df[col]
                    valid_data = valid_data[valid_data.notna()]
                    
                    if len(valid_data) > 0:
                        stats_dict[label] = {
                            'mean': valid_data.mean(),
                            'min': valid_data.min(),
                            'max': valid_data.max(),
                            'valid': len(valid_data)
                        }
                    else:
                        stats_dict[label] = {
                            'mean': None,
                            'min': None,
                            'max': None,
                            'valid': 0
                        }
            
            # Mostrar tabla de estadísticas
            stats_df = pd.DataFrame({
                'Propiedad': stats_dict.keys(),
                'Promedio': [f"{v['mean']:.4f}" if v['mean'] is not None else "-" for v in stats_dict.values()],
                'Mínimo': [f"{v['min']:.4f}" if v['min'] is not None else "-" for v in stats_dict.values()],
                'Máximo': [f"{v['max']:.4f}" if v['max'] is not None else "-" for v in stats_dict.values()],
                'Válidos': [v['valid'] for v in stats_dict.values()],
            })
            
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Distribución litológica - Mejorada
            if 'LITOLOGIA' in df.columns:
                st.subheader("🪨 Distribución Litológica")
                lith_counts = df['LITOLOGIA'].value_counts()
                lith_pct = (lith_counts / len(df) * 100).round(1)
                
                lith_df = pd.DataFrame({
                    'Litología': lith_counts.index,
                    'Muestras': lith_counts.values,
                    'Porcentaje (%)': lith_pct.values
                })
                
                col1, col2 = st.columns([1, 1.5])
                with col1:
                    st.dataframe(lith_df, use_container_width=True, hide_index=True)
                
                with col2:
                    fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')
                    colors_pie = [LITHO_COLORS.get(lith, '#CCCCCC') for lith in lith_counts.index]
                    wedges, texts, autotexts = ax.pie(
                        lith_counts.values, 
                        labels=lith_counts.index, 
                        autopct='%1.1f%%',
                        colors=colors_pie, 
                        startangle=90,
                        textprops={'fontsize': 9}
                    )
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    ax.set_title('Composición Litológica', fontweight='bold', fontsize=11, pad=10)
                    plt.tight_layout()
                    st.pyplot(fig, use_container_width=True)
            
            
            # ======================================================
            # VISUALIZACIÓN DEL REGISTRO
            # ======================================================
            st.subheader("📈 Registro Petrofísico")
            
            depth_min_data, depth_max_data = get_valid_data_range(df)
            depth_min = depth_min_data
            depth_max = depth_max_data
            
            # Crear figura simple con 8 subplots - Tamaño optimizado
            fig, axes = plt.subplots(1, 8, figsize=(18, 8), sharey='row', facecolor='white')
            fig.suptitle(f"Registro: {well_name.upper().replace('.LAS', '')}", 
                        fontsize=14, fontweight='bold', y=0.98)
            
            # Configurar límites Y para todos los tracks
            for i, ax in enumerate(axes):
                ax.set_ylim(depth_max, depth_min)
                ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
                ax.tick_params(labelsize=7)
                ax.margins(0)
                if i > 0:
                    ax.set_yticklabels([])
                if i == 0:
                    ax.set_ylabel('Profundidad (ft)', fontsize=9, fontweight='bold')
            
            # Track 1: GR
            ax = axes[0]
            valid_gr = df['GR'].notna()
            if valid_gr.any():
                ax.plot(df.loc[valid_gr, 'GR'], df.loc[valid_gr, 'DEPTH_FT'], 'k-', linewidth=1.5)
                ax.fill_betweenx(df.loc[valid_gr, 'DEPTH_FT'], 0, df.loc[valid_gr, 'GR'],
                               where=(df.loc[valid_gr, 'GR'] <= 75), color='yellow', alpha=0.4)
                ax.set_xlim(0, 150)
            else:
                ax.set_xlim(0, 150)
            ax.set_title('GR', fontweight='bold', fontsize=9)
            ax.set_xlabel('API', fontsize=7)
            
            # Track 2: RHOB
            ax = axes[1]
            valid_rhob = df['RHOB'].notna()
            if valid_rhob.any():
                ax.plot(df.loc[valid_rhob, 'RHOB'], df.loc[valid_rhob, 'DEPTH_FT'], 'r-', linewidth=1.5)
                ax.fill_betweenx(df.loc[valid_rhob, 'DEPTH_FT'], 1.95, df.loc[valid_rhob, 'RHOB'],
                               where=(df.loc[valid_rhob, 'RHOB'] >= 1.95), color='red', alpha=0.2)
                ax.set_xlim(2.95, 1.95)
            else:
                ax.set_xlim(2.95, 1.95)
            ax.set_title('RHOB', fontweight='bold', fontsize=9, color='red')
            ax.set_xlabel('g/cc', fontsize=7)
            
            # Track 3: NPHI
            ax = axes[2]
            valid_nphi = df['NPHI'].notna()
            if valid_nphi.any():
                ax.plot(df.loc[valid_nphi, 'NPHI'], df.loc[valid_nphi, 'DEPTH_FT'], 'b-', linewidth=1.5)
                ax.fill_betweenx(df.loc[valid_nphi, 'DEPTH_FT'], -0.15, df.loc[valid_nphi, 'NPHI'],
                               where=(df.loc[valid_nphi, 'NPHI'] >= -0.15), color='blue', alpha=0.2)
                ax.set_xlim(0.45, -0.15)
            else:
                ax.set_xlim(0.45, -0.15)
            ax.set_title('NPHI', fontweight='bold', fontsize=9, color='blue')
            ax.set_xlabel('v/v', fontsize=7)
            
            # Track 4: Resistividad - Todas las curvas disponibles
            ax = axes[3]
            
            # Definir colores y estilos para cada tipo de resistividad
            res_styles = {
                'RT': {'color': 'red', 'linestyle': '-', 'linewidth': 2.0, 'label': 'RT (Deep)'},
                'RM_RES': {'color': 'orange', 'linestyle': '-', 'linewidth': 1.5, 'label': 'RM (Medium)'},
                'RXOS': {'color': 'blue', 'linestyle': '--', 'linewidth': 1.5, 'label': 'RXOS (Shallow)'},
                'RMC': {'color': 'purple', 'linestyle': ':', 'linewidth': 1.2, 'label': 'RMC (Mud Cake)'},
                'RMUD': {'color': 'green', 'linestyle': '-.', 'linewidth': 1.2, 'label': 'RMUD (Mud)'},
                'RW': {'color': 'brown', 'linestyle': ':', 'linewidth': 1.0, 'label': 'RW (Formation Water)'},
            }
            
            # Plotear todas las resistividades disponibles
            plotted = False
            all_res_data = []
            
            for res_type, style in res_styles.items():
                if res_type in df.columns:
                    valid = df[res_type].notna()
                    if valid.any():
                        res_valid = df.loc[valid, res_type]
                        depth_res = df.loc[valid, 'DEPTH_FT']
                        
                        # Filtrar valores > 0.1 para escala logarítmica
                        mask = res_valid > 0.1
                        if mask.any():
                            ax.semilogx(res_valid[mask], depth_res[mask], 
                                       color=style['color'], linestyle=style['linestyle'],
                                       linewidth=style['linewidth'], label=style['label'], alpha=0.8)
                            all_res_data.extend(res_valid[mask].values)
                            plotted = True
            
            if plotted:
                # Calcular límites dinámicos basado en TODOS los datos
                all_res_array = np.array(all_res_data)
                all_res_array = all_res_array[all_res_array > 0.1]
                
                if len(all_res_array) > 0:
                    res_min = all_res_array.min()
                    res_max = all_res_array.max()
                    
                    if res_max / res_min < 100:
                        x_min = max(0.1, res_min / 10)
                        x_max = min(10000, res_max * 10)
                    else:
                        x_min = max(0.1, res_min / 2)
                        x_max = min(10000, res_max * 2)
                    
                    ax.set_xlim(x_min, x_max)
                    
                    # Líneas de referencia
                    ref_lines = [0.2, 1, 2, 10, 20, 100, 200, 1000, 2000]
                    for ref_val in ref_lines:
                        if x_min < ref_val < x_max:
                            ax.axvline(x=ref_val, color='gray', linestyle=':', 
                                      linewidth=0.5, alpha=0.2)
            else:
                ax.set_xlim(0.1, 1000)
            
            ax.grid(True, alpha=0.3, which='both')
            ax.legend(loc='upper right', fontsize=5, ncol=2)
            ax.set_title('RESISTIVITY', fontweight='bold', fontsize=9, color='darkred')
            ax.set_xlabel('ohm-m', fontsize=7)
            
            # Track 5: Porosidad
            ax = axes[4]
            valid_phi = df['PHI_E'].notna()
            if valid_phi.any():
                ax.plot(df.loc[valid_phi, 'PHI_E'], df.loc[valid_phi, 'DEPTH_FT'], 'c-', linewidth=1.5)
                ax.axvline(PetroConfig.PHI_CUTOFF, color='r', linestyle='--', alpha=0.7, linewidth=1.5)
                ax.fill_betweenx(df.loc[valid_phi, 'DEPTH_FT'], 0, df.loc[valid_phi, 'PHI_E'],
                               where=(df.loc[valid_phi, 'PHI_E'] >= PetroConfig.PHI_CUTOFF),
                               color='cyan', alpha=0.3)
                ax.set_xlim(-0.02, 0.45)
            else:
                ax.set_xlim(-0.02, 0.45)
            ax.set_title('PHI_E', fontweight='bold', fontsize=9, color='cyan')
            ax.set_xlabel('v/v', fontsize=7)
            
            # Track 6: VSH
            ax = axes[5]
            valid_vsh = df['VSH'].notna()
            if valid_vsh.any():
                ax.plot(df.loc[valid_vsh, 'VSH'], df.loc[valid_vsh, 'DEPTH_FT'], 'brown', linewidth=1.5)
                ax.axvline(PetroConfig.VSH_CUTOFF, color='r', linestyle='--', alpha=0.7, linewidth=1.5)
                ax.fill_betweenx(df.loc[valid_vsh, 'DEPTH_FT'], 0, df.loc[valid_vsh, 'VSH'],
                               where=(df.loc[valid_vsh, 'VSH'] <= PetroConfig.VSH_CUTOFF),
                               color='tan', alpha=0.3)
                ax.set_xlim(0, 1)
            else:
                ax.set_xlim(0, 1)
            ax.set_title('VSH', fontweight='bold', fontsize=9)
            ax.set_xlabel('v/v', fontsize=7)
            
            # Track 7: Net Pay
            ax = axes[6]
            pay_array = df['IS_PAY'].astype(int).values.reshape(-1, 1)
            pay_cmap = ListedColormap(['#F0F0F0', '#32CD32'])
            im = ax.imshow(pay_array, aspect='auto', cmap=pay_cmap, origin='upper',
                     extent=[0, 1, depth_max, depth_min], interpolation='nearest')
            ax.set_xticks([])
            ax.set_xlim(-0.5, 1.5)
            ax.set_title('NET PAY', fontweight='bold', fontsize=9, color='#32CD32')
            ax.grid(False)
            
            # Track 8: Litología
            ax = axes[7]
            litho_unique = df['LITOLOGIA'].unique()
            litho_mapping = {lith: i for i, lith in enumerate(litho_unique)}
            lith_num = df['LITOLOGIA'].map(litho_mapping)
            colors_present = [LITHO_COLORS.get(lith, '#CCCCCC') for lith in litho_unique]
            cmap = ListedColormap(colors_present)
            img = np.array(lith_num).reshape(-1, 1)
            ax.imshow(img, aspect='auto', cmap=cmap, origin='upper',
                     extent=[0, 1, depth_max, depth_min], interpolation='nearest')
            ax.set_xticks([])
            ax.set_xlim(-0.5, 1.5)
            ax.set_title('LITOLOGÍA', fontweight='bold', fontsize=9)
            ax.grid(False)
            
            # Leyenda de litología
            legend_patches = [mpatches.Patch(color=LITHO_COLORS.get(lith, '#CCCCCC'),
                                             label=lith.replace('_', ' ').title())
                            for lith in litho_unique]
            ax.legend(handles=legend_patches, loc='lower left', fontsize=6, framealpha=0.9)
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            
            # ======================================================
            # EXPORTACIÓN
            # ======================================================
            st.subheader("💾 Exportación de Resultados")
            
            col1, col2, col3 = st.columns(3)
            
            # CSV
            with col1:
                csv_data = df[['DEPTH_FT', 'GR', 'RHOB', 'NPHI', 'RT', 
                              'VSH', 'PHI_T', 'PHI_E', 'SW', 'PERM',
                              'LITOLOGIA', 'RHO_MATRIX', 'IS_PAY']].copy()
                csv_str = csv_data.to_csv(index=False)
                csv_bytes = csv_str.encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_bytes,
                    file_name=f"{well_name}_results.csv",
                    mime="text/csv",
                    key=f"csv_{file_idx}"
                )
            
            # Excel
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    csv_data.to_excel(writer, sheet_name='Datos', index=False)
                excel_bytes = excel_buffer.getvalue()
                st.download_button(
                    label="📊 Descargar Excel",
                    data=excel_bytes,
                    file_name=f"{well_name}_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_{file_idx}"
                )
            
            # PDF
            with col3:
                config_dict = {
                    'DOMINANT_MATRIX': PetroConfig.DOMINANT_MATRIX,
                    'DOMINANT_RHO': PetroConfig.DOMINANT_RHO,
                    'A': PetroConfig.A,
                    'M': PetroConfig.M,
                    'N': PetroConfig.N,
                    'RW': PetroConfig.RW,
                    'PHI_CUTOFF': PetroConfig.PHI_CUTOFF,
                    'VSH_CUTOFF': PetroConfig.VSH_CUTOFF,
                    'SW_CUTOFF': PetroConfig.SW_CUTOFF,
                }
                
                pdf_buffer = create_pdf_report(df, well_name, config_dict, stats_dict, available_curves)
                pdf_bytes = pdf_buffer.getvalue()
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"{well_name}_analysis.pdf",
                    mime="application/pdf",
                    key=f"pdf_{file_idx}"
                )
            
            # Almacenar datos del pozo para exportación batch
            all_wells_data.append({
                'df': df,
                'well_name': well_name,
                'config': config_dict,
                'stats': stats_dict,
                'curve_mapping': available_curves
            })
            
            st.success("✅ Procesamiento completado")
            
            # Limpiar archivo temporal
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        except Exception as e:
            st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
            # Limpiar archivo temporal en caso de error
            import os
            temp_path = f'/tmp/temp_well_{file_idx}.las'
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # ======================================================
    # DESCARGAS POR LOTE (BATCH)
    # ======================================================
    if all_wells_data:
        st.markdown("---")
        st.subheader("📦 Exportación Consolidada (Todos los Pozos)")
        
        col1, col2 = st.columns(2)
        
        # PDF consolidado
        with col1:
            if st.button("📄 Descargar Reporte PDF Consolidado", key="btn_pdf_batch"):
                pdf_buffer = create_pdf_batch_report(all_wells_data)
                st.download_button(
                    label="📥 Descargar PDF Consolidado",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Analisis_Consolidado_{len(all_wells_data)}_pozos.pdf",
                    mime="application/pdf",
                    key="download_pdf_batch"
                )
        
        # CSV consolidado
        with col2:
            if st.button("📊 Descargar CSV Consolidado", key="btn_csv_batch"):
                # Concatenar todos los DataFrames
                combined_df = pd.concat([
                    well['df'][['DEPTH_FT', 'GR', 'RHOB', 'NPHI', 'RT', 
                               'VSH', 'PHI_T', 'PHI_E', 'SW', 'PERM',
                               'LITOLOGIA', 'RHO_MATRIX', 'IS_PAY']].copy()
                    for well in all_wells_data
                ], keys=[well['well_name'] for well in all_wells_data])
                
                csv_str = combined_df.to_csv()
                csv_bytes = csv_str.encode('utf-8')
                st.download_button(
                    label="📥 Descargar CSV Consolidado",
                    data=csv_bytes,
                    file_name=f"Análisis_Consolidado_{len(all_wells_data)}_pozos.csv",
                    mime="text/csv",
                    key="download_csv_batch"
                )
        
        st.success(f"✅ {len(all_wells_data)} pozo(s) procesado(s) exitosamente")

else:
    st.info("👆 Carga archivos LAS para comenzar")
    st.markdown("""
    ### 📋 Características:
    
    - ✅ **Lectura automática de LAS** - Detecta columnas de profundidad
    - ✅ **Explorador de datos** - Visualiza y analiza columnas del archivo
    - ✅ **Selector de columnas** - Elige qué datos inspeccionar
    - ✅ **Procesamiento batch** - Múltiples archivos simultáneamente
    - ✅ **Mapeo flexible** - 40+ alias de nombres de curvas
    - ✅ **Detección de matriz** - Identifica automáticamente ARENISCA/CALIZA/DOLOMITA
    - ✅ **Cálculos completos** - VSH, Porosidad, Saturación, Permeabilidad
    - ✅ **Visualización profesional** - Registro de 8 tracks
    - ✅ **Exportación múltiple** - CSV, Excel, PDF
    
    ### 🔧 Parámetros ajustables en el panel lateral
    """)
