#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCA Security Assessment - Modular Application
==============================================
Enhanced and modularized version of the IDCA Security Assessment tool.

Features:
- Improved UI components with better user experience
- Modular architecture for easier maintenance
- Enhanced data validation and error handling
- Better theme support and visual consistency
- Advanced table editing capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import sys
import locale
import warnings
from typing import Dict, Any, List
from datetime import datetime

# Import custom modules
from config.themes import ThemeManager
from ui.components import ImprovedTableEntry, StatusIndicator, ProgressDialog
from core.data_manager import DataManager
from visualization.chart_generator import ChartGenerator

# Configure locale and warnings
if sys.platform.startswith('win'):
    try:
        locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
    except:
        locale.setlocale(locale.LC_ALL, 'C')
else:
    try:
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, 'C')

warnings.filterwarnings('ignore')

# Configure matplotlib
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'sans-serif']
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

class IDCAApplication:
    """Main IDCA Application with improved modular design"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IDCA Security Assessment - Gelişmiş Rapor Görselleştirici v6.0")
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.data_manager = DataManager()
        self.chart_generator = None  # Will be initialized after UI setup
        
        # Application settings
        self.transparent_bg = tk.BooleanVar(value=True)
        self.visual_settings = {
            'fig_width': 12,
            'fig_height': 8,
            'fig_dpi': 300
        }
        
        self.setup_window()
        self.create_styles()
        self.create_gui()
        self.initialize_chart_generator()
        self.show_welcome_message()
    
    def setup_window(self):
        """Setup main window properties"""
        # Window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(1600, screen_width - 100)
        window_height = min(900, screen_height - 100)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1200, 700)
        
        # Configure for Turkish characters
        try:
            self.root.tk.call('encoding', 'system', 'utf-8')
        except:
            pass
        
        self.root.option_add('*Font', 'Arial 10')
    
    def create_styles(self):
        """Create and configure TTK styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Success.TButton', foreground='white', background='#10B981')
        self.style.configure('Warning.TButton', foreground='white', background='#F59E0B')
        self.style.configure('Danger.TButton', foreground='white', background='#EF4444')
        self.style.configure('Invalid.TEntry', fieldbackground='#FEE2E2', bordercolor='#EF4444')
        
        # Header styles
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Arial', 10, 'bold'))
    
    def create_gui(self):
        """Create the main GUI"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create main content area
        self.create_main_content(main_frame)
        
        # Create status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Create the application toolbar"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Left side buttons
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        buttons = [
            ("📖 Kılavuz", self.show_guide, None),
            ("📁 Yükle", self.load_data, None),
            ("💾 Kaydet", self.save_data, None),
            ("📊 Örnek Veri", self.load_sample_data, None),
            ("🎨 GÖRSELLER OLUŞTUR", self.generate_all_visuals, 'Success.TButton'),
            ("🔄 Yenile", self.refresh_preview, None),
            ("🗑️ Temizle", self.clear_all_data, 'Danger.TButton')
        ]
        
        for text, command, style in buttons:
            btn = ttk.Button(left_frame, text=text, command=command)
            if style:
                btn.configure(style=style)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Right side - Theme selector
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_frame, text="Tema:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.theme_combo = ttk.Combobox(right_frame, 
                                       values=self.theme_manager.get_theme_names(),
                                       width=15, state='readonly')
        self.theme_combo.set(self.theme_manager.get_current_theme_name())
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
    
    def create_main_content(self, parent):
        """Create main content area with tabs and preview"""
        # PanedWindow for resizable layout
        self.paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left panel - Data input tabs
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=3)
        
        self.create_data_tabs(left_frame)
        
        # Right panel - Preview
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=2)
        
        self.create_preview_panel(right_frame)
    
    def create_data_tabs(self, parent):
        """Create data input tabs"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create all tabs
        self.create_general_tab()
        self.create_test_results_tab()
        self.create_mitre_tab()
        self.create_rules_tab()
        self.create_recommendations_tab()
        self.create_settings_tab()
    
    def create_general_tab(self):
        """Create general information tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="1. 🏢 Genel Bilgiler")
        
        # Scrollable content
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content frame
        content_frame = ttk.LabelFrame(scrollable_frame, text="Rapor Bilgileri", padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info label
        info_label = ttk.Label(content_frame, 
                              text="ℹ️ Türkçe karakterler desteklenmektedir. Tüm zorunlu alanları doldurun.",
                              foreground='blue', font=('Arial', 9))
        info_label.grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky='w')
        
        # Form fields
        fields = [
            ("Kurum/Şirket Adı: *", "company_name", "Örn: ABC Teknoloji A.Ş."),
            ("Rapor Tarihi: *", "report_date", "Örn: Ocak 2025"),
            ("Hazırlayan: *", "prepared_by", "Örn: Siber Güvenlik Ekibi"),
            ("Rapor No:", "report_id", "Örn: IDCA-2025-001"),
            ("Rapor Başlığı:", "report_title", "Örn: Güvenlik Değerlendirmesi"),
            ("Gizlilik Sınıfı:", "classification", "Örn: Gizli")
        ]
        
        self.general_entries = {}
        for i, (label_text, field_key, placeholder) in enumerate(fields, 1):
            # Label
            label = ttk.Label(content_frame, text=label_text, font=('Arial', 10, 'bold'))
            label.grid(row=i, column=0, sticky='w', pady=8)
            
            # Entry
            entry = ttk.Entry(content_frame, width=40, font=('Arial', 10))
            entry.grid(row=i, column=1, pady=8, padx=10, sticky='ew')
            
            # Placeholder
            placeholder_label = ttk.Label(content_frame, text=placeholder, 
                                        foreground='gray', font=('Arial', 8, 'italic'))
            placeholder_label.grid(row=i, column=2, sticky='w', padx=5)
            
            self.general_entries[field_key] = entry
        
        content_frame.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_test_results_tab(self):
        """Create test results tab with improved validation"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="2. 📊 Test Sonuçları")
        
        main_frame = ttk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Bilgi", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """• Toplam Kural: SIEM/SOAR sistemindeki tüm korelasyon kuralları
