#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and constants for IDCA Visualizer
"""

import os
import sys
import locale
from pathlib import Path

# Application info
APP_NAME = "IDCA Security Assessment - Report Visualizer"
APP_VERSION = "6.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
THEMES_DIR = BASE_DIR / "themes"
OUTPUT_DIR = Path.home() / "IDCA_Reports"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Encoding settings
ENCODING = 'utf-8'

# Set locale for Turkish character support
try:
    if sys.platform.startswith('win'):
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    else:
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except:
    # Fallback to default locale
    pass

# Window settings
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700

# Figure settings
DEFAULT_FIG_WIDTH = 12
DEFAULT_FIG_HEIGHT = 8
DEFAULT_DPI = 300
MIN_DPI = 100
MAX_DPI = 600

# Font settings
DEFAULT_FONT_FAMILY = 'Arial'
DEFAULT_FONT_SIZE = 10
TITLE_FONT_SIZE = 14
HEADER_FONT_SIZE = 12

# Table settings
TABLE_HEADER_HEIGHT = 2
TABLE_ROW_HEIGHT = 1.8
MAX_TABLE_ROWS = 20

# Validation rules
VALIDATION_RULES = {
    'total_rules': {'min': 1, 'max': 10000},
    'tested_rules': {'min': 0, 'max': 10000},
    'triggered_rules': {'min': 0, 'max': 10000},
    'confidence': {'min': 0, 'max': 100},
    'success_rate': {'min': 0, 'max': 100}
}

# MITRE ATT&CK Tactics (ordered)
MITRE_TACTICS = [
    'Initial Access',
    'Execution',
    'Persistence',
    'Privilege Escalation',
    'Defense Evasion',
    'Credential Access',
    'Discovery',
    'Lateral Movement',
    'Collection',
    'Command and Control',
    'Exfiltration',
    'Impact'
]

# Criticality levels
CRITICALITY_LEVELS = ['Critical', 'High', 'Medium', 'Low']
CRITICALITY_LEVELS_TR = ['Kritik', 'Yüksek', 'Orta', 'Düşük']

# Recommendation categories
RECOMMENDATION_CATEGORIES = [
    'Log Sources',
    'Rule Optimization',
    'New Rules',
    'UEBA/SIEM',
    'Testing Cycle',
    'Training',
    'Automation',
    'Other'
]

RECOMMENDATION_CATEGORIES_TR = [
    'Log Kaynakları',
    'Kural Optimizasyonu',
    'Yeni Kurallar',
    'UEBA/SIEM',
    'Test Döngüsü',
    'Eğitim',
    'Otomasyon',
    'Diğer'
]

# Status indicators
STATUS_ICONS = {
    'success': '✅',
    'warning': '⚠️',
    'error': '❌',
    'info': 'ℹ️',
    'pending': '🔄'
}

# File formats
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.svg', '.pdf']
EXPORT_FORMAT = '.png'

# Matplotlib settings
MATPLOTLIB_PARAMS = {
    'font.family': ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'sans-serif'],
    'font.sans-serif': ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma'],
    'axes.unicode_minus': False,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'figure.autolayout': True,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
}