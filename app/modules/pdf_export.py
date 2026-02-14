# ==========================================================
# MÓDULO: EXPORTACIÓN A PDF
# ==========================================================
import io
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import numpy as np
from PIL import Image as PILImage


PDF_TEXTS = {
    'es': {
        'petrophysical_log': 'Registro Petrofísico',
        'depth_ft': 'Profundidad (ft)',
        'res_title': 'RES\n(ohm·m)',
        'lith_title': 'LITOLOGÍA\n(Tipo)',
        'report_title': 'ANÁLISIS PETROFÍSICO',
        'well': 'Pozo',
        'section_1': '1. IDENTIFICACIÓN DE PROFUNDIDAD',
        'section_2': '2. MAPEO DE CURVAS DISPONIBLES',
        'section_3': '3. DETECCIÓN DE MATRIZ DOMINANTE',
        'section_4': '4. PARÁMETROS DE CÁLCULO (CUTOFFS)',
        'section_5': '5. RESUMEN ESTADÍSTICO',
        'section_6': '6. REGISTRO PETROFÍSICO',
        'section_7': '7. DISTRIBUCIÓN LITOLÓGICA',
        'section_8': '8. ZONAS PRODUCTIVAS (NET PAY)',
        'param': 'PARÁMETRO',
        'value': 'VALOR',
        'depth_start': 'Profundidad Inicial (ft)',
        'depth_end': 'Profundidad Final (ft)',
        'depth_interval': 'Intervalo Total (ft)',
        'samples_total': 'Total de Muestras',
        'spacing': 'Espaciamiento (ft)',
        'std_curve': 'CURVA ESTÁNDAR',
        'orig_column': 'COLUMNA ORIGINAL',
        'valid_samples': 'MUESTRAS VÁLIDAS',
        'dominant_matrix': 'Matriz Dominante',
        'matrix_density': 'Densidad de Matriz (g/cc)',
        'archie_a': 'Parámetro A (Archie)',
        'archie_m': 'Parámetro M (Archie)',
        'archie_n': 'Parámetro N (Archie)',
        'rw': 'Rw (ohm-m)',
        'phi_cutoff': 'Cutoff Porosidad Mínima (%)',
        'vsh_cutoff': 'Cutoff VSH Máximo (%)',
        'sw_cutoff': 'Cutoff Sw Máximo (%)',
        'property': 'PROPIEDAD',
        'mean': 'PROMEDIO',
        'min': 'MÍNIMO',
        'max': 'MÁXIMO',
        'valid': 'VÁLIDOS',
        'lithology': 'LITOLOGÍA',
        'samples': 'MUESTRAS',
        'percentage': 'PORCENTAJE',
        'lith_distribution': 'Distribución Litológica (%)',
        'samples_by_lith': 'Muestras por Litología',
        'samples_count': 'Número de Muestras',
        'metric': 'MÉTRICA',
        'net_pay_samples': 'Net Pay (muestras)',
        'interval_pct': 'Porcentaje del intervalo',
        'avg_phi_pay': 'Porosidad promedio en pay',
        'avg_vsh_pay': 'VSH promedio en pay',
        'avg_sw_pay': 'Sw promedio en pay',
        'generated': 'Reporte generado',
        'na': 'N/A',
    },
    'en': {
        'petrophysical_log': 'Petrophysical Log',
        'depth_ft': 'Depth (ft)',
        'res_title': 'RES\n(ohm·m)',
        'lith_title': 'LITHOLOGY\n(Type)',
        'report_title': 'PETROPHYSICAL ANALYSIS',
        'well': 'Well',
        'section_1': '1. DEPTH IDENTIFICATION',
        'section_2': '2. AVAILABLE CURVE MAPPING',
        'section_3': '3. DOMINANT MATRIX DETECTION',
        'section_4': '4. CALCULATION PARAMETERS (CUTOFFS)',
        'section_5': '5. STATISTICAL SUMMARY',
        'section_6': '6. PETROPHYSICAL LOG',
        'section_7': '7. LITHOLOGY DISTRIBUTION',
        'section_8': '8. PRODUCTIVE ZONES (NET PAY)',
        'param': 'PARAMETER',
        'value': 'VALUE',
        'depth_start': 'Start Depth (ft)',
        'depth_end': 'End Depth (ft)',
        'depth_interval': 'Total Interval (ft)',
        'samples_total': 'Total Samples',
        'spacing': 'Spacing (ft)',
        'std_curve': 'STANDARD CURVE',
        'orig_column': 'ORIGINAL COLUMN',
        'valid_samples': 'VALID SAMPLES',
        'dominant_matrix': 'Dominant Matrix',
        'matrix_density': 'Matrix Density (g/cc)',
        'archie_a': 'A Parameter (Archie)',
        'archie_m': 'M Parameter (Archie)',
        'archie_n': 'N Parameter (Archie)',
        'rw': 'Rw (ohm-m)',
        'phi_cutoff': 'Minimum Porosity Cutoff (%)',
        'vsh_cutoff': 'Maximum VSH Cutoff (%)',
        'sw_cutoff': 'Maximum Sw Cutoff (%)',
        'property': 'PROPERTY',
        'mean': 'MEAN',
        'min': 'MIN',
        'max': 'MAX',
        'valid': 'VALID',
        'lithology': 'LITHOLOGY',
        'samples': 'SAMPLES',
        'percentage': 'PERCENTAGE',
        'lith_distribution': 'Lithology Distribution (%)',
        'samples_by_lith': 'Samples by Lithology',
        'samples_count': 'Number of Samples',
        'metric': 'METRIC',
        'net_pay_samples': 'Net Pay (samples)',
        'interval_pct': 'Interval percentage',
        'avg_phi_pay': 'Average porosity in pay',
        'avg_vsh_pay': 'Average VSH in pay',
        'avg_sw_pay': 'Average Sw in pay',
        'generated': 'Report generated',
        'na': 'N/A',
    },
    'fr': {
        'petrophysical_log': 'Diagraphie pétrophysique',
        'depth_ft': 'Profondeur (ft)',
        'res_title': 'RES\n(ohm·m)',
        'lith_title': 'LITHOLOGIE\n(Type)',
        'report_title': 'ANALYSE PÉTROPHYSIQUE',
        'well': 'Puits',
        'section_1': '1. IDENTIFICATION DE LA PROFONDEUR',
        'section_2': '2. CARTOGRAPHIE DES COURBES DISPONIBLES',
        'section_3': '3. DÉTECTION DE LA MATRICE DOMINANTE',
        'section_4': '4. PARAMÈTRES DE CALCUL (SEUILS)',
        'section_5': '5. RÉSUMÉ STATISTIQUE',
        'section_6': '6. DIAGRAPHIE PÉTROPHYSIQUE',
        'section_7': '7. DISTRIBUTION LITHOLOGIQUE',
        'section_8': '8. ZONES PRODUCTIVES (NET PAY)',
        'param': 'PARAMÈTRE',
        'value': 'VALEUR',
        'depth_start': 'Profondeur initiale (ft)',
        'depth_end': 'Profondeur finale (ft)',
        'depth_interval': 'Intervalle total (ft)',
        'samples_total': 'Total des échantillons',
        'spacing': 'Espacement (ft)',
        'std_curve': 'COURBE STANDARD',
        'orig_column': 'COLONNE ORIGINALE',
        'valid_samples': 'ÉCHANTILLONS VALIDES',
        'dominant_matrix': 'Matrice dominante',
        'matrix_density': 'Densité de matrice (g/cc)',
        'archie_a': 'Paramètre A (Archie)',
        'archie_m': 'Paramètre M (Archie)',
        'archie_n': 'Paramètre N (Archie)',
        'rw': 'Rw (ohm-m)',
        'phi_cutoff': 'Seuil minimum de porosité (%)',
        'vsh_cutoff': 'Seuil maximum VSH (%)',
        'sw_cutoff': 'Seuil maximum Sw (%)',
        'property': 'PROPRIÉTÉ',
        'mean': 'MOYENNE',
        'min': 'MIN',
        'max': 'MAX',
        'valid': 'VALIDES',
        'lithology': 'LITHOLOGIE',
        'samples': 'ÉCHANTILLONS',
        'percentage': 'POURCENTAGE',
        'lith_distribution': 'Distribution lithologique (%)',
        'samples_by_lith': 'Échantillons par lithologie',
        'samples_count': "Nombre d'échantillons",
        'metric': 'MÉTRIQUE',
        'net_pay_samples': 'Net Pay (échantillons)',
        'interval_pct': "Pourcentage de l'intervalle",
        'avg_phi_pay': 'Porosité moyenne en pay',
        'avg_vsh_pay': 'VSH moyenne en pay',
        'avg_sw_pay': 'Sw moyenne en pay',
        'generated': 'Rapport généré',
        'na': 'N/D',
    }
}