• Test Edilen: IDCA test sürecine dahil edilen kurallar  
• Tetiklenen: Test sırasında başarıyla alarm üreten kurallar
• Diğer metrikler otomatik olarak hesaplanır"""
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 9)).pack(anchor='w')
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Test Verileri", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create input fields with validation
        fields = [
            ("Toplam Kural Sayısı:", "total_rules", "Sistemdeki tüm kurallar"),
            ("Test Edilen Kural:", "tested_rules", "IDCA testine dahil edilenler"),
            ("Tetiklenen Kural:", "triggered_rules", "Başarıyla tespit edenler")
        ]
        
        self.test_entries = {}
        for i, (label_text, field_key, description) in enumerate(fields):
            # Label
            label = ttk.Label(input_frame, text=label_text, font=('Arial', 10, 'bold'))
            label.grid(row=i, column=0, sticky='w', pady=8)
            
            # Entry with validation
            entry = ttk.Entry(input_frame, width=15, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=8, padx=10)
            entry.bind('<KeyRelease>', self.validate_and_calculate)
            entry.bind('<FocusOut>', self.validate_and_calculate)
            
            # Description
            desc_label = ttk.Label(input_frame, text=description, 
                                 foreground='gray', font=('Arial', 9))
            desc_label.grid(row=i, column=2, sticky='w', padx=10)
            
            self.test_entries[field_key] = entry
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="📈 Hesaplanan Metrikler", padding=15)
        results_frame.pack(fill=tk.X)
        
        # Create result labels in a grid
        metrics = [
            ("Test Edilmeyen:", "not_tested"),
            ("Başarısız Kurallar:", "failed"),
            ("Başarı Oranı:", "success_rate"),
            ("Kapsama Oranı:", "coverage_rate")
        ]
        
        self.calc_labels = {}
        for i, (label_text, field_key) in enumerate(metrics):
            row = i // 2
            col = (i % 2) * 2
            
            label = ttk.Label(results_frame, text=label_text, font=('Arial', 10))
            label.grid(row=row, column=col, sticky='w', pady=5, padx=5)
            
            value_label = ttk.Label(results_frame, text="0", 
                                  font=('Arial', 12, 'bold'), foreground='blue')
            value_label.grid(row=row, column=col+1, pady=5, padx=10, sticky='w')
            
            self.calc_labels[field_key] = value_label
    
    def create_mitre_tab(self):
        """Create MITRE ATT&CK tab with improved table"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="3. 🎯 MITRE ATT&CK")
        
        main_frame = ttk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text="Her MITRE taktik için test edilen ve tetiklenen kural sayılarını girin. Başarı oranları otomatik hesaplanır.",
                              font=('Arial', 9), foreground='blue')
        info_label.pack(pady=5)
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="MITRE ATT&CK Taktikleri", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create improved table
        columns = ['Taktik Adı', 'Test Edilen', 'Tetiklenen', 'Başarı %']
        validation_rules = {
            'Test Edilen': 'numeric',
            'Tetiklenen': 'numeric',
            'Başarı %': 'percentage'
        }
        
        self.mitre_table = ImprovedTableEntry(table_frame, columns, rows=12, 
                                            validation_rules=validation_rules)
        self.mitre_table.pack(fill=tk.BOTH, expand=True)
        
        # Pre-fill tactic names
        default_tactics = [
            'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
            'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
            'Collection', 'Command and Control', 'Exfiltration', 'Impact'
        ]
        
        for i, tactic in enumerate(default_tactics):
            if i < len(self.mitre_table.entries):
                self.mitre_table.entries[i][0].insert(0, tactic)
                self.mitre_table.entries[i][0].configure(state='readonly')
        
        # Bind calculation events
        for row in self.mitre_table.entries:
            row[1].bind('<KeyRelease>', self.calculate_mitre_rates)
            row[2].bind('<KeyRelease>', self.calculate_mitre_rates)
    
    def create_rules_tab(self):
        """Create rules tab with enhanced tables"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="4. 📋 Kurallar")
        
        # Notebook for sub-tabs
        rules_notebook = ttk.Notebook(tab_frame)
        rules_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Triggered rules tab
        triggered_frame = ttk.Frame(rules_notebook)
        rules_notebook.add(triggered_frame, text="✅ Tetiklenen Kurallar")
        
        ttk.Label(triggered_frame, text="Başarıyla tetiklenen korelasyon kuralları (Table 3)",
                 font=('Arial', 10, 'bold'), foreground='green').pack(pady=5)
        
        columns = ['Kural Adı', 'MITRE ID', 'Taktik', 'Güven Skoru (%)']
        validation_rules = {'Güven Skoru (%)': 'percentage'}
        
        self.triggered_table = ImprovedTableEntry(triggered_frame, columns, rows=15,
                                                validation_rules=validation_rules)
        self.triggered_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Undetected techniques tab
        undetected_frame = ttk.Frame(rules_notebook)
        rules_notebook.add(undetected_frame, text="❌ Algılanamayan Teknikler")
        
        ttk.Label(undetected_frame, text="Tespit edilemeyen MITRE teknikleri (Table 4)",
                 font=('Arial', 10, 'bold'), foreground='red').pack(pady=5)
        
        columns = ['MITRE ID', 'Teknik Adı', 'Taktik', 'Kritiklik']
        self.undetected_table = ImprovedTableEntry(undetected_frame, columns, rows=15)
        self.undetected_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add criticality dropdowns
        for i, row in enumerate(self.undetected_table.entries):
            combo = ttk.Combobox(self.undetected_table.scrollable_frame,
                               values=['Kritik', 'Yüksek', 'Orta', 'Düşük'],
                               width=10, font=('Arial', 10))
            combo.grid(row=i, column=3, sticky='ew', padx=1, pady=1)
            row[3].destroy()
            row[3] = combo
    
    def create_recommendations_tab(self):
        """Create recommendations tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="5. 💡 Öneriler")
        
        main_frame = ttk.Frame(tab_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Güvenlik iyileştirme önerileri (Table 5)",
                 font=('Arial', 10, 'bold'), foreground='blue').pack(pady=5)
        
        columns = ['Öncelik', 'Kategori', 'Öneri Açıklaması']
        self.recommendations_table = ImprovedTableEntry(main_frame, columns, rows=10)
        self.recommendations_table.pack(fill=tk.BOTH, expand=True)
        
        # Pre-fill priorities and setup category dropdowns
        categories = ['Log Kaynakları', 'Kural Optimizasyonu', 'Yeni Kurallar', 
                     'UEBA/SIEM', 'Test Döngüsü', 'Eğitim', 'Otomasyon', 'Diğer']
        
        for i, row in enumerate(self.recommendations_table.entries):
            # Priority
            row[0].insert(0, f"P{i+1}")
            row[0].configure(state='readonly')
            
            # Category dropdown
            combo = ttk.Combobox(self.recommendations_table.scrollable_frame,
                               values=categories, width=20, font=('Arial', 10))
            combo.grid(row=i, column=1, sticky='ew', padx=1, pady=1)
            row[1].destroy()
            row[1] = combo
    
    def create_settings_tab(self):
        """Create settings and configuration tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ Ayarlar")
        
        # Scrollable content
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", 
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Visual settings
        visual_frame = ttk.LabelFrame(scrollable_frame, text="🎨 Görsel Ayarları", padding=15)
        visual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Size settings
        settings = [
            ("Genişlik (inch):", "fig_width", 12, 8, 20),
            ("Yükseklik (inch):", "fig_height", 8, 6, 15),
            ("DPI (Çözünürlük):", "fig_dpi", 300, 100, 600)
        ]
        
        self.settings_widgets = {}
        for i, (label_text, key, default, min_val, max_val) in enumerate(settings):
            ttk.Label(visual_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=5)
            
            spinbox = ttk.Spinbox(visual_frame, from_=min_val, to=max_val, width=10)
            spinbox.set(default)
            spinbox.grid(row=i, column=1, pady=5, padx=10)
            
            self.settings_widgets[key] = spinbox
        
        # Transparent background
        ttk.Checkbutton(visual_frame, text="🔍 Şeffaf Arkaplan (Word için önerilen)",
                       variable=self.transparent_bg).grid(row=3, column=0, columnspan=2, pady=10, sticky='w')
        
        # Theme preview
        theme_frame = ttk.LabelFrame(scrollable_frame, text="🎨 Tema Önizleme", padding=15)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.create_theme_preview(theme_frame)
        
        # Export settings
        export_frame = ttk.LabelFrame(scrollable_frame, text="📁 Dışa Aktarma Ayarları", padding=15)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(export_frame, text="Kayıt Klasörü:").grid(row=0, column=0, sticky='w')
        
        self.save_path = tk.StringVar(value=os.path.join(os.getcwd(), "IDCA_Gorseller"))
        path_entry = ttk.Entry(export_frame, textvariable=self.save_path, width=50)
        path_entry.grid(row=0, column=1, padx=10)
        
        ttk.Button(export_frame, text="📁 Seç", 
                  command=self.select_export_folder).grid(row=0, column=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_theme_preview(self, parent):
        """Create theme color preview"""
        colors_frame = ttk.Frame(parent)
        colors_frame.pack(fill=tk.X)
        
        self.color_preview_labels = {}
        colors = [
            ('Primary', 'primary'), ('Secondary', 'secondary'), 
            ('Accent', 'accent'), ('Success', 'success'),
            ('Warning', 'warning'), ('Danger', 'danger')
        ]
        
        for i, (name, key) in enumerate(colors):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(colors_frame, text=f"{name}:").grid(row=row, column=col, sticky='w', padx=5, pady=3)
            
            color_label = tk.Label(colors_frame, text="   ", 
                                 bg=self.theme_manager.colors[key], width=12)
            color_label.grid(row=row, column=col+1, padx=5, pady=3)
            self.color_preview_labels[key] = color_label
    
    def create_preview_panel(self, parent):
        """Create preview panel"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Önizleme", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Preview selector
        self.preview_combo = ttk.Combobox(header_frame, values=[
            'Figure 1 - Test Uygunluk',
            'Figure 2 - Test Durumu', 
            'Table 1 - Sonuç Tablosu',
            'Table 2 - MITRE Kapsama',
            'Table 3 - Tetiklenen Kurallar',
            'Table 4 - Algılanamayan',
            'Table 5 - Öneriler'
        ], width=25, state='readonly')
        self.preview_combo.pack(side=tk.LEFT, padx=10)
        self.preview_combo.current(0)
        self.preview_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        ttk.Button(header_frame, text="🔄", command=self.update_preview, width=3).pack(side=tk.LEFT)
        
        # Preview area
        self.preview_frame = ttk.LabelFrame(parent, text="", padding=5)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self, parent):
        """Create application status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Status indicator
        self.status_indicator = StatusIndicator(status_frame)
        self.status_indicator.pack(side=tk.LEFT, padx=10)
        
        # Data validation indicator  
        self.validation_label = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.validation_label.pack(side=tk.RIGHT, padx=10)
    
    def initialize_chart_generator(self):
        """Initialize chart generator after UI is ready"""
        self.chart_generator = ChartGenerator(
            theme_manager=self.theme_manager,
            transparent_bg=self.transparent_bg,
            visual_settings=self.settings_widgets
        )
    
    # Event handlers and methods...
    def on_theme_change(self, event=None):
        """Handle theme change"""
        new_theme = self.theme_combo.get()
        if self.theme_manager.set_theme(new_theme):
            # Update color previews
            for key, label in self.color_preview_labels.items():
                label.configure(bg=self.theme_manager.colors[key])
            
            # Update preview
            self.update_preview()
            
            self.status_indicator.set_status('success', f"✅ {new_theme} teması uygulandı", 'green')
    
    def validate_and_calculate(self, event=None):
        """Validate input and calculate derived values"""
        try:
            # Get values
            total = int(self.test_entries['total_rules'].get() or 0)
            tested = int(self.test_entries['tested_rules'].get() or 0)
            triggered = int(self.test_entries['triggered_rules'].get() or 0)
            
            # Validation
            errors = []
            if tested > total:
                errors.append("Test edilen > Toplam olamaz!")
            if triggered > tested:
                errors.append("Tetiklenen > Test edilen olamaz!")
            
            if errors:
                self.status_indicator.set_status('error', '; '.join(errors), 'red')
                return
            
            # Calculate derived values
            not_tested = total - tested
            failed = tested - triggered
            success_rate = (triggered / tested * 100) if tested > 0 else 0
            coverage_rate = (tested / total * 100) if total > 0 else 0
            
            # Update labels
            self.calc_labels['not_tested'].configure(text=str(not_tested))
            self.calc_labels['failed'].configure(text=str(failed))
            self.calc_labels['success_rate'].configure(text=f"%{success_rate:.1f}")
            self.calc_labels['coverage_rate'].configure(text=f"%{coverage_rate:.1f}")
            
            # Color coding
            color = 'green' if success_rate >= 70 else 'orange' if success_rate >= 50 else 'red'
            self.calc_labels['success_rate'].configure(foreground=color)
            
            # Update data manager
            self.data_manager.update_test_results({
                'total_rules': total,
                'tested_rules': tested,
                'triggered_rules': triggered
            })
            
            self.status_indicator.set_status('success', "✅ Hesaplandı", 'green')
            
        except ValueError:
            pass  # Ignore invalid input during typing
    
    def calculate_mitre_rates(self, event=None):
        """Calculate MITRE success rates"""
        mitre_data = {}
        
        for row in self.mitre_table.entries:
            try:
                tactic = row[0].get().strip()
                test = int(row[1].get() or 0)
                triggered = int(row[2].get() or 0)
                
                if tactic and test > 0:
                    rate = (triggered / test) * 100
                    row[3].delete(0, tk.END)
                    row[3].insert(0, f"{rate:.1f}")
                    
                    # Color coding
                    if rate >= 70:
                        row[3].configure(style='TEntry')
                    elif rate >= 40:
                        row[3].configure(style='TEntry')  # Could add warning style
                    else:
                        row[3].configure(style='TEntry')   # Could add error style
                    
                    mitre_data[tactic] = {
                        'test': test,
                        'triggered': triggered,
                        'rate': rate
                    }
            except:
                pass
        
        self.data_manager.update_mitre_tactics(mitre_data)
        self.status_indicator.set_status('success', "✅ MITRE oranları hesaplandı", 'green')
    
    def update_preview(self):
        """Update preview panel"""
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        if not self.chart_generator:
            return
        
        try:
            # Collect current data
            self.collect_all_data()
            
            # Generate preview
            selected = self.preview_combo.get()
            
            if 'Figure 1' in selected:
                chart = self.chart_generator.create_figure1_preview(self.data_manager.get_data())
            elif 'Figure 2' in selected:
                chart = self.chart_generator.create_figure2_preview(self.data_manager.get_data())
            else:
                chart = self.chart_generator.create_table_preview(selected, self.data_manager.get_data())
            
            if chart:
                canvas = FigureCanvasTkAgg(chart, master=self.preview_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
        except Exception as e:
            error_label = ttk.Label(self.preview_frame, 
                                   text=f"Önizleme hatası:\n{str(e)}",
                                   font=('Arial', 10))
            error_label.pack(expand=True)
    
    def collect_all_data(self):
        """Collect data from all tabs and update data manager"""
        # General info
        general_data = {key: entry.get() for key, entry in self.general_entries.items()}
        self.data_manager.update_general_info(general_data)
        
        # Test results (already updated in validate_and_calculate)
        
        # MITRE tactics (already updated in calculate_mitre_rates)
        
        # Triggered rules
        triggered_data = []
        for row_data in self.triggered_table.get_data():
            if len(row_data) >= 4 and row_data[0]:
                triggered_data.append({
                    'name': row_data[0],
                    'mitre': row_data[1],
                    'tactic': row_data[2],
                    'confidence': row_data[3].replace('%', '')
                })
        self.data_manager.update_triggered_rules(triggered_data)
        
        # Undetected techniques
        undetected_data = []
        for row_data in self.undetected_table.get_data():
            if len(row_data) >= 4 and row_data[0]:
                undetected_data.append({
                    'id': row_data[0],
                    'name': row_data[1],
                    'tactic': row_data[2],
                    'criticality': row_data[3]
                })
        self.data_manager.update_undetected_techniques(undetected_data)
        
        # Recommendations
        recommendations_data = []
        for row_data in self.recommendations_table.get_data():
            if len(row_data) >= 3 and row_data[2]:
                recommendations_data.append({
                    'priority': row_data[0],
                    'category': row_data[1],
                    'text': row_data[2]
                })
        self.data_manager.update_recommendations(recommendations_data)
    
    def show_welcome_message(self):
        """Show welcome message"""
        self.status_indicator.set_status('info', 
            f"Hoş geldiniz! IDCA v6.0 - Aktif tema: {self.theme_manager.get_current_theme_name()}", 
            'blue')
    
    def show_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 Kullanım Kılavuzu")
        guide_window.geometry("900x700")
        guide_window.transient(self.root)
        
        # Create scrollable text
        text = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Arial', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guide_content = """
