# ==========================================================
# MÓDULO: EXPORTACIÓN BATCH A PDF
# ==========================================================
import io
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import numpy as np


def create_pdf_batch_report(wells_data):
    """Crea un reporte PDF consolidado con reportes completos de múltiples pozos
    
    Args:
        wells_data: Lista de diccionarios con datos de cada pozo
                   [{'df': df, 'well_name': str, 'config': dict, 'stats': dict, 'curve_mapping': dict}, ...]
    """
    
    from .pdf_export import generate_8track_figure
    from .petrofisica import LITHO_COLORS
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    well_title_style = ParagraphStyle(
        'WellTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.white,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#1f77b4'),
        borderPadding=10
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
    
    # PORTADA: Título consolidado
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("ANÁLISIS PETROFÍSICO", main_title_style))
    elements.append(Paragraph("REPORTE CONSOLIDADO DE POZOS", main_title_style))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Total: {len(wells_data)} Pozos", ParagraphStyle(
        'SubTitle', parent=styles['Normal'], fontSize=14, 
        alignment=TA_CENTER, textColor=colors.HexColor('#666666')
    )))
    elements.append(Spacer(1, 0.4*inch))
    
    # Resumen general
    elements.append(Paragraph("RESUMEN GENERAL DE POZOS", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    summary_data = [['POZO', 'PROF. INI. (FT)', 'PROF. FIN. (FT)', 'MUESTRAS', 'MATRIZ', 'NET PAY (%)']]
    
    for well in wells_data:
        df = well['df']
        config = well['config']
        depth_init = df['DEPTH_FT'].min()
        depth_fin = df['DEPTH_FT'].max()
        samples = len(df)
        matrix = config.get('DOMINANT_MATRIX', 'N/A')
        
        if 'IS_PAY' in df.columns:
            net_pay_pct = 100 * df['IS_PAY'].sum() / len(df)
        else:
            net_pay_pct = 0
        
        summary_data.append([
            well['well_name'][:20],
            f"{depth_init:.1f}",
            f"{depth_fin:.1f}",
            f"{samples}",
            matrix,
            f"{net_pay_pct:.1f}%"
        ])
    
    summary_table = Table(summary_data, colWidths=[1.4*inch, 1.6*inch, 1.6*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # REPORTES INDIVIDUALES DE CADA POZO
    for well_idx, well_data in enumerate(wells_data):
        df = well_data['df']
        well_name = well_data['well_name']
        config = well_data['config']
        stats = well_data['stats']
        curve_mapping = well_data.get('curve_mapping', {})
        
        # ===== TÍTULO DEL POZO =====
        elements.append(Paragraph(f"POZO: {well_name.upper()}", well_title_style))
        elements.append(Spacer(1, 0.15*inch))
        
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
        
        # ===== SECCIÓN 2: PARÁMETROS DE CÁLCULO =====
        elements.append(Paragraph("2. PARÁMETROS DE CÁLCULO", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        calc_data = [
            ['PARÁMETRO', 'VALOR'],
            ['Matriz Dominante', config.get('DOMINANT_MATRIX', 'N/A')],
            ['Densidad de Matriz (g/cc)', f"{config.get('DOMINANT_RHO', 0):.3f}"],
            ['Parámetro A (Archie)', f"{config.get('A', 0):.3f}"],
            ['Parámetro M (Cementación)', f"{config.get('M', 0):.3f}"],
            ['Parámetro N (Saturación)', f"{config.get('N', 0):.3f}"],
            ['Resistividad Agua Rw (ohm-m)', f"{config.get('RW', 0):.4f}"],
            ['Cutoff Porosidad (%)', f"{config.get('PHI_CUTOFF', 0)*100:.1f}"],
            ['Cutoff VSH (%)', f"{config.get('VSH_CUTOFF', 0)*100:.1f}"],
            ['Cutoff Sw (%)', f"{config.get('SW_CUTOFF', 0)*100:.1f}"],
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
        
        # ===== SECCIÓN 3: RESUMEN ESTADÍSTICO =====
        elements.append(Paragraph("3. RESUMEN ESTADÍSTICO", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
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
        
        # ===== SECCIÓN 4: REGISTRO PETROFÍSICO (8 TRACKS) =====
        elements.append(Paragraph("4. REGISTRO PETROFÍSICO", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        try:
            track_buffer = generate_8track_figure(df, LITHO_COLORS)
            if track_buffer:
                track_img = Image(track_buffer, width=7.5*inch, height=3.2*inch)
                elements.append(track_img)
                elements.append(Spacer(1, 0.15*inch))
        except Exception as e:
            print(f"Error agregando registro para {well_name}: {e}")
        
        # ===== SECCIÓN 5: DISTRIBUCIÓN LITOLÓGICA =====
        if 'LITOLOGIA' in df.columns:
            elements.append(Paragraph("5. DISTRIBUCIÓN LITOLÓGICA", heading_style))
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
            
            # Gráfico pie + barras para litología
            try:
                fig = plt.figure(figsize=(12, 5), facecolor='white')
                
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
                
                # Pie chart
                ax1 = plt.subplot(1, 2, 1)
                wedges, texts, autotexts = ax1.pie(lith_counts.values, 
                                                   colors=colors_plot,
                                                   autopct='%1.0f%%',
                                                   startangle=90,
                                                   textprops={'fontsize': 8, 'weight': 'bold'})
                ax1.set_title('Distribución Litológica (%)', fontweight='bold', fontsize=11, pad=15)
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
                
                legend_labels = [f"{l.replace('_', ' ').title()}" for l in lith_unique]
                ax1.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), 
                          fontsize=9, frameon=True, fancybox=True)
                
                # Bar chart
                ax2 = plt.subplot(1, 2, 2)
                lith_sorted = lith_counts.sort_values(ascending=True)
                colors_sorted = [colors_plot[lith_unique.index(lith)] for lith in lith_sorted.index]
                
                bars = ax2.barh(range(len(lith_sorted)), lith_sorted.values, 
                               color=colors_sorted, edgecolor='black', linewidth=1.2)
                
                ax2.set_yticks(range(len(lith_sorted)))
                ax2.set_yticklabels([l.replace('_', ' ').title() for l in lith_sorted.index], 
                                   fontsize=9, fontweight='bold')
                ax2.set_xlabel('Número de Muestras', fontsize=10, fontweight='bold')
                ax2.set_title('Muestras por Litología', fontweight='bold', fontsize=11, pad=15)
                
                ax2.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
                ax2.set_axisbelow(True)
                
                for i, (bar, val) in enumerate(zip(bars, lith_sorted.values)):
                    ax2.text(val + max(lith_sorted.values)*0.01, i, f'{int(val)}', 
                            va='center', fontsize=9, fontweight='bold')
                
                plt.tight_layout()
                
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
                img_buffer.seek(0)
                plt.close()
                
                litho_img = Image(img_buffer, width=6.5*inch, height=2.5*inch)
                elements.append(litho_img)
                elements.append(Spacer(1, 0.15*inch))
                
            except Exception as e:
                print(f"Error creando gráficos litología para {well_name}: {e}")
        
        # ===== SECCIÓN 6: ZONAS PRODUCTIVAS (NET PAY) =====
        if 'IS_PAY' in df.columns:
            elements.append(Paragraph("6. ZONAS PRODUCTIVAS (NET PAY)", heading_style))
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
        
        # Salto de página entre pozos (excepto el último)
        if well_idx < len(wells_data) - 1:
            elements.append(PageBreak())
    
    # Pie del documento
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"<i>Reporte Consolidado generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, 
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
