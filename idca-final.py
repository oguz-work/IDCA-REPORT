#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCA Security Assessment - Rapor Görselleştirici DÜZELTILMIŞ FINAL
Türkçe karakter desteği ve tablo veri girişi ile
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import warnings
import sys
import locale

# Türkçe karakter encoding ayarları
if sys.platform.startswith('win'):
    locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
else:
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')

warnings.filterwarnings('ignore')

# Matplotlib Türkçe karakter desteği - GÜNCELLENDİ
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'sans-serif']
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# Matplotlib backend ayarı
import matplotlib
matplotlib.use('TkAgg')

class TableEntry(ttk.Frame):
    """Tablo şeklinde veri girişi için özel widget"""
    def __init__(self, parent, columns, rows=10, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.rows = rows
        self.entries = []
        
        # Başlıklar
        for j, col in enumerate(columns):
            label = ttk.Label(self, text=col, font=('Arial', 10, 'bold'),
                            background='#2c3e50', foreground='white')
            label.grid(row=0, column=j, sticky='ew', padx=1, pady=1)
        
        # Giriş hücreleri
        for i in range(1, rows + 1):
            row_entries = []
            for j in range(len(columns)):
                entry = ttk.Entry(self, font=('Arial', 10))
                entry.grid(row=i, column=j, sticky='ew', padx=1, pady=1)
                row_entries.append(entry)
            self.entries.append(row_entries)
        
        # Grid ağırlıkları
        for j in range(len(columns)):
            self.grid_columnconfigure(j, weight=1)
    
    def get_data(self):
        """Tablo verilerini al"""
        data = []
        for row in self.entries:
            row_data = [entry.get().strip() for entry in row]
            if any(row_data):  # En az bir hücre doluysa
                data.append(row_data)
        return data
    
    def set_data(self, data):
        """Tabloya veri yükle"""
        for i, row_data in enumerate(data):
            if i < len(self.entries):
                for j, value in enumerate(row_data):
                    if j < len(self.entries[i]):
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(value))
    
    def clear(self):
        """Tabloyu temizle"""
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)
    
    def add_row(self):
        """Yeni satır ekle"""
        row_entries = []
        row_num = len(self.entries) + 1
        for j in range(len(self.columns)):
            entry = ttk.Entry(self, font=('Arial', 10))
            entry.grid(row=row_num, column=j, sticky='ew', padx=1, pady=1)
            row_entries.append(entry)
        self.entries.append(row_entries)

class IDCAFixedFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("IDCA Security Assessment - Rapor Görselleştirici v5.0 FINAL")
        
        # Pencere boyutu ve pozisyon
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(1600, screen_width - 100)
        window_height = min(900, screen_height - 100)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Türkçe karakter için encoding
        self.root.option_add('*Font', 'Arial 10')
        
        # Tema renkleri ve şeffaf arkaplan seçeneği
        self.transparent_bg = tk.BooleanVar(value=True)  # Varsayılan şeffaf
        self.current_theme = 'Varsayılan'
        
        # Varsayılan tema
        self.colors = {
            'primary': '#0F172A',
            'secondary': '#1E293B',
            'accent': '#00D9FF',
            'accent_secondary': '#7C3AED',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'dark': '#020617',
            'light': '#F8FAFC',
            'gray': '#64748B'
        }
        
        # Tema listesi
        self.themes = {
            'Varsayılan': {
                'primary': '#0F172A', 'secondary': '#1E293B', 'accent': '#00D9FF',
                'accent_secondary': '#7C3AED', 'success': '#10B981', 'warning': '#F59E0B',
                'danger': '#EF4444', 'dark': '#020617', 'light': '#F8FAFC', 'gray': '#64748B'
            },
            'Profesyonel': {
                'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#0f3460',
                'accent_secondary': '#533483', 'success': '#53c653', 'warning': '#e94560',
                'danger': '#ff1744', 'dark': '#0f0f0f', 'light': '#eaeaea', 'gray': '#7a7a7a'
            },
            'Modern': {
                'primary': '#2d3436', 'secondary': '#636e72', 'accent': '#00b894',
                'accent_secondary': '#6c5ce7', 'success': '#55efc4', 'warning': '#fdcb6e',
                'danger': '#ff7675', 'dark': '#2d3436', 'light': '#dfe6e9', 'gray': '#b2bec3'
            },
            'Klasik': {
                'primary': '#2c3e50', 'secondary': '#34495e', 'accent': '#3498db',
                'accent_secondary': '#9b59b6', 'success': '#2ecc71', 'warning': '#f39c12',
                'danger': '#e74c3c', 'dark': '#1a1a1a', 'light': '#ecf0f1', 'gray': '#95a5a6'
            },
            'Açık': {
                'primary': '#ffffff', 'secondary': '#f5f5f5', 'accent': '#2196F3',
                'accent_secondary': '#673AB7', 'success': '#4CAF50', 'warning': '#FF9800',
                'danger': '#F44336', 'dark': '#ffffff', 'light': '#212121', 'gray': '#757575'
            }
        }
        
        # Veri yapısı
        self.init_data()
        
        # GUI oluştur
        self.create_gui()
        
        # Başlangıç mesajı
        self.show_welcome()
    
    def init_data(self):
        """Veri yapısını başlat"""
        self.data = {
            'general': {},
            'test_results': {},
            'mitre_tactics': {},
            'triggered_rules': [],
            'undetected_techniques': [],
            'recommendations': []
        }
    
    def create_gui(self):
        """Ana GUI oluştur"""
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ana container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Üst toolbar
        self.create_toolbar(main_frame)
        
        # Ana içerik alanı - PanedWindow
        self.paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Sol panel - Veri girişi
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=3)
        
        # Sağ panel - Önizleme
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=2)
        
        # Sol panel içeriği
        self.create_data_panel(left_frame)
        
        # Sağ panel içeriği
        self.create_preview_panel(right_frame)
        
        # Durum çubuğu
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        """Üst araç çubuğu"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Butonlar
        buttons = [
            ("📖 Kılavuz", self.show_guide),
            ("📁 Yükle", self.load_json),
            ("💾 Kaydet", self.save_json),
            ("📊 Örnek Veri", self.load_sample_data),
            ("🎨 GÖRSELLER OLUŞTUR", self.generate_all),
            ("🔄 Yenile", self.refresh_preview),
            ("🗑️ Temizle", self.clear_all)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(toolbar, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=2)
            
            # Ana buton vurgulama
            if "GÖRSELLER" in text:
                btn.configure(style='Success.TButton')
    
    def create_data_panel(self, parent):
        """Sol panel - Veri girişi sekmeli yapı"""
        # Notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sekmeler
        self.tab_general = self.create_general_tab()
        self.tab_test = self.create_test_tab()
        self.tab_mitre = self.create_mitre_tab()
        self.tab_rules = self.create_rules_tab()
        self.tab_recommendations = self.create_recommendations_tab()
        self.tab_settings = self.create_settings_tab()
    
    def create_general_tab(self):
        """Genel bilgiler sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Genel Bilgiler")
        
        # Scrollable frame
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form
        frame = ttk.LabelFrame(scrollable_frame, text="Rapor Bilgileri", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi
        info = ttk.Label(frame, text="ℹ️ Türkçe karakterler desteklenmektedir. Tüm alanları doldurun.",
                        foreground='blue', font=('Arial', 9))
        info.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky='w')
        
        # Form alanları
        fields = [
            ("Kurum/Şirket Adı:", "company_name", "Örn: Teknoloji A.Ş."),
            ("Rapor Tarihi:", "report_date", "Örn: Ocak 2025"),
            ("Hazırlayan:", "prepared_by", "Örn: Güvenlik Ekibi"),
            ("Rapor No:", "report_id", "Örn: IDCA-2025-001"),
            ("Başlık:", "report_title", "Örn: Güvenlik Değerlendirmesi"),
            ("Gizlilik:", "classification", "Örn: Gizli")
        ]
        
        self.general_entries = {}
        for i, (label, key, hint) in enumerate(fields, 1):
            ttk.Label(frame, text=label, font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=5)
            
            entry = ttk.Entry(frame, width=35, font=('Arial', 10))
            entry.grid(row=i, column=1, pady=5, padx=10, sticky='ew')
            
            ttk.Label(frame, text=hint, foreground='gray',
                     font=('Arial', 8, 'italic')).grid(
                row=i, column=2, sticky='w', padx=5)
            
            self.general_entries[key] = entry
        
        frame.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tab
    
    def create_test_tab(self):
        """Test sonuçları sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Test Sonuçları")
        
        # Ana frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi
        info_frame = ttk.LabelFrame(main_frame, text="Bilgi", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """• Toplam Kural: Sistemdeki tüm kurallar