IDCA GELİŞMİŞ RAPOR GÖRSELLEŞTİRİCİ v6.0 - KULLANIM KILAVUZU
==========================================================

🎯 AMAÇ
Bu araç, IDCA (Intelligent Detection Coverage Assessment) test sonuçlarınızı 
profesyonel Word raporları için görselleştirmeye yarar.

✨ YENİ ÖZELLİKLER v6.0
• Gelişmiş tablo editörü (Excel benzeri navigasyon)
• Otomatik veri doğrulama ve hata kontrolü
• 7 farklı profesyonel tema seçeneği
• Pano desteği (Excel'den kopyala-yapıştır)
• Gelişmiş önizleme sistemi
• Modüler kod yapısı

📊 ÜRETILEN GÖRSELLER
• Figure 1: Test Uygunluk Pasta Grafiği
• Figure 2: Test Durumu ve MITRE Performans Grafikleri
• Table 1: Sonuç Değerlendirme Matrisi
• Table 2: MITRE ATT&CK Kapsama Analizi
• Table 3: Tetiklenen Korelasyon Kuralları
• Table 4: Algılanamayan MITRE Teknikleri
• Table 5: Güvenlik İyileştirme Önerileri

📝 VERİ GİRİŞİ REHBERİ

1. GENEL BİLGİLER (Zorunlu alanlar * ile işaretli)
   ✓ Kurum adı, rapor tarihi ve hazırlayan bilgileri
   ✓ Türkçe karakterler tam desteklenir

2. TEST SONUÇLARI
   ✓ Sadece sayısal değerler girin
   ✓ Otomatik doğrulama: Test edilen ≤ Toplam, Tetiklenen ≤ Test edilen
   ✓ Başarı oranları otomatik hesaplanır

3. MITRE ATT&CK TAKTİKLERİ
   ✓ Taktik isimleri önceden yüklenmiştir
   ✓ Test edilen ve tetiklenen sayıları girin
   ✓ Başarı yüzdeleri otomatik hesaplanır

4. KURALLAR
   🔹 Tetiklenen Kurallar: Başarılı tespit kuralları
   🔹 Algılanamayan Teknikler: Kritiklik seviyeleri ile

5. ÖNERİLER
   ✓ Öncelikler otomatik numaralanır (P1, P2, ...)
   ✓ Kategori seçimi dropdown menüden
   ✓ Detaylı öneri açıklamaları yazın

💡 GELİŞMİŞ KULLANIM İPUÇLARI

🔸 TABLO NAVİGASYONU
• Tab: Sonraki hücre
• Shift+Tab: Önceki hücre  
• Enter: Alt satır, aynı sütun
• Sağ tık: Bağlam menüsü (kes/kopyala/yapıştır)

🔸 EXCEL ENTEGRASYONİ
• Excel'den verileri kopyalayın (Ctrl+C)
• "Excel'den Yapıştır" butonuna tıklayın
• Tab-ayrılmış veriler otomatik olarak tabloya yerleşir

🔸 TEMA SİSTEMİ
• 7 farklı profesyonel tema
• Gerçek zamanlı önizleme
• Açık tema: Beyaz arkaplan raporlar için
• Koyu temalar: Dijital sunumlar için

🔸 ŞEFFAFLıK
• Word belgeleri için şeffaf arkaplan seçin
• Dijital görüntüleme için renkli arkaplan

⚙️ AYARLAR VE KONFİGÜRASYON

📐 Görsel Boyutları
• Genişlik: 8-20 inch (Word için 12 önerilen)
• Yükseklik: 6-15 inch (Word için 8 önerilen)  
• DPI: 300 (baskı kalitesi), 150 (web)

📁 Dosya İşlemleri
• JSON formatında kaydet/yükle
• Otomatik veri doğrulama
• Metadata ile versiyon kontrolü

🚀 GÖRSEL OLUŞTURMA SÜRECİ

1. Tüm zorunlu alanları doldurun
2. Veri doğrulamadan geçin (alt durum çubuğunda kontrol edin)
3. Tema ve ayarları seçin
4. "GÖRSELLER OLUŞTUR" butonuna tıklayın
5. İlerleme penceresini takip edin
6. Oluşturulan dosyaları Word'e ekleyin

📋 WORD ENTEGRASYONU

1. PNG dosyalarını Word'e sürükleyin
2. Görsel seçimi → "Metinle Satır İçi" 
3. Boyutlandırma → "Sıkıştırmayı devre dışı bırak"
4. 300 DPI kaliteyi koruyun

⚠️ ÖNEMLİ UYARILAR

❗ Veri Doğrulama
• Kırmızı kenarlı alanlar hatalı veri içerir
• Durum çubuğundaki hata mesajlarını kontrol edin
• Sayısal alanlara sadece rakam girin

❗ Dosya Güvenliği  
• Düzenli olarak çalışmanızı kaydedin
• Yedek dosyalar oluşturun
• Büyük veri setlerinde "Örnek Veri" ile test edin

❗ Performans
• Çok fazla satır eklemeyin (>50 satır)
• Önizlemeyi sık güncelleyerek kontrol edin
• Sistem kaynaklarını izleyin

🔧 SORUN GİDERME

🐛 Yaygın Hatalar
• "Matplotlib hatası": Sistem yeniden başlatın
• "Encoding hatası": Türkçe karakter kullanımını kontrol edin
• "JSON hatası": Dosya bozulması, yedekten yükleyin

📞 DESTEK
• GitHub: https://github.com/[repo-link]
• E-posta: security@company.com
• Dokümantasyon: [doc-link]

═══════════════════════════════════════════════════════════════

Başarılı güvenlik raporlamaları! 🛡️

v6.0 - Ocak 2025 | IDCA Geliştirme Ekibi
"""
        
        text.insert(tk.END, guide_content)
        text.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(guide_window, text="Kapat", 
                  command=guide_window.destroy).pack(pady=10)
    
    def load_data(self):
        """Load data from JSON file"""
        filename = filedialog.askopenfilename(
            title="IDCA Veri Dosyası Seç",
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename and self.data_manager.load_from_file(filename):
            self.populate_ui_from_data()
            self.status_indicator.set_status('success', "✅ Veriler yüklendi", 'green')
            
    def save_data(self):
        """Save data to JSON file"""
        self.collect_all_data()
        
        # Validate before saving
        errors = self.data_manager.validate_all_data()
        if errors:
            messagebox.showwarning("Doğrulama Hatası", 
                                 "Veriler kaydedildi ancak hatalar var:\n\n" + 
                                 "\n".join(errors[:5]))
        
        filename = filedialog.asksaveasfilename(
            title="IDCA Verilerini Kaydet",
            defaultextension=".json",
            filetypes=[("JSON dosyaları", "*.json")],
            initialname=f"IDCA_{self.data_manager.data['general'].get('company_name', 'Rapor').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename and self.data_manager.save_to_file(filename):
            self.status_indicator.set_status('success', "✅ Kaydedildi", 'green')
    
    def load_sample_data(self):
        """Load sample data for testing"""
        sample_data = self.data_manager.get_sample_data()
        self.data_manager.set_data(sample_data)
        self.populate_ui_from_data()
        
        messagebox.showinfo("Başarılı", "Örnek veriler yüklendi!\n\nBu veriler test amaçlıdır.")
        self.status_indicator.set_status('success', "✅ Örnek veri yüklendi", 'green')
    
    def populate_ui_from_data(self):
        """Populate UI elements from data manager"""
        data = self.data_manager.get_data()
        
        # General info
        for key, entry in self.general_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, data['general'].get(key, ''))
        
        # Test results
        for key, entry in self.test_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(data['test_results'].get(key, '')))
        
        self.validate_and_calculate()
        
        # MITRE tactics
        mitre_data = []
        tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
                  'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
                  'Collection', 'Command and Control', 'Exfiltration', 'Impact']
        
        for tactic in tactics:
            if tactic in data['mitre_tactics']:
                values = data['mitre_tactics'][tactic]
                mitre_data.append([tactic, str(values['test']), str(values['triggered']), f"{values['rate']:.1f}"])
            else:
                mitre_data.append([tactic, '', '', ''])
        
        self.mitre_table.set_data(mitre_data)
        
        # Other tables
        triggered_data = [[r['name'], r['mitre'], r['tactic'], r['confidence']] 
                         for r in data['triggered_rules']]
        self.triggered_table.set_data(triggered_data)
        
        undetected_data = [[t['id'], t['name'], t['tactic'], t['criticality']]
                          for t in data['undetected_techniques']]
        self.undetected_table.set_data(undetected_data)
        
        rec_data = [[r['priority'], r['category'], r['text']]
                   for r in data['recommendations']]
        self.recommendations_table.set_data(rec_data)
    
    def clear_all_data(self):
        """Clear all data"""
        if messagebox.askyesno("Onay", "Tüm veriler silinecek. Emin misiniz?"):
            self.data_manager.reset_data()
            
            # Clear UI
            for entry in self.general_entries.values():
                entry.delete(0, tk.END)
            
            for entry in self.test_entries.values():
                entry.delete(0, tk.END)
            
            for label in self.calc_labels.values():
                label.configure(text="0", foreground='blue')
            
            # Clear tables but keep tactic names
            self.mitre_table.clear()
            tactics = ['Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
                      'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
                      'Collection', 'Command and Control', 'Exfiltration', 'Impact']
            
            for i, tactic in enumerate(tactics):
                if i < len(self.mitre_table.entries):
                    self.mitre_table.entries[i][0].configure(state='normal')
                    self.mitre_table.entries[i][0].delete(0, tk.END)
                    self.mitre_table.entries[i][0].insert(0, tactic)
                    self.mitre_table.entries[i][0].configure(state='readonly')
            
            self.triggered_table.clear()
            self.undetected_table.clear()
            self.recommendations_table.clear()
            
            self.status_indicator.set_status('info', "✅ Veriler temizlendi", 'orange')
    
    def select_export_folder(self):
        """Select export folder"""
        folder = filedialog.askdirectory(title="Görsellerin Kaydedileceği Klasörü Seçin")
        if folder:
            self.save_path.set(folder)
    
    def generate_all_visuals(self):
        """Generate all visual outputs"""
        self.collect_all_data()
        
        # Validate data
        errors = self.data_manager.validate_all_data()
        if errors:
            messagebox.showerror("Veri Hatası", 
                               "Lütfen şu hataları düzeltin:\n\n" + 
                               "\n".join(errors[:5]))
            return
        
        # Get settings
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Update chart generator settings
        self.chart_generator.update_settings({
            'fig_width': float(self.settings_widgets['fig_width'].get()),
            'fig_height': float(self.settings_widgets['fig_height'].get()),
            'fig_dpi': int(self.settings_widgets['fig_dpi'].get())
        })
        
        # Create progress dialog
        progress = ProgressDialog(self.root, "Görseller Oluşturuluyor")
        
        # Generate visuals
        visuals = [
            ('Figure_1_Test_Uygunluk', self.chart_generator.generate_figure1),
            ('Figure_2_Test_Durumu', self.chart_generator.generate_figure2),
            ('Table_1_Sonuc_Degerlendirme', self.chart_generator.generate_table1),
            ('Table_2_MITRE_Kapsama', self.chart_generator.generate_table2),
            ('Table_3_Tetiklenen_Kurallar', self.chart_generator.generate_table3),
            ('Table_4_Algilanamayan_Teknikler', self.chart_generator.generate_table4),
            ('Table_5_Oneriler', self.chart_generator.generate_table5)
        ]
        
        success_count = 0
        data = self.data_manager.get_data()
        
        for i, (name, func) in enumerate(visuals):
            progress.update_progress(i, len(visuals), f"Oluşturuluyor: {name}", 
                                   f"{name}.png dosyası oluşturuluyor...")
            
            try:
                filepath = os.path.join(save_dir, f"{name}.png")
                func(data, filepath)
                success_count += 1
                progress.add_detail(f"✅ {name}.png başarıyla oluşturuldu")
            except Exception as e:
                progress.add_detail(f"❌ {name}.png oluşturulamadı: {str(e)}")
        
        progress.set_complete(f"✅ {success_count}/{len(visuals)} görsel oluşturuldu!")
        progress.add_detail(f"📁 Kayıt yeri: {save_dir}")
        
        if self.transparent_bg.get():
            progress.add_detail("ℹ️ Görseller şeffaf arkaplanla kaydedildi (Word için ideal)")
        
        self.status_indicator.set_status('success', 
                                       f"✅ {success_count} görsel oluşturuldu", 'green')
    
    def refresh_preview(self):
        """Refresh preview"""
        self.update_preview()
        self.status_indicator.set_status('success', "✅ Önizleme yenilendi", 'green')


def main():
    """Main application entry point"""
    root = tk.Tk()
    
    try:
        app = IDCAApplication(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Uygulama Hatası", f"Uygulama başlatılamadı:\n{str(e)}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()