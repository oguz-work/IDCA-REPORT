#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Import/Export Handler for IDCA Visualizer
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox
# pandas import removed for testing environment


@dataclass
class CSVMapping:
    """Stores CSV column to data field mappings"""
    source_column: str
    target_field: str
    data_type: str = 'string'
    required: bool = False
    default_value: Any = ''


class CSVMappingDialog(tk.Toplevel):
    """Dialog for mapping CSV columns to data fields"""
    
    def __init__(self, parent, csv_columns: List[str], target_fields: Dict[str, List[str]]):
        super().__init__(parent)
        self.title("CSV Field Mapping")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self.csv_columns = csv_columns
        self.target_fields = target_fields
        self.mappings = {}
        self.result = None
        
        self._create_ui()
        self._center_window()
    
    def _center_window(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        """Create the mapping interface"""
        # Instructions
        info_frame = ttk.Frame(self, padding=10)
        info_frame.pack(fill='x')
        
        ttk.Label(info_frame, text="Map CSV columns to data fields:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text="Select which CSV column corresponds to each field",
                 font=('Arial', 9)).pack(anchor='w')
        
        # Mapping area
        mapping_frame = ttk.Frame(self, padding=10)
        mapping_frame.pack(fill='both', expand=True)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(mapping_frame, bg='white')
        scrollbar = ttk.Scrollbar(mapping_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create mapping widgets
        self.mapping_widgets = {}
        
        for category, fields in self.target_fields.items():
            # Category label
            category_frame = ttk.LabelFrame(scrollable_frame, text=category, padding=10)
            category_frame.pack(fill='x', padx=5, pady=5)
            
            for field in fields:
                field_frame = ttk.Frame(category_frame)
                field_frame.pack(fill='x', pady=2)
                
                # Field label
                ttk.Label(field_frame, text=f"{field}:", width=25).pack(side='left')
                
                # CSV column dropdown
                var = tk.StringVar()
                combo = ttk.Combobox(field_frame, textvariable=var, 
                                    values=['<None>'] + self.csv_columns,
                                    state='readonly', width=30)
                combo.set('<None>')
                combo.pack(side='left', padx=5)
                
                self.mapping_widgets[f"{category}.{field}"] = var
        
        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Import", command=self._on_import).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side='right')
    
    def _on_import(self):
        """Process the mappings and close dialog"""
        self.result = {}
        for key, var in self.mapping_widgets.items():
            value = var.get()
            if value and value != '<None>':
                self.result[key] = value
        self.destroy()
    
    def _on_cancel(self):
        """Cancel without saving"""
        self.result = None
        self.destroy()


class CSVHandler:
    """Handles CSV import and export operations"""
    
    @staticmethod
    def detect_delimiter(file_path: str) -> str:
        """Auto-detect CSV delimiter"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            # Check common delimiters
            for delimiter in [',', ';', '\t', '|']:
                if delimiter in first_line:
                    return delimiter
        return ','
    
    @staticmethod
    def read_csv(file_path: str, delimiter: str = None) -> Tuple[List[str], List[Dict[str, str]]]:
        """Read CSV file and return headers and data"""
        if delimiter is None:
            delimiter = CSVHandler.detect_delimiter(file_path)
        
        data = []
        headers = []
        
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            headers = reader.fieldnames
            for row in reader:
                data.append(row)
        
        return headers, data
    
    @staticmethod
    def import_mitre_tactics(csv_data: List[Dict[str, str]], mappings: Dict[str, str]) -> Dict[str, Dict]:
        """Import MITRE tactics from CSV data"""
        tactics = {}
        
        tactic_name_col = mappings.get('MITRE.Tactic Name')
        test_count_col = mappings.get('MITRE.Test Count')
        triggered_count_col = mappings.get('MITRE.Triggered Count')
        
        if not tactic_name_col:
            return tactics
        
        for row in csv_data:
            tactic_name = row.get(tactic_name_col, '').strip()
            if tactic_name:
                tactics[tactic_name] = {
                    'name': tactic_name,
                    'test_count': int(row.get(test_count_col, 0)) if test_count_col else 0,
                    'triggered_count': int(row.get(triggered_count_col, 0)) if triggered_count_col else 0
                }
        
        return tactics
    
    @staticmethod
    def import_triggered_rules(csv_data: List[Dict[str, str]], mappings: Dict[str, str]) -> List[Dict]:
        """Import triggered rules from CSV data"""
        rules = []
        
        rule_name_col = mappings.get('Rules.Rule Name')
        mitre_id_col = mappings.get('Rules.MITRE ID')
        tactic_col = mappings.get('Rules.Tactic')
        confidence_col = mappings.get('Rules.Confidence')
        
        if not rule_name_col:
            return rules
        
        for row in csv_data:
            rule_name = row.get(rule_name_col, '').strip()
            if rule_name:
                rules.append({
                    'name': rule_name,
                    'mitre_id': row.get(mitre_id_col, '') if mitre_id_col else '',
                    'tactic': row.get(tactic_col, '') if tactic_col else '',
                    'confidence': int(row.get(confidence_col, 0)) if confidence_col else 0
                })
        
        return rules
    
    @staticmethod
    def import_undetected_techniques(csv_data: List[Dict[str, str]], mappings: Dict[str, str]) -> List[Dict]:
        """Import undetected techniques from CSV data"""
        techniques = []
        
        mitre_id_col = mappings.get('Undetected.MITRE ID')
        technique_name_col = mappings.get('Undetected.Technique Name')
        tactic_col = mappings.get('Undetected.Tactic')
        criticality_col = mappings.get('Undetected.Criticality')
        
        if not mitre_id_col:
            return techniques
        
        for row in csv_data:
            mitre_id = row.get(mitre_id_col, '').strip()
            if mitre_id:
                techniques.append({
                    'mitre_id': mitre_id,
                    'name': row.get(technique_name_col, '') if technique_name_col else '',
                    'tactic': row.get(tactic_col, '') if tactic_col else '',
                    'criticality': row.get(criticality_col, 'Medium') if criticality_col else 'Medium'
                })
        
        return techniques
    
    @staticmethod
    def export_to_csv(data: Dict[str, Any], file_path: str):
        """Export data to CSV format"""
        # Create separate CSV files for different data types
        base_path = Path(file_path).parent
        base_name = Path(file_path).stem
        
        # Export MITRE tactics
        if 'mitre_tactics' in data and data['mitre_tactics']:
            mitre_path = base_path / f"{base_name}_mitre_tactics.csv"
            with open(mitre_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Tactic Name', 'Test Count', 'Triggered Count', 'Success Rate %'])
                for tactic_data in data['mitre_tactics'].values():
                    success_rate = (tactic_data['triggered_count'] / tactic_data['test_count'] * 100) if tactic_data['test_count'] > 0 else 0
                    writer.writerow([
                        tactic_data['name'],
                        tactic_data['test_count'],
                        tactic_data['triggered_count'],
                        f"{success_rate:.1f}"
                    ])
        
        # Export triggered rules
        if 'triggered_rules' in data and data['triggered_rules']:
            rules_path = base_path / f"{base_name}_triggered_rules.csv"
            with open(rules_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Rule Name', 'MITRE ID', 'Tactic', 'Confidence %'])
                for rule in data['triggered_rules']:
                    writer.writerow([
                        rule.get('name', ''),
                        rule.get('mitre_id', ''),
                        rule.get('tactic', ''),
                        rule.get('confidence', '')
                    ])
        
        # Export undetected techniques
        if 'undetected_techniques' in data and data['undetected_techniques']:
            undetected_path = base_path / f"{base_name}_undetected_techniques.csv"
            with open(undetected_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['MITRE ID', 'Technique Name', 'Tactic', 'Criticality'])
                for tech in data['undetected_techniques']:
                    writer.writerow([
                        tech.get('mitre_id', ''),
                        tech.get('name', ''),
                        tech.get('tactic', ''),
                        tech.get('criticality', '')
                    ])
        
        return True