• Test Edilen: Test sürecine dahil edilenler
• Tetiklenen: Başarıyla alarm üretenler
• Diğer değerler otomatik hesaplanır"""
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 9)).pack()
        
        # Veri girişi
        entry_frame = ttk.LabelFrame(main_frame, text="Test Verileri", padding=15)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        fields = [
            ("Toplam Kural:", "total_rules"),
            ("Test Edilen:", "tested_rules"),
            ("Tetiklenen:", "triggered_rules")
        ]
        
        self.test_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(entry_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=8)
            
            entry = ttk.Entry(entry_frame, width=15, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=8, padx=10)
            entry.bind('<KeyRelease>', self.calculate_stats)
            
            self.test_entries[key] = entry
        
        # Otomatik hesaplamalar
        calc_frame = ttk.LabelFrame(main_frame, text="Otomatik Hesaplamalar", padding=15)
        calc_frame.pack(fill=tk.X)
        
        self.calc_labels = {}
        calcs = [
            ("Test Edilmeyen:", "not_tested"),
            ("Başarısız:", "failed"),
            ("Başarı Oranı:", "success_rate"),
            ("Kapsama:", "coverage_rate")
        ]
        
        for i, (label, key) in enumerate(calcs):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(calc_frame, text=label, font=('Arial', 10)).grid(
                row=row, column=col, sticky='w', pady=5, padx=5)
            
            value_label = ttk.Label(calc_frame, text="0",
                                   font=('Arial', 12, 'bold'), foreground='blue')
            value_label.grid(row=row, column=col+1, pady=5, padx=10)
            
            self.calc_labels[key] = value_label
        
        return tab
    
    def create_mitre_tab(self):
        """MITRE ATT&CK sekmesi - TABLO GİRİŞİ"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. MITRE ATT&CK")
        
        # Ana frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi
        info = ttk.Label(main_frame, 
                        text="Her satıra bir taktik girin. Test ve tetiklenen sayılarını yazın.",
                        font=('Arial', 9), foreground='blue')
        info.pack(pady=5)
        
        # Tablo frame
        table_frame = ttk.LabelFrame(main_frame, text="MITRE Taktikleri", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tablo widget
        columns = ['Taktik Adı', 'Test Edilen', 'Tetiklenen', 'Başarı %']
        self.mitre_table = TableEntry(table_frame, columns, rows=12)
        self.mitre_table.pack(fill=tk.BOTH, expand=True)
        
        # Varsayılan taktikler
        default_tactics = [
            ['Initial Access', '', '', ''],
            ['Execution', '', '', ''],
            ['Persistence', '', '', ''],
            ['Privilege Escalation', '', '', ''],
            ['Defense Evasion', '', '', ''],
            ['Credential Access', '', '', ''],
            ['Discovery', '', '', ''],
            ['Lateral Movement', '', '', ''],
            ['Collection', '', '', ''],
            ['Command and Control', '', '', ''],
            ['Exfiltration', '', '', ''],
            ['Impact', '', '', '']
        ]
        
        # Taktik isimlerini doldur
        for i, row in enumerate(default_tactics):
            if i < len(self.mitre_table.entries):
                self.mitre_table.entries[i][0].insert(0, row[0])
                self.mitre_table.entries[i][0].config(state='readonly')
        
        # Otomatik hesaplama için binding
        for row in self.mitre_table.entries:
            row[1].bind('<KeyRelease>', lambda e: self.calculate_mitre_rates())
            row[2].bind('<KeyRelease>', lambda e: self.calculate_mitre_rates())
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Başarı Oranlarını Hesapla",
                  command=self.calculate_mitre_rates).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Tabloyu Temizle",
                  command=self.clear_mitre_table).pack(side=tk.LEFT, padx=5)
        
        return tab
    
    def create_rules_tab(self):
        """Kurallar sekmesi - TABLO GİRİŞİ"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4. Kurallar")
        
        # İki panel için notebook
        rules_notebook = ttk.Notebook(tab)
        rules_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tetiklenen kurallar
        triggered_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(triggered_tab, text="✅ Tetiklenen Kurallar")
        
        ttk.Label(triggered_tab, text="Başarıyla tetiklenen kurallar (Table 3)",
                 font=('Arial', 9), foreground='green').pack(pady=5)
        
        # Tablo
        columns = ['Kural Adı', 'MITRE ID', 'Taktik', 'Güven %']
        self.triggered_table = TableEntry(triggered_tab, columns, rows=15)
        self.triggered_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Algılanamayan teknikler
        undetected_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(undetected_tab, text="❌ Algılanamayan")
        
        ttk.Label(undetected_tab, text="Tespit edilemeyen teknikler (Table 4)",
                 font=('Arial', 9), foreground='red').pack(pady=5)
        
        # Tablo
        columns = ['MITRE ID', 'Teknik Adı', 'Taktik', 'Kritiklik']
        self.undetected_table = TableEntry(undetected_tab, columns, rows=15)
        self.undetected_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Kritiklik için dropdown ekle
        for row in self.undetected_table.entries:
            # Kritiklik sütununu combobox yap
            combo = ttk.Combobox(self.undetected_table, 
                                values=['Kritik', 'Yüksek', 'Orta', 'Düşük'],
                                width=10, font=('Arial', 10))
            combo.grid(row=self.undetected_table.entries.index(row)+1, 
                      column=3, sticky='ew', padx=1, pady=1)
            row[3].destroy()
            row[3] = combo
        
        return tab
    
    def create_recommendations_tab(self):
        """Öneriler sekmesi - TABLO GİRİŞİ"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="5. Öneriler")
        
        # Ana frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Öneri listesi (Table 5)",
                 font=('Arial', 9), foreground='blue').pack(pady=5)
        
        # Tablo
        columns = ['Öncelik', 'Kategori', 'Öneri Metni']
        self.recommendations_table = TableEntry(main_frame, columns, rows=10)
        self.recommendations_table.pack(fill=tk.BOTH, expand=True)
        
        # Öncelik otomatik doldur
        for i, row in enumerate(self.recommendations_table.entries):
            row[0].insert(0, f"P{i+1}")
            row[0].config(state='readonly')
            
            # Kategori için dropdown
            combo = ttk.Combobox(self.recommendations_table,
                                values=['Log Kaynakları', 'Kural Optimizasyonu', 
                                       'Yeni Kurallar', 'UEBA/SIEM', 'Test Döngüsü',
                                       'Eğitim', 'Otomasyon', 'Diğer'],
                                width=15, font=('Arial', 10))
            combo.grid(row=i+1, column=1, sticky='ew', padx=1, pady=1)
            row[1].destroy()
            row[1] = combo
        
        # Satır ekleme butonu
        ttk.Button(main_frame, text="➕ Yeni Satır Ekle",
                  command=self.add_recommendation_row).pack(pady=10)
        
        return tab
    
    def create_settings_tab(self):
        """Ayarlar sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Ayarlar")
        
        # Görsel ayarları
        visual_frame = ttk.LabelFrame(tab, text="Görsel Ayarları", padding=15)
        visual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Boyut ayarları
        settings = [
            ("Figure Genişlik (inch):", "fig_width", 12, 8, 20),
            ("Figure Yükseklik (inch):", "fig_height", 8, 6, 15),
            ("DPI (Çözünürlük):", "fig_dpi", 300, 100, 600)
        ]
        
        self.visual_settings = {}
        for i, (label, key, default, min_val, max_val) in enumerate(settings):
            ttk.Label(visual_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            
            spinbox = ttk.Spinbox(visual_frame, from_=min_val, to=max_val, width=10)
            spinbox.set(default)
            spinbox.grid(row=i, column=1, pady=5, padx=10)
            
            self.visual_settings[key] = spinbox
        
        # Şeffaf arkaplan seçeneği
        ttk.Checkbutton(visual_frame, text="Şeffaf Arkaplan (Word için önerilen)",
                       variable=self.transparent_bg,
                       command=self.update_preview).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Tema ayarları
        theme_frame = ttk.LabelFrame(tab, text="Tema Seçimi", padding=15)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Tema listesi
        ttk.Label(theme_frame, text="Hazır Temalar:").grid(row=0, column=0, sticky='w', pady=5)
        
        self.theme_combo = ttk.Combobox(theme_frame, values=list(self.themes.keys()), width=20)
        self.theme_combo.set(self.current_theme)
        self.theme_combo.grid(row=0, column=1, padx=10, pady=5)
        self.theme_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_theme())
        
        ttk.Button(theme_frame, text="Temayı Uygula", command=self.apply_theme).grid(row=0, column=2, padx=5)
        
        # Renk önizleme
        color_preview_frame = ttk.LabelFrame(theme_frame, text="Tema Renkleri", padding=10)
        color_preview_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')
        
        self.color_labels = {}
        color_items = [
            ('Primary', 'primary'), ('Secondary', 'secondary'), ('Accent', 'accent'),
            ('Success', 'success'), ('Warning', 'warning'), ('Danger', 'danger')
        ]
        
        for i, (name, key) in enumerate(color_items):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(color_preview_frame, text=f"{name}:").grid(row=row, column=col, sticky='w', padx=5, pady=3)
            
            color_label = tk.Label(color_preview_frame, text="   ", bg=self.colors[key], width=10)
            color_label.grid(row=row, column=col+1, padx=5, pady=3)
            self.color_labels[key] = color_label
        
        # Kayıt ayarları
        save_frame = ttk.LabelFrame(tab, text="Kayıt Ayarları", padding=15)
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(save_frame, text="Kayıt Klasörü:").grid(row=0, column=0, sticky='w')
        
        self.save_path = tk.StringVar(value=os.path.join(os.getcwd(), "IDCA_Gorseller"))
        entry = ttk.Entry(save_frame, textvariable=self.save_path, width=50)
        entry.grid(row=0, column=1, padx=10)
        
        ttk.Button(save_frame, text="📁 Seç",
                  command=self.select_folder).grid(row=0, column=2)
        
        return tab
    
    def apply_theme(self):
        """Seçili temayı uygula"""
        selected_theme = self.theme_combo.get()
        if selected_theme in self.themes:
            self.current_theme = selected_theme
            self.colors = self.themes[selected_theme].copy()
            
            # Renk önizlemelerini güncelle
            for key, label in self.color_labels.items():
                if key in self.colors:
                    label.config(bg=self.colors[key])
            
            # Önizlemeyi güncelle
            self.update_preview()
            
            self.status_label.config(text=f"✅ {selected_theme} teması uygulandı", foreground='green')
    
    def create_preview_panel(self, parent):
        """Sağ panel - Önizleme"""
        # Başlık
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header, text="Önizleme", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Görsel seçimi
        self.preview_combo = ttk.Combobox(header, values=[
            'Figure 1 - Test Uygunluk',
            'Figure 2 - Test Durumu',
            'Table 1 - Sonuç',
            'Table 2 - MITRE',
            'Table 3 - Tetiklenen',
            'Table 4 - Algılanamayan',
            'Table 5 - Öneriler'
        ], width=20)
        self.preview_combo.pack(side=tk.LEFT, padx=10)
        self.preview_combo.current(0)
        self.preview_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        ttk.Button(header, text="🔄", command=self.update_preview, width=3).pack(side=tk.LEFT)
        
        # Önizleme alanı
        self.preview_frame = ttk.LabelFrame(parent, text="", padding=5)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self, parent):
        """Durum çubuğu"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Hazır", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.data_status = ttk.Label(status_frame, text="", font=('Arial', 9))
        self.data_status.pack(side=tk.RIGHT, padx=10)
    
    def calculate_stats(self, event=None):
        """Test istatistiklerini hesapla"""
        try:
            total = int(self.test_entries['total_rules'].get() or 0)
            tested = int(self.test_entries['tested_rules'].get() or 0)
            triggered = int(self.test_entries['triggered_rules'].get() or 0)
            
            # Validasyon
            if tested > total:
                self.status_label.config(text="⚠️ Test edilen > Toplam olamaz!", foreground='red')
                return
            if triggered > tested:
                self.status_label.config(text="⚠️ Tetiklenen > Test edilen olamaz!", foreground='red')
                return
            
            # Hesaplamalar
            not_tested = total - tested
            failed = tested - triggered
            success_rate = (triggered / tested * 100) if tested > 0 else 0
            coverage_rate = (tested / total * 100) if total > 0 else 0
            
            # Güncelle
            self.calc_labels['not_tested'].config(text=str(not_tested))
            self.calc_labels['failed'].config(text=str(failed))
            self.calc_labels['success_rate'].config(text=f"%{success_rate:.1f}")
            self.calc_labels['coverage_rate'].config(text=f"%{coverage_rate:.1f}")
            
            # Renk
            color = 'green' if success_rate >= 70 else 'orange' if success_rate >= 50 else 'red'
            self.calc_labels['success_rate'].config(foreground=color)
            
            self.status_label.config(text="✅ Hesaplandı", foreground='green')
            
        except ValueError:
            pass
    
    def calculate_mitre_rates(self):
        """MITRE başarı oranlarını hesapla"""
        for row in self.mitre_table.entries:
            try:
                test = int(row[1].get() or 0)
                triggered = int(row[2].get() or 0)
                
                if test > 0:
                    rate = (triggered / test) * 100
                    row[3].delete(0, tk.END)
                    row[3].insert(0, f"{rate:.1f}")
                    
                    # Renk kodlaması
                    if rate >= 70:
                        row[3].config(foreground='green')
                    elif rate >= 40:
                        row[3].config(foreground='orange')
                    else:
                        row[3].config(foreground='red')
            except:
                pass
        
        self.status_label.config(text="✅ MITRE oranları hesaplandı", foreground='green')
    
    def clear_mitre_table(self):
        """MITRE tablosunu temizle (sadece sayıları)"""
        for row in self.mitre_table.entries:
            row[1].delete(0, tk.END)
            row[2].delete(0, tk.END)
            row[3].delete(0, tk.END)
    
    def add_recommendation_row(self):
        """Öneri tablosuna yeni satır ekle"""
        self.recommendations_table.add_row()
        # Yeni satırı ayarla
        new_row = self.recommendations_table.entries[-1]
        new_row[0].insert(0, f"P{len(self.recommendations_table.entries)}")
        new_row[0].config(state='readonly')
    
    def show_welcome(self):
        """Hoş geldiniz mesajı"""
        welcome_text = f"""
IDCA Rapor Görselleştirici v5.0 FINAL

✅ Türkçe karakter tam desteği
✅ Tablo şeklinde kolay veri girişi
✅ 5 farklı hazır tema seçeneği
✅ Şeffaf arkaplan desteği (Word için ideal)
✅ Tema değişiklikleri önizlemede anında görünür
✅ Tüm görseller seçili tema ile oluşturulur

Aktif Tema: {self.current_theme}
Arkaplan: {'Şeffaf' if self.transparent_bg.get() else 'Renkli'}

Başlamak için:
1. Sekmelerde verileri girin
2. Ayarlar sekmesinden tema seçin
3. 'GÖRSELLER OLUŞTUR' butonuna tıklayın
        """
        self.status_label.config(text="Hoş geldiniz! Kılavuz için '📖 Kılavuz' butonuna tıklayın.")
    
    def show_guide(self):
        """Kullanım kılavuzu"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 Kullanım Kılavuzu")
        guide_window.geometry("800x600")
        
        text = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Arial', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guide_text = """
