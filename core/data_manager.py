"""
IDCA Security Assessment - Data Management
==========================================
Handles data validation, storage, and file operations.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import tkinter.messagebox as messagebox

class DataValidator:
    """Validates IDCA data according to business rules"""
    
    @staticmethod
    def validate_test_results(data: Dict[str, Any]) -> List[str]:
        """Validate test results data"""
        errors = []
        
        total = data.get('total_rules', 0)
        tested = data.get('tested_rules', 0)
        triggered = data.get('triggered_rules', 0)
        
        if not isinstance(total, (int, float)) or total <= 0:
            errors.append("Toplam kural sayısı pozitif bir sayı olmalı")
        
        if not isinstance(tested, (int, float)) or tested < 0:
            errors.append("Test edilen kural sayısı negatif olamaz")
        
        if not isinstance(triggered, (int, float)) or triggered < 0:
            errors.append("Tetiklenen kural sayısı negatif olamaz")
        
        if tested > total:
            errors.append("Test edilen kural sayısı toplam kurattan fazla olamaz")
        
        if triggered > tested:
            errors.append("Tetiklenen kural sayısı test edilen kurattan fazla olamaz")
        
        return errors
    
    @staticmethod
    def validate_mitre_tactics(data: Dict[str, Any]) -> List[str]:
        """Validate MITRE ATT&CK tactics data"""
        errors = []
        
        for tactic, values in data.items():
            if not isinstance(values, dict):
                errors.append(f"MITRE taktik '{tactic}' verisi geçersiz format")
                continue
            
            test = values.get('test', 0)
            triggered = values.get('triggered', 0)
            
            if test < 0:
                errors.append(f"'{tactic}' taktik için test sayısı negatif olamaz")
            
            if triggered < 0:
                errors.append(f"'{tactic}' taktik için tetiklenen sayısı negatif olamaz")
            
            if triggered > test:
                errors.append(f"'{tactic}' taktik için tetiklenen > test edilen olamaz")
        
        return errors
    
    @staticmethod
    def validate_triggered_rules(data: List[Dict[str, Any]]) -> List[str]:
        """Validate triggered rules data"""
        errors = []
        
        for i, rule in enumerate(data, 1):
            if not rule.get('name', '').strip():
                errors.append(f"Tetiklenen kural {i}: Kural adı boş olamaz")
            
            if not rule.get('mitre', '').strip():
                errors.append(f"Tetiklenen kural {i}: MITRE ID boş olamaz")
            
            confidence = rule.get('confidence', '')
            if confidence:
                try:
                    conf_val = float(str(confidence).replace('%', ''))
                    if not 0 <= conf_val <= 100:
                        errors.append(f"Tetiklenen kural {i}: Güven skoru 0-100 arası olmalı")
                except ValueError:
                    errors.append(f"Tetiklenen kural {i}: Güven skoru sayısal olmalı")
        
        return errors
    
    @staticmethod
    def validate_general_info(data: Dict[str, Any]) -> List[str]:
        """Validate general information"""
        errors = []
        
        required_fields = ['company_name', 'report_date', 'prepared_by']
        for field in required_fields:
            if not data.get(field, '').strip():
                field_names = {
                    'company_name': 'Kurum/Şirket Adı',
                    'report_date': 'Rapor Tarihi',
                    'prepared_by': 'Hazırlayan'
                }
                errors.append(f"{field_names[field]} boş olamaz")
        
        return errors


class DataManager:
    """Manages IDCA data operations"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.reset_data()
    
    def reset_data(self):
        """Reset data to initial state"""
        self.data = {
            'general': {
                'company_name': '',
                'report_date': '',
                'prepared_by': '',
                'report_id': '',
                'report_title': '',
                'classification': ''
            },
            'test_results': {
                'total_rules': 0,
                'tested_rules': 0,
                'triggered_rules': 0,
                'not_tested': 0,
                'failed': 0,
                'success_rate': 0.0,
                'coverage_rate': 0.0
            },
            'mitre_tactics': {},
            'triggered_rules': [],
            'undetected_techniques': [],
            'recommendations': []
        }
    
    def update_general_info(self, info: Dict[str, str]):
        """Update general information"""
        self.data['general'].update(info)
    
    def update_test_results(self, results: Dict[str, Any]):
        """Update test results and calculate derived values"""
        self.data['test_results'].update(results)
        self._calculate_derived_test_values()
    
    def _calculate_derived_test_values(self):
        """Calculate derived test values"""
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        triggered = self.data['test_results']['triggered_rules']
        
        # Calculate derived values
        self.data['test_results']['not_tested'] = max(0, total - tested)
        self.data['test_results']['failed'] = max(0, tested - triggered)
        
        # Calculate rates
        if tested > 0:
            self.data['test_results']['success_rate'] = (triggered / tested) * 100
        else:
            self.data['test_results']['success_rate'] = 0.0
        
        if total > 0:
            self.data['test_results']['coverage_rate'] = (tested / total) * 100
        else:
            self.data['test_results']['coverage_rate'] = 0.0
    
    def update_mitre_tactics(self, tactics: Dict[str, Dict[str, Any]]):
        """Update MITRE tactics data"""
        for tactic, values in tactics.items():
            if values.get('test', 0) > 0:
                rate = (values.get('triggered', 0) / values['test']) * 100
                values['rate'] = round(rate, 1)
        
        self.data['mitre_tactics'] = tactics
    
    def update_triggered_rules(self, rules: List[Dict[str, Any]]):
        """Update triggered rules data"""
        self.data['triggered_rules'] = rules
    
    def update_undetected_techniques(self, techniques: List[Dict[str, Any]]):
        """Update undetected techniques data"""
        self.data['undetected_techniques'] = techniques
    
    def update_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Update recommendations data"""
        self.data['recommendations'] = recommendations
    
    def validate_all_data(self) -> List[str]:
        """Validate all data and return list of errors"""
        all_errors = []
        
        # Validate each section
        all_errors.extend(self.validator.validate_general_info(self.data['general']))
        all_errors.extend(self.validator.validate_test_results(self.data['test_results']))
        all_errors.extend(self.validator.validate_mitre_tactics(self.data['mitre_tactics']))
        all_errors.extend(self.validator.validate_triggered_rules(self.data['triggered_rules']))
        
        return all_errors
    
    def get_data(self) -> Dict[str, Any]:
        """Get complete data"""
        return self.data.copy()
    
    def set_data(self, data: Dict[str, Any]):
        """Set complete data"""
        self.data = data.copy()
        # Recalculate derived values
        self._calculate_derived_test_values()
    
    def save_to_file(self, filepath: str) -> bool:
        """Save data to JSON file"""
        try:
            # Add metadata
            save_data = self.data.copy()
            save_data['_metadata'] = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'application': 'IDCA Security Assessment'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", f"Dosya kaydedilemedi:\n{str(e)}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Remove metadata if present
            if '_metadata' in loaded_data:
                del loaded_data['_metadata']
            
            # Validate structure
            if not self._validate_data_structure(loaded_data):
                messagebox.showerror("Yükleme Hatası", "Dosya formatı geçersiz")
                return False
            
            self.set_data(loaded_data)
            return True
            
        except FileNotFoundError:
            messagebox.showerror("Yükleme Hatası", "Dosya bulunamadı")
            return False
        except json.JSONDecodeError:
            messagebox.showerror("Yükleme Hatası", "Dosya formatı geçersiz (JSON hatası)")
            return False
        except Exception as e:
            messagebox.showerror("Yükleme Hatası", f"Dosya yüklenemedi:\n{str(e)}")
            return False
    
    def _validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """Validate data structure"""
        required_keys = ['general', 'test_results', 'mitre_tactics', 
                        'triggered_rules', 'undetected_techniques', 'recommendations']
        
        for key in required_keys:
            if key not in data:
                return False
        
        return True
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get sample data for testing"""
        return {
            'general': {
                'company_name': 'Örnek Teknoloji A.Ş.',
                'report_date': 'Ocak 2025',
                'prepared_by': 'Siber Güvenlik Ekibi',
                'report_id': 'IDCA-2025-001',
                'report_title': 'Gelişmiş Güvenlik Değerlendirmesi',
                'classification': 'Gizli'
            },
            'test_results': {
                'total_rules': 350,
                'tested_rules': 124,
                'triggered_rules': 78
            },
            'mitre_tactics': {
                'Initial Access': {'test': 12, 'triggered': 8, 'rate': 66.7},
                'Execution': {'test': 15, 'triggered': 11, 'rate': 73.3},
                'Persistence': {'test': 18, 'triggered': 14, 'rate': 77.8},
                'Privilege Escalation': {'test': 14, 'triggered': 9, 'rate': 64.3},
                'Defense Evasion': {'test': 22, 'triggered': 12, 'rate': 54.5},
                'Credential Access': {'test': 16, 'triggered': 10, 'rate': 62.5},
                'Discovery': {'test': 13, 'triggered': 8, 'rate': 61.5},
                'Lateral Movement': {'test': 8, 'triggered': 4, 'rate': 50.0},
                'Collection': {'test': 6, 'triggered': 2, 'rate': 33.3}
            },
            'triggered_rules': [
                {'name': 'Şüpheli PowerShell Aktivitesi', 'mitre': 'T1059.001', 
                 'tactic': 'Execution', 'confidence': '92'},
                {'name': 'Brute Force Saldırı Tespiti', 'mitre': 'T1110', 
                 'tactic': 'Credential Access', 'confidence': '88'},
                {'name': 'Mimikatz Kullanımı', 'mitre': 'T1003.001', 
                 'tactic': 'Credential Access', 'confidence': '95'},
                {'name': 'Zamanlanmış Görev Oluşturma', 'mitre': 'T1053.005', 
                 'tactic': 'Persistence', 'confidence': '85'}
            ],
            'undetected_techniques': [
                {'id': 'T1566.001', 'name': 'Zararlı E-posta Ekleri', 
                 'tactic': 'Initial Access', 'criticality': 'Kritik'},
                {'id': 'T1548.002', 'name': 'UAC Bypass', 
                 'tactic': 'Privilege Escalation', 'criticality': 'Yüksek'},
                {'id': 'T1055', 'name': 'Process Injection', 
                 'tactic': 'Defense Evasion', 'criticality': 'Yüksek'},
                {'id': 'T1082', 'name': 'System Information Discovery', 
                 'tactic': 'Discovery', 'criticality': 'Orta'}
            ],
            'recommendations': [
                {'priority': 'P1', 'category': 'Log Kaynakları', 
                 'text': 'Windows Security Event loglarının tam entegrasyonu'},
                {'priority': 'P2', 'category': 'Kural Optimizasyonu',
                 'text': 'PowerShell loglarında daha detaylı izleme'},
                {'priority': 'P3', 'category': 'Yeni Kurallar',
                 'text': 'E-posta güvenliği için yeni detection kuralları'},
                {'priority': 'P4', 'category': 'UEBA/SIEM',
                 'text': 'Kullanıcı davranış analitiği entegrasyonu'}
            ]
        }