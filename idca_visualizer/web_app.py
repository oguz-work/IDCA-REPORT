#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCA Security Assessment Report Visualizer - Web Application
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import json
import os
from pathlib import Path
from datetime import datetime
import csv
import io
import base64
from typing import Dict, List, Any, Optional

# Import project modules (without tkinter dependencies)
from data.models import IDCAData
from core.config import STATUS_COLORS, STATUS_ICONS
from utils.validators import InputValidator

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'idca-visualizer-secret-key'

# Global data storage (in production, use proper database)
current_data = IDCAData()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    """Handle data retrieval and updates"""
    global current_data
    
    if request.method == 'GET':
        return jsonify(current_data.to_dict())
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'status': 'error', 'message': 'No JSON data provided or invalid content-type'}), 400
            
            # Update general info
            if 'general' in data:
                for key, value in data['general'].items():
                    setattr(current_data.general, key, value)
            
            # Update test results
            if 'test_results' in data:
                for key, value in data['test_results'].items():
                    setattr(current_data.test_results, key, value)
            
            # Update MITRE tactics
            if 'mitre_tactics' in data:
                current_data.mitre_tactics = []
                for tactic in data['mitre_tactics']:
                    current_data.add_mitre_tactic(
                        tactic['name'],
                        int(tactic['test_count']),
                        int(tactic['triggered_count'])
                    )
            
            # Update triggered rules
            if 'triggered_rules' in data:
                current_data.triggered_rules = []
                for rule in data['triggered_rules']:
                    current_data.add_triggered_rule(
                        rule['mitre_id'],
                        rule['rule_name'],
                        rule['severity']
                    )
            
            # Update undetected techniques
            if 'undetected_techniques' in data:
                current_data.undetected_techniques = []
                for technique in data['undetected_techniques']:
                    current_data.add_undetected_technique(
                        technique['mitre_id'],
                        technique['technique_name'],
                        technique['description']
                    )
            
            # Update recommendations
            if 'recommendations' in data:
                current_data.recommendations = []
                for rec in data['recommendations']:
                    current_data.add_recommendation(
                        rec['priority'],
                        rec['description']
                    )
            
            return jsonify({'status': 'success', 'message': 'Data updated successfully'})
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import data from CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Use the CSV handler
        from utils.csv_handler_web import CSVHandler
        csv_handler = CSVHandler()
        
        # Read the CSV content
        file_content = file.stream.read().decode("UTF8")
        headers, rows = csv_handler.read_csv(file_content)
        
        imported_data = {
            'headers': headers,
            'rows': rows,
            'suggested_mappings': csv_handler.suggest_mappings(headers)
        }
        
        return jsonify({'status': 'success', 'data': imported_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export data to CSV files"""
    try:
        # Create a zip file with multiple CSVs
        import zipfile
        from io import BytesIO
        
        memory_file = BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Export MITRE tactics
            mitre_csv = io.StringIO()
            mitre_writer = csv.writer(mitre_csv)
            mitre_writer.writerow(['Tactic Name', 'Test Count', 'Triggered Count', 'Success Rate'])
            
            for tactic in current_data.mitre_tactics.values():
                mitre_writer.writerow([
                    tactic.name,
                    tactic.test_count,
                    tactic.triggered_count,
                    f"{tactic.success_rate:.1f}%"
                ])
            
            zf.writestr('mitre_tactics.csv', mitre_csv.getvalue())
            
            # Export triggered rules
            rules_csv = io.StringIO()
            rules_writer = csv.writer(rules_csv)
            rules_writer.writerow(['MITRE ID', 'Rule Name', 'Severity'])
            
            for rule in current_data.triggered_rules:
                rules_writer.writerow([
                    getattr(rule, 'mitre_id', ''),
                    getattr(rule, 'name', getattr(rule, 'rule_name', '')),
                    getattr(rule, 'severity', 'Medium')
                ])
            
            zf.writestr('triggered_rules.csv', rules_csv.getvalue())
            
            # Export undetected techniques
            undetected_csv = io.StringIO()
            undetected_writer = csv.writer(undetected_csv)
            undetected_writer.writerow(['MITRE ID', 'Technique Name', 'Description'])
            
            for technique in current_data.undetected_techniques:
                undetected_writer.writerow([
                    getattr(technique, 'mitre_id', ''),
                    getattr(technique, 'name', getattr(technique, 'technique_name', '')),
                    getattr(technique, 'description', '')
                ])
            
            zf.writestr('undetected_techniques.csv', undetected_csv.getvalue())
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'idca_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/visualizations/<viz_type>')
def get_visualization(viz_type):
    """Generate and return visualization as base64 image"""
    try:
        # Import matplotlib only when needed
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from core.visualizations import VisualizationGenerator
        from themes.theme_manager import ThemeManager
        
        theme_manager = ThemeManager()
        viz_gen = VisualizationGenerator(theme_manager)
        
        # Generate the requested visualization
        fig = None
        if viz_type == 'coverage':
            fig = viz_gen.create_test_coverage_chart(current_data)
        elif viz_type == 'mitre_heatmap':
            fig = viz_gen.create_mitre_heatmap(current_data)
        elif viz_type == 'severity':
            fig = viz_gen.create_severity_distribution(current_data)
        elif viz_type == 'top_gaps':
            fig = viz_gen.create_top_gaps_chart(current_data)
        elif viz_type == 'summary':
            fig = viz_gen.create_summary_dashboard(current_data)
        
        if fig:
            # Convert to base64
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close(fig)
            
            return jsonify({
                'status': 'success',
                'image': f'data:image/png;base64,{image_base64}'
            })
        else:
            return jsonify({'status': 'error', 'message': 'Invalid visualization type'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_data():
    """Validate input data"""
    try:
        data = request.get_json()
        field_type = data.get('type')
        value = data.get('value')
        field_name = data.get('field')
        
        validator = InputValidator()
        
        if field_type == 'mitre_id':
            is_valid = validator.validate_mitre_id(value)
        elif field_type == 'numeric':
            is_valid = validator.validate_numeric(value, allow_negative=False)
        elif field_type == 'required':
            is_valid = validator.validate_required(value)
        else:
            is_valid = True
        
        return jsonify({
            'status': 'success',
            'valid': is_valid,
            'message': 'Valid' if is_valid else f'Invalid {field_type}'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400



if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Run the app
    import os
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)