def _pdf_t(language, key):
    return PDF_TEXTS.get(language, PDF_TEXTS['es']).get(key, PDF_TEXTS['es'].get(key, key))


def generate_8track_figure(df, LITHO_COLORS, language='es'):
    """Genera figura de 8 tracks para el PDF
    
    Args:
        df: DataFrame con datos petrofísicos
        LITHO_COLORS: Diccionario con colores para litologías
    
    Returns:
        BytesIO object con la imagen PNG
    """
    try:
        from modules.petrofisica import get_valid_data_range
        
        # Obtener rangos de profundidad
        depth_min_data, depth_max_data = get_valid_data_range(df)
        depth_min = depth_min_data
        depth_max = depth_max_data
        
        # Crear figura con 8 subplots - Tamaño optimizado para PDF
        fig, axes = plt.subplots(1, 8, figsize=(16, 7), sharey='row', facecolor='white')
        fig.suptitle(f"{_pdf_t(language, 'petrophysical_log')}", fontsize=12, fontweight='bold', y=1.0)
        
        # Configurar límites Y y escala superior para todos los tracks
        # Calcular intervalo apropiado para los ticks de profundidad
        depth_range = depth_max - depth_min
        if depth_range <= 100:
            major_interval = 10
        elif depth_range <= 500:
            major_interval = 50
        elif depth_range <= 1000:
            major_interval = 100
        elif depth_range <= 2000:
            major_interval = 200
        else:
            major_interval = 500
        
        for i, ax in enumerate(axes):
            ax.set_ylim(depth_max, depth_min)
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.tick_params(axis='y', labelsize=6, left=True, labelleft=(i == 0))
            ax.tick_params(axis='x', labelsize=5, top=True, bottom=False, labeltop=True, labelbottom=False)
            ax.xaxis.set_ticks_position('top')
            ax.yaxis.set_major_locator(MultipleLocator(major_interval))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax.margins(0)
            if i == 0:
                ax.set_ylabel(_pdf_t(language, 'depth_ft'), fontsize=8, fontweight='bold')
                ax.tick_params(axis='y', which='major', labelsize=6, left=True, labelleft=True)
                ax.tick_params(axis='y', which='minor', left=True, length=2)
        
        # Track 1: GR
        ax = axes[0]
        valid_gr = df['GR'].notna()
        if valid_gr.any():
            ax.plot(df.loc[valid_gr, 'GR'], df.loc[valid_gr, 'DEPTH_FT'], 'k-', linewidth=1.2)
            ax.fill_betweenx(df.loc[valid_gr, 'DEPTH_FT'], 0, df.loc[valid_gr, 'GR'],
                           where=(df.loc[valid_gr, 'GR'] <= 75), color='yellow', alpha=0.4)
            ax.set_xlim(0, 150)
        else:
            ax.set_xlim(0, 150)
        ax.set_title('GR\n(API)', fontweight='bold', fontsize=8, pad=16)
        
        # Track 2: RHOB
        ax = axes[1]
        valid_rhob = df['RHOB'].notna()
        if valid_rhob.any():
            ax.plot(df.loc[valid_rhob, 'RHOB'], df.loc[valid_rhob, 'DEPTH_FT'], 'r-', linewidth=1.2)
            ax.fill_betweenx(df.loc[valid_rhob, 'DEPTH_FT'], 1.95, df.loc[valid_rhob, 'RHOB'],
                           where=(df.loc[valid_rhob, 'RHOB'] >= 1.95), color='red', alpha=0.2)
            ax.set_xlim(2.95, 1.95)
        else:
            ax.set_xlim(2.95, 1.95)
        ax.set_title('RHOB\n(g/cc)', fontweight='bold', fontsize=8, color='red', pad=16)
        
        # Track 3: NPHI
        ax = axes[2]
        valid_nphi = df['NPHI'].notna()
        if valid_nphi.any():
            ax.plot(df.loc[valid_nphi, 'NPHI'], df.loc[valid_nphi, 'DEPTH_FT'], 'b-', linewidth=1.2)
            ax.fill_betweenx(df.loc[valid_nphi, 'DEPTH_FT'], -0.15, df.loc[valid_nphi, 'NPHI'],
                           where=(df.loc[valid_nphi, 'NPHI'] >= -0.15), color='blue', alpha=0.2)
            ax.set_xlim(0.45, -0.15)
        else:
            ax.set_xlim(0.45, -0.15)
        ax.set_title('NPHI\n(v/v)', fontweight='bold', fontsize=8, color='blue', pad=16)
        
        # Track 4: Resistividad
        ax = axes[3]
        res_styles = {
            'RT': {'color': 'red', 'linestyle': '-', 'linewidth': 1.5, 'label': 'RT'},
            'RM_RES': {'color': 'orange', 'linestyle': '-', 'linewidth': 1.2, 'label': 'RM'},
            'RXOS': {'color': 'blue', 'linestyle': '--', 'linewidth': 1.2, 'label': 'RXOS'},
        }
        
        plotted = False
        all_res_data = []
        
        for res_type, style in res_styles.items():
            if res_type in df.columns:
                valid = df[res_type].notna()
                if valid.any():
                    res_valid = df.loc[valid, res_type]
                    depth_res = df.loc[valid, 'DEPTH_FT']
                    mask = res_valid > 0.1
                    if mask.any():
                        ax.semilogx(res_valid[mask], depth_res[mask], 
                                   color=style['color'], linestyle=style['linestyle'],
                                   linewidth=style['linewidth'], label=style['label'], alpha=0.8)
                        all_res_data.extend(res_valid[mask].values)
                        plotted = True
        
        if plotted:
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
        else:
            ax.set_xlim(0.1, 1000)
        
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(loc='upper right', fontsize=5, ncol=2)
        ax.set_title(_pdf_t(language, 'res_title'), fontweight='bold', fontsize=8, color='darkred', pad=16)
        
        # Track 5: Porosidad
        ax = axes[4]
        valid_phi = df['PHI_E'].notna()
        if valid_phi.any():
            ax.plot(df.loc[valid_phi, 'PHI_E'], df.loc[valid_phi, 'DEPTH_FT'], 'c-', linewidth=1.2)
            ax.fill_betweenx(df.loc[valid_phi, 'DEPTH_FT'], 0, df.loc[valid_phi, 'PHI_E'],
                           where=(df.loc[valid_phi, 'PHI_E'] >= 0.06), color='cyan', alpha=0.3)
            ax.set_xlim(-0.02, 0.45)
        else:
            ax.set_xlim(-0.02, 0.45)
        ax.set_title('PHI_E\n(v/v)', fontweight='bold', fontsize=8, color='darkcyan', pad=16)
        
        # Track 6: VSH
        ax = axes[5]
        valid_vsh = df['VSH'].notna()
        if valid_vsh.any():
            ax.plot(df.loc[valid_vsh, 'VSH'], df.loc[valid_vsh, 'DEPTH_FT'], 'brown', linewidth=1.2)
            ax.fill_betweenx(df.loc[valid_vsh, 'DEPTH_FT'], 0, df.loc[valid_vsh, 'VSH'],
                           where=(df.loc[valid_vsh, 'VSH'] <= 0.5), color='tan', alpha=0.3)
            ax.set_xlim(0, 1)
        else:
            ax.set_xlim(0, 1)
        ax.set_title('VSH\n(v/v)', fontweight='bold', fontsize=8, pad=16)
        
        # Track 7: Net Pay
        ax = axes[6]
        pay_array = df['IS_PAY'].astype(int).values.reshape(-1, 1)
        pay_cmap = ListedColormap(['#F0F0F0', '#32CD32'])
        im = ax.imshow(pay_array, aspect='auto', cmap=pay_cmap, origin='upper',
                 extent=[0, 1, depth_max, depth_min], interpolation='nearest')
        ax.set_xticks([])
        ax.set_xlim(-0.5, 1.5)
        ax.set_title('NET PAY\n(Flag)', fontweight='bold', fontsize=8, color='#32CD32', pad=16)
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
        ax.set_title(_pdf_t(language, 'lith_title'), fontweight='bold', fontsize=8, pad=16)
        ax.grid(False)
        
        # Leyenda de litología
        legend_patches = [mpatches.Patch(color=LITHO_COLORS.get(lith, '#CCCCCC'),
                                         label=lith.replace('_', ' ').title()[:15])
                        for lith in litho_unique]
        ax.legend(handles=legend_patches, loc='lower left', fontsize=6, framealpha=0.9)
        
        plt.tight_layout()
        
        # Guardar imagen
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    except Exception as e:
        print(f"Error generando 8 tracks: {e}")
        return None