IDCA RAPOR GÖRSELLEŞTİRİCİ KULLANIM KILAVUZU
==============================================

🎯 AMAÇ
Bu araç, IDCA test sonuçlarınızı Word raporları için profesyonel görsellere dönüştürür.

📊 ÜRETILEN GÖRSELLER
• Figure 1: Test Uygunluk Grafiği
• Figure 2: Test Durumu Grafikleri
• Table 1: Sonuç Değerlendirme
• Table 2: MITRE ATT&CK Kapsama
• Table 3: Tetiklenen Kurallar
• Table 4: Algılanamayan Teknikler
• Table 5: Öneriler

📝 VERİ GİRİŞİ

1. GENEL BİLGİLER
   - Kurum adı, tarih, hazırlayan bilgileri
   - Türkçe karakterler desteklenir (ç, ğ, ı, ö, ş, ü)

2. TEST SONUÇLARI
   - Toplam, test edilen, tetiklenen sayıları
   - Diğer değerler otomatik hesaplanır

3. MITRE ATT&CK (TABLO GİRİŞİ)
   - Her satıra test ve tetiklenen sayıları girin
   - Başarı oranları otomatik hesaplanır
   - Taktik isimleri sabittir

4. KURALLAR (TABLO GİRİŞİ)
   - Tetiklenen kuralları tabloya girin
   - Algılanamayan teknikleri ayrı tabloya girin
   - Kritiklik seviyeleri dropdown menüden seçilir

