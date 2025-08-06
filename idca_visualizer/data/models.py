#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data models for IDCA Visualizer
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class GeneralInfo:
    """General report information"""
    company_name: str = ""
    report_date: str = ""
    prepared_by: str = ""
    report_id: str = ""
    report_title: str = ""
    classification: str = ""
    
    def validate(self) -> List[str]:
        """Validate general info fields"""
        errors = []
        if not self.company_name:
            errors.append("Company name is required")
        if not self.report_date:
            errors.append("Report date is required")
        return errors
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            'company_name': self.company_name,
            'report_date': self.report_date,
            'prepared_by': self.prepared_by,
            'report_id': self.report_id,
            'report_title': self.report_title,
            'classification': self.classification
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'GeneralInfo':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TestResults:
    """Test results data"""
    total_rules: int = 0
    tested_rules: int = 0
    triggered_rules: int = 0
    not_tested: int = 0
    failed: int = 0
    success_rate: float = 0.0
    coverage_rate: float = 0.0
    
    def calculate_derived_values(self):
        """Calculate derived values"""
        self.not_tested = self.total_rules - self.tested_rules
        self.failed = self.tested_rules - self.triggered_rules
        
        if self.tested_rules > 0:
            self.success_rate = (self.triggered_rules / self.tested_rules) * 100
        else:
            self.success_rate = 0.0
            
        if self.total_rules > 0:
            self.coverage_rate = (self.tested_rules / self.total_rules) * 100
        else:
            self.coverage_rate = 0.0
    
    def validate(self) -> List[str]:
        """Validate test results"""
        errors = []
        
        if self.total_rules < 0:
            errors.append("Total rules cannot be negative")
        if self.tested_rules < 0:
            errors.append("Tested rules cannot be negative")
        if self.triggered_rules < 0:
            errors.append("Triggered rules cannot be negative")
        if self.tested_rules > self.total_rules:
            errors.append("Tested rules cannot exceed total rules")
        if self.triggered_rules > self.tested_rules:
            errors.append("Triggered rules cannot exceed tested rules")
            
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_rules': self.total_rules,
            'tested_rules': self.tested_rules,
            'triggered_rules': self.triggered_rules,
            'not_tested': self.not_tested,
            'failed': self.failed,
            'success_rate': self.success_rate,
            'coverage_rate': self.coverage_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResults':
        """Create from dictionary"""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


@dataclass
class MitreTactic:
    """MITRE ATT&CK tactic data"""
    name: str
    test_count: int = 0
    triggered_count: int = 0
    success_rate: float = 0.0
    
    def calculate_success_rate(self):
        """Calculate success rate"""
        if self.test_count > 0:
            self.success_rate = (self.triggered_count / self.test_count) * 100
        else:
            self.success_rate = 0.0
    
    def validate(self) -> List[str]:
        """Validate tactic data"""
        errors = []
        if self.test_count < 0:
            errors.append(f"{self.name}: Test count cannot be negative")
        if self.triggered_count < 0:
            errors.append(f"{self.name}: Triggered count cannot be negative")
        if self.triggered_count > self.test_count:
            errors.append(f"{self.name}: Triggered count cannot exceed test count")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'test': self.test_count,
            'triggered': self.triggered_count,
            'rate': self.success_rate
        }


@dataclass
class TriggeredRule:
    """Triggered rule data"""
    name: str
    mitre_id: str
    tactic: str
    confidence: int
    
    def validate(self) -> List[str]:
        """Validate rule data"""
        errors = []
        if not self.name:
            errors.append("Rule name is required")
        if not self.mitre_id:
            errors.append("MITRE ID is required")
        if self.confidence < 0 or self.confidence > 100:
            errors.append(f"{self.name}: Confidence must be between 0 and 100")
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'mitre': self.mitre_id,
            'tactic': self.tactic,
            'confidence': str(self.confidence)
        }