def create_pdf_report(df, well_name, config, stats, curve_mapping=None, dominant_matrix_info=None, language='es'):
    """Crea reporte PDF completo con análisis petrofísico
    
    Args:
        df: DataFrame con datos del pozo
        well_name: Nombre del pozo
        config: Diccionario con configuración petrofísica
        stats: Diccionario con estadísticas
        curve_mapping: Diccionario con mapeo de curvas disponibles
        dominant_matrix_info: Diccionario con info de matriz dominante
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    t = lambda key: _pdf_t(language, key)
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Título
    elements.append(Paragraph(f"{t('report_title')}", title_style))
    elements.append(Paragraph(f"{t('well')}: {well_name.upper()}", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 1: IDENTIFICACIÓN DE PROFUNDIDAD =====
    elements.append(Paragraph(t('section_1'), heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    depth_data = [
        [t('param'), t('value')],
        [t('depth_start'), f"{df['DEPTH_FT'].min():.1f}"],
        [t('depth_end'), f"{df['DEPTH_FT'].max():.1f}"],
        [t('depth_interval'), f"{df['DEPTH_FT'].max() - df['DEPTH_FT'].min():.1f}"],
        [t('samples_total'), f"{len(df)}"],
        [t('spacing'), f"{(df['DEPTH_FT'].max() - df['DEPTH_FT'].min()) / len(df):.4f}"],
    ]
    
    depth_table = Table(depth_data, colWidths=[3*inch, 2*inch])
    depth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(depth_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 2: MAPEO DE CURVAS =====
    if curve_mapping:
        elements.append(Paragraph(t('section_2'), heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        curve_data = [[t('std_curve'), t('orig_column'), t('valid_samples')]]
        for standard, original in sorted(curve_mapping.items()):
            valid_count = df[standard].notna().sum() if standard in df.columns else 0
            pct_valid = 100 * valid_count / len(df) if len(df) > 0 else 0
            curve_data.append([
                standard,
                original,
                f"{valid_count} ({pct_valid:.1f}%)"
            ])
        
        curve_table = Table(curve_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        curve_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(curve_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 3: DETECCIÓN DE MATRIZ =====
    elements.append(Paragraph(t('section_3'), heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    matrix_data = [
        [t('param'), t('value')],
        [t('dominant_matrix'), config.get('DOMINANT_MATRIX', t('na'))],
        [t('matrix_density'), f"{config.get('DOMINANT_RHO', 0):.3f}"],
        [t('archie_a'), f"{config.get('A', 0):.2f}"],
        [t('archie_m'), f"{config.get('M', 0):.2f}"],
        [t('archie_n'), f"{config.get('N', 0):.2f}"],
        [t('rw'), f"{config.get('RW', 0):.3f}"],
    ]
    
    matrix_table = Table(matrix_data, colWidths=[3*inch, 2*inch])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(matrix_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 4: CÁLCULOS PETROFÍSICOS =====
    elements.append(Paragraph(t('section_4'), heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    calc_data = [
        [t('param'), t('value')],
        [t('phi_cutoff'), f"{config.get('PHI_CUTOFF', 0)*100:.1f}"],
        [t('vsh_cutoff'), f"{config.get('VSH_CUTOFF', 0)*100:.1f}"],
        [t('sw_cutoff'), f"{config.get('SW_CUTOFF', 0)*100:.1f}"],
    ]
    
    calc_table = Table(calc_data, colWidths=[3*inch, 2*inch])
    calc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(calc_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 5: RESUMEN ESTADÍSTICO =====
    elements.append(Paragraph(t('section_5'), heading_style))
    
    stats_data = [[t('property'), t('mean'), t('min'), t('max'), t('valid')]]
    
    for prop_name, prop_data in stats.items():
        stats_data.append([
            prop_name,
            f"{prop_data['mean']:.4f}" if prop_data['mean'] else t('na'),
            f"{prop_data['min']:.4f}" if prop_data['min'] else t('na'),
            f"{prop_data['max']:.4f}" if prop_data['max'] else t('na'),
            f"{prop_data['valid']}"
        ])
    
    stats_table = Table(stats_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 6: REGISTRO PETROFÍSICO (8 TRACKS) =====
    elements.append(Paragraph(t('section_6'), heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    try:
        from modules.petrofisica import LITHO_COLORS
        track_buffer = generate_8track_figure(df, LITHO_COLORS, language=language)
        if track_buffer:
            track_img = Image(track_buffer, width=7.5*inch, height=3.2*inch)
            elements.append(track_img)
            elements.append(Spacer(1, 0.15*inch))
    except Exception as e:
        print(f"Error agregando registro: {e}")
    
    # ===== SECCIÓN 7: DISTRIBUCIÓN LITOLÓGICA =====
    if 'LITOLOGIA' in df.columns:
        elements.append(Paragraph(t('section_7'), heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        lith_counts = df['LITOLOGIA'].value_counts()
        lith_data = [[t('lithology'), t('samples'), t('percentage')]]
        
        for lith, count in lith_counts.items():
            pct = 100 * count / len(df)
            lith_data.append([
                lith.replace('_', ' ').title(),
                str(int(count)),
                f"{pct:.1f}%"
            ])
        
        lith_table = Table(lith_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        lith_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(lith_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Agregar gráficos de distribución litológica mejorados
        try:
            from reportlab.lib.colors import HexColor
            
            # Crear figura con mejor dimensionamiento
            fig = plt.figure(figsize=(12, 5), facecolor='white')
            
            # Colores para litologías
            litho_colors_custom = {
                'ARENISCA': '#FFE17F',
                'ARENISCA_ARCILLOSA': '#D4AC0D',
                'LUTITA': '#808080',
                'CALIZA': '#87CEEB',
                'CARBONATO': '#87CEEB',
                'DOLOMITA': '#FFB6C1',
                'CONGLOMERADO': '#CD853F',
            }
            
            lith_unique = lith_counts.index.tolist()
            colors_plot = [litho_colors_custom.get(lith, '#CCCCCC') for lith in lith_unique]
            
            # Subplot 1: Pie chart con leyenda separada
            ax1 = plt.subplot(1, 2, 1)
            
            # Crear pie chart sin etiquetas (solo con porcentajes pequeños)
            wedges, texts, autotexts = ax1.pie(lith_counts.values, 
                                               colors=colors_plot,
                                               autopct='%1.0f%%',
                                               startangle=90,
                                               textprops={'fontsize': 8, 'weight': 'bold'})
            
            ax1.set_title(t('lith_distribution'), fontweight='bold', fontsize=11, pad=15)
            
            # Hacer el texto de porcentajes más legible
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            # Crear leyenda fuera del gráfico
            legend_labels = [f"{l.replace('_', ' ').title()}" for l in lith_unique]
            ax1.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), 
                      fontsize=9, frameon=True, fancybox=True)
            
            # Subplot 2: Gráfico de barras horizontal mejorado
            ax2 = plt.subplot(1, 2, 2)
            
            lith_sorted = lith_counts.sort_values(ascending=True)
            colors_sorted = [colors_plot[lith_unique.index(lith)] for lith in lith_sorted.index]
            
            bars = ax2.barh(range(len(lith_sorted)), lith_sorted.values, 
                           color=colors_sorted, edgecolor='black', linewidth=1.2)
            
            # Etiquetas y títulos
            ax2.set_yticks(range(len(lith_sorted)))
            ax2.set_yticklabels([l.replace('_', ' ').title() for l in lith_sorted.index], 
                               fontsize=9, fontweight='bold')
            ax2.set_xlabel(t('samples_count'), fontsize=10, fontweight='bold')
            ax2.set_title(t('samples_by_lith'), fontweight='bold', fontsize=11, pad=15)
            
            # Grid y mejoras visuales
            ax2.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
            ax2.set_axisbelow(True)
            
            # Añadir valores claramente en las barras (al final)
            for i, (bar, val) in enumerate(zip(bars, lith_sorted.values)):
                ax2.text(val + max(lith_sorted.values)*0.01, i, f'{int(val)}', 
                        va='center', fontsize=9, fontweight='bold')
            
            # Mejorar espacios
            plt.tight_layout()
            
            # Guardar imagen con alta resolución
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight', facecolor='white')
            img_buffer.seek(0)
            plt.close()
            
            # Agregar imagen al PDF con mejor tamaño
            litho_img = Image(img_buffer, width=7.0*inch, height=3.0*inch)
            elements.append(litho_img)
            elements.append(Spacer(1, 0.15*inch))
            
        except Exception as e:
            pass
    
    # ===== SECCIÓN 8: ZONAS PRODUCTIVAS (NET PAY) =====
    if 'IS_PAY' in df.columns:
        elements.append(Paragraph(t('section_8'), heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        net_pay = df['IS_PAY'].sum()
        pct_pay = 100 * net_pay / len(df)
        
        pay_data = [
            [t('metric'), t('value')],
            [t('net_pay_samples'), str(int(net_pay))],
            [t('interval_pct'), f"{pct_pay:.1f}%"],
        ]
        
        if net_pay > 0:
            pay_mask = df['IS_PAY']
            if df.loc[pay_mask, 'PHI_E'].notna().any():
                pay_data.append([t('avg_phi_pay'), 
                               f"{df.loc[pay_mask, 'PHI_E'].mean():.4f}"])
            if df.loc[pay_mask, 'VSH'].notna().any():
                pay_data.append([t('avg_vsh_pay'), 
                               f"{df.loc[pay_mask, 'VSH'].mean():.4f}"])
            if df.loc[pay_mask, 'SW'].notna().any():
                pay_data.append([t('avg_sw_pay'), 
                               f"{df.loc[pay_mask, 'SW'].mean():.4f}"])
        
        pay_table = Table(pay_data, colWidths=[3*inch, 2*inch])
        pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(pay_table)
    
    # Pie
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        f"<i>{t('generated')}: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, 
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