5. ÖNERİLER (TABLO GİRİŞİ)
   - Öncelikler otomatik numaralanır
   - Kategoriler dropdown menüden seçilir
   - Öneri metinlerini yazın

💡 İPUÇLARI

• TABLO GİRİŞİ: Tab tuşu ile hücreler arası geçiş yapın
• EXCEL'DEN KOPYALAMA: Verileri Excel'den kopyalayıp yapıştırabilirsiniz
• TÜRKÇE KARAKTER: Tüm alanlarda Türkçe karakterler kullanılabilir
• KAYDETME: JSON formatında kayıt yaparak daha sonra devam edebilirsiniz

📁 GÖRSEL OLUŞTURMA

1. Tüm verileri girin
2. "GÖRSELLER OLUŞTUR" butonuna tıklayın
3. Görseller belirlenen klasöre kaydedilir
4. Her görsel ayrı PNG dosyası olarak oluşturulur

📋 WORD'E EKLEME

1. PNG dosyalarını Word'e ekleyin
2. "Metinle Satır İçi" seçeneğini kullanın
3. Sıkıştırmayı kapatın (300 DPI kalite)

⚠️ DİKKAT EDİLECEKLER

• Sayısal alanlara sadece rakam girin
• Test edilen ≤ Toplam kural
• Tetiklenen ≤ Test edilen
• Güven skorları 0-100 arası

