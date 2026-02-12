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
import numpy as np
from PIL import Image as PILImage


def generate_8track_figure(df, LITHO_COLORS):
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
        fig.suptitle(f"Registro Petrofísico", fontsize=12, fontweight='bold', y=0.98)
        
        # Configurar límites Y para todos los tracks
        for i, ax in enumerate(axes):
            ax.set_ylim(depth_max, depth_min)
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.tick_params(labelsize=6)
            ax.margins(0)
            if i > 0:
                ax.set_yticklabels([])
            if i == 0:
                ax.set_ylabel('Profundidad (ft)', fontsize=8, fontweight='bold')
        
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
        ax.set_title('GR\n(API)', fontweight='bold', fontsize=8)
        
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
        ax.set_title('RHOB\n(g/cc)', fontweight='bold', fontsize=8, color='red')
        
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
        ax.set_title('NPHI\n(v/v)', fontweight='bold', fontsize=8, color='blue')
        
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
        ax.set_title('RES\n(ohm-m)', fontweight='bold', fontsize=8, color='darkred')
        
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
        ax.set_title('PHI_E\n(v/v)', fontweight='bold', fontsize=8, color='cyan')
        
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
        ax.set_title('VSH\n(v/v)', fontweight='bold', fontsize=8)
        
        # Track 7: Net Pay
        ax = axes[6]
        pay_array = df['IS_PAY'].astype(int).values.reshape(-1, 1)
        pay_cmap = ListedColormap(['#F0F0F0', '#32CD32'])
        im = ax.imshow(pay_array, aspect='auto', cmap=pay_cmap, origin='upper',
                 extent=[0, 1, depth_max, depth_min], interpolation='nearest')
        ax.set_xticks([])
        ax.set_xlim(-0.5, 1.5)
        ax.set_title('NET PAY', fontweight='bold', fontsize=8, color='#32CD32')
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
        ax.set_title('LITOLOGÍA', fontweight='bold', fontsize=8)
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


def create_pdf_report(df, well_name, config, stats, curve_mapping=None, dominant_matrix_info=None):
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
    elements.append(Paragraph(f"ANÁLISIS PETROFÍSICO", title_style))
    elements.append(Paragraph(f"Pozo: {well_name.upper()}", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # ===== SECCIÓN 1: IDENTIFICACIÓN DE PROFUNDIDAD =====
    elements.append(Paragraph("1. IDENTIFICACIÓN DE PROFUNDIDAD", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    depth_data = [
        ['PARÁMETRO', 'VALOR'],
        ['Profundidad Inicial (ft)', f"{df['DEPTH_FT'].min():.1f}"],
        ['Profundidad Final (ft)', f"{df['DEPTH_FT'].max():.1f}"],
        ['Intervalo Total (ft)', f"{df['DEPTH_FT'].max() - df['DEPTH_FT'].min():.1f}"],
        ['Total de Muestras', f"{len(df)}"],
        ['Espaciamiento (ft)', f"{(df['DEPTH_FT'].max() - df['DEPTH_FT'].min()) / len(df):.4f}"],
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
        elements.append(Paragraph("2. MAPEO DE CURVAS DISPONIBLES", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        curve_data = [['CURVA ESTÁNDAR', 'COLUMNA ORIGINAL', 'MUESTRAS VÁLIDAS']]
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
    elements.append(Paragraph("3. DETECCIÓN DE MATRIZ DOMINANTE", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    matrix_data = [
        ['PARÁMETRO', 'VALOR'],
        ['Matriz Dominante', config.get('DOMINANT_MATRIX', 'N/A')],
        ['Densidad de Matriz (g/cc)', f"{config.get('DOMINANT_RHO', 0):.3f}"],
        ['Parámetro A (Archie)', f"{config.get('A', 0):.2f}"],
        ['Parámetro M (Archie)', f"{config.get('M', 0):.2f}"],
        ['Parámetro N (Archie)', f"{config.get('N', 0):.2f}"],
        ['Rw (ohm-m)', f"{config.get('RW', 0):.3f}"],
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
    elements.append(Paragraph("4. PARÁMETROS DE CÁLCULO (CUTOFFS)", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    calc_data = [
        ['PARÁMETRO', 'VALOR'],
        ['Cutoff Porosidad Mínima (%)', f"{config.get('PHI_CUTOFF', 0)*100:.1f}"],
        ['Cutoff VSH Máximo (%)', f"{config.get('VSH_CUTOFF', 0)*100:.1f}"],
        ['Cutoff Sw Máximo (%)', f"{config.get('SW_CUTOFF', 0)*100:.1f}"],
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
    elements.append(Paragraph("5. RESUMEN ESTADÍSTICO", heading_style))
    
    stats_data = [['PROPIEDAD', 'PROMEDIO', 'MÍNIMO', 'MÁXIMO', 'VÁLIDOS']]
    
    for prop_name, prop_data in stats.items():
        stats_data.append([
            prop_name,
            f"{prop_data['mean']:.4f}" if prop_data['mean'] else 'N/A',
            f"{prop_data['min']:.4f}" if prop_data['min'] else 'N/A',
            f"{prop_data['max']:.4f}" if prop_data['max'] else 'N/A',
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
    elements.append(Paragraph("6. REGISTRO PETROFÍSICO", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    try:
        from modules.petrofisica import LITHO_COLORS
        track_buffer = generate_8track_figure(df, LITHO_COLORS)
        if track_buffer:
            track_img = Image(track_buffer, width=7.5*inch, height=3.2*inch)
            elements.append(track_img)
            elements.append(Spacer(1, 0.15*inch))
    except Exception as e:
        print(f"Error agregando registro: {e}")
    
    # ===== SECCIÓN 7: DISTRIBUCIÓN LITOLÓGICA =====
    if 'LITOLOGIA' in df.columns:
        elements.append(Paragraph("7. DISTRIBUCIÓN LITOLÓGICA", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        lith_counts = df['LITOLOGIA'].value_counts()
        lith_data = [['LITOLOGÍA', 'MUESTRAS', 'PORCENTAJE']]
        
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
            
            ax1.set_title('Distribución Litológica (%)', fontweight='bold', fontsize=11, pad=15)
            
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
            ax2.set_xlabel('Número de Muestras', fontsize=10, fontweight='bold')
            ax2.set_title('Muestras por Litología', fontweight='bold', fontsize=11, pad=15)
            
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
        elements.append(Paragraph("8. ZONAS PRODUCTIVAS (NET PAY)", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        net_pay = df['IS_PAY'].sum()
        pct_pay = 100 * net_pay / len(df)
        
        pay_data = [
            ['MÉTRICA', 'VALOR'],
            ['Net Pay (muestras)', str(int(net_pay))],
            ['Porcentaje del intervalo', f"{pct_pay:.1f}%"],
        ]
        
        if net_pay > 0:
            pay_mask = df['IS_PAY']
            if df.loc[pay_mask, 'PHI_E'].notna().any():
                pay_data.append(['Porosidad promedio en pay', 
                               f"{df.loc[pay_mask, 'PHI_E'].mean():.4f}"])
            if df.loc[pay_mask, 'VSH'].notna().any():
                pay_data.append(['VSH promedio en pay', 
                               f"{df.loc[pay_mask, 'VSH'].mean():.4f}"])
            if df.loc[pay_mask, 'SW'].notna().any():
                pay_data.append(['Sw promedio en pay', 
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
        f"<i>Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, 
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
