#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input validators for IDCA Visualizer
"""

import re
from typing import Optional, Tuple


class InputValidator:
    """Validates user input"""
    
    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None) -> Tuple[bool, Optional[int], str]:
        """
        Validate integer input
        Returns: (is_valid, converted_value, error_message)
        """
        if not value:
            return True, 0, ""
        
        try:
            int_value = int(value)
            
            if min_val is not None and int_value < min_val:
                return False, None, f"Value must be at least {min_val}"
            
            if max_val is not None and int_value > max_val:
                return False, None, f"Value must be at most {max_val}"
            
            return True, int_value, ""
            
        except ValueError:
            return False, None, "Please enter a valid number"
    
    @staticmethod
    def validate_percentage(value: str) -> Tuple[bool, Optional[float], str]:
        """
        Validate percentage input (0-100)
        Returns: (is_valid, converted_value, error_message)
        """
        if not value:
            return True, 0.0, ""
        
        # Remove % sign if present
        value = value.strip().rstrip('%')
        
        try:
            float_value = float(value)
            
            if float_value < 0:
                return False, None, "Percentage cannot be negative"
            
            if float_value > 100:
                return False, None, "Percentage cannot exceed 100%"
            
            return True, float_value, ""
            
        except ValueError:
            return False, None, "Please enter a valid percentage"
    
    @staticmethod
    def validate_mitre_id(value: str) -> Tuple[bool, str, str]:
        """
        Validate MITRE ATT&CK ID format
        Returns: (is_valid, cleaned_value, error_message)
        """
        if not value:
            return False, "", "MITRE ID is required"
        
        # Clean the input
        value = value.strip().upper()
        
        # MITRE ID pattern: T####, T####.###, TA####, etc.
        pattern = r'^(TA|T)\d{4}(\.\d{3})?$'
        
        if re.match(pattern, value):
            return True, value, ""
        else:
            return False, value, "Invalid MITRE ID format (e.g., T1059, T1059.001)"
    
    @staticmethod
    def validate_required_text(value: str, field_name: str, max_length: int = None) -> Tuple[bool, str, str]:
        """
        Validate required text field
        Returns: (is_valid, cleaned_value, error_message)
        """
        if not value or not value.strip():
            return False, "", f"{field_name} is required"
        
        cleaned = value.strip()
        
        if max_length and len(cleaned) > max_length:
            return False, cleaned, f"{field_name} must be at most {max_length} characters"
        
        return True, cleaned, ""
    
    @staticmethod
    def validate_email(value: str) -> Tuple[bool, str, str]:
        """
        Validate email address
        Returns: (is_valid, cleaned_value, error_message)
        """
        if not value:
            return True, "", ""  # Email is optional
        
        value = value.strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, value):
            return True, value, ""
        else:
            return False, value, "Please enter a valid email address"
    
    @staticmethod
    def validate_date(value: str) -> Tuple[bool, str, str]:
        """
        Validate date format (flexible)
        Returns: (is_valid, cleaned_value, error_message)
        """
        if not value:
            return False, "", "Date is required"
        
        value = value.strip()
        
        # Accept various date formats
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY or MM/DD/YYYY
            r'^\d{2}\.\d{2}\.\d{4}$',  # DD.MM.YYYY
            r'^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$',  # Month YYYY
            r'^(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık) \d{4}$',  # Turkish Month YYYY
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, value, re.IGNORECASE):
                return True, value, ""
        
        return False, value, "Please enter a valid date (e.g., January 2025, 01/01/2025)"
    
    @staticmethod
    def validate_confidence_score(value: str) -> Tuple[bool, int, str]:
        """
        Validate confidence score (0-100)
        Returns: (is_valid, converted_value, error_message)
        """
        if not value:
            return True, 0, ""
        
        # Remove % sign if present
        value = value.strip().rstrip('%')
        
        is_valid, int_value, error = InputValidator.validate_integer(value, 0, 100)
        
        if not is_valid:
            return False, None, "Confidence score must be between 0 and 100"
        
        return True, int_value, ""


class CrossFieldValidator:
    """Validates relationships between fields"""
    
    @staticmethod
    def validate_test_results(total: int, tested: int, triggered: int) -> Tuple[bool, str]:
        """
        Validate test results relationships
        Returns: (is_valid, error_message)
        """
        errors = []
        
        if tested > total:
            errors.append("Tested rules cannot exceed total rules")
        
        if triggered > tested:
            errors.append("Triggered rules cannot exceed tested rules")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""
    
    @staticmethod
    def validate_mitre_tactic(test_count: int, triggered_count: int) -> Tuple[bool, str]:
        """
        Validate MITRE tactic counts
        Returns: (is_valid, error_message)
        """
        if triggered_count > test_count:
            return False, "Triggered count cannot exceed test count"
        
        return True, ""