Başarılı raporlamalar! 🚀
"""
        
        text.insert(tk.END, guide_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(guide_window, text="Kapat", 
                  command=guide_window.destroy).pack(pady=10)
    
    def collect_data(self):
        """Tüm verileri topla"""
        # Genel bilgiler
        for key, entry in self.general_entries.items():
            self.data['general'][key] = entry.get()
        
        # Test sonuçları
        for key, entry in self.test_entries.items():
            try:
                self.data['test_results'][key] = int(entry.get() or 0)
            except:
                self.data['test_results'][key] = 0
        
        # Hesaplanmış değerler
        total = self.data['test_results'].get('total_rules', 0)
        tested = self.data['test_results'].get('tested_rules', 0)
        triggered = self.data['test_results'].get('triggered_rules', 0)
        
        self.data['test_results']['not_tested'] = total - tested
        self.data['test_results']['failed'] = tested - triggered
        self.data['test_results']['success_rate'] = (triggered/tested*100) if tested > 0 else 0
        
        # MITRE taktikleri - TABLODAN
        self.data['mitre_tactics'] = {}
        for row in self.mitre_table.get_data():
            if len(row) >= 4 and row[0]:
                try:
                    test = int(row[1] or 0)
                    trig = int(row[2] or 0)
                    self.data['mitre_tactics'][row[0]] = {
                        'test': test,
                        'triggered': trig,
                        'rate': float(row[3] or 0)
                    }
                except:
                    pass
        
        # Tetiklenen kurallar - TABLODAN
        self.data['triggered_rules'] = []
        for row in self.triggered_table.get_data():
            if len(row) >= 4 and row[0]:
                self.data['triggered_rules'].append({
                    'name': row[0],
                    'mitre': row[1],
                    'tactic': row[2],
                    'confidence': row[3].replace('%', '')
                })
        
        # Algılanamayan teknikler - TABLODAN
        self.data['undetected_techniques'] = []
        for row in self.undetected_table.get_data():
            if len(row) >= 4 and row[0]:
                self.data['undetected_techniques'].append({
                    'id': row[0],
                    'name': row[1],
                    'tactic': row[2],
                    'criticality': row[3]
                })
        
        # Öneriler - TABLODAN
        self.data['recommendations'] = []
        for row in self.recommendations_table.get_data():
            if len(row) >= 3 and row[2]:
                self.data['recommendations'].append({
                    'priority': row[0],
                    'category': row[1],
                    'text': row[2]
                })
    
    def save_json(self):
        """Verileri JSON olarak kaydet"""
        self.collect_data()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON dosyaları", "*.json")],
            initialfile=f"IDCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Başarılı", "Veriler kaydedildi!")
                self.status_label.config(text="✅ Kaydedildi", foreground='green')
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt hatası: {str(e)}")
    
    def load_json(self):
        """JSON dosyasından veri yükle"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON dosyaları", "*.json")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                self.populate_forms()
                messagebox.showinfo("Başarılı", "Veriler yüklendi!")
                self.status_label.config(text="✅ Yüklendi", foreground='green')
            except Exception as e:
                messagebox.showerror("Hata", f"Yükleme hatası: {str(e)}")
    
    def populate_forms(self):
        """Yüklenen veriyi formlara doldur"""
        # Genel bilgiler
        for key, value in self.data.get('general', {}).items():
            if key in self.general_entries:
                self.general_entries[key].delete(0, tk.END)
                self.general_entries[key].insert(0, value)
        
        # Test sonuçları
        for key, value in self.data.get('test_results', {}).items():
            if key in self.test_entries:
                self.test_entries[key].delete(0, tk.END)
                self.test_entries[key].insert(0, str(value))
        
        self.calculate_stats()
        
        # MITRE taktikleri - TABLOYA
        mitre_data = []
        for tactic in ['Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
                      'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
                      'Collection', 'Command and Control', 'Exfiltration', 'Impact']:
            if tactic in self.data.get('mitre_tactics', {}):
                values = self.data['mitre_tactics'][tactic]
                mitre_data.append([tactic, str(values['test']), str(values['triggered']), f"{values['rate']:.1f}"])
            else:
                mitre_data.append([tactic, '', '', ''])
        
        self.mitre_table.set_data(mitre_data)
        
        # Diğer tablolar
        triggered_data = [[r['name'], r['mitre'], r['tactic'], r['confidence']] 
                         for r in self.data.get('triggered_rules', [])]
        self.triggered_table.set_data(triggered_data)
        
        undetected_data = [[t['id'], t['name'], t['tactic'], t['criticality']]
                          for t in self.data.get('undetected_techniques', [])]
        self.undetected_table.set_data(undetected_data)
        
        rec_data = [[r['priority'], r['category'], r['text']]
                   for r in self.data.get('recommendations', [])]
        self.recommendations_table.set_data(rec_data)
    
    def load_sample_data(self):
        """Örnek veri yükle"""
        sample = {
            'general': {
                'company_name': 'Örnek Şirket A.Ş.',
                'report_date': 'Ocak 2025',
                'prepared_by': 'Güvenlik Ekibi',
                'report_id': 'IDCA-2025-001',
                'report_title': 'Güvenlik Değerlendirme Raporu',
                'classification': 'Gizli'
            },
            'test_results': {
                'total_rules': 291,
                'tested_rules': 114,
                'triggered_rules': 65
            },
            'mitre_tactics': {
                'Initial Access': {'test': 8, 'triggered': 3, 'rate': 37.5},
                'Execution': {'test': 12, 'triggered': 5, 'rate': 41.7},
                'Persistence': {'test': 16, 'triggered': 8, 'rate': 50.0},
                'Privilege Escalation': {'test': 10, 'triggered': 3, 'rate': 30.0}
            },
            'triggered_rules': [
                {'name': 'Şüpheli PowerShell Komutu', 'mitre': 'T1059.001', 
                 'tactic': 'Execution', 'confidence': '95'},
                {'name': 'Brute Force Saldırısı', 'mitre': 'T1110', 
                 'tactic': 'Credential Access', 'confidence': '88'}
            ],
            'undetected_techniques': [
                {'id': 'T1566.001', 'name': 'Phishing Ekleri', 
                 'tactic': 'Initial Access', 'criticality': 'Kritik'},
                {'id': 'T1548.002', 'name': 'UAC Bypass', 
                 'tactic': 'Privilege Escalation', 'criticality': 'Yüksek'}
            ],
            'recommendations': [
                {'priority': 'P1', 'category': 'Log Kaynakları', 
                 'text': 'Windows Security loglarının tam entegrasyonu sağlanmalı'},
                {'priority': 'P2', 'category': 'Kural Optimizasyonu',
                 'text': 'Başarısız kuralların eşik değerleri güncellenmeli'}
            ]
        }
        
        self.data = sample
        self.populate_forms()
        
        messagebox.showinfo("Başarılı", "Örnek veriler yüklendi!")
        self.status_label.config(text="✅ Örnek veri yüklendi", foreground='green')
    
    def clear_all(self):
        """Tüm verileri temizle"""
        if messagebox.askyesno("Onay", "Tüm veriler silinecek. Emin misiniz?"):
            # Formları temizle
            for entry in self.general_entries.values():
                entry.delete(0, tk.END)
            
            for entry in self.test_entries.values():
                entry.delete(0, tk.END)
            
            for label in self.calc_labels.values():
                label.config(text="0")
            
            # Tabloları temizle
            self.clear_mitre_table()
            self.triggered_table.clear()
            self.undetected_table.clear()
            self.recommendations_table.clear()
            
            self.init_data()
            
            self.status_label.config(text="✅ Temizlendi", foreground='orange')
    
    def select_folder(self):
        """Kayıt klasörü seç"""
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)
    
    def update_preview(self):
        """Önizlemeyi güncelle - TEMA DESTEKLİ"""
        # Önizleme alanını temizle
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        try:
            self.collect_data()
            
            # Figure oluştur
            fig = plt.figure(figsize=(5, 4), dpi=80)
            
            # Şeffaf arkaplan kontrolü
            if self.transparent_bg.get():
                fig.patch.set_facecolor('none')
                fig.patch.set_alpha(0)
            else:
                fig.patch.set_facecolor(self.colors['dark'])
            
            selected = self.preview_combo.get()
            
            if 'Figure 1' in selected:
                self.preview_figure1(fig)
            elif 'Figure 2' in selected:
                self.preview_figure2(fig)
            else:
                self.preview_table(fig, selected)
            
            # Canvas'a ekle
            canvas = FigureCanvasTkAgg(fig, master=self.preview_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            error_label = ttk.Label(self.preview_frame,
                                   text=f"Önizleme hatası:\n{str(e)}",
                                   font=('Arial', 10))
            error_label.pack(expand=True)
    
    def preview_figure1(self, fig):
        """Figure 1 önizleme - TEMA DESTEKLİ"""
        ax = fig.add_subplot(111)
        
        # Şeffaf arkaplan kontrolü
        if self.transparent_bg.get():
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            ax.set_facecolor(self.colors['primary'])
        
        total = self.data['test_results'].get('total_rules', 100)
        tested = self.data['test_results'].get('tested_rules', 50)
        not_tested = total - tested if total > tested else 0
        
        sizes = [tested, not_tested]
        labels = ['Test\nEdilmiş', 'Test\nEdilmemiş']
        colors = [self.colors['accent_secondary'], self.colors['gray']]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                          autopct='%1.1f%%', startangle=90,
                                          textprops={'color': self.colors['light']})
        
        # Merkez daire
        centre_circle = plt.Circle((0, 0), 0.70, 
                                  fc='none' if self.transparent_bg.get() else self.colors['primary'],
                                  linewidth=2, edgecolor=self.colors['accent'])
        ax.add_artist(centre_circle)
        
        ax.set_title('Test Uygunluk', fontsize=11, color=self.colors['light'], pad=10)
    
    def preview_figure2(self, fig):
        """Figure 2 önizleme - TEMA DESTEKLİ"""
        ax = fig.add_subplot(111)
        
        # Şeffaf arkaplan kontrolü
        if self.transparent_bg.get():
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            ax.set_facecolor(self.colors['primary'])
        
        triggered = self.data['test_results'].get('triggered_rules', 30)
        failed = self.data['test_results'].get('failed', 20)
        
        bars = ax.bar(['Tetiklenen', 'Başarısız'], [triggered, failed],
                     color=[self.colors['success'], self.colors['danger']],
                     edgecolor=self.colors['accent'], linewidth=2)
        
        ax.set_title('Test Durumu', fontsize=11, color=self.colors['light'])
        ax.tick_params(colors=self.colors['gray'])
        ax.set_ylabel('Sayı', color=self.colors['light'])
        
        # Grid
        ax.grid(True, alpha=0.3, color=self.colors['gray'])
    
    def preview_table(self, fig, selected):
        """Tablo önizleme - TEMA DESTEKLİ"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            ax.set_facecolor('none')
        
        # Örnek tablo
        table_data = [['Başlık 1', 'Başlık 2', 'Başlık 3'],
                     ['Veri 1', 'Veri 2', 'Veri 3'],
                     ['Veri 4', 'Veri 5', 'Veri 6']]
        
        # Renk şeması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 3)  # Başlık
        cell_colors.append([self.colors['secondary']] * 3)
        cell_colors.append([self.colors['secondary']] * 3)
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors)
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Başlık satırı
        for i in range(3):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title(selected, fontsize=11, color=self.colors['light'])
    
    def refresh_preview(self):
        """Önizlemeyi yenile - Tema değişikliklerini uygula"""
        self.update_preview()
        self.status_label.config(text="✅ Önizleme yenilendi", foreground='green')
    
    def generate_all(self):
        """Tüm görselleri oluştur - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        self.collect_data()
        
        # Validasyon
        if not self.data['general'].get('company_name'):
            messagebox.showwarning("Uyarı", "Lütfen en azından kurum adını girin!")
            return
        
        if not self.data['test_results'].get('total_rules'):
            messagebox.showwarning("Uyarı", "Lütfen test sonuçlarını girin!")
            return
        
        # Kayıt klasörü
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Progress penceresi
        progress = tk.Toplevel(self.root)
        progress.title("Görseller Oluşturuluyor")
        progress.geometry("500x250")
        progress.transient(self.root)
        
        # Tema ve arkaplan bilgisi
        theme_info = ttk.Label(progress, 
                              text=f"Tema: {self.current_theme} | Arkaplan: {'Şeffaf' if self.transparent_bg.get() else 'Renkli'}",
                              font=('Arial', 10, 'italic'), foreground='blue')
        theme_info.pack(pady=10)
        
        label = ttk.Label(progress, text="Başlıyor...", font=('Arial', 12))
        label.pack(pady=10)
        
        pbar = ttk.Progressbar(progress, length=400, mode='determinate')
        pbar.pack(pady=20)
        
        details = ttk.Label(progress, text="", font=('Arial', 9), foreground='gray')
        details.pack(pady=5)
        
        # Görseller
        visuals = [
            ('Figure_1_Test_Uygunluk', self.generate_figure1),
            ('Figure_2_Test_Durumu', self.generate_figure2),
            ('Table_1_Sonuc_Degerlendirme', self.generate_table1),
            ('Table_2_MITRE_Kapsama', self.generate_table2),
            ('Table_3_Tetiklenen_Kurallar', self.generate_table3),
            ('Table_4_Algilanamayan_Teknikler', self.generate_table4),
            ('Table_5_Oneriler', self.generate_table5)
        ]
        
        pbar['maximum'] = len(visuals)
        success = 0
        
        for i, (name, func) in enumerate(visuals):
            label.config(text=f"Oluşturuluyor: {name}")
            details.config(text=f"({i+1}/{len(visuals)}) {name}.png")
            pbar['value'] = i
            progress.update()
            
            try:
                filepath = os.path.join(save_dir, f"{name}.png")
                func(filepath)
                success += 1
            except Exception as e:
                print(f"Hata {name}: {e}")
        
        pbar['value'] = len(visuals)
        label.config(text=f"✅ Tamamlandı! {success}/{len(visuals)} görsel oluşturuldu")
        details.config(text=f"Kayıt yeri: {save_dir}")
        
        # Arkaplan bilgisi
        if self.transparent_bg.get():
            info_label = ttk.Label(progress, 
                                  text="ℹ️ Görseller şeffaf arkaplanla kaydedildi (Word için ideal)",
                                  font=('Arial', 9), foreground='green')
            info_label.pack(pady=5)
        
        ttk.Button(progress, text="Klasörü Aç", 
                  command=lambda: self.open_folder(save_dir)).pack(side=tk.LEFT, padx=50, pady=10)
        ttk.Button(progress, text="Kapat", 
                  command=progress.destroy).pack(side=tk.RIGHT, padx=50, pady=10)
    
    def open_folder(self, folder_path):
        """Klasörü aç"""
        if sys.platform.startswith('win'):
            os.startfile(folder_path)
        elif sys.platform.startswith('darwin'):
            os.system(f'open "{folder_path}"')
        else:
            os.system(f'xdg-open "{folder_path}"')
    
    def generate_figure1(self, filepath):
        """Figure 1 oluştur - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        width = float(self.visual_settings['fig_width'].get())
        height = float(self.visual_settings['fig_height'].get())
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan ayarı
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
            ax.set_facecolor(self.colors['primary'])
        
        # Veriler
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        not_tested = self.data['test_results']['not_tested']
        triggered = self.data['test_results']['triggered_rules']
        success_rate = self.data['test_results']['success_rate']
        
        # Pasta grafik
        sizes = [tested, not_tested]
        labels = [f'Test Edilmiş\n{tested} kural\n(%{tested/total*100:.1f})',
                 f'Test Edilmemiş\n{not_tested} kural\n(%{not_tested/total*100:.1f})']
        colors = [self.colors['accent_secondary'], self.colors['gray']]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          explode=(0.05, 0), startangle=90, shadow=not self.transparent_bg.get(),
                                          textprops={'fontsize': 11, 'color': self.colors['light']})
        
        # Merkez daire
        centre_circle = plt.Circle((0, 0), 0.70, 
                                  fc='none' if self.transparent_bg.get() else self.colors['primary'],
                                  linewidth=2, edgecolor=self.colors['accent'])
        ax.add_artist(centre_circle)
        
        # Merkez metin
        ax.text(0, 0.1, str(total), ha='center', va='center',
               fontsize=36, fontweight='bold', color=self.colors['accent'])
        ax.text(0, -0.15, 'Toplam Kural', ha='center', va='center',
               fontsize=12, color=self.colors['gray'])
        ax.text(0, -0.3, f'Başarı: %{success_rate:.1f}', ha='center', va='center',
               fontsize=11, fontweight='bold',
               color=self.colors['success'] if success_rate >= 70 else self.colors['warning'])
        
        # Başlık
        ax.set_title('Figure 1: Analiz Edilen Korelasyonların Test Uygunluk Grafiği',
                    fontsize=14, fontweight='bold', color=self.colors['light'], pad=20)
        
        # Alt bilgi
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']} - {self.data['general']['report_date']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_figure2(self, filepath):
        """Figure 2 oluştur - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        width = float(self.visual_settings['fig_width'].get())
        height = float(self.visual_settings['fig_height'].get())
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig = plt.figure(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan ayarı
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        # Sol grafik
        ax1 = plt.subplot(1, 2, 1)
        if self.transparent_bg.get():
            ax1.set_facecolor('none')
            ax1.patch.set_alpha(0)
        else:
            ax1.set_facecolor(self.colors['primary'])
        
        triggered = self.data['test_results']['triggered_rules']
        failed = self.data['test_results']['failed']
        
        bars = ax1.bar(['Tetiklenen', 'Başarısız'], [triggered, failed],
                      color=[self.colors['success'], self.colors['danger']],
                      edgecolor=self.colors['accent'], linewidth=2)
        
        for bar, val in zip(bars, [triggered, failed]):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max([triggered, failed])*0.02,
                    str(val), ha='center', fontweight='bold', color=self.colors['light'])
        
        ax1.set_title('Test Sonuç Dağılımı', fontsize=12, color=self.colors['light'])
        ax1.set_ylabel('Kural Sayısı', color=self.colors['light'])
        ax1.tick_params(colors=self.colors['gray'])
        ax1.grid(True, alpha=0.3, color=self.colors['gray'], linestyle='--')
        
        # Sağ grafik - MITRE
        ax2 = plt.subplot(1, 2, 2)
        if self.transparent_bg.get():
            ax2.set_facecolor('none')
            ax2.patch.set_alpha(0)
        else:
            ax2.set_facecolor(self.colors['primary'])
        
        if self.data['mitre_tactics']:
            tactics_sorted = sorted(self.data['mitre_tactics'].items(),
                                  key=lambda x: x[1]['rate'])[:6]
            
            tactics = [t[0] for t in tactics_sorted]
            rates = [t[1]['rate'] for t in tactics_sorted]
            
            colors_bar = []
            for r in rates:
                if r < 40:
                    colors_bar.append(self.colors['danger'])
                elif r < 60:
                    colors_bar.append(self.colors['warning'])
                else:
                    colors_bar.append(self.colors['success'])
            
            bars2 = ax2.barh(range(len(tactics)), rates, color=colors_bar,
                           edgecolor=self.colors['accent'], linewidth=1)
            
            for bar, val in zip(bars2, rates):
                ax2.text(val + 1, bar.get_y() + bar.get_height()/2,
                        f'%{val:.1f}', va='center', fontweight='bold', color=self.colors['light'])
            
            ax2.set_yticks(range(len(tactics)))
            ax2.set_yticklabels(tactics, fontsize=9, color=self.colors['light'])
            ax2.set_xlim(0, 100)
            ax2.set_xlabel('Başarı Oranı (%)', color=self.colors['light'])
            ax2.set_title('En Düşük Performanslı Taktikler', fontsize=12, color=self.colors['light'])
            ax2.tick_params(colors=self.colors['gray'])
            ax2.grid(True, axis='x', alpha=0.3, color=self.colors['gray'], linestyle='--')
        
        fig.suptitle('Figure 2: Test Edilen Korelasyonların Durumu',
                    fontsize=14, fontweight='bold', color=self.colors['light'])
        
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']} - {self.data['general']['prepared_by']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table1(self, filepath):
        """Table 1 oluştur - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        width = float(self.visual_settings['fig_width'].get())
        height = 6
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
            ax.set_facecolor('none')
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        success_rate = self.data['test_results']['success_rate']
        not_tested = self.data['test_results']['not_tested']
        
        table_data = [
            ['Metrik', 'Değer', 'Hedef', 'Durum', 'Açıklama'],
            ['Toplam Kural', str(total), '300+', 
             '✅' if total >= 300 else '⚠️' if total >= 200 else '❌', 
             'Kapsam değerlendirmesi'],
            ['Test Edilen', str(tested), '200+',
             '✅' if tested >= 200 else '⚠️' if tested >= 100 else '❌',
             'Test kapsamı'],
            ['Başarı Oranı', f'%{success_rate:.1f}', '%70+',
             '✅' if success_rate >= 70 else '⚠️' if success_rate >= 50 else '❌',
             'Tespit yeteneği'],
            ['Test Edilmeyen', str(not_tested), '<50',
             '✅' if not_tested < 50 else '⚠️' if not_tested < 100 else '❌',
             'Kapsam dışı']
        ]
        
        # Renk şeması
        cell_colors = []
        for i, row in enumerate(table_data):
            if i == 0:
                cell_colors.append([self.colors['accent_secondary']] * 5)
            else:
                row_colors = [self.colors['secondary']] * 5
                if '✅' in row[3]:
                    row_colors[3] = self.colors['success']
                elif '⚠️' in row[3]:
                    row_colors[3] = self.colors['warning']
                elif '❌' in row[3]:
                    row_colors[3] = self.colors['danger']
                cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.2, 0.12, 0.12, 0.1, 0.36])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 1: Sonuç Değerlendirme Tablosu',
                    fontsize=14, fontweight='bold', pad=20, color=self.colors['light'])
        
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']} - {self.data['general']['report_date']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close() Kural', str(total), '300+', 
             '✅' if total >= 300 else '⚠️' if total >= 200 else '❌', 
             'Kapsam değerlendirmesi'],
            ['Test Edilen', str(tested), '200+',
             '✅' if tested >= 200 else '⚠️' if tested >= 100 else '❌',
             'Test kapsamı'],
            ['Başarı Oranı', f'%{success_rate:.1f}', '%70+',
             '✅' if success_rate >= 70 else '⚠️' if success_rate >= 50 else '❌',
             'Tespit yeteneği'],
            ['Test Edilmeyen', str(not_tested), '<50',
             '✅' if not_tested < 50 else '⚠️' if not_tested < 100 else '❌',
             'Kapsam dışı']
        ]
        
        # Renk şeması
        cell_colors = []
        for i, row in enumerate(table_data):
            if i == 0:
                cell_colors.append([self.colors['accent_secondary']] * 5)
            else:
                row_colors = [self.colors['secondary']] * 5
                if '✅' in row[3]:
                    row_colors[3] = self.colors['success']
                elif '⚠️' in row[3]:
                    row_colors[3] = self.colors['warning']
                elif '❌' in row[3]:
                    row_colors[3] = self.colors['danger']
                cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.2, 0.12, 0.12, 0.1, 0.36])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 1: Sonuç Değerlendirme Tablosu',
                    fontsize=14, fontweight='bold', pad=20)
        
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']} - {self.data['general']['report_date']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table2(self, filepath):
        """Table 2 - MITRE Kapsama - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        if not self.data['mitre_tactics']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(8, len(self.data['mitre_tactics']) * 0.6)
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['Taktik', 'Test Edilen', 'Tetiklenen', 'Başarı %', 'Kritiklik']
        rows = []
        
        sorted_tactics = sorted(self.data['mitre_tactics'].items(),
                              key=lambda x: x[1]['rate'])
        
        for tactic, values in sorted_tactics:
            kritiklik = 'Kritik' if values['rate'] < 40 else 'Orta' if values['rate'] < 60 else 'İyi'
            rows.append([
                tactic,
                str(values['test']),
                str(values['triggered']),
                f"%{values['rate']:.1f}",
                kritiklik
            ])
        
        table_data = [headers] + rows
        
        # Renk şeması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            rate = float(row[3].strip('%'))
            if rate < 40:
                row_colors[3] = self.colors['danger']
                row_colors[4] = self.colors['danger']
            elif rate < 60:
                row_colors[3] = self.colors['warning']
                row_colors[4] = self.colors['warning']
            else:
                row_colors[3] = self.colors['success']
                row_colors[4] = self.colors['success']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.28, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 2: MITRE ATT&CK Kapsama Analizi',
                    fontsize=14, fontweight='bold', pad=20, color=self.colors['light'])
        
        # Özet
        avg_success = np.mean([v['rate'] for v in self.data['mitre_tactics'].values()])
        fig.text(0.5, 0.05, f'Ortalama Başarı: %{avg_success:.1f}',
                ha='center', fontsize=10, color=self.colors['light'])
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table3(self, filepath):
        """Table 3 - Tetiklenen Kurallar - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        if not self.data['triggered_rules']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['triggered_rules']) * 0.5))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['ID', 'Kural Adı', 'MITRE Teknik', 'Taktik', 'Güven Skoru']
        rows = []
        
        for i, rule in enumerate(self.data['triggered_rules'][:20], 1):
            rows.append([
                str(i),
                rule['name'][:40] + '...' if len(rule['name']) > 40 else rule['name'],
                rule['mitre'],
                rule['tactic'],
                f"%{rule['confidence']}"
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            try:
                confidence = int(row[4].strip('%'))
                if confidence >= 90:
                    row_colors[4] = self.colors['success']
                elif confidence >= 80:
                    row_colors[4] = self.colors['warning']
                else:
                    row_colors[4] = self.colors['danger']
            except:
                pass
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.08, 0.38, 0.15, 0.2, 0.12])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.8)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 3: Tetiklenen Korelasyon Kuralları Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=self.colors['light'])
        
        fig.text(0.5, 0.02, f"Toplam {len(self.data['triggered_rules'])} kural - {self.data['general']['company_name']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table4(self, filepath):
        """Table 4 - Algılanamayan Teknikler - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        if not self.data['undetected_techniques']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['undetected_techniques']) * 0.5))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['MITRE ID', 'Teknik Adı', 'Taktik', 'Kritiklik', 'Öncelik']
        rows = []
        
        # Kritiklik sıralama
        kritiklik_order = {'Kritik': 0, 'Yüksek': 1, 'Orta': 2, 'Düşük': 3}
        sorted_techniques = sorted(self.data['undetected_techniques'],
                                 key=lambda x: kritiklik_order.get(x['criticality'], 4))
        
        for i, tech in enumerate(sorted_techniques[:20], 1):
            rows.append([
                tech['id'],
                tech['name'][:35] + '...' if len(tech['name']) > 35 else tech['name'],
                tech['tactic'],
                tech['criticality'],
                f"P{i}"
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            if 'Kritik' in row[3]:
                row_colors[3] = self.colors['danger']
                row_colors[4] = self.colors['danger']
            elif 'Yüksek' in row[3]:
                row_colors[3] = self.colors['warning']
                row_colors[4] = self.colors['warning']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.12, 0.35, 0.2, 0.12, 0.1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 4: Algılanamayan MITRE Teknikleri Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=self.colors['light'])
        
        kritik_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Kritik')
        yuksek_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Yüksek')
        
        fig.text(0.5, 0.02, f"⚠️ {kritik_count} Kritik, {yuksek_count} Yüksek seviyeli teknik için acil önlem gerekli",
                ha='center', fontsize=10, weight='bold', color=self.colors['warning'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table5(self, filepath):
        """Table 5 - Öneriler - TEMA VE ŞEFFAF ARKAPLAN DESTEKLİ"""
        if not self.data['recommendations']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['recommendations']) * 0.6))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        
        # Şeffaf arkaplan
        if self.transparent_bg.get():
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)
        else:
            fig.patch.set_facecolor(self.colors['dark'])
        
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['Öncelik', 'Kategori', 'Öneri', 'Beklenen Etki']
        rows = []
        
        for i, rec in enumerate(self.data['recommendations'][:15], 1):
            etki = 'Yüksek' if i <= 3 else 'Orta' if i <= 7 else 'Normal'
            rows.append([
                rec['priority'],
                rec['category'],
                rec['text'][:50] + '...' if len(rec['text']) > 50 else rec['text'],
                etki
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 4)
        
        for i, row in enumerate(rows):
            row_colors = [self.colors['secondary']] * 4
            if i < 3:
                row_colors[0] = self.colors['danger']
                row_colors[3] = self.colors['success']
            elif i < 7:
                row_colors[0] = self.colors['warning']
                row_colors[3] = self.colors['warning']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.1, 0.2, 0.45, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(4):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 5: Yazılması Gereken Korelasyon Kurallarının Öneri Listesi',
                    fontsize=14, fontweight='bold', pad=20, color=self.colors['light'])
        
        fig.text(0.5, 0.03, f'Toplam {len(self.data["recommendations"])} öneri',
                ha='center', fontsize=9, style='italic', color=self.colors['success'])
        fig.text(0.5, 0.005, f"{self.data['general']['company_name']} - {self.data['general']['prepared_by']}",
                ha='center', fontsize=8, color=self.colors['gray'])
        
        plt.tight_layout()
        
        # Kaydet
        if self.transparent_bg.get():
            plt.savefig(filepath, dpi=dpi, transparent=True, bbox_inches='tight')
        else:
            plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()size=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['Taktik', 'Test Edilen', 'Tetiklenen', 'Başarı %', 'Kritiklik']
        rows = []
        
        sorted_tactics = sorted(self.data['mitre_tactics'].items(),
                              key=lambda x: x[1]['rate'])
        
        for tactic, values in sorted_tactics:
            kritiklik = 'Kritik' if values['rate'] < 40 else 'Orta' if values['rate'] < 60 else 'İyi'
            rows.append([
                tactic,
                str(values['test']),
                str(values['triggered']),
                f"%{values['rate']:.1f}",
                kritiklik
            ])
        
        table_data = [headers] + rows
        
        # Renk şeması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            rate = float(row[3].strip('%'))
            if rate < 40:
                row_colors[3] = self.colors['danger']
                row_colors[4] = self.colors['danger']
            elif rate < 60:
                row_colors[3] = self.colors['warning']
                row_colors[4] = self.colors['warning']
            else:
                row_colors[3] = self.colors['success']
                row_colors[4] = self.colors['success']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.28, 0.15, 0.15, 0.15, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 2: MITRE ATT&CK Kapsama Analizi',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Özet
        avg_success = np.mean([v['rate'] for v in self.data['mitre_tactics'].values()])
        fig.text(0.5, 0.05, f'Ortalama Başarı: %{avg_success:.1f}',
                ha='center', fontsize=10, color=self.colors['light'])
        fig.text(0.5, 0.02, f"{self.data['general']['company_name']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table3(self, filepath):
        """Table 3 - Tetiklenen Kurallar"""
        if not self.data['triggered_rules']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['triggered_rules']) * 0.5))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['ID', 'Kural Adı', 'MITRE Teknik', 'Taktik', 'Güven Skoru']
        rows = []
        
        for i, rule in enumerate(self.data['triggered_rules'][:20], 1):
            rows.append([
                str(i),
                rule['name'][:40] + '...' if len(rule['name']) > 40 else rule['name'],
                rule['mitre'],
                rule['tactic'],
                f"%{rule['confidence']}"
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            try:
                confidence = int(row[4].strip('%'))
                if confidence >= 90:
                    row_colors[4] = self.colors['success']
                elif confidence >= 80:
                    row_colors[4] = self.colors['warning']
                else:
                    row_colors[4] = self.colors['danger']
            except:
                pass
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.08, 0.38, 0.15, 0.2, 0.12])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.8)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 3: Tetiklenen Korelasyon Kuralları Listesi',
                    fontsize=14, fontweight='bold', pad=20)
        
        fig.text(0.5, 0.02, f"Toplam {len(self.data['triggered_rules'])} kural - {self.data['general']['company_name']}",
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table4(self, filepath):
        """Table 4 - Algılanamayan Teknikler"""
        if not self.data['undetected_techniques']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['undetected_techniques']) * 0.5))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['MITRE ID', 'Teknik Adı', 'Taktik', 'Kritiklik', 'Öncelik']
        rows = []
        
        # Kritiklik sıralama
        kritiklik_order = {'Kritik': 0, 'Yüksek': 1, 'Orta': 2, 'Düşük': 3}
        sorted_techniques = sorted(self.data['undetected_techniques'],
                                 key=lambda x: kritiklik_order.get(x['criticality'], 4))
        
        for i, tech in enumerate(sorted_techniques[:20], 1):
            rows.append([
                tech['id'],
                tech['name'][:35] + '...' if len(tech['name']) > 35 else tech['name'],
                tech['tactic'],
                tech['criticality'],
                f"P{i}"
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            if 'Kritik' in row[3]:
                row_colors[3] = self.colors['danger']
                row_colors[4] = self.colors['danger']
            elif 'Yüksek' in row[3]:
                row_colors[3] = self.colors['warning']
                row_colors[4] = self.colors['warning']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.12, 0.35, 0.2, 0.12, 0.1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 4: Algılanamayan MITRE Teknikleri Listesi',
                    fontsize=14, fontweight='bold', pad=20)
        
        kritik_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Kritik')
        yuksek_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Yüksek')
        
        fig.text(0.5, 0.02, f"⚠️ {kritik_count} Kritik, {yuksek_count} Yüksek seviyeli teknik için acil önlem gerekli",
                ha='center', fontsize=10, weight='bold', color=self.colors['warning'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table5(self, filepath):
        """Table 5 - Öneriler"""
        if not self.data['recommendations']:
            return
        
        width = float(self.visual_settings['fig_width'].get())
        height = max(6, min(12, len(self.data['recommendations']) * 0.6))
        dpi = int(self.visual_settings['fig_dpi'].get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['Öncelik', 'Kategori', 'Öneri', 'Beklenen Etki']
        rows = []
        
        for i, rec in enumerate(self.data['recommendations'][:15], 1):
            etki = 'Yüksek' if i <= 3 else 'Orta' if i <= 7 else 'Normal'
            rows.append([
                rec['priority'],
                rec['category'],
                rec['text'][:50] + '...' if len(rec['text']) > 50 else rec['text'],
                etki
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 4)
        
        for i, row in enumerate(rows):
            row_colors = [self.colors['secondary']] * 4
            if i < 3:
                row_colors[0] = self.colors['danger']
                row_colors[3] = self.colors['success']
            elif i < 7:
                row_colors[0] = self.colors['warning']
                row_colors[3] = self.colors['warning']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.1, 0.2, 0.45, 0.15])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(4):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
        
        ax.set_title('Table 5: Yazılması Gereken Korelasyon Kurallarının Öneri Listesi',
                    fontsize=14, fontweight='bold', pad=20)
        
        fig.text(0.5, 0.03, f'Toplam {len(self.data["recommendations"])} öneri',
                ha='center', fontsize=9, style='italic', color=self.colors['success'])
        fig.text(0.5, 0.005, f"{self.data['general']['company_name']} - {self.data['general']['prepared_by']}",
                ha='center', fontsize=8, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()

def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    
    # Türkçe karakter için sistem ayarı
    try:
        root.tk.call('encoding', 'system', 'utf-8')
    except:
        pass
    
    app = IDCAFixedFinal(root)
    root.mainloop()

if __name__ == "__main__":
    main()
