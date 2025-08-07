#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization generation for IDCA reports
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from data.models import IDCAData
from themes.theme_manager import ThemeManager
from core.config import (
    DEFAULT_FIG_WIDTH, DEFAULT_FIG_HEIGHT, DEFAULT_DPI,
    TABLE_HEADER_HEIGHT, TABLE_ROW_HEIGHT, STATUS_ICONS
)


class VisualizationGenerator:
    """Generates all IDCA report visualizations"""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.fig_width = DEFAULT_FIG_WIDTH
        self.fig_height = DEFAULT_FIG_HEIGHT
        self.dpi = DEFAULT_DPI
        self.transparent = True
    
    def set_dimensions(self, width: float, height: float, dpi: int):
        """Set figure dimensions"""
        self.fig_width = width
        self.fig_height = height
        self.dpi = dpi
    
    def set_transparent(self, transparent: bool):
        """Set transparency mode"""
        self.transparent = transparent
    
    def generate_all(self, data: IDCAData, output_dir: Path) -> Dict[str, bool]:
        """Generate all visualizations"""
        results = {}
        
        visualizations = [
            ('Figure_1_Test_Coverage', self.generate_figure1),
            ('Figure_2_Test_Status', self.generate_figure2),
            ('Table_1_Summary', self.generate_table1),
            ('Table_2_MITRE_Coverage', self.generate_table2),
            ('Table_3_Triggered_Rules', self.generate_table3),
            ('Table_4_Undetected_Techniques', self.generate_table4),
            ('Table_5_Recommendations', self.generate_table5)
        ]
        
        for filename, generator in visualizations:
            try:
                filepath = output_dir / f"{filename}.png"
                generator(data, filepath)
                results[filename] = True
            except Exception as e:
                print(f"Error generating {filename}: {e}")
                results[filename] = False
        
        return results
    
    def _setup_figure(self, figsize: Tuple[float, float] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Set up a figure with theme colors"""
        if figsize is None:
            figsize = (self.fig_width, self.fig_height)
        
        # Apply theme to matplotlib
        self.theme_manager.apply_to_matplotlib(self.transparent)
        
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
        
        # Set background
        if self.transparent:
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.theme_manager.get_color('background'))
            ax.set_facecolor(self.theme_manager.get_color('surface'))
        
        return fig, ax
    
    def generate_figure1(self, data: IDCAData, filepath: Path):
        """Generate Figure 1: Test Coverage Pie Chart"""
        fig, ax = self._setup_figure()
        
        # Data
        total = data.test_results.total_rules
        tested = data.test_results.tested_rules
        not_tested = data.test_results.not_tested
        success_rate = data.test_results.success_rate
        
        # Pie chart
        sizes = [tested, not_tested]
        labels = [
            f'Tested\n{tested} rules\n({tested/total*100:.1f}%)',
            f'Not Tested\n{not_tested} rules\n({not_tested/total*100:.1f}%)'
        ]
        colors = [
            self.theme_manager.get_color('accent'),
            self.theme_manager.get_color('gray')
        ]
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            explode=(0.05, 0), startangle=90,
            shadow=not self.transparent,
            textprops={
                'fontsize': 11,
                'color': self.theme_manager.get_color('text_primary')
            }
        )
        
        # Center circle for donut effect
        centre_circle = plt.Circle(
            (0, 0), 0.70,
            fc='none' if self.transparent else self.theme_manager.get_color('surface'),
            linewidth=2,
            edgecolor=self.theme_manager.get_color('accent_secondary')
        )
        ax.add_artist(centre_circle)
        
        # Center text
        ax.text(0, 0.1, str(total), ha='center', va='center',
                fontsize=36, fontweight='bold',
                color=self.theme_manager.get_color('accent'))
        ax.text(0, -0.15, 'Total Rules', ha='center', va='center',
                fontsize=12, color=self.theme_manager.get_color('text_secondary'))
        
        # Success rate indicator
        success_color = (
            self.theme_manager.get_color('success') if success_rate >= 70
            else self.theme_manager.get_color('warning') if success_rate >= 50
            else self.theme_manager.get_color('danger')
        )
        ax.text(0, -0.3, f'Success Rate: {success_rate:.1f}%',
                ha='center', va='center', fontsize=11, fontweight='bold',
                color=success_color)
        
        # Title
        ax.set_title('Figure 1: Test Coverage Analysis',
                    fontsize=14, fontweight='bold',
                    color=self.theme_manager.get_color('text_primary'),
                    pad=20)
        
        # Footer
        fig.text(0.5, 0.02, f"{data.general.company_name} - {data.general.report_date}",
                ha='center', fontsize=9,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_figure2(self, data: IDCAData, filepath: Path):
        """Generate Figure 2: Test Status Charts"""
        fig = plt.figure(figsize=(self.fig_width, self.fig_height), dpi=100)
        
        # Apply theme
        self.theme_manager.apply_to_matplotlib(self.transparent)
        
        if self.transparent:
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.theme_manager.get_color('background'))
        
        # Left subplot - Test Results
        ax1 = plt.subplot(1, 2, 1)
        self._setup_axes(ax1)
        
        triggered = data.test_results.triggered_rules
        failed = data.test_results.failed
        
        bars = ax1.bar(['Triggered', 'Failed'], [triggered, failed],
                       color=[self.theme_manager.get_color('success'),
                             self.theme_manager.get_color('danger')],
                       edgecolor=self.theme_manager.get_color('accent'),
                       linewidth=2)
        
        # Value labels
        for bar, val in zip(bars, [triggered, failed]):
            ax1.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + max([triggered, failed])*0.02,
                    str(val), ha='center', fontweight='bold',
                    color=self.theme_manager.get_color('text_primary'))
        
        ax1.set_title('Test Results Distribution', fontsize=12,
                     color=self.theme_manager.get_color('text_primary'))
        ax1.set_ylabel('Rule Count', color=self.theme_manager.get_color('text_primary'))
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Right subplot - MITRE Performance
        ax2 = plt.subplot(1, 2, 2)
        self._setup_axes(ax2)
        
        if data.mitre_tactics:
            # Get lowest performing tactics
            tactics_sorted = sorted(
                data.mitre_tactics.items(),
                key=lambda x: x[1].success_rate
            )[:6]
            
            tactics = [t[0] for t in tactics_sorted]
            rates = [t[1].success_rate for t in tactics_sorted]
            
            # Color based on performance
            colors_bar = []
            for r in rates:
                if r < 40:
                    colors_bar.append(self.theme_manager.get_color('danger'))
                elif r < 60:
                    colors_bar.append(self.theme_manager.get_color('warning'))
                else:
                    colors_bar.append(self.theme_manager.get_color('success'))
            
            bars2 = ax2.barh(range(len(tactics)), rates, color=colors_bar,
                            edgecolor=self.theme_manager.get_color('accent'),
                            linewidth=1)
            
            # Value labels
            for bar, val in zip(bars2, rates):
                ax2.text(val + 1, bar.get_y() + bar.get_height()/2,
                        f'{val:.1f}%', va='center', fontweight='bold',
                        color=self.theme_manager.get_color('text_primary'))
            
            ax2.set_yticks(range(len(tactics)))
            ax2.set_yticklabels(tactics, fontsize=9)
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Success Rate (%)',
                          color=self.theme_manager.get_color('text_primary'))
            ax2.set_title('Lowest Performing Tactics', fontsize=12,
                         color=self.theme_manager.get_color('text_primary'))
            ax2.grid(True, axis='x', alpha=0.3, linestyle='--')
        
        # Main title
        fig.suptitle('Figure 2: Test Status Overview',
                    fontsize=14, fontweight='bold',
                    color=self.theme_manager.get_color('text_primary'))
        
        # Footer
        fig.text(0.5, 0.02, f"{data.general.company_name} - {data.general.prepared_by}",
                ha='center', fontsize=9,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_table1(self, data: IDCAData, filepath: Path):
        """Generate Table 1: Summary Table"""
        fig, ax = self._setup_figure((self.fig_width, 6))
        ax.axis('tight')
        ax.axis('off')
        
        # Table data
        total = data.test_results.total_rules
        tested = data.test_results.tested_rules
        success_rate = data.test_results.success_rate
        not_tested = data.test_results.not_tested
        
        table_data = [
            ['Metric', 'Value', 'Target', 'Status', 'Description'],
            ['Total Rules', str(total), '300+',
             STATUS_ICONS['success'] if total >= 300 else STATUS_ICONS['warning'] if total >= 200 else STATUS_ICONS['error'],
             'Coverage assessment'],
            ['Tested Rules', str(tested), '200+',
             STATUS_ICONS['success'] if tested >= 200 else STATUS_ICONS['warning'] if tested >= 100 else STATUS_ICONS['error'],
             'Test coverage'],
            ['Success Rate', f'{success_rate:.1f}%', '70%+',
             STATUS_ICONS['success'] if success_rate >= 70 else STATUS_ICONS['warning'] if success_rate >= 50 else STATUS_ICONS['error'],
             'Detection capability'],
            ['Not Tested', str(not_tested), '<50',
             STATUS_ICONS['success'] if not_tested < 50 else STATUS_ICONS['warning'] if not_tested < 100 else STATUS_ICONS['error'],
             'Out of scope']
        ]
        
        # Create color map
        cell_colors = self._create_table_colors(table_data)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.2, 0.12, 0.12, 0.1, 0.36])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, TABLE_HEADER_HEIGHT)
        
        # Style header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 1: Assessment Summary',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.theme_manager.get_color('text_primary'))
        
        fig.text(0.5, 0.02, f"{data.general.company_name} - {data.general.report_date}",
                ha='center', fontsize=9,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_table2(self, data: IDCAData, filepath: Path):
        """Generate Table 2: MITRE Coverage Table"""
        if not data.mitre_tactics:
            return
        
        height = max(8, len(data.mitre_tactics) * 0.6)
        fig, ax = self._setup_figure((self.fig_width, height))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        headers = ['Tactic', 'Tested', 'Triggered', 'Success %', 'Risk Level']
        rows = []
        
        sorted_tactics = sorted(
            data.mitre_tactics.items(),
            key=lambda x: x[1].success_rate
        )
        
        for name, tactic in sorted_tactics:
            risk_level = (
                'Critical' if tactic.success_rate < 40
                else 'Medium' if tactic.success_rate < 60
                else 'Low'
            )
            rows.append([
                name,
                str(tactic.test_count),
                str(tactic.triggered_count),
                f"{tactic.success_rate:.1f}%",
                risk_level
            ])
        
        table_data = [headers] + rows
        
        # Create color map
        cell_colors = []
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * 5)
        
        for row in rows:
            row_colors = [self.theme_manager.get_color('secondary')] * 5
            rate = float(row[3].strip('%'))
            
            if rate < 40:
                row_colors[3] = self.theme_manager.get_color('danger')
                row_colors[4] = self.theme_manager.get_color('danger')
            elif rate < 60:
                row_colors[3] = self.theme_manager.get_color('warning')
                row_colors[4] = self.theme_manager.get_color('warning')
            else:
                row_colors[3] = self.theme_manager.get_color('success')
                row_colors[4] = self.theme_manager.get_color('success')
            
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.28, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, TABLE_ROW_HEIGHT)
        
        # Style header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 2: MITRE ATT&CK Coverage Analysis',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.theme_manager.get_color('text_primary'))
        
        # Summary
        avg_success = np.mean([t.success_rate for t in data.mitre_tactics.values()])
        fig.text(0.5, 0.05, f'Average Success Rate: {avg_success:.1f}%',
                ha='center', fontsize=10,
                color=self.theme_manager.get_color('text_primary'))
        
        fig.text(0.5, 0.02, f"{data.general.company_name}",
                ha='center', fontsize=9,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_table3(self, data: IDCAData, filepath: Path):
        """Generate Table 3: Triggered Rules Table"""
        if not data.triggered_rules:
            return
        
        height = max(6, min(12, len(data.triggered_rules) * 0.5))
        fig, ax = self._setup_figure((self.fig_width, height))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        headers = ['ID', 'Rule Name', 'MITRE ID', 'Tactic', 'Confidence']
        rows = []
        
        for i, rule in enumerate(data.triggered_rules[:20], 1):
            rule_name = (rule.name[:40] + '...' 
                        if len(rule.name) > 40 else rule.name)
            rows.append([
                str(i),
                rule_name,
                rule.mitre_id,
                rule.tactic,
                f"{rule.confidence}%"
            ])
        
        table_data = [headers] + rows
        
        # Create color map
        cell_colors = []
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * 5)
        
        for row in rows:
            row_colors = [self.theme_manager.get_color('secondary')] * 5
            confidence = int(row[4].strip('%'))
            
            if confidence >= 90:
                row_colors[4] = self.theme_manager.get_color('success')
            elif confidence >= 80:
                row_colors[4] = self.theme_manager.get_color('warning')
            else:
                row_colors[4] = self.theme_manager.get_color('danger')
            
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.08, 0.38, 0.15, 0.2, 0.12])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, TABLE_ROW_HEIGHT)
        
        # Style header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 3: Triggered Correlation Rules',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.theme_manager.get_color('text_primary'))
        
        fig.text(0.5, 0.02,
                f"Total: {len(data.triggered_rules)} rules - {data.general.company_name}",
                ha='center', fontsize=9,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_table4(self, data: IDCAData, filepath: Path):
        """Generate Table 4: Undetected Techniques Table"""
        if not data.undetected_techniques:
            return
        
        height = max(6, min(12, len(data.undetected_techniques) * 0.5))
        fig, ax = self._setup_figure((self.fig_width, height))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        headers = ['MITRE ID', 'Technique Name', 'Tactic', 'Criticality', 'Priority']
        rows = []
        
        # Sort by criticality
        criticality_order = {'Critical': 0, 'Kritik': 0, 'High': 1, 'Yüksek': 1,
                           'Medium': 2, 'Orta': 2, 'Low': 3, 'Düşük': 3}
        sorted_techniques = sorted(
            data.undetected_techniques,
            key=lambda x: criticality_order.get(x.criticality, 4)
        )
        
        for i, tech in enumerate(sorted_techniques[:20], 1):
            tech_name = (tech.name[:35] + '...' 
                        if len(tech.name) > 35 else tech.name)
            rows.append([
                tech.mitre_id,
                tech_name,
                tech.tactic,
                tech.criticality,
                f"P{i}"
            ])
        
        table_data = [headers] + rows
        
        # Create color map
        cell_colors = []
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * 5)
        
        for row in rows:
            row_colors = [self.theme_manager.get_color('secondary')] * 5
            
            if row[3] in ['Critical', 'Kritik']:
                row_colors[3] = self.theme_manager.get_color('danger')
                row_colors[4] = self.theme_manager.get_color('danger')
            elif row[3] in ['High', 'Yüksek']:
                row_colors[3] = self.theme_manager.get_color('warning')
                row_colors[4] = self.theme_manager.get_color('warning')
            
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.12, 0.35, 0.2, 0.12, 0.1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, TABLE_ROW_HEIGHT)
        
        # Style header row
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 4: Undetected MITRE Techniques',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.theme_manager.get_color('text_primary'))
        
        # Count critical/high
        critical_count = sum(1 for t in data.undetected_techniques 
                           if t.criticality in ['Critical', 'Kritik'])
        high_count = sum(1 for t in data.undetected_techniques 
                        if t.criticality in ['High', 'Yüksek'])
        
        fig.text(0.5, 0.02,
                f"{STATUS_ICONS['warning']} {critical_count} Critical, {high_count} High priority techniques require immediate attention",
                ha='center', fontsize=10, weight='bold',
                color=self.theme_manager.get_color('warning'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def generate_table5(self, data: IDCAData, filepath: Path):
        """Generate Table 5: Recommendations Table"""
        if not data.recommendations:
            return
        
        height = max(6, min(12, len(data.recommendations) * 0.6))
        fig, ax = self._setup_figure((self.fig_width, height))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare table data
        headers = ['Priority', 'Category', 'Recommendation', 'Impact']
        rows = []
        
        for i, rec in enumerate(data.recommendations[:15], 1):
            impact = 'High' if i <= 3 else 'Medium' if i <= 7 else 'Normal'
            rec_text = (rec.text[:50] + '...' 
                       if len(rec.text) > 50 else rec.text)
            rows.append([
                rec.priority,
                rec.category,
                rec_text,
                impact
            ])
        
        table_data = [headers] + rows
        
        # Create color map
        cell_colors = []
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * 4)
        
        for i, row in enumerate(rows):
            row_colors = [self.theme_manager.get_color('secondary')] * 4
            
            if i < 3:
                row_colors[0] = self.theme_manager.get_color('danger')
                row_colors[3] = self.theme_manager.get_color('success')
            elif i < 7:
                row_colors[0] = self.theme_manager.get_color('warning')
                row_colors[3] = self.theme_manager.get_color('warning')
            
            cell_colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.1, 0.2, 0.45, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, TABLE_ROW_HEIGHT)
        
        # Style header row
        for i in range(4):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 5: Recommended Correlation Rules',
                    fontsize=14, fontweight='bold', pad=20,
                    color=self.theme_manager.get_color('text_primary'))
        
        fig.text(0.5, 0.03, f'Total: {len(data.recommendations)} recommendations',
                ha='center', fontsize=9, style='italic',
                color=self.theme_manager.get_color('success'))
        
        fig.text(0.5, 0.005,
                f"{data.general.company_name} - {data.general.prepared_by}",
                ha='center', fontsize=8,
                color=self.theme_manager.get_color('text_secondary'))
        
        plt.tight_layout()
        self._save_figure(fig, filepath)
    
    def _setup_axes(self, ax):
        """Set up axes with theme colors"""
        if self.transparent:
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            ax.set_facecolor(self.theme_manager.get_color('surface'))
        
        ax.tick_params(colors=self.theme_manager.get_color('text_secondary'))
        ax.spines['bottom'].set_color(self.theme_manager.get_color('border'))
        ax.spines['top'].set_color(self.theme_manager.get_color('border'))
        ax.spines['left'].set_color(self.theme_manager.get_color('border'))
        ax.spines['right'].set_color(self.theme_manager.get_color('border'))
    
    def _create_table_colors(self, table_data: List[List[str]]) -> List[List[str]]:
        """Create color map for table"""
        cell_colors = []
        
        # Header row
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * len(table_data[0]))
        
        # Data rows
        for row in table_data[1:]:
            row_colors = [self.theme_manager.get_color('secondary')] * len(row)
            
            # Color status column based on icon
            if len(row) > 3:
                if STATUS_ICONS['success'] in row[3]:
                    row_colors[3] = self.theme_manager.get_color('success')
                elif STATUS_ICONS['warning'] in row[3]:
                    row_colors[3] = self.theme_manager.get_color('warning')
                elif STATUS_ICONS['error'] in row[3]:
                    row_colors[3] = self.theme_manager.get_color('danger')
            
            cell_colors.append(row_colors)
        
        return cell_colors
    
    def _save_figure(self, fig: plt.Figure, filepath: Path):
        """Save figure with proper settings"""
        if self.transparent:
            plt.savefig(filepath, dpi=self.dpi, transparent=True,
                       bbox_inches='tight', pad_inches=0.1)
        else:
            plt.savefig(filepath, dpi=self.dpi,
                       facecolor=self.theme_manager.get_color('background'),
                       bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)
    
    # API methods that return figures instead of saving them
    def create_test_coverage_chart(self, data: IDCAData) -> plt.Figure:
        """Create test coverage pie chart and return figure"""
        fig, ax = self._setup_figure()
        
        # Data
        total = data.test_results.total_rules
        tested = data.test_results.tested_rules
        not_tested = total - tested
        
        if total == 0:
            ax.text(0.5, 0.5, 'No data available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=16, color=self.theme_manager.get_color('text_primary'))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        # Create pie chart
        sizes = [tested, not_tested]
        labels = ['Tested', 'Not Tested']
        colors = [self.theme_manager.get_color('success'), 
                 self.theme_manager.get_color('error')]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90,
                                          textprops={'color': self.theme_manager.get_color('text_primary')})
        
        # Title
        ax.set_title('Test Coverage Overview', fontsize=16, 
                    color=self.theme_manager.get_color('text_primary'),
                    pad=20)
        
        return fig
    
    def create_mitre_heatmap(self, data: IDCAData) -> plt.Figure:
        """Create MITRE ATT&CK heatmap and return figure"""
        fig, ax = self._setup_figure(figsize=(12, 8))
        
        # Build list from tactics
        mitre_values = list(data.mitre_tactics.values())
        if not mitre_values:
            ax.text(0.5, 0.5, 'No MITRE data available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=16, color=self.theme_manager.get_color('text_primary'))
            ax.axis('off')
            return fig
        
        tactics = [t.name for t in mitre_values]
        coverage = [t.success_rate for t in mitre_values]
        
        # Create horizontal bars
        y_pos = np.arange(len(tactics))
        bars = ax.barh(y_pos, coverage, color=self.theme_manager.get_color('primary'))
        
        # Color bars based on success rate
        for bar, cov in zip(bars, coverage):
            if cov >= 70:
                bar.set_color(self.theme_manager.get_color('success'))
            elif cov >= 40:
                bar.set_color(self.theme_manager.get_color('warning'))
            else:
                bar.set_color(self.theme_manager.get_color('danger'))
        
        # Customize
        ax.set_yticks(y_pos)
        ax.set_yticklabels(tactics)
        ax.set_xlabel('Success Rate (%)', fontsize=12)
        ax.set_title('MITRE ATT&CK Tactics Success', fontsize=16, pad=20)
        ax.set_xlim(0, 100)
        
        for bar, cov in zip(bars, coverage):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                   f'{cov:.1f}%', va='center')
        
        ax.tick_params(colors=self.theme_manager.get_color('text_primary'))
        ax.xaxis.label.set_color(self.theme_manager.get_color('text_primary'))
        ax.title.set_color(self.theme_manager.get_color('text_primary'))
        
        plt.tight_layout()
        return fig
    
    def create_severity_distribution(self, data: IDCAData) -> plt.Figure:
        """Create severity distribution chart and return figure"""
        fig, ax = self._setup_figure()
        
        # Count triggered rules by severity (fallback to Medium if missing)
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for rule in data.triggered_rules:
            sev = getattr(rule, 'severity', 'Medium') or 'Medium'
            if sev not in severity_counts:
                sev = 'Medium'
            severity_counts[sev] += 1
        
        severities = list(severity_counts.keys())
        counts = list(severity_counts.values())
        colors = [self.theme_manager.get_color('danger'),
                 self.theme_manager.get_color('warning'),
                 self.theme_manager.get_color('info'),
                 self.theme_manager.get_color('success')]
        
        bars = ax.bar(severities, counts, color=colors)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Triggered Rules by Severity', fontsize=16, pad=20)
        
        ax.tick_params(colors=self.theme_manager.get_color('text_primary'))
        ax.yaxis.label.set_color(self.theme_manager.get_color('text_primary'))
        ax.title.set_color(self.theme_manager.get_color('text_primary'))
        
        return fig
    
    def create_top_gaps_chart(self, data: IDCAData) -> plt.Figure:
        """Create top security gaps chart and return figure"""
        fig, ax = self._setup_figure(figsize=(10, 6))
        
        # Use undetected techniques as gaps; sort by criticality
        if not data.undetected_techniques:
            ax.text(0.5, 0.5, 'No security gaps identified', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=16, color=self.theme_manager.get_color('text_primary'))
            ax.axis('off')
            return fig
        
        crit_rank = {'Critical': 3, 'High': 2, 'Medium': 1, 'Low': 0, 'Kritik': 3, 'Yüksek': 2, 'Orta': 1, 'Düşük': 0}
        sorted_gaps = sorted(list(data.undetected_techniques), key=lambda t: crit_rank.get(t.criticality, 0), reverse=True)[:10]
        
        names = [f"{t.mitre_id} - {t.name[:40]}" + ("..." if len(t.name) > 40 else "") for t in sorted_gaps]
        y_pos = np.arange(len(names))
        colors = []
        for t in sorted_gaps:
            if t.criticality in ['Critical', 'Kritik']:
                colors.append(self.theme_manager.get_color('danger'))
            elif t.criticality in ['High', 'Yüksek']:
                colors.append(self.theme_manager.get_color('warning'))
            else:
                colors.append(self.theme_manager.get_color('info'))
        
        ax.barh(y_pos, [1]*len(names), color=colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9)
        ax.set_xlabel('Priority', fontsize=12)
        ax.set_title('Top Detection Gaps (Undetected Techniques)', fontsize=16, pad=20)
        ax.set_xlim(0, 1.2)
        ax.set_xticks([])
        
        for i, t in enumerate(sorted_gaps):
            ax.text(1.05, i, t.criticality, va='center', fontsize=10,
                   color=self.theme_manager.get_color('text_secondary'))
        
        ax.tick_params(colors=self.theme_manager.get_color('text_primary'))
        ax.xaxis.label.set_color(self.theme_manager.get_color('text_primary'))
        ax.title.set_color(self.theme_manager.get_color('text_primary'))
        
        plt.tight_layout()
        return fig
    
    def create_summary_dashboard(self, data: IDCAData) -> plt.Figure:
        """Create summary dashboard and return figure"""
        fig = plt.figure(figsize=(12, 8))
        fig.patch.set_facecolor(self.theme_manager.get_color('background') if not self.transparent else 'none')
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Key metrics
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        # Calculate metrics
        total_tests = data.test_results.total_rules
        passed_tests = data.test_results.triggered_rules
        coverage_pct = (data.test_results.coverage_rate)
        critical_findings = sum(1 for f in data.undetected_techniques if f.criticality in ['Critical', 'Kritik'])
        high_findings = sum(1 for f in data.undetected_techniques if f.criticality in ['High', 'Yüksek'])
        
        # Display metrics
        metrics_text = f"""
        Test Coverage: {coverage_pct:.1f}%    |    Total Rules: {total_tests}    |    
        Triggered: {passed_tests}    |    Critical Gaps: {critical_findings}    |    
        High Gaps: {high_findings}
        """
        ax1.text(0.5, 0.5, metrics_text, transform=ax1.transAxes,
                ha='center', va='center', fontsize=14,
                bbox=dict(boxstyle="round,pad=0.3", 
                         facecolor=self.theme_manager.get_color('surface'),
                         edgecolor=self.theme_manager.get_color('border')))
        
        # Test coverage pie
        ax2 = fig.add_subplot(gs[1, 0])
        if total_tests > 0:
            tested = data.test_results.tested_rules
            not_tested = total_tests - tested
            colors = [self.theme_manager.get_color('success'), 
                     self.theme_manager.get_color('error')]
            ax2.pie([tested, not_tested], labels=['Tested', 'Not Tested'], colors=colors,
                   autopct='%1.1f%%', startangle=90)
            ax2.set_title('Test Coverage', fontsize=12)
        else:
            ax2.text(0.5, 0.5, 'No data', transform=ax2.transAxes,
                    ha='center', va='center')
            ax2.axis('off')
        
        # Severity distribution of triggered rules
        ax3 = fig.add_subplot(gs[1, 1])
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for r in data.triggered_rules:
            sev = getattr(r, 'severity', 'Medium') or 'Medium'
            if sev not in severity_counts:
                sev = 'Medium'
            severity_counts[sev] += 1
        if sum(severity_counts.values()) > 0:
            ax3.bar(severity_counts.keys(), severity_counts.values(),
                   color=[self.theme_manager.get_color('danger'),
                         self.theme_manager.get_color('warning'),
                         self.theme_manager.get_color('info'),
                         self.theme_manager.get_color('success')])
            ax3.set_title('Triggered Rules by Severity', fontsize=12)
            ax3.set_ylabel('Count')
        else:
            ax3.text(0.5, 0.5, 'No triggered rules', transform=ax3.transAxes,
                    ha='center', va='center')
            ax3.axis('off')
        
        # MITRE coverage summary (top 5 by lowest success)
        ax4 = fig.add_subplot(gs[1:, 2])
        if data.mitre_tactics:
            items = sorted(list(data.mitre_tactics.items()), key=lambda x: x[1].success_rate)[:5]
            tactics = [name[:15] + '...' if len(name) > 15 else name for name, _ in items]
            coverage = [t.success_rate for _, t in items]
            ax4.barh(tactics, coverage)
            ax4.set_xlabel('Success %')
            ax4.set_title('Lowest Performing Tactics', fontsize=12)
            ax4.set_xlim(0, 100)
        else:
            ax4.text(0.5, 0.5, 'No MITRE data', transform=ax4.transAxes,
                    ha='center', va='center')
            ax4.axis('off')
        
        # Overall title
        fig.suptitle('Security Assessment Summary Dashboard', 
                    fontsize=18, color=self.theme_manager.get_color('text_primary'))
        
        # Apply theme to all axes
        for ax in [ax2, ax3, ax4]:
            if ax.get_visible():
                ax.set_facecolor(self.theme_manager.get_color('surface'))
                ax.tick_params(colors=self.theme_manager.get_color('text_primary'))
                ax.title.set_color(self.theme_manager.get_color('text_primary'))
                if hasattr(ax, 'xaxis') and ax.xaxis.label:
                    ax.xaxis.label.set_color(self.theme_manager.get_color('text_primary'))
                if hasattr(ax, 'yaxis') and ax.yaxis.label:
                    ax.yaxis.label.set_color(self.theme_manager.get_color('text_primary'))
        
        return fig