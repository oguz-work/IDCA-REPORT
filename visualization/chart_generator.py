"""
IDCA Security Assessment - Chart and Table Generator
===================================================
Handles the generation of all charts and tables with theme support.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import Dict, Any, Optional
import tkinter as tk


class ChartGenerator:
    """Generates charts and tables for IDCA reports with theme support"""
    
    def __init__(self, theme_manager, transparent_bg: tk.BooleanVar, visual_settings: Dict):
        self.theme_manager = theme_manager
        self.transparent_bg = transparent_bg
        self.visual_settings = visual_settings
        
        # Default settings
        self.default_settings = {
            'fig_width': 12,
            'fig_height': 8,
            'fig_dpi': 300
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update visual settings"""
        self.default_settings.update(settings)
    
    def _get_figure_background(self, fig, ax):
        """Configure figure and axes background based on transparency setting"""
        colors = self.theme_manager.get_current_colors()
        
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(colors['dark'])
            ax.set_facecolor(colors['primary'])
    
    def _get_text_color(self):
        """Get appropriate text color based on theme and transparency"""
        colors = self.theme_manager.get_current_colors()
        if self.transparent_bg.get():
            # For transparent background, use dark text for light themes, light for dark
            if colors['primary'] == '#ffffff':  # Light theme
                return '#212121'
            else:
                return colors['text']
        else:
            return colors['text']
    
    def create_figure1_preview(self, data: Dict[str, Any]):
        """Create Figure 1 preview - Test Suitability"""
        fig, ax = plt.subplots(figsize=(5, 4), dpi=80)
        self._get_figure_background(fig, ax)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        # Data
        total = data['test_results'].get('total_rules', 100)
        tested = data['test_results'].get('tested_rules', 50)
        not_tested = total - tested if total > tested else 0
        
        if total == 0:
            # No data preview
            ax.text(0.5, 0.5, 'Veri girilmedi', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color=text_color)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            sizes = [tested, not_tested]
            labels = ['Test\nEdilmiş', 'Test\nEdilmemiş']
            chart_colors = [colors['accent_secondary'], colors['gray']]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=chart_colors,
                                              autopct='%1.1f%%', startangle=90,
                                              textprops={'color': text_color, 'fontsize': 9})
            
            # Center circle for donut effect
            centre_circle = plt.Circle((0, 0), 0.70, 
                                      fc='none' if self.transparent_bg.get() else colors['primary'],
                                      linewidth=2, edgecolor=colors['accent'])
            ax.add_artist(centre_circle)
        
        ax.set_title('Test Uygunluk (Önizleme)', fontsize=11, color=text_color, pad=10)
        
        plt.tight_layout()
        return fig
    
    def create_figure2_preview(self, data: Dict[str, Any]):
        """Create Figure 2 preview - Test Status"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3), dpi=80)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        for ax in [ax1, ax2]:
            if self.transparent_bg.get():
                ax.set_facecolor('none')
                ax.patch.set_alpha(0)
            else:
                ax.set_facecolor(colors['primary'])
        
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(colors['dark'])
        
        # Left chart - Test results
        triggered = data['test_results'].get('triggered_rules', 30)
        failed = data['test_results'].get('failed', 20)
        
        if triggered + failed > 0:
            bars = ax1.bar(['Tetiklenen', 'Başarısız'], [triggered, failed],
                          color=[colors['success'], colors['danger']],
                          edgecolor=colors['accent'], linewidth=1)
            
            for bar, val in zip(bars, [triggered, failed]):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max([triggered, failed])*0.02,
                        str(val), ha='center', fontweight='bold', color=text_color, fontsize=9)
        
        ax1.set_title('Test Sonuçları', fontsize=10, color=text_color)
        ax1.tick_params(colors=text_color, labelsize=8)
        ax1.grid(True, alpha=0.3, color=colors['gray'])
        
        # Right chart - Sample MITRE data
        if data['mitre_tactics']:
            tactics_sorted = sorted(data['mitre_tactics'].items(),
                                  key=lambda x: x[1]['rate'])[:4]
            
            tactics = [t[0][:10] + '...' if len(t[0]) > 10 else t[0] for t in tactics_sorted]
            rates = [t[1]['rate'] for t in tactics_sorted]
            
            colors_bar = [self.theme_manager.get_performance_color(r) for r in rates]
            
            bars2 = ax2.barh(range(len(tactics)), rates, color=colors_bar,
                           edgecolor=colors['accent'], linewidth=1)
            
            ax2.set_yticks(range(len(tactics)))
            ax2.set_yticklabels(tactics, fontsize=8, color=text_color)
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Başarı %', color=text_color, fontsize=8)
            ax2.tick_params(colors=text_color, labelsize=8)
            ax2.grid(True, axis='x', alpha=0.3, color=colors['gray'])
        
        ax2.set_title('MITRE Performans', fontsize=10, color=text_color)
        
        plt.tight_layout()
        return fig
    
    def create_table_preview(self, table_name: str, data: Dict[str, Any]):
        """Create table preview"""
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        ax.axis('tight')
        ax.axis('off')
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(colors['dark'])
        
        # Sample table data based on type
        if 'Table 1' in table_name:
            table_data = [
                ['Metrik', 'Değer', 'Durum'],
                ['Toplam Kural', str(data['test_results'].get('total_rules', 0)), '✅'],
                ['Test Edilen', str(data['test_results'].get('tested_rules', 0)), '✅'],
                ['Başarı Oranı', f"%{data['test_results'].get('success_rate', 0):.1f}", '⚠️']
            ]
        elif 'Table 2' in table_name:
            table_data = [['Taktik', 'Test', 'Tetiklenen', 'Başarı %']]
            for tactic, values in list(data['mitre_tactics'].items())[:3]:
                table_data.append([tactic[:15], str(values['test']), 
                                 str(values['triggered']), f"%{values['rate']:.1f}"])
        else:
            table_data = [
                ['Başlık 1', 'Başlık 2', 'Başlık 3'],
                ['Örnek veri', 'Önizleme', 'Tablosu'],
                ['Detaylı veri', 'girildikten sonra', 'görünecek']
            ]
        
        # Create table
        if len(table_data) > 1:
            cell_colors = []
            cell_colors.append([colors['accent_secondary']] * len(table_data[0]))
            for _ in range(len(table_data) - 1):
                cell_colors.append([colors['secondary']] * len(table_data[0]))
            
            table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                           cellColours=cell_colors)
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1.2, 1.5)
            
            # Header row styling
            for i in range(len(table_data[0])):
                cell = table[(0, i)]
                cell.set_text_props(weight='bold', color='white')
        
        ax.set_title(f'{table_name} (Önizleme)', fontsize=11, color=text_color)
        
        plt.tight_layout()
        return fig
    
    def generate_figure1(self, data: Dict[str, Any], filepath: str):
        """Generate Figure 1 - Test Suitability Chart"""
        width = self.default_settings['fig_width']
        height = self.default_settings['fig_height']
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        
        # Data
        total = data['test_results']['total_rules']
        tested = data['test_results']['tested_rules']
        not_tested = data['test_results']['not_tested']
        triggered = data['test_results']['triggered_rules']
        success_rate = data['test_results']['success_rate']
        
        # Pie chart
        sizes = [tested, not_tested]
        labels = [f'Test Edilmiş\n{tested} kural\n(%{tested/total*100:.1f})',
                 f'Test Edilmemiş\n{not_tested} kural\n(%{not_tested/total*100:.1f})']
        chart_colors = [colors['accent_secondary'], colors['gray']]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=chart_colors,
                                          explode=(0.05, 0), startangle=90, 
                                          shadow=not self.transparent_bg.get(),
                                          textprops={'fontsize': 11, 'color': text_color})
        
        # Center circle
        centre_circle = plt.Circle((0, 0), 0.70, 
                                  fc='none' if self.transparent_bg.get() else colors['primary'],
                                  linewidth=2, edgecolor=colors['accent'])
        ax.add_artist(centre_circle)
        
        # Center text
        ax.text(0, 0.1, str(total), ha='center', va='center',
               fontsize=36, fontweight='bold', color=colors['accent'])
        ax.text(0, -0.15, 'Toplam Kural', ha='center', va='center',
               fontsize=12, color=text_color)
        ax.text(0, -0.3, f'Başarı: %{success_rate:.1f}', ha='center', va='center',
               fontsize=11, fontweight='bold',
               color=self.theme_manager.get_performance_color(success_rate))
        
        # Title
        ax.set_title('Figure 1: Analiz Edilen Korelasyonların Test Uygunluk Grafiği',
                    fontsize=14, fontweight='bold', color=text_color, pad=20)
        
        # Footer
        fig.text(0.5, 0.02, f"{data['general']['company_name']} - {data['general']['report_date']}",
                ha='center', fontsize=9, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_figure2(self, data: Dict[str, Any], filepath: str):
        """Generate Figure 2 - Test Status Charts"""
        width = self.default_settings['fig_width']
        height = self.default_settings['fig_height']
        dpi = self.default_settings['fig_dpi']
        
        fig = plt.figure(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(colors['dark'])
        
        # Left subplot
        ax1 = plt.subplot(1, 2, 1)
        self._get_figure_background(fig, ax1)
        
        triggered = data['test_results']['triggered_rules']
        failed = data['test_results']['failed']
        
        bars = ax1.bar(['Tetiklenen', 'Başarısız'], [triggered, failed],
                      color=[colors['success'], colors['danger']],
                      edgecolor=colors['accent'], linewidth=2)
        
        for bar, val in zip(bars, [triggered, failed]):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max([triggered, failed])*0.02,
                    str(val), ha='center', fontweight='bold', color=text_color)
        
        ax1.set_title('Test Sonuç Dağılımı', fontsize=12, color=text_color)
        ax1.set_ylabel('Kural Sayısı', color=text_color)
        ax1.tick_params(colors=text_color)
        ax1.grid(True, alpha=0.3, color=colors['gray'], linestyle='--')
        
        # Right subplot
        ax2 = plt.subplot(1, 2, 2)
        self._get_figure_background(fig, ax2)
        
        if data['mitre_tactics']:
            tactics_sorted = sorted(data['mitre_tactics'].items(),
                                  key=lambda x: x[1]['rate'])[:6]
            
            tactics = [t[0] for t in tactics_sorted]
            rates = [t[1]['rate'] for t in tactics_sorted]
            
            colors_bar = [self.theme_manager.get_performance_color(r) for r in rates]
            
            bars2 = ax2.barh(range(len(tactics)), rates, color=colors_bar,
                           edgecolor=colors['accent'], linewidth=1)
            
            for bar, val in zip(bars2, rates):
                ax2.text(val + 1, bar.get_y() + bar.get_height()/2,
                        f'%{val:.1f}', va='center', fontweight='bold', color=text_color)
            
            ax2.set_yticks(range(len(tactics)))
            ax2.set_yticklabels(tactics, fontsize=9, color=text_color)
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Başarı Oranı (%)', color=text_color)
            ax2.set_title('En Düşük Performanslı Taktikler', fontsize=12, color=text_color)
            ax2.tick_params(colors=text_color)
            ax2.grid(True, axis='x', alpha=0.3, color=colors['gray'], linestyle='--')
        
        fig.suptitle('Figure 2: Test Edilen Korelasyonların Durumu',
                    fontsize=14, fontweight='bold', color=text_color)
        
        fig.text(0.5, 0.02, f"{data['general']['company_name']} - {data['general']['prepared_by']}",
                ha='center', fontsize=9, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table1(self, data: Dict[str, Any], filepath: str):
        """Generate Table 1 - Results Assessment"""
        width = self.default_settings['fig_width']
        height = 6
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        total = data['test_results']['total_rules']
        tested = data['test_results']['tested_rules']
        success_rate = data['test_results']['success_rate']
        not_tested = data['test_results']['not_tested']
        
        table_data = [
            ['Metrik', 'Değer', 'Hedef', 'Durum', 'Açıklama'],
            ['Toplam Kural', str(total), '300+', 
             '✅' if total >= 300 else '⚠️' if total >= 200 else '❌', 
             'Kapsam değerlendirmesi'],
            ['Test Edilen', str(tested), '200+',
             '✅' if tested >= 200 else '⚠️' if tested >= 100 else '❌',
             'Test kapsamı'],
            ['Başarı Oranı', f'%{success_rate:.1f}', '%70+',
             '✅' if success_rate >= 70 else '⚠️' if success_rate >= 50 else '❌',
             'Tespit yeteneği'],
            ['Test Edilmeyen', str(not_tested), '<50',
             '✅' if not_tested < 50 else '⚠️' if not_tested < 100 else '❌',
             'Kapsam dışı']
        ]
        
        # Color scheme
        cell_colors = []
        for i, row in enumerate(table_data):
            if i == 0:
                cell_colors.append([colors['accent_secondary']] * 5)
            else:
                row_colors = [colors['secondary']] * 5
                if '✅' in row[3]:
                    row_colors[3] = colors['success']
                elif '⚠️' in row[3]:
                    row_colors[3] = colors['warning']
                elif '❌' in row[3]:
                    row_colors[3] = colors['danger']
                cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.2, 0.12, 0.12, 0.1, 0.36])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)
        
        # Header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 1: Sonuç Değerlendirme Tablosu',
                    fontsize=14, fontweight='bold', pad=20, color=text_color)
        
        fig.text(0.5, 0.02, f"{data['general']['company_name']} - {data['general']['report_date']}",
                ha='center', fontsize=9, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table2(self, data: Dict[str, Any], filepath: str):
        """Generate Table 2 - MITRE Coverage"""
        if not data['mitre_tactics']:
            return
        
        width = self.default_settings['fig_width']
        height = max(8, len(data['mitre_tactics']) * 0.6)
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        headers = ['Taktik', 'Test Edilen', 'Tetiklenen', 'Başarı %', 'Kritiklik']
        rows = []
        
        sorted_tactics = sorted(data['mitre_tactics'].items(),
                              key=lambda x: x[1]['rate'])
        
        for tactic, values in sorted_tactics:
            kritiklik = 'Kritik' if values['rate'] < 40 else 'Orta' if values['rate'] < 60 else 'İyi'
            rows.append([
                tactic,
                str(values['test']),
                str(values['triggered']),
                f"%{values['rate']:.1f}",
                kritiklik
            ])
        
        table_data = [headers] + rows
        
        # Color scheme
        cell_colors = []
        cell_colors.append([colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [colors['secondary']] * 5
            rate = float(row[3].strip('%'))
            color = self.theme_manager.get_performance_color(rate)
            row_colors[3] = color
            row_colors[4] = color
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.28, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        
        # Header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 2: MITRE ATT&CK Kapsama Analizi',
                    fontsize=14, fontweight='bold', pad=20, color=text_color)
        
        # Summary
        avg_success = np.mean([v['rate'] for v in data['mitre_tactics'].values()])
        fig.text(0.5, 0.05, f'Ortalama Başarı: %{avg_success:.1f}',
                ha='center', fontsize=10, color=text_color)
        fig.text(0.5, 0.02, f"{data['general']['company_name']}",
                ha='center', fontsize=9, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table3(self, data: Dict[str, Any], filepath: str):
        """Generate Table 3 - Triggered Rules"""
        if not data['triggered_rules']:
            return
        
        width = self.default_settings['fig_width']
        height = max(6, min(12, len(data['triggered_rules']) * 0.5))
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        headers = ['ID', 'Kural Adı', 'MITRE Teknik', 'Taktik', 'Güven Skoru']
        rows = []
        
        for i, rule in enumerate(data['triggered_rules'][:20], 1):
            rows.append([
                str(i),
                rule['name'][:40] + '...' if len(rule['name']) > 40 else rule['name'],
                rule['mitre'],
                rule['tactic'],
                f"%{rule['confidence']}"
            ])
        
        table_data = [headers] + rows
        
        # Color coding
        cell_colors = []
        cell_colors.append([colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [colors['secondary']] * 5
            try:
                confidence = int(row[4].strip('%'))
                if confidence >= 90:
                    row_colors[4] = colors['success']
                elif confidence >= 80:
                    row_colors[4] = colors['warning']
                else:
                    row_colors[4] = colors['danger']
            except:
                pass
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.08, 0.38, 0.15, 0.2, 0.12])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.8)
        
        # Header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 3: Tetiklenen Korelasyon Kuralları Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=text_color)
        
        fig.text(0.5, 0.02, f"Toplam {len(data['triggered_rules'])} kural - {data['general']['company_name']}",
                ha='center', fontsize=9, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table4(self, data: Dict[str, Any], filepath: str):
        """Generate Table 4 - Undetected Techniques"""
        if not data['undetected_techniques']:
            return
        
        width = self.default_settings['fig_width']
        height = max(6, min(12, len(data['undetected_techniques']) * 0.5))
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        headers = ['MITRE ID', 'Teknik Adı', 'Taktik', 'Kritiklik', 'Öncelik']
        rows = []
        
        # Sort by criticality
        kritiklik_order = {'Kritik': 0, 'Yüksek': 1, 'Orta': 2, 'Düşük': 3}
        sorted_techniques = sorted(data['undetected_techniques'],
                                 key=lambda x: kritiklik_order.get(x['criticality'], 4))
        
        for i, tech in enumerate(sorted_techniques[:20], 1):
            rows.append([
                tech['id'],
                tech['name'][:35] + '...' if len(tech['name']) > 35 else tech['name'],
                tech['tactic'],
                tech['criticality'],
                f"P{i}"
            ])
        
        table_data = [headers] + rows
        
        # Color coding
        cell_colors = []
        cell_colors.append([colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [colors['secondary']] * 5
            if 'Kritik' in row[3]:
                row_colors[3] = colors['danger']
                row_colors[4] = colors['danger']
            elif 'Yüksek' in row[3]:
                row_colors[3] = colors['warning']
                row_colors[4] = colors['warning']
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.12, 0.35, 0.2, 0.12, 0.1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 4: Algılanamayan MITRE Teknikleri Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=text_color)
        
        kritik_count = sum(1 for t in data['undetected_techniques'] if t['criticality'] == 'Kritik')
        yuksek_count = sum(1 for t in data['undetected_techniques'] if t['criticality'] == 'Yüksek')
        
        fig.text(0.5, 0.02, f"⚠️ {kritik_count} Kritik, {yuksek_count} Yüksek seviyeli teknik için acil önlem gerekli",
                ha='center', fontsize=10, weight='bold', color=colors['warning'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table5(self, data: Dict[str, Any], filepath: str):
        """Generate Table 5 - Recommendations"""
        if not data['recommendations']:
            return
        
        width = self.default_settings['fig_width']
        height = max(6, min(12, len(data['recommendations']) * 0.6))
        dpi = self.default_settings['fig_dpi']
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        colors = self.theme_manager.get_current_colors()
        text_color = self._get_text_color()
        
        self._get_figure_background(fig, ax)
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        headers = ['Öncelik', 'Kategori', 'Öneri', 'Beklenen Etki']
        rows = []
        
        for i, rec in enumerate(data['recommendations'][:15], 1):
            etki = 'Yüksek' if i <= 3 else 'Orta' if i <= 7 else 'Normal'
            rows.append([
                rec['priority'],
                rec['category'],
                rec['text'][:50] + '...' if len(rec['text']) > 50 else rec['text'],
                etki
            ])
        
        table_data = [headers] + rows
        
        # Color coding
        cell_colors = []
        cell_colors.append([colors['accent_secondary']] * 4)
        
        for i, row in enumerate(rows):
            row_colors = [colors['secondary']] * 4
            if i < 3:
                row_colors[0] = colors['danger']
                row_colors[3] = colors['success']
            elif i < 7:
                row_colors[0] = colors['warning']
                row_colors[3] = colors['warning']
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.1, 0.2, 0.45, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Header row
        for i in range(4):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 5: Yazılması Gereken Korelasyon Kurallarının Öneri Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=text_color)
        
        fig.text(0.5, 0.03, f'Toplam {len(data["recommendations"])} öneri',
                ha='center', fontsize=9, style='italic', color=colors['success'])
        fig.text(0.5, 0.005, f"{data['general']['company_name']} - {data['general']['prepared_by']}",
                ha='center', fontsize=8, color=colors['gray'])
        
        plt.tight_layout()
        
        # Save
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=colors['dark'], bbox_inches='tight')
        plt.close()