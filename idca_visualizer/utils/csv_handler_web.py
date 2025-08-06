#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Import/Export Handler for IDCA Visualizer - Web Version (No GUI dependencies)
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from io import StringIO


@dataclass
class CSVMapping:
    """Stores CSV column to data field mappings"""
    source_column: str
    target_field: str
    data_type: str = 'string'
    required: bool = False
    default_value: Any = ''


class CSVHandler:
    """Handles CSV import and export operations without GUI dependencies"""
    
    def __init__(self):
        self.supported_delimiters = [',', ';', '\t', '|']
        
    def detect_delimiter(self, sample_text: str) -> str:
        """Auto-detect CSV delimiter from sample text"""
        lines = sample_text.strip().split('\n')[:5]  # Check first 5 lines
        
        delimiter_counts = {delim: 0 for delim in self.supported_delimiters}
        
        for line in lines:
            for delim in self.supported_delimiters:
                delimiter_counts[delim] += line.count(delim)
        
        # Return delimiter with highest count
        return max(delimiter_counts.items(), key=lambda x: x[1])[0]
    
    def read_csv(self, file_content: str, delimiter: Optional[str] = None) -> Tuple[List[str], List[Dict]]:
        """Read CSV content and return headers and rows"""
        if delimiter is None:
            delimiter = self.detect_delimiter(file_content)
        
        csv_reader = csv.DictReader(StringIO(file_content), delimiter=delimiter)
        headers = csv_reader.fieldnames
        rows = list(csv_reader)
        
        return headers, rows
    
    def suggest_mappings(self, headers: List[str]) -> Dict[str, str]:
        """Suggest field mappings based on CSV headers"""
        mappings = {}
        
        # Common header patterns for IDCA data
        patterns = {
            'company_name': ['company', 'organization', 'org_name', 'client'],
            'report_date': ['date', 'report_date', 'assessment_date'],
            'tester_name': ['tester', 'analyst', 'pentester', 'assessor'],
            'manager_name': ['manager', 'supervisor', 'lead'],
            'manager_title': ['title', 'position', 'role'],
            'total_rules': ['total', 'total_rules', 'rule_count'],
            'tested_rules': ['tested', 'tested_rules', 'test_count'],
            'triggered_rules': ['triggered', 'detected', 'triggered_rules'],
            'tactic_name': ['tactic', 'attack', 'mitre_tactic', 'technique_name'],
            'test_count': ['test', 'tested', 'test_count', 'tests'],
            'triggered_count': ['triggered', 'detected', 'success', 'triggered_count'],
            'mitre_id': ['mitre', 'id', 'mitre_id', 'technique_id', 'attack_id'],
            'rule_name': ['rule', 'name', 'rule_name', 'detection', 'alert'],
            'severity': ['severity', 'priority', 'level', 'criticality'],
            'technique_name': ['technique', 'name', 'technique_name', 'attack_technique'],
            'description': ['description', 'desc', 'details', 'notes']
        }
        
        for header in headers:
            header_lower = header.lower().strip()
            for field, patterns_list in patterns.items():
                for pattern in patterns_list:
                    if pattern in header_lower or header_lower in pattern:
                        mappings[field] = header
                        break
        
        return mappings
    
    def import_data(self, file_content: str, mappings: Dict[str, str]) -> Dict[str, Any]:
        """Import CSV data using provided mappings"""
        headers, rows = self.read_csv(file_content)
        
        imported_data = {
            'general': {},
            'test_results': {},
            'mitre_tactics': [],
            'triggered_rules': [],
            'undetected_techniques': [],
            'recommendations': []
        }
        
        # Process each row based on mappings
        for row in rows:
            # Determine data type and process accordingly
            if 'tactic_name' in mappings and mappings['tactic_name'] in row:
                # MITRE Tactics data
                tactic = {
                    'name': row.get(mappings.get('tactic_name', ''), ''),
                    'test_count': int(row.get(mappings.get('test_count', ''), 0) or 0),
                    'triggered_count': int(row.get(mappings.get('triggered_count', ''), 0) or 0)
                }
                if tactic['name']:
                    imported_data['mitre_tactics'].append(tactic)
            
            elif 'rule_name' in mappings and mappings['rule_name'] in row and row.get(mappings['rule_name']):
                # Triggered Rules data
                rule = {
                    'mitre_id': row.get(mappings.get('mitre_id', ''), ''),
                    'rule_name': row.get(mappings.get('rule_name', ''), ''),
                    'severity': row.get(mappings.get('severity', ''), 'Medium')
                }
                if rule['rule_name']:
                    imported_data['triggered_rules'].append(rule)
            
            elif 'technique_name' in mappings and mappings['technique_name'] in row:
                # Undetected Techniques data
                technique = {
                    'mitre_id': row.get(mappings.get('mitre_id', ''), ''),
                    'technique_name': row.get(mappings.get('technique_name', ''), ''),
                    'description': row.get(mappings.get('description', ''), '')
                }
                if technique['technique_name']:
                    imported_data['undetected_techniques'].append(technique)
        
        # Import general info if present
        if rows and any(field in mappings for field in ['company_name', 'report_date', 'tester_name']):
            first_row = rows[0]
            general_fields = ['company_name', 'report_date', 'tester_name', 'manager_name', 'manager_title']
            for field in general_fields:
                if field in mappings and mappings[field] in first_row:
                    imported_data['general'][field] = first_row[mappings[field]]
        
        # Import test results if present
        if rows and any(field in mappings for field in ['total_rules', 'tested_rules', 'triggered_rules']):
            first_row = rows[0]
            test_fields = ['total_rules', 'tested_rules', 'triggered_rules']
            for field in test_fields:
                if field in mappings and mappings[field] in first_row:
                    try:
                        imported_data['test_results'][field] = int(first_row[mappings[field]] or 0)
                    except ValueError:
                        imported_data['test_results'][field] = 0
        
        return imported_data
    
    def export_to_csv(self, data: Dict[str, Any], output_format: str = 'separate') -> Dict[str, str]:
        """Export data to CSV format(s)
        
        Args:
            data: The data dictionary to export
            output_format: 'separate' for multiple files, 'combined' for single file
            
        Returns:
            Dictionary with filename as key and CSV content as value
        """
        csv_files = {}
        
        if output_format == 'separate':
            # Export MITRE tactics
            if 'mitre_tactics' in data and data['mitre_tactics']:
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['Tactic Name', 'Test Count', 'Triggered Count', 'Success Rate'])
                
                for tactic in data['mitre_tactics']:
                    success_rate = 0
                    if tactic.get('test_count', 0) > 0:
                        success_rate = (tactic.get('triggered_count', 0) / tactic['test_count']) * 100
                    
                    writer.writerow([
                        tactic.get('name', ''),
                        tactic.get('test_count', 0),
                        tactic.get('triggered_count', 0),
                        f"{success_rate:.1f}%"
                    ])
                
                csv_files['mitre_tactics.csv'] = output.getvalue()
            
            # Export triggered rules
            if 'triggered_rules' in data and data['triggered_rules']:
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['MITRE ID', 'Rule Name', 'Severity'])
                
                for rule in data['triggered_rules']:
                    writer.writerow([
                        rule.get('mitre_id', ''),
                        rule.get('rule_name', ''),
                        rule.get('severity', 'Medium')
                    ])
                
                csv_files['triggered_rules.csv'] = output.getvalue()
            
            # Export undetected techniques
            if 'undetected_techniques' in data and data['undetected_techniques']:
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['MITRE ID', 'Technique Name', 'Description'])
                
                for technique in data['undetected_techniques']:
                    writer.writerow([
                        technique.get('mitre_id', ''),
                        technique.get('technique_name', ''),
                        technique.get('description', '')
                    ])
                
                csv_files['undetected_techniques.csv'] = output.getvalue()
            
            # Export recommendations
            if 'recommendations' in data and data['recommendations']:
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['Priority', 'Description'])
                
                for rec in data['recommendations']:
                    writer.writerow([
                        rec.get('priority', 'Medium'),
                        rec.get('description', '')
                    ])
                
                csv_files['recommendations.csv'] = output.getvalue()
        
        else:  # combined format
            output = StringIO()
            writer = csv.writer(output)
            
            # Write general info
            writer.writerow(['Section', 'Field', 'Value'])
            
            if 'general' in data:
                for key, value in data['general'].items():
                    writer.writerow(['General Info', key.replace('_', ' ').title(), value])
            
            if 'test_results' in data:
                for key, value in data['test_results'].items():
                    writer.writerow(['Test Results', key.replace('_', ' ').title(), value])
            
            writer.writerow([])  # Empty row
            
            # Write all other data in sections
            if 'mitre_tactics' in data and data['mitre_tactics']:
                writer.writerow(['MITRE Tactics'])
                writer.writerow(['Tactic Name', 'Test Count', 'Triggered Count'])
                for tactic in data['mitre_tactics']:
                    writer.writerow([
                        tactic.get('name', ''),
                        tactic.get('test_count', 0),
                        tactic.get('triggered_count', 0)
                    ])
                writer.writerow([])
            
            csv_files['idca_report.csv'] = output.getvalue()
        
        return csv_files
    
    def validate_import(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate imported data"""
        errors = []
        
        # Validate MITRE tactics
        if 'mitre_tactics' in data:
            for i, tactic in enumerate(data['mitre_tactics']):
                if not tactic.get('name'):
                    errors.append(f"MITRE tactic at row {i+1} missing name")
                if tactic.get('triggered_count', 0) > tactic.get('test_count', 0):
                    errors.append(f"MITRE tactic '{tactic.get('name', 'Unknown')}' has triggered count > test count")
        
        # Validate MITRE IDs
        mitre_pattern = r'^(T|TA)\d{4}(\.\d{3})?$'
        import re
        
        for rule in data.get('triggered_rules', []):
            if rule.get('mitre_id') and not re.match(mitre_pattern, rule['mitre_id']):
                errors.append(f"Invalid MITRE ID format: {rule['mitre_id']}")
        
        for technique in data.get('undetected_techniques', []):
            if technique.get('mitre_id') and not re.match(mitre_pattern, technique['mitre_id']):
                errors.append(f"Invalid MITRE ID format: {technique['mitre_id']}")
        
        # Validate test results
        test_results = data.get('test_results', {})
        if test_results:
            total = test_results.get('total_rules', 0)
            tested = test_results.get('tested_rules', 0)
            triggered = test_results.get('triggered_rules', 0)
            
            if tested > total:
                errors.append("Tested rules count exceeds total rules")
            if triggered > tested:
                errors.append("Triggered rules count exceeds tested rules")
        
        return len(errors) == 0, errors