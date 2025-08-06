#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate IDCA Visualizer fixes
"""

import json
from pathlib import Path
from utils.html_preview import HTMLPreviewGenerator

# Sample data with complete fields
sample_data = {
    'general': {
        'company_name': 'Acme Corporation',
        'report_date': '2024-01-15',
        'tester_name': 'John Doe',
        'manager_name': 'Jane Smith',
        'manager_title': 'Security Manager'
    },
    'test_results': {
        'total_rules': 150,
        'tested_rules': 120,
        'triggered_rules': 85
    },
    'mitre_tactics': {
        'Initial Access': {
            'name': 'Initial Access',
            'test_count': 10,
            'triggered_count': 8
        },
        'Execution': {
            'name': 'Execution',
            'test_count': 15,
            'triggered_count': 12
        },
        'Persistence': {
            'name': 'Persistence',
            'test_count': 12,
            'triggered_count': 7
        },
        'Privilege Escalation': {
            'name': 'Privilege Escalation',
            'test_count': 8,
            'triggered_count': 5
        },
        'Defense Evasion': {
            'name': 'Defense Evasion',
            'test_count': 20,
            'triggered_count': 15
        },
        'Credential Access': {
            'name': 'Credential Access',
            'test_count': 10,
            'triggered_count': 3
        },
        'Discovery': {
            'name': 'Discovery',
            'test_count': 15,
            'triggered_count': 11
        },
        'Lateral Movement': {
            'name': 'Lateral Movement',
            'test_count': 8,
            'triggered_count': 6
        },
        'Collection': {
            'name': 'Collection',
            'test_count': 10,
            'triggered_count': 8
        },
        'Command and Control': {
            'name': 'Command and Control',
            'test_count': 12,
            'triggered_count': 10
        }
    },
    'triggered_rules': [
        {
            'name': 'Suspicious PowerShell Command',
            'mitre_id': 'T1059.001',
            'tactic': 'Execution',
            'confidence': 95
        },
        {
            'name': 'Brute Force Attack Detected',
            'mitre_id': 'T1110',
            'tactic': 'Credential Access',
            'confidence': 88
        },
        {
            'name': 'Process Injection',
            'mitre_id': 'T1055',
            'tactic': 'Defense Evasion',
            'confidence': 92
        },
        {
            'name': 'Persistence via Registry',
            'mitre_id': 'T1547.001',
            'tactic': 'Persistence',
            'confidence': 85
        },
        {
            'name': 'Data Staging',
            'mitre_id': 'T1074',
            'tactic': 'Collection',
            'confidence': 78
        }
    ],
    'undetected_techniques': [
        {
            'mitre_id': 'T1190',
            'name': 'Exploit Public-Facing Application',
            'tactic': 'Initial Access',
            'criticality': 'Critical'
        },
        {
            'mitre_id': 'T1053',
            'name': 'Scheduled Task/Job',
            'tactic': 'Persistence',
            'criticality': 'High'
        },
        {
            'mitre_id': 'T1003',
            'name': 'OS Credential Dumping',
            'tactic': 'Credential Access',
            'criticality': 'Critical'
        }
    ],
    'recommendations': [
        {
            'category': 'Technical',
            'text': 'Implement PowerShell script block logging and enhanced monitoring'
        },
        {
            'category': 'Process',
            'text': 'Establish regular security assessment schedule for new attack patterns'
        },
        {
            'category': 'Technical',
            'text': 'Deploy EDR solution for better visibility into process injection attempts'
        },
        {
            'category': 'Training',
            'text': 'Conduct security awareness training focusing on phishing attacks'
        }
    ]
}

def test_csv_export():
    """Test CSV export functionality"""
    from utils.csv_handler import CSVHandler
    
    print("Testing CSV Export...")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Export to CSV
    csv_file = str(output_dir / "test_export.csv")
    
    export_data = {
        'mitre_tactics': sample_data['mitre_tactics'],
        'triggered_rules': sample_data['triggered_rules'],
        'undetected_techniques': sample_data['undetected_techniques']
    }
    
    try:
        CSVHandler.export_to_csv(export_data, csv_file)
        print(f"✅ CSV export successful!")
        
        # List created files
        for file in output_dir.glob("*.csv"):
            print(f"   Created: {file.name}")
    except Exception as e:
        print(f"❌ CSV export failed: {e}")

def test_html_preview():
    """Test HTML preview generation"""
    print("\nTesting HTML Preview Generation...")
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate HTML preview
    generator = HTMLPreviewGenerator()
    html_file = str(output_dir / "preview.html")
    
    try:
        generator.generate_preview(sample_data, html_file)
        print(f"✅ HTML preview generated successfully!")
        print(f"   View at: file://{Path(html_file).absolute()}")
    except Exception as e:
        print(f"❌ HTML preview generation failed: {e}")

def test_data_validation():
    """Test data validation"""
    from utils.validators import InputValidator, CrossFieldValidator
    
    print("\nTesting Data Validation...")
    
    # Test MITRE ID validation
    test_cases = [
        ("T1059", True),
        ("T1059.001", True),
        ("TA0001", True),
        ("Invalid", False),
        ("", False)
    ]
    
    for test_id, expected in test_cases:
        is_valid, _, _ = InputValidator.validate_mitre_id(test_id)
        status = "✅" if is_valid == expected else "❌"
        print(f"   {status} MITRE ID '{test_id}': {'Valid' if is_valid else 'Invalid'}")
    
    # Test cross-field validation
    print("\n   Testing MITRE tactic validation:")
    test_cases = [
        (10, 8, True),   # Valid: triggered < tested
        (10, 12, False), # Invalid: triggered > tested
        (0, 5, False),   # Invalid: tested = 0 but triggered > 0
    ]
    
    for tested, triggered, expected in test_cases:
        is_valid, _ = CrossFieldValidator.validate_mitre_tactic(tested, triggered)
        status = "✅" if is_valid == expected else "❌"
        print(f"   {status} Tested: {tested}, Triggered: {triggered}: {'Valid' if is_valid else 'Invalid'}")

def main():
    """Run all tests"""
    print("🔧 IDCA Visualizer Fix Demonstration")
    print("=" * 50)
    
    # Create test output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save sample data as JSON
    json_file = output_dir / "sample_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Sample data saved to: {json_file}")
    
    # Run tests
    test_csv_export()
    test_html_preview()
    test_data_validation()
    
    print("\n✅ All tests completed!")
    print(f"📁 Check the 'test_output' directory for generated files")

if __name__ == "__main__":
    main()