@dataclass
class UndetectedTechnique:
    """Undetected technique data"""
    mitre_id: str
    name: str
    tactic: str
    criticality: str
    
    def validate(self) -> List[str]:
        """Validate technique data"""
        errors = []
        if not self.mitre_id:
            errors.append("MITRE ID is required")
        if not self.name:
            errors.append("Technique name is required")
        if self.criticality not in ['Critical', 'High', 'Medium', 'Low', 
                                    'Kritik', 'Yüksek', 'Orta', 'Düşük']:
            errors.append(f"{self.name}: Invalid criticality level")
        return errors
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            'id': self.mitre_id,
            'name': self.name,
            'tactic': self.tactic,
            'criticality': self.criticality
        }


@dataclass
class Recommendation:
    """Recommendation data"""
    priority: str
    category: str
    text: str
    
    def validate(self) -> List[str]:
        """Validate recommendation data"""
        errors = []
        if not self.text:
            errors.append(f"{self.priority}: Recommendation text is required")
        return errors
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            'priority': self.priority,
            'category': self.category,
            'text': self.text
        }


@dataclass
class IDCAData:
    """Complete IDCA assessment data"""
    general: GeneralInfo = field(default_factory=GeneralInfo)
    test_results: TestResults = field(default_factory=TestResults)
    mitre_tactics: Dict[str, MitreTactic] = field(default_factory=dict)
    triggered_rules: List[TriggeredRule] = field(default_factory=list)
    undetected_techniques: List[UndetectedTechnique] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """Validate all data"""
        errors = []
        
        # Validate each component
        errors.extend(self.general.validate())
        errors.extend(self.test_results.validate())
        
        for tactic in self.mitre_tactics.values():
            errors.extend(tactic.validate())
        
        for rule in self.triggered_rules:
            errors.extend(rule.validate())
        
        for technique in self.undetected_techniques:
            errors.extend(technique.validate())
        
        for rec in self.recommendations:
            errors.extend(rec.validate())
        
        return errors
    
    def calculate_all_derived_values(self):
        """Calculate all derived values"""
        self.test_results.calculate_derived_values()
        for tactic in self.mitre_tactics.values():
            tactic.calculate_success_rate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            'general': self.general.to_dict(),
            'test_results': self.test_results.to_dict(),
            'mitre_tactics': {
                name: tactic.to_dict() 
                for name, tactic in self.mitre_tactics.items()
            },
            'triggered_rules': [rule.to_dict() for rule in self.triggered_rules],
            'undetected_techniques': [tech.to_dict() for tech in self.undetected_techniques],
            'recommendations': [rec.to_dict() for rec in self.recommendations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IDCAData':
        """Create from dictionary"""
        instance = cls()
        
        # Load general info
        if 'general' in data:
            instance.general = GeneralInfo.from_dict(data['general'])
        
        # Load test results
        if 'test_results' in data:
            instance.test_results = TestResults.from_dict(data['test_results'])
        
        # Load MITRE tactics
        if 'mitre_tactics' in data:
            for name, tactic_data in data['mitre_tactics'].items():
                instance.mitre_tactics[name] = MitreTactic(
                    name=name,
                    test_count=tactic_data.get('test', 0),
                    triggered_count=tactic_data.get('triggered', 0),
                    success_rate=tactic_data.get('rate', 0.0)
                )
        
        # Load triggered rules
        if 'triggered_rules' in data:
            for rule_data in data['triggered_rules']:
                instance.triggered_rules.append(TriggeredRule(
                    name=rule_data.get('name', ''),
                    mitre_id=rule_data.get('mitre', ''),
                    tactic=rule_data.get('tactic', ''),
                    confidence=int(rule_data.get('confidence', 0))
                ))
        
        # Load undetected techniques
        if 'undetected_techniques' in data:
            for tech_data in data['undetected_techniques']:
                instance.undetected_techniques.append(UndetectedTechnique(
                    mitre_id=tech_data.get('id', ''),
                    name=tech_data.get('name', ''),
                    tactic=tech_data.get('tactic', ''),
                    criticality=tech_data.get('criticality', 'Medium')
                ))
        
        # Load recommendations
        if 'recommendations' in data:
            for rec_data in data['recommendations']:
                instance.recommendations.append(Recommendation(
                    priority=rec_data.get('priority', ''),
                    category=rec_data.get('category', ''),
                    text=rec_data.get('text', '')
                ))
        
        return instance
    
    def save_to_json(self, filepath: str):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> 'IDCAData':
        """Load data from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)