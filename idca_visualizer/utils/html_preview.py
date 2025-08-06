#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Preview Generator for IDCA Visualizer
Generates an HTML preview of the data and visualizations
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import base64
from io import BytesIO
# matplotlib imports removed for testing environment
from datetime import datetime


class HTMLPreviewGenerator:
    """Generates HTML preview of IDCA data and visualizations"""
    
    def __init__(self):
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDCA Visualizer Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
        .info {{ color: blue; }}
        .chart {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-badge.success {{ background: #d4edda; color: #155724; }}
        .status-badge.warning {{ background: #fff3cd; color: #856404; }}
        .status-badge.error {{ background: #f8d7da; color: #721c24; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            color: #6c757d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>IDCA Security Assessment Report Preview</h1>
    <p>Generated on: {timestamp}</p>
    
    {content}
    
</body>
</html>
"""
    
    def generate_preview(self, data: Dict[str, Any], output_path: str = None) -> str:
        """Generate HTML preview from data"""
        sections = []
        
        # General Information
        if 'general' in data:
            sections.append(self._generate_general_section(data['general']))
        
        # Test Results
        if 'test_results' in data:
            sections.append(self._generate_test_results_section(data['test_results']))
        
        # MITRE ATT&CK
        if 'mitre_tactics' in data:
            sections.append(self._generate_mitre_section(data['mitre_tactics']))
        
        # Rules
        if 'triggered_rules' in data or 'undetected_techniques' in data:
            sections.append(self._generate_rules_section(
                data.get('triggered_rules', []),
                data.get('undetected_techniques', [])
            ))
        
        # Recommendations
        if 'recommendations' in data:
            sections.append(self._generate_recommendations_section(data['recommendations']))
        
        # Generate visualizations
        sections.append(self._generate_visualizations_section(data))
        
        # Combine all sections
        content = '\n'.join(sections)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = self.html_template.format(
            timestamp=timestamp,
            content=content
        )
        
        # Save to file if path provided
        if output_path:
            Path(output_path).write_text(html, encoding='utf-8')
        
        return html
    
    def _generate_general_section(self, general: Dict) -> str:
        """Generate general information section"""
        return f"""
    <div class="section">
        <h2>📋 General Information</h2>
        <table>
            <tr><th>Company Name</th><td>{general.get('company_name', 'N/A')}</td></tr>
            <tr><th>Report Date</th><td>{general.get('report_date', 'N/A')}</td></tr>
            <tr><th>Tester Name</th><td>{general.get('tester_name', 'N/A')}</td></tr>
            <tr><th>Manager Name</th><td>{general.get('manager_name', 'N/A')}</td></tr>
            <tr><th>Manager Title</th><td>{general.get('manager_title', 'N/A')}</td></tr>
        </table>
    </div>
"""
    
    def _generate_test_results_section(self, results: Dict) -> str:
        """Generate test results section"""
        total = results.get('total_rules', 0)
        tested = results.get('tested_rules', 0)
        triggered = results.get('triggered_rules', 0)
        
        test_rate = (tested / total * 100) if total > 0 else 0
        success_rate = (triggered / tested * 100) if tested > 0 else 0
        
        return f"""
    <div class="section">
        <h2>📊 Test Results Summary</h2>
        <div class="grid">
            <div class="metric">
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total Rules</div>
            </div>
            <div class="metric">
                <div class="metric-value">{tested}</div>
                <div class="metric-label">Tested Rules</div>
            </div>
            <div class="metric">
                <div class="metric-value">{triggered}</div>
                <div class="metric-label">Triggered Rules</div>
            </div>
            <div class="metric">
                <div class="metric-value">{test_rate:.1f}%</div>
                <div class="metric-label">Test Coverage</div>
            </div>
            <div class="metric">
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
    </div>
"""
    
    def _generate_mitre_section(self, tactics: Dict) -> str:
        """Generate MITRE ATT&CK section"""
        rows = []
        for tactic_name, tactic_data in tactics.items():
            test_count = tactic_data.get('test_count', 0)
            triggered_count = tactic_data.get('triggered_count', 0)
            success_rate = (triggered_count / test_count * 100) if test_count > 0 else 0
            
            rate_class = 'success' if success_rate >= 70 else 'warning' if success_rate >= 40 else 'error'
            
            rows.append(f"""
            <tr>
                <td>{tactic_name}</td>
                <td>{test_count}</td>
                <td>{triggered_count}</td>
                <td class="{rate_class}">{success_rate:.1f}%</td>
            </tr>
""")
        
        return f"""
    <div class="section">
        <h2>🎯 MITRE ATT&CK Coverage</h2>
        <table>
            <thead>
                <tr>
                    <th>Tactic Name</th>
                    <th>Tested</th>
                    <th>Triggered</th>
                    <th>Success Rate</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
"""
    
    def _generate_rules_section(self, triggered: List, undetected: List) -> str:
        """Generate rules section"""
        triggered_rows = []
        for rule in triggered:
            triggered_rows.append(f"""
            <tr>
                <td>{rule.get('name', 'N/A')}</td>
                <td>{rule.get('mitre_id', 'N/A')}</td>
                <td>{rule.get('tactic', 'N/A')}</td>
                <td>{rule.get('confidence', 0)}%</td>
            </tr>
""")
        
        undetected_rows = []
        for tech in undetected:
            criticality = tech.get('criticality', 'Medium')
            crit_class = 'error' if criticality == 'Critical' else 'warning' if criticality == 'High' else 'info'
            
            undetected_rows.append(f"""
            <tr>
                <td>{tech.get('mitre_id', 'N/A')}</td>
                <td>{tech.get('name', 'N/A')}</td>
                <td>{tech.get('tactic', 'N/A')}</td>
                <td><span class="status-badge {crit_class}">{criticality}</span></td>
            </tr>
""")
        
        return f"""
    <div class="section">
        <h2>🛡️ Detection Rules</h2>
        
        <h3>✅ Triggered Rules ({len(triggered)})</h3>
        <table>
            <thead>
                <tr>
                    <th>Rule Name</th>
                    <th>MITRE ID</th>
                    <th>Tactic</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
                {''.join(triggered_rows) if triggered_rows else '<tr><td colspan="4">No triggered rules</td></tr>'}
            </tbody>
        </table>
        
        <h3>❌ Undetected Techniques ({len(undetected)})</h3>
        <table>
            <thead>
                <tr>
                    <th>MITRE ID</th>
                    <th>Technique Name</th>
                    <th>Tactic</th>
                    <th>Criticality</th>
                </tr>
            </thead>
            <tbody>
                {''.join(undetected_rows) if undetected_rows else '<tr><td colspan="4">No undetected techniques</td></tr>'}
            </tbody>
        </table>
    </div>
"""
    
    def _generate_recommendations_section(self, recommendations: List) -> str:
        """Generate recommendations section"""
        rows = []
        for i, rec in enumerate(recommendations, 1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{rec.get('category', 'N/A')}</td>
                <td>{rec.get('text', 'N/A')}</td>
            </tr>
""")
        
        return f"""
    <div class="section">
        <h2>💡 Recommendations</h2>
        <table>
            <thead>
                <tr>
                    <th>Priority</th>
                    <th>Category</th>
                    <th>Recommendation</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows) if rows else '<tr><td colspan="3">No recommendations</td></tr>'}
            </tbody>
        </table>
    </div>
"""
    
    def _generate_visualizations_section(self, data: Dict) -> str:
        """Generate sample visualizations"""
        charts = []
        
        # Test Coverage Chart
        if 'test_results' in data:
            chart_data = self._create_test_coverage_chart(data['test_results'])
            if chart_data:
                charts.append(f'<div class="chart"><h3>Test Coverage Analysis</h3><img src="{chart_data}" alt="Test Coverage"></div>')
        
        # MITRE Coverage Chart
        if 'mitre_tactics' in data:
            chart_data = self._create_mitre_coverage_chart(data['mitre_tactics'])
            if chart_data:
                charts.append(f'<div class="chart"><h3>MITRE ATT&CK Coverage</h3><img src="{chart_data}" alt="MITRE Coverage"></div>')
        
        return f"""
    <div class="section">
        <h2>📈 Visualizations</h2>
        {''.join(charts) if charts else '<p>No visualizations available</p>'}
    </div>
"""
    
    def _create_test_coverage_chart(self, test_results: Dict) -> str:
        """Create test coverage pie chart"""
        # Disabled in testing environment - matplotlib not available
        return None
    
    def _create_mitre_coverage_chart(self, mitre_tactics: Dict) -> str:
        """Create MITRE coverage bar chart"""
        # Disabled in testing environment - matplotlib not available
        return None