#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCA Security Assessment - Rapor Görselleştirici FINAL VERSİYON
Profesyonel Word raporu için tam özellikli görselleştirme aracı
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
warnings.filterwarnings('ignore')

# Matplotlib Türkçe karakter desteği
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class IDCAFinalVersion:
    def __init__(self, root):
        self.root = root
        self.root.title("IDCA Security Assessment - Rapor Görselleştirici FINAL v4.0")
        self.root.geometry("1600x900")
        self.root.state('zoomed')  # Tam ekran başlat
        
        # Varsayılan tema renkleri
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
        
        # Veri yapısı - başlangıç değerleri
        self.reset_all_data()
        
        # GUI oluştur
        self.create_gui()
        
        # Kılavuz mesajını göster
        self.show_guide()
    
    def reset_all_data(self):
        """Tüm verileri sıfırla"""
        self.data = {
            'general': {
                'company_name': '',
                'report_date': '',
                'prepared_by': '',
                'report_id': '',
                'report_title': 'IDCA Security Assessment',
                'classification': 'Kurumsal - Gizli'
            },
            'test_results': {
                'total_rules': 0,
                'tested_rules': 0,
                'triggered_rules': 0,
                'failed_rules': 0,
                'not_tested': 0,
                'success_rate': 0.0
            },
            'mitre_tactics': {},
            'triggered_rules': [],
            'undetected_techniques': [],
            'recommendations': []
        }
    
    def create_gui(self):
        """Ana GUI oluştur"""
        # Ana container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Üst toolbar
        self.create_toolbar(main_container)
        
        # Ana içerik - PanedWindow ile bölünmüş
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Sol panel - Veri girişi
        left_frame = ttk.Frame(paned, relief=tk.RIDGE, borderwidth=1)
        paned.add(left_frame, weight=3)
        
        # Sağ panel - Önizleme
        right_frame = ttk.Frame(paned, relief=tk.RIDGE, borderwidth=1)
        paned.add(right_frame, weight=2)
        
        # Sol panel içeriği
        self.create_data_entry_panel(left_frame)
        
        # Sağ panel içeriği
        self.create_preview_panel(right_frame)
        
        # Durum çubuğu
        self.create_status_bar(main_container)
    
    def create_toolbar(self, parent):
        """Üst toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Sol butonlar
        left_buttons = ttk.Frame(toolbar)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="📖 Kılavuz", command=self.show_guide,
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_buttons, text="📁 Veri Yükle", command=self.load_data,
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_buttons, text="💾 Veri Kaydet", command=self.save_data,
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(left_buttons, text="📋 Toplu Giriş", command=self.bulk_data_entry,
                  width=12).pack(side=tk.LEFT, padx=2)
        
        # Orta butonlar
        ttk.Button(toolbar, text="🎨 TÜM GÖRSELLERİ OLUŞTUR", 
                  command=self.generate_all_visuals,
                  width=25).pack(side=tk.LEFT, padx=20)
        
        # Sağ butonlar
        right_buttons = ttk.Frame(toolbar)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="🔄 Önizle", command=self.refresh_preview,
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(right_buttons, text="🗑️ Sıfırla", command=self.reset_data,
                  width=10).pack(side=tk.LEFT, padx=2)
    
    def create_data_entry_panel(self, parent):
        """Sol panel - Veri girişi"""
        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sekmeler
        self.create_general_tab()
        self.create_test_results_tab()
        self.create_mitre_tab()
        self.create_rules_tab()
        self.create_recommendations_tab()
        self.create_settings_tab()
    
    def create_general_tab(self):
        """Genel bilgiler sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1️⃣ Genel Bilgiler")
        
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
        
        # İçerik
        frame = ttk.LabelFrame(scrollable_frame, text="📋 Rapor Bilgileri", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi mesajı
        info_label = ttk.Label(frame, text="ℹ️ Tüm alanları doldurun. Bu bilgiler raporun başlığında görünecektir.",
                              foreground='blue')
        info_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Form alanları
        fields = [
            ("Kurum/Şirket Adı: *", "company_name", "Örn: ABC Teknoloji A.Ş."),
            ("Rapor Tarihi: *", "report_date", "Örn: Ocak 2025"),
            ("Hazırlayan Birim/Kişi: *", "prepared_by", "Örn: SOC Team / Güvenlik Birimi"),
            ("Rapor No/ID: *", "report_id", "Örn: IDCA-2025-001"),
            ("Rapor Başlığı:", "report_title", "Örn: IDCA Security Assessment"),
            ("Gizlilik Seviyesi:", "classification", "Örn: Kurumsal - Gizli")
        ]
        
        self.general_entries = {}
        for i, (label, key, placeholder) in enumerate(fields, 1):
            # Label
            ttk.Label(frame, text=label, font=('Arial', 10)).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            
            # Entry
            entry = ttk.Entry(frame, width=40, font=('Arial', 10))
            entry.grid(row=i, column=1, pady=5, sticky=tk.W+tk.E)
            
            # Placeholder
            ttk.Label(frame, text=placeholder, foreground='gray', 
                     font=('Arial', 9, 'italic')).grid(
                row=i, column=2, sticky=tk.W, padx=(10, 0))
            
            # Varsayılan değer
            if key in ['report_title', 'classification']:
                entry.insert(0, self.data['general'][key])
            
            self.general_entries[key] = entry
        
        # Grid ağırlıkları
        frame.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_test_results_tab(self):
        """Test sonuçları sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2️⃣ Test Sonuçları")
        
        # Ana frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi mesajı
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Bilgi", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """• Toplam Kural: Sistemdeki tüm korelasyon kurallarının sayısı
• Test Edilen: Test sürecine dahil edilen kural sayısı
• Tetiklenen: Başarıyla alarm üreten kural sayısı
• Diğer değerler otomatik hesaplanır"""
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 9)).pack()
        
        # Veri giriş alanları
        entry_frame = ttk.LabelFrame(main_frame, text="📊 Test Verileri", padding=15)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid layout
        fields = [
            ("Toplam Kural Sayısı:", "total_rules", "Örn: 291"),
            ("Test Edilen Kural Sayısı:", "tested_rules", "Örn: 114"),
            ("Başarıyla Tetiklenen:", "triggered_rules", "Örn: 65")
        ]
        
        self.test_entries = {}
        for i, (label, key, hint) in enumerate(fields):
            ttk.Label(entry_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=8)
            
            entry = ttk.Entry(entry_frame, width=15, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=8, padx=10)
            entry.bind('<KeyRelease>', self.calculate_test_stats)
            
            ttk.Label(entry_frame, text=hint, foreground='gray',
                     font=('Arial', 9, 'italic')).grid(
                row=i, column=2, sticky=tk.W, padx=10)
            
            self.test_entries[key] = entry
        
        # Otomatik hesaplamalar
        calc_frame = ttk.LabelFrame(main_frame, text="🔢 Otomatik Hesaplamalar", padding=15)
        calc_frame.pack(fill=tk.X)
        
        self.calc_labels = {}
        calcs = [
            ("Test Edilmeyen Kural:", "not_tested", "Toplam - Test Edilen"),
            ("Başarısız Kural:", "failed", "Test Edilen - Tetiklenen"),
            ("Başarı Oranı:", "success_rate", "(Tetiklenen / Test Edilen) × 100"),
            ("Kapsama Oranı:", "coverage_rate", "(Test Edilen / Toplam) × 100")
        ]
        
        for i, (label, key, formula) in enumerate(calcs):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(calc_frame, text=label, font=('Arial', 10)).grid(
                row=row, column=col, sticky=tk.W, pady=5)
            
            value_label = ttk.Label(calc_frame, text="0", 
                                   font=('Arial', 12, 'bold'), foreground='blue')
            value_label.grid(row=row, column=col+1, pady=5, padx=10)
            
            ttk.Label(calc_frame, text=f"({formula})", foreground='gray',
                     font=('Arial', 8, 'italic')).grid(
                row=row, column=col+2, sticky=tk.W, padx=5)
            
            self.calc_labels[key] = value_label
    
    def create_mitre_tab(self):
        """MITRE ATT&CK sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3️⃣ MITRE ATT&CK")
        
        # Ana frame
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bilgi
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ MITRE ATT&CK Taktikleri", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = ttk.Label(info_frame, text="Her taktik için test edilen ve tetiklenen kural sayılarını girin. Başarı oranı otomatik hesaplanır.",
                              font=('Arial', 9))
        info_label.pack()
        
        # Hızlı ekleme
        add_frame = ttk.LabelFrame(main_frame, text="➕ Taktik Ekle", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Taktik listesi
        tactics = [
            'Initial Access', 'Execution', 'Persistence', 'Privilege Escalation',
            'Defense Evasion', 'Credential Access', 'Discovery', 'Lateral Movement',
            'Collection', 'Command and Control', 'Exfiltration', 'Impact'
        ]
        
        ttk.Label(add_frame, text="Taktik:").grid(row=0, column=0, padx=5)
        self.tactic_combo = ttk.Combobox(add_frame, values=tactics, width=20, font=('Arial', 10))
        self.tactic_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Test Edilen:").grid(row=0, column=2, padx=5)
        self.tactic_test = ttk.Entry(add_frame, width=10, font=('Arial', 10))
        self.tactic_test.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Tetiklenen:").grid(row=0, column=4, padx=5)
        self.tactic_triggered = ttk.Entry(add_frame, width=10, font=('Arial', 10))
        self.tactic_triggered.grid(row=0, column=5, padx=5)
        
        ttk.Button(add_frame, text="➕ Ekle", command=self.add_mitre_tactic,
                  width=10).grid(row=0, column=6, padx=10)
        
        # Taktik listesi
        list_frame = ttk.LabelFrame(main_frame, text="📊 Taktik Listesi", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('Taktik', 'Test', 'Tetiklenen', 'Başarı %', 'Durum')
        self.tactic_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Kolon başlıkları ve genişlikler
        widths = [200, 80, 80, 80, 100]
        for col, width in zip(columns, widths):
            self.tactic_tree.heading(col, text=col)
            self.tactic_tree.column(col, width=width, anchor='center')
        
        self.tactic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tactic_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tactic_tree.configure(yscrollcommand=scrollbar.set)
        
        # Sil butonu
        ttk.Button(list_frame, text="🗑️ Seçili Sil", 
                  command=self.delete_selected_tactic).pack(side=tk.BOTTOM, pady=5)
    
    def create_rules_tab(self):
        """Kurallar sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4️⃣ Kurallar")
        
        # Ana notebook
        rules_notebook = ttk.Notebook(tab)
        rules_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tetiklenen kurallar sekmesi
        triggered_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(triggered_tab, text="✅ Tetiklenen Kurallar")
        
        # Bilgi
        info1 = ttk.Label(triggered_tab, text="Başarıyla tetiklenen kuralların listesi (Table 3 için)",
                         font=('Arial', 9, 'italic'), foreground='blue')
        info1.pack(pady=5)
        
        # Ekleme alanı
        add_frame1 = ttk.Frame(triggered_tab)
        add_frame1.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(add_frame1, text="Kural Adı:").pack(side=tk.LEFT, padx=5)
        self.rule_name = ttk.Entry(add_frame1, width=30)
        self.rule_name.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame1, text="MITRE ID:").pack(side=tk.LEFT, padx=5)
        self.rule_mitre = ttk.Entry(add_frame1, width=15)
        self.rule_mitre.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame1, text="Taktik:").pack(side=tk.LEFT, padx=5)
        self.rule_tactic = ttk.Entry(add_frame1, width=20)
        self.rule_tactic.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame1, text="Güven %:").pack(side=tk.LEFT, padx=5)
        self.rule_confidence = ttk.Entry(add_frame1, width=10)
        self.rule_confidence.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame1, text="➕ Ekle", command=self.add_triggered_rule).pack(side=tk.LEFT, padx=10)
        
        # Liste
        self.triggered_text = scrolledtext.ScrolledText(triggered_tab, height=15, width=80)
        self.triggered_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Algılanamayan teknikler sekmesi
        undetected_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(undetected_tab, text="❌ Algılanamayan Teknikler")
        
        # Bilgi
        info2 = ttk.Label(undetected_tab, text="Tespit edilemeyen MITRE teknikleri (Table 4 için)",
                         font=('Arial', 9, 'italic'), foreground='red')
        info2.pack(pady=5)
        
        # Ekleme alanı
        add_frame2 = ttk.Frame(undetected_tab)
        add_frame2.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(add_frame2, text="MITRE ID:").pack(side=tk.LEFT, padx=5)
        self.undetected_id = ttk.Entry(add_frame2, width=15)
        self.undetected_id.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame2, text="Teknik Adı:").pack(side=tk.LEFT, padx=5)
        self.undetected_name = ttk.Entry(add_frame2, width=30)
        self.undetected_name.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame2, text="Taktik:").pack(side=tk.LEFT, padx=5)
        self.undetected_tactic = ttk.Entry(add_frame2, width=20)
        self.undetected_tactic.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_frame2, text="Kritiklik:").pack(side=tk.LEFT, padx=5)
        self.undetected_criticality = ttk.Combobox(add_frame2, 
                                                   values=['Kritik', 'Yüksek', 'Orta', 'Düşük'],
                                                   width=10)
        self.undetected_criticality.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_frame2, text="➕ Ekle", command=self.add_undetected_technique).pack(side=tk.LEFT, padx=10)
        
        # Liste
        self.undetected_text = scrolledtext.ScrolledText(undetected_tab, height=15, width=80)
        self.undetected_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def create_recommendations_tab(self):
        """Öneriler sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="5️⃣ Öneriler")
        
        # Bilgi
        info_frame = ttk.LabelFrame(tab, text="ℹ️ Öneri Listesi (Table 5 için)", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Tespit edilen eksiklikler için önerilerinizi ekleyin. Öncelik otomatik atanır.",
                 font=('Arial', 9)).pack()
        
        # Ekleme alanı
        add_frame = ttk.LabelFrame(tab, text="➕ Öneri Ekle", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(add_frame, text="Kategori:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.rec_category = ttk.Combobox(add_frame, values=[
            'Log Kaynakları', 'Kural Optimizasyonu', 'Yeni Kurallar',
            'UEBA/SIEM', 'Test Döngüsü', 'Eğitim', 'Otomasyon', 'Diğer'
        ], width=20)
        self.rec_category.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Öneri:").grid(row=1, column=0, padx=5, sticky=tk.W, pady=5)
        self.rec_text = ttk.Entry(add_frame, width=60)
        self.rec_text.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(add_frame, text="➕ Ekle", command=self.add_recommendation,
                  width=15).grid(row=1, column=2, padx=10)
        
        # Liste
        list_frame = ttk.LabelFrame(tab, text="📝 Öneri Listesi", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.recommendations_text = scrolledtext.ScrolledText(list_frame, height=15, width=80)
        self.recommendations_text.pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        """Ayarlar sekmesi"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Ayarlar")
        
        # Görsel ayarları
        visual_frame = ttk.LabelFrame(tab, text="📐 Görsel Ayarları", padding=15)
        visual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Boyut ayarları
        ttk.Label(visual_frame, text="Figure Genişlik (inch):").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.fig_width = ttk.Spinbox(visual_frame, from_=8, to=20, increment=1, width=10)
        self.fig_width.set(12)
        self.fig_width.grid(row=0, column=1, padx=5)
        
        ttk.Label(visual_frame, text="Figure Yükseklik (inch):").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.fig_height = ttk.Spinbox(visual_frame, from_=6, to=15, increment=1, width=10)
        self.fig_height.set(8)
        self.fig_height.grid(row=0, column=3, padx=5)
        
        ttk.Label(visual_frame, text="DPI (Çözünürlük):").grid(row=1, column=0, padx=5, sticky=tk.W, pady=5)
        self.fig_dpi = ttk.Spinbox(visual_frame, from_=100, to=600, increment=50, width=10)
        self.fig_dpi.set(300)
        self.fig_dpi.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(visual_frame, text="(Word için 300 DPI önerilir)", 
                 font=('Arial', 9, 'italic'), foreground='gray').grid(row=1, column=2, columnspan=2, sticky=tk.W)
        
        # Kayıt ayarları
        save_frame = ttk.LabelFrame(tab, text="💾 Kayıt Ayarları", padding=15)
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(save_frame, text="Kayıt Klasörü:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.save_path = tk.StringVar(value=os.path.join(os.getcwd(), "IDCA_Output"))
        ttk.Entry(save_frame, textvariable=self.save_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(save_frame, text="📁 Seç", command=self.select_save_path).grid(row=0, column=2, padx=5)
        
        # Tema ayarları
        theme_frame = ttk.LabelFrame(tab, text="🎨 Hazır Temalar", padding=15)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        themes = ['Varsayılan (Koyu)', 'Profesyonel', 'Modern', 'Klasik', 'Minimalist']
        for i, theme in enumerate(themes):
            ttk.Button(theme_frame, text=theme, 
                      command=lambda t=theme: self.apply_theme(t),
                      width=15).grid(row=0, column=i, padx=5)
    
    def create_preview_panel(self, parent):
        """Sağ panel - Önizleme"""
        # Başlık
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(title_frame, text="👁️ Önizleme", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Görsel seçimi
        ttk.Label(title_frame, text="Görsel:").pack(side=tk.LEFT, padx=(20, 5))
        self.preview_combo = ttk.Combobox(title_frame, values=[
            'Figure 1 - Test Uygunluk',
            'Figure 2 - Test Durumu',
            'Table 1 - Sonuç Değerlendirme',
            'Table 2 - MITRE Kapsama',
            'Table 3 - Tetiklenen Kurallar',
            'Table 4 - Algılanamayan Teknikler',
            'Table 5 - Öneriler'
        ], width=25)
        self.preview_combo.pack(side=tk.LEFT)
        self.preview_combo.current(0)
        self.preview_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        ttk.Button(title_frame, text="🔄", command=self.update_preview, width=3).pack(side=tk.LEFT, padx=5)
        
        # Önizleme alanı
        self.preview_frame = ttk.LabelFrame(parent, text="Görsel Önizleme", padding=5)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # İlk önizleme
        self.update_preview()
    
    def create_status_bar(self, parent):
        """Durum çubuğu"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="✅ Hazır", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Veri durumu
        self.data_status = ttk.Label(status_frame, text="", font=('Arial', 9), foreground='blue')
        self.data_status.pack(side=tk.RIGHT, padx=10)
        
        self.update_data_status()
    
    def show_guide(self):
        """Kılavuz penceresi"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 Kullanım Kılavuzu")
        guide_window.geometry("800x600")
        
        # Scrolled text
        text_widget = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guide_text = """
IDCA RAPOR GÖRSELLEŞTİRİCİ - KULLANIM KILAVUZU
================================================

🎯 AMAÇ:
Bu araç, IDCA (Intrusion Detection Capability Analysis) test sonuçlarınızı profesyonel 
Word raporları için görselleştirmenizi sağlar.

📊 ÜRETİLEN GÖRSELLER:
• Figure 1: Test Uygunluk Grafiği (Donut Chart)
• Figure 2: Test Durumu Grafikleri (Bar Charts) 
• Table 1: Sonuç Değerlendirme Tablosu
• Table 2: MITRE ATT&CK Kapsama Analizi
• Table 3: Tetiklenen Korelasyon Kuralları
• Table 4: Algılanamayan MITRE Teknikleri
• Table 5: Öneri Listesi

📝 VERİ GİRİŞ ADIMLARI:

1️⃣ GENEL BİLGİLER:
   • Kurum adı, tarih, hazırlayan gibi temel bilgileri girin
   • Bu bilgiler tüm görsellerde alt bilgi olarak görünür
   
2️⃣ TEST SONUÇLARI:
   • Toplam kural sayısı: Sistemdeki tüm kurallar (örn: 291)
   • Test edilen: Test sürecine dahil edilenler (örn: 114)
   • Tetiklenen: Başarıyla alarm üretenler (örn: 65)
   • Diğer değerler otomatik hesaplanır
   
3️⃣ MITRE ATT&CK:
   • Her taktik için test edilen ve tetiklenen sayıları girin
   • Örnek: Initial Access - Test: 8, Tetiklenen: 3
   • Başarı oranı ve durum otomatik hesaplanır
   
4️⃣ KURALLAR:
   • Tetiklenen Kurallar: Başarılı kuralların detayları
   • Algılanamayan Teknikler: Tespit edilemeyen MITRE teknikleri
   • Her satır için ayrı ayrı bilgi girin
   
5️⃣ ÖNERİLER:
   • Tespit edilen eksiklikler için öneriler
   • Kategori seçin ve öneri metnini yazın
   • Öncelik numaraları otomatik atanır

💡 İPUÇLARI:

• TOPLU VERİ GİRİŞİ:
  - "Toplu Giriş" butonu ile tüm verileri tek seferde girebilirsiniz
  - Excel'den kopyala-yapıştır yapabilirsiniz
  
• VERİ KAYDETME:
  - Çalışmanızı JSON formatında kaydedin
  - Daha sonra "Veri Yükle" ile devam edebilirsiniz
  
• ÖNİZLEME:
  - Sağ panelde anlık önizleme görebilirsiniz
  - Görsel seçimi yaparak farklı çıktıları kontrol edin
  
• GÖRSEL OLUŞTURMA:
  - Tüm verileri girdikten sonra "TÜM GÖRSELLERİ OLUŞTUR" butonuna tıklayın
  - Görseller belirlediğiniz klasöre ayrı ayrı kaydedilir
  
• WORD'E EKLEME:
  - PNG dosyalarını Word'e "Ekle > Resim" ile ekleyin
  - "Metinle Satır İçi" seçeneğini kullanın
  - Sıkıştırmayı kapatın (300 DPI kalite korunur)

⚠️ ÖNEMLİ NOTLAR:

• Sayısal alanlara sadece rakam girin
• Test edilen ≤ Toplam kural olmalı
• Tetiklenen ≤ Test edilen olmalı
• Güven skorları 0-100 arasında olmalı
• Tüm zorunlu alanları (*) doldurun

📧 DESTEK:
Sorunlarınız için SOC ekibiyle iletişime geçin.

İyi çalışmalar! 🚀
"""
        
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
        
        # Kapat butonu
        ttk.Button(guide_window, text="Kapat", command=guide_window.destroy,
                  width=20).pack(pady=10)
    
    def calculate_test_stats(self, event=None):
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
            
            # Renk kodlama
            if success_rate >= 70:
                self.calc_labels['success_rate'].config(foreground='green')
            elif success_rate >= 50:
                self.calc_labels['success_rate'].config(foreground='orange')
            else:
                self.calc_labels['success_rate'].config(foreground='red')
            
            self.status_label.config(text="✅ Hesaplamalar güncellendi", foreground='green')
            self.update_data_status()
            
        except ValueError:
            pass
    
    def add_mitre_tactic(self):
        """MITRE taktik ekle"""
        tactic = self.tactic_combo.get()
        if not tactic:
            messagebox.showwarning("Uyarı", "Lütfen bir taktik seçin!")
            return
        
        try:
            test = int(self.tactic_test.get() or 0)
            triggered = int(self.tactic_triggered.get() or 0)
            
            if triggered > test:
                messagebox.showwarning("Hata", "Tetiklenen sayısı test edilenden fazla olamaz!")
                return
            
            success_rate = (triggered / test * 100) if test > 0 else 0
            
            # Durum belirleme
            if success_rate >= 70:
                status = "✅ Çok İyi"
                tag = 'success'
            elif success_rate >= 60:
                status = "✓ İyi"
                tag = 'good'
            elif success_rate >= 40:
                status = "⚠️ Orta"
                tag = 'warning'
            else:
                status = "❌ Kritik"
                tag = 'danger'
            
            # Ağaca ekle
            item = self.tactic_tree.insert('', 'end', values=(
                tactic, test, triggered, f"%{success_rate:.1f}", status
            ), tags=(tag,))
            
            # Renklendirme
            self.tactic_tree.tag_configure('success', foreground='green')
            self.tactic_tree.tag_configure('good', foreground='blue')
            self.tactic_tree.tag_configure('warning', foreground='orange')
            self.tactic_tree.tag_configure('danger', foreground='red')
            
            # Temizle
            self.tactic_combo.set('')
            self.tactic_test.delete(0, tk.END)
            self.tactic_triggered.delete(0, tk.END)
            
            self.status_label.config(text=f"✅ {tactic} eklendi", foreground='green')
            self.update_data_status()
            
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
    
    def delete_selected_tactic(self):
        """Seçili taktiği sil"""
        selected = self.tactic_tree.selection()
        if selected:
            self.tactic_tree.delete(selected)
            self.status_label.config(text="✅ Taktik silindi", foreground='green')
    
    def add_triggered_rule(self):
        """Tetiklenen kural ekle"""
        name = self.rule_name.get().strip()
        mitre = self.rule_mitre.get().strip()
        tactic = self.rule_tactic.get().strip()
        confidence = self.rule_confidence.get().strip()
        
        if not all([name, mitre, tactic, confidence]):
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun!")
            return
        
        try:
            conf_val = int(confidence)
            if conf_val < 0 or conf_val > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Güven skoru 0-100 arasında olmalı!")
            return
        
        # Listeye ekle
        rule_text = f"{name} | {mitre} | {tactic} | %{confidence}\n"
        self.triggered_text.insert(tk.END, rule_text)
        
        # Temizle
        self.rule_name.delete(0, tk.END)
        self.rule_mitre.delete(0, tk.END)
        self.rule_tactic.delete(0, tk.END)
        self.rule_confidence.delete(0, tk.END)
        
        self.status_label.config(text="✅ Kural eklendi", foreground='green')
    
    def add_undetected_technique(self):
        """Algılanamayan teknik ekle"""
        tech_id = self.undetected_id.get().strip()
        name = self.undetected_name.get().strip()
        tactic = self.undetected_tactic.get().strip()
        criticality = self.undetected_criticality.get()
        
        if not all([tech_id, name, tactic, criticality]):
            messagebox.showwarning("Uyarı", "Tüm alanları doldurun!")
            return
        
        # Listeye ekle
        tech_text = f"{tech_id} | {name} | {tactic} | {criticality}\n"
        self.undetected_text.insert(tk.END, tech_text)
        
        # Temizle
        self.undetected_id.delete(0, tk.END)
        self.undetected_name.delete(0, tk.END)
        self.undetected_tactic.delete(0, tk.END)
        self.undetected_criticality.set('')
        
        self.status_label.config(text="✅ Teknik eklendi", foreground='green')
    
    def add_recommendation(self):
        """Öneri ekle"""
        category = self.rec_category.get()
        text = self.rec_text.get().strip()
        
        if not category or not text:
            messagebox.showwarning("Uyarı", "Kategori ve öneri metni gerekli!")
            return
        
        # Öncelik numarası
        current_count = len(self.recommendations_text.get("1.0", tk.END).strip().split('\n'))
        if self.recommendations_text.get("1.0", tk.END).strip():
            priority = current_count
        else:
            priority = 1
        
        # Listeye ekle
        rec_text = f"P{priority} | {category} | {text}\n"
        self.recommendations_text.insert(tk.END, rec_text)
        
        # Temizle
        self.rec_category.set('')
        self.rec_text.delete(0, tk.END)
        
        self.status_label.config(text="✅ Öneri eklendi", foreground='green')
    
    def bulk_data_entry(self):
        """Toplu veri girişi penceresi"""
        bulk_window = tk.Toplevel(self.root)
        bulk_window.title("📋 Toplu Veri Girişi")
        bulk_window.geometry("900x700")
        
        # Bilgi
        info_label = ttk.Label(bulk_window, 
                              text="Excel'den kopyalayıp yapıştırabilir veya manuel olarak girebilirsiniz. TAB ile alanlar arası geçiş yapın.",
                              font=('Arial', 10), foreground='blue')
        info_label.pack(pady=10)
        
        # Notebook
        bulk_notebook = ttk.Notebook(bulk_window)
        bulk_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # MITRE Taktikleri sekmesi
        mitre_tab = ttk.Frame(bulk_notebook)
        bulk_notebook.add(mitre_tab, text="MITRE Taktikleri")
        
        ttk.Label(mitre_tab, text="Format: Taktik_Adı[TAB]Test_Sayısı[TAB]Tetiklenen_Sayısı",
                 font=('Arial', 9, 'italic')).pack(pady=5)
        
        mitre_text = scrolledtext.ScrolledText(mitre_tab, height=15, width=80)
        mitre_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Örnek veri
        mitre_example = """Initial Access	8	3
Execution	12	5
Persistence	16	8
Privilege Escalation	10	3
Defense Evasion	28	14
Credential Access	20	11
Discovery	15	8
Lateral Movement	6	4
Collection	4	2
Command and Control	8	5
Exfiltration	2	1
Impact	10	6"""
        
        ttk.Button(mitre_tab, text="Örnek Veri Yükle", 
                  command=lambda: mitre_text.insert(tk.END, mitre_example)).pack(pady=5)
        
        # İşle butonu
        def process_mitre():
            lines = mitre_text.get("1.0", tk.END).strip().split('\n')
            success_count = 0
            
            for line in lines:
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        try:
                            tactic = parts[0].strip()
                            test = int(parts[1].strip())
                            triggered = int(parts[2].strip())
                            
                            if triggered <= test:
                                success_rate = (triggered / test * 100) if test > 0 else 0
                                status = "✅ Çok İyi" if success_rate >= 70 else "✓ İyi" if success_rate >= 60 else "⚠️ Orta" if success_rate >= 40 else "❌ Kritik"
                                
                                self.tactic_tree.insert('', 'end', values=(
                                    tactic, test, triggered, f"%{success_rate:.1f}", status
                                ))
                                success_count += 1
                        except ValueError:
                            continue
            
            messagebox.showinfo("Başarılı", f"{success_count} taktik eklendi!")
            bulk_window.destroy()
        
        ttk.Button(mitre_tab, text="✅ Verileri İşle ve Ekle", 
                  command=process_mitre, width=30).pack(pady=10)
        
        # Butonlar
        button_frame = ttk.Frame(bulk_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="İptal", command=bulk_window.destroy,
                  width=15).pack(side=tk.LEFT, padx=5)
    
    def collect_all_data(self):
        """Tüm verileri topla"""
        # Genel bilgiler
        for key, entry in self.general_entries.items():
            self.data['general'][key] = entry.get().strip()
        
        # Test sonuçları
        for key, entry in self.test_entries.items():
            try:
                self.data['test_results'][key] = int(entry.get() or 0)
            except ValueError:
                self.data['test_results'][key] = 0
        
        # Hesaplanmış değerler
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        triggered = self.data['test_results']['triggered_rules']
        
        self.data['test_results']['failed_rules'] = tested - triggered
        self.data['test_results']['not_tested'] = total - tested
        self.data['test_results']['success_rate'] = (triggered / tested * 100) if tested > 0 else 0
        
        # MITRE taktikleri
        self.data['mitre_tactics'] = {}
        for item in self.tactic_tree.get_children():
            values = self.tactic_tree.item(item)['values']
            self.data['mitre_tactics'][values[0]] = {
                'test': int(values[1]),
                'triggered': int(values[2]),
                'rate': float(values[3].strip('%'))
            }
        
        # Tetiklenen kurallar
        self.data['triggered_rules'] = []
        rules_text = self.triggered_text.get("1.0", tk.END).strip()
        if rules_text:
            for line in rules_text.split('\n'):
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        self.data['triggered_rules'].append({
                            'name': parts[0],
                            'mitre': parts[1],
                            'tactic': parts[2],
                            'confidence': parts[3].strip('%')
                        })
        
        # Algılanamayan teknikler
        self.data['undetected_techniques'] = []
        undetected_text = self.undetected_text.get("1.0", tk.END).strip()
        if undetected_text:
            for line in undetected_text.split('\n'):
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 4:
                        self.data['undetected_techniques'].append({
                            'id': parts[0],
                            'name': parts[1],
                            'tactic': parts[2],
                            'criticality': parts[3]
                        })
        
        # Öneriler
        self.data['recommendations'] = []
        rec_text = self.recommendations_text.get("1.0", tk.END).strip()
        if rec_text:
            for line in rec_text.split('\n'):
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        self.data['recommendations'].append({
                            'priority': parts[0],
                            'category': parts[1],
                            'text': parts[2]
                        })
    
    def save_data(self):
        """Verileri JSON olarak kaydet"""
        self.collect_all_data()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")],
            initialfile=f"IDCA_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Başarılı", f"Veriler kaydedildi:\n{filename}")
                self.status_label.config(text="✅ Veriler kaydedildi", foreground='green')
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt hatası:\n{str(e)}")
    
    def load_data(self):
        """JSON'dan veri yükle"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON dosyaları", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                self.populate_from_data()
                messagebox.showinfo("Başarılı", "Veriler yüklendi!")
                self.status_label.config(text="✅ Veriler yüklendi", foreground='green')
                
            except Exception as e:
                messagebox.showerror("Hata", f"Yükleme hatası:\n{str(e)}")
    
    def populate_from_data(self):
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
        
        self.calculate_test_stats()
        
        # MITRE taktikleri
        self.tactic_tree.delete(*self.tactic_tree.get_children())
        for tactic, values in self.data.get('mitre_tactics', {}).items():
            rate = values.get('rate', 0)
            status = "✅ Çok İyi" if rate >= 70 else "✓ İyi" if rate >= 60 else "⚠️ Orta" if rate >= 40 else "❌ Kritik"
            
            self.tactic_tree.insert('', 'end', values=(
                tactic, values['test'], values['triggered'], f"%{rate}", status
            ))
        
        # Diğer alanları temizle ve doldur
        self.triggered_text.delete("1.0", tk.END)
        for rule in self.data.get('triggered_rules', []):
            text = f"{rule['name']} | {rule['mitre']} | {rule['tactic']} | %{rule['confidence']}\n"
            self.triggered_text.insert(tk.END, text)
        
        self.undetected_text.delete("1.0", tk.END)
        for tech in self.data.get('undetected_techniques', []):
            text = f"{tech['id']} | {tech['name']} | {tech['tactic']} | {tech['criticality']}\n"
            self.undetected_text.insert(tk.END, text)
        
        self.recommendations_text.delete("1.0", tk.END)
        for rec in self.data.get('recommendations', []):
            text = f"{rec['priority']} | {rec['category']} | {rec['text']}\n"
            self.recommendations_text.insert(tk.END, text)
    
    def reset_data(self):
        """Tüm verileri sıfırla"""
        if messagebox.askyesno("Onay", "Tüm veriler silinecek. Emin misiniz?"):
            # Formu temizle
            for entry in self.general_entries.values():
                entry.delete(0, tk.END)
            
            for entry in self.test_entries.values():
                entry.delete(0, tk.END)
            
            for label in self.calc_labels.values():
                label.config(text="0")
            
            self.tactic_tree.delete(*self.tactic_tree.get_children())
            self.triggered_text.delete("1.0", tk.END)
            self.undetected_text.delete("1.0", tk.END)
            self.recommendations_text.delete("1.0", tk.END)
            
            self.reset_all_data()
            
            # Varsayılan değerleri geri yükle
            self.general_entries['report_title'].insert(0, 'IDCA Security Assessment')
            self.general_entries['classification'].insert(0, 'Kurumsal - Gizli')
            
            self.status_label.config(text="✅ Veriler sıfırlandı", foreground='orange')
            self.update_data_status()
    
    def update_data_status(self):
        """Veri durumunu güncelle"""
        self.collect_all_data()
        
        filled_sections = []
        if self.data['general'].get('company_name'):
            filled_sections.append("Genel")
        if self.data['test_results'].get('total_rules'):
            filled_sections.append("Test")
        if self.data['mitre_tactics']:
            filled_sections.append("MITRE")
        if self.data['triggered_rules']:
            filled_sections.append("Kurallar")
        if self.data['recommendations']:
            filled_sections.append("Öneriler")
        
        if filled_sections:
            self.data_status.config(
                text=f"Dolu: {', '.join(filled_sections)} ({len(filled_sections)}/5)",
                foreground='green' if len(filled_sections) == 5 else 'blue'
            )
        else:
            self.data_status.config(text="Veri girilmemiş", foreground='gray')
    
    def select_save_path(self):
        """Kayıt klasörü seç"""
        path = filedialog.askdirectory()
        if path:
            self.save_path.set(path)
    
    def apply_theme(self, theme_name):
        """Tema uygula"""
        themes = {
            'Varsayılan (Koyu)': {
                'primary': '#0F172A', 'secondary': '#1E293B', 'accent': '#00D9FF',
                'success': '#10B981', 'warning': '#F59E0B', 'danger': '#EF4444'
            },
            'Profesyonel': {
                'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#0f3460',
                'success': '#53c653', 'warning': '#e94560', 'danger': '#ff1744'
            },
            'Modern': {
                'primary': '#2d3436', 'secondary': '#636e72', 'accent': '#00b894',
                'success': '#55efc4', 'warning': '#fdcb6e', 'danger': '#ff7675'
            },
            'Klasik': {
                'primary': '#2c3e50', 'secondary': '#34495e', 'accent': '#3498db',
                'success': '#2ecc71', 'warning': '#f39c12', 'danger': '#e74c3c'
            },
            'Minimalist': {
                'primary': '#ffffff', 'secondary': '#f5f5f5', 'accent': '#333333',
                'success': '#4caf50', 'warning': '#ff9800', 'danger': '#f44336'
            }
        }
        
        if theme_name in themes:
            self.colors.update(themes[theme_name])
            self.status_label.config(text=f"✅ {theme_name} teması uygulandı", foreground='green')
            self.update_preview()
    
    def update_preview(self):
        """Önizlemeyi güncelle"""
        # Önizleme alanını temizle
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        selected = self.preview_combo.get()
        
        try:
            # Mini figure oluştur
            fig = plt.figure(figsize=(6, 4), dpi=80)
            fig.patch.set_facecolor(self.colors['dark'])
            
            if 'Figure 1' in selected:
                self.create_preview_figure1(fig)
            elif 'Figure 2' in selected:
                self.create_preview_figure2(fig)
            elif 'Table 1' in selected:
                self.create_preview_table1(fig)
            elif 'Table 2' in selected:
                self.create_preview_table2(fig)
            elif 'Table 3' in selected:
                self.create_preview_table3(fig)
            elif 'Table 4' in selected:
                self.create_preview_table4(fig)
            elif 'Table 5' in selected:
                self.create_preview_table5(fig)
            
            # Canvas'a ekle
            canvas = FigureCanvasTkAgg(fig, master=self.preview_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            # Hata durumunda bilgi göster
            error_label = ttk.Label(self.preview_frame, 
                                   text=f"Önizleme için veri yetersiz\n\n{str(e)}", 
                                   font=('Arial', 10), foreground='gray')
            error_label.pack(expand=True)
    
    def refresh_preview(self):
        """Önizlemeyi yenile"""
        self.collect_all_data()
        self.update_preview()
        self.status_label.config(text="✅ Önizleme güncellendi", foreground='green')
    
    def create_preview_figure1(self, fig):
        """Figure 1 önizleme"""
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['primary'])
        
        total = self.data['test_results'].get('total_rules', 0) or 100
        tested = self.data['test_results'].get('tested_rules', 0) or 40
        not_tested = total - tested
        
        # Pasta grafik
        sizes = [tested, not_tested]
        labels = [f'Test Edilmiş\n{tested}', f'Test Edilmemiş\n{not_tested}']
        colors = [self.colors['accent_secondary'], self.colors['gray']]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Figure 1: Test Uygunluk Grafiği', fontsize=12, 
                    color=self.colors['light'], pad=15)
    
    def create_preview_figure2(self, fig):
        """Figure 2 önizleme"""
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        
        for ax in [ax1, ax2]:
            ax.set_facecolor(self.colors['primary'])
        
        # Sol grafik
        triggered = self.data['test_results'].get('triggered_rules', 0) or 30
        failed = self.data['test_results'].get('failed_rules', 0) or 10
        
        ax1.bar(['Tetiklenen', 'Başarısız'], [triggered, failed],
               color=[self.colors['success'], self.colors['danger']])
        ax1.set_title('Test Sonuçları', fontsize=10, color=self.colors['light'])
        ax1.tick_params(colors=self.colors['gray'])
        
        # Sağ grafik - MITRE
        if self.data['mitre_tactics']:
            tactics = list(self.data['mitre_tactics'].keys())[:4]
            rates = [self.data['mitre_tactics'][t]['rate'] for t in tactics]
        else:
            tactics = ['Taktik 1', 'Taktik 2', 'Taktik 3']
            rates = [45, 60, 35]
        
        colors_bar = [self.colors['danger'] if r < 40 else self.colors['warning'] if r < 60 else self.colors['success'] for r in rates]
        ax2.barh(range(len(tactics)), rates, color=colors_bar)
        ax2.set_yticks(range(len(tactics)))
        ax2.set_yticklabels(tactics, fontsize=8)
        ax2.set_xlim(0, 100)
        ax2.set_title('Taktik Performans', fontsize=10, color=self.colors['light'])
        ax2.tick_params(colors=self.colors['gray'])
        
        fig.suptitle('Figure 2: Test Durumu', fontsize=12, color=self.colors['light'])
    
    def create_preview_table1(self, fig):
        """Table 1 önizleme"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        total = self.data['test_results'].get('total_rules', 0)
        tested = self.data['test_results'].get('tested_rules', 0)
        success_rate = self.data['test_results'].get('success_rate', 0)
        
        table_data = [
            ['Metrik', 'Değer', 'Hedef', 'Durum'],
            ['Toplam Kural', str(total), '300+', '✓' if total >= 300 else '✗'],
            ['Test Edilen', str(tested), '200+', '✓' if tested >= 200 else '✗'],
            ['Başarı Oranı', f'%{success_rate:.1f}', '%70+', '✓' if success_rate >= 70 else '✗']
        ]
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # Başlık satırı rengi
        for i in range(4):
            table[(0, i)].set_facecolor(self.colors['accent_secondary'])
            
        ax.set_title('Table 1: Sonuç Değerlendirme', fontsize=12, pad=10)
    
    def create_preview_table2(self, fig):
        """Table 2 önizleme"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        # MITRE verileri
        table_data = [['Taktik', 'Test', 'Tetik', 'Başarı %']]
        
        if self.data['mitre_tactics']:
            for tactic, values in list(self.data['mitre_tactics'].items())[:5]:
                table_data.append([
                    tactic[:15], 
                    str(values['test']), 
                    str(values['triggered']),
                    f"%{values['rate']:.1f}"
                ])
        else:
            table_data.append(['Örnek Taktik', '10', '5', '%50.0'])
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        for i in range(4):
            table[(0, i)].set_facecolor(self.colors['accent_secondary'])
        
        ax.set_title('Table 2: MITRE ATT&CK Kapsama', fontsize=12, pad=10)
    
    def create_preview_table3(self, fig):
        """Table 3 önizleme"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [['ID', 'Kural Adı', 'MITRE', 'Güven']]
        
        if self.data['triggered_rules']:
            for i, rule in enumerate(self.data['triggered_rules'][:3], 1):
                table_data.append([
                    str(i),
                    rule['name'][:20] + '...' if len(rule['name']) > 20 else rule['name'],
                    rule['mitre'],
                    f"%{rule['confidence']}"
                ])
        else:
            table_data.append(['1', 'Örnek Kural', 'T1055', '%85'])
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        for i in range(4):
            table[(0, i)].set_facecolor(self.colors['success'])
        
        ax.set_title('Table 3: Tetiklenen Kurallar', fontsize=12, pad=10)
    
    def create_preview_table4(self, fig):
        """Table 4 önizleme"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [['MITRE ID', 'Teknik', 'Kritiklik']]
        
        if self.data['undetected_techniques']:
            for tech in self.data['undetected_techniques'][:3]:
                table_data.append([
                    tech['id'],
                    tech['name'][:20] + '...' if len(tech['name']) > 20 else tech['name'],
                    tech['criticality']
                ])
        else:
            table_data.append(['T1566', 'Örnek Teknik', 'Kritik'])
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        for i in range(3):
            table[(0, i)].set_facecolor(self.colors['danger'])
        
        ax.set_title('Table 4: Algılanamayan Teknikler', fontsize=12, pad=10)
    
    def create_preview_table5(self, fig):
        """Table 5 önizleme"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        table_data = [['Öncelik', 'Kategori', 'Öneri']]
        
        if self.data['recommendations']:
            for rec in self.data['recommendations'][:3]:
                table_data.append([
                    rec['priority'],
                    rec['category'],
                    rec['text'][:30] + '...' if len(rec['text']) > 30 else rec['text']
                ])
        else:
            table_data.append(['P1', 'Log Kaynakları', 'Örnek öneri metni'])
        
        table = ax.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        for i in range(3):
            table[(0, i)].set_facecolor(self.colors['warning'])
        
        ax.set_title('Table 5: Öneriler', fontsize=12, pad=10)
    
    def generate_all_visuals(self):
        """Tüm görselleri oluştur ve kaydet"""
        # Veri topla
        self.collect_all_data()
        
        # Validasyon
        if not self.data['general'].get('company_name'):
            messagebox.showwarning("Uyarı", "Lütfen en azından kurum adını girin!")
            return
        
        if not self.data['test_results'].get('total_rules'):
            messagebox.showwarning("Uyarı", "Lütfen test sonuçlarını girin!")
            return
        
        # Kayıt klasörünü oluştur
        save_dir = self.save_path.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Progress penceresi
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Görseller Oluşturuluyor")
        progress_window.geometry("500x250")
        progress_window.transient(self.root)
        
        progress_label = ttk.Label(progress_window, text="Başlıyor...", font=('Arial', 12))
        progress_label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, length=400, mode='determinate')
        progress_bar.pack(pady=20)
        
        details_label = ttk.Label(progress_window, text="", font=('Arial', 9), foreground='gray')
        details_label.pack(pady=10)
        
        # Görseller listesi
        visuals = [
            ('Figure_1_Test_Uygunluk', self.generate_figure1),
            ('Figure_2_Test_Durumu', self.generate_figure2),
            ('Table_1_Sonuc_Degerlendirme', self.generate_table1),
            ('Table_2_MITRE_Kapsama', self.generate_table2),
            ('Table_3_Tetiklenen_Kurallar', self.generate_table3),
            ('Table_4_Algilanamayan_Teknikler', self.generate_table4),
            ('Table_5_Oneriler', self.generate_table5)
        ]
        
        progress_bar['maximum'] = len(visuals)
        success_count = 0
        
        for i, (filename, func) in enumerate(visuals):
            progress_label.config(text=f"Oluşturuluyor: {filename}")
            details_label.config(text=f"({i+1}/{len(visuals)}) {filename}.png")
            progress_bar['value'] = i
            progress_window.update()
            
            try:
                full_path = os.path.join(save_dir, f"{filename}.png")
                func(full_path)
                success_count += 1
            except Exception as e:
                print(f"Hata {filename}: {str(e)}")
        
        progress_bar['value'] = len(visuals)
        progress_label.config(text=f"✅ Tamamlandı! {success_count}/{len(visuals)} görsel oluşturuldu")
        details_label.config(text=f"Kayıt yeri: {save_dir}")
        
        # Kapat butonu
        ttk.Button(progress_window, text="Kapat", 
                  command=progress_window.destroy).pack(pady=20)
        
        # Klasörü aç
        if messagebox.askyesno("Başarılı", f"{success_count} görsel oluşturuldu.\n\nKlasörü açmak ister misiniz?"):
            os.startfile(save_dir) if os.name == 'nt' else os.system(f'open "{save_dir}"')
    
    def generate_figure1(self, filepath):
        """Figure 1 - Test Uygunluk Grafiği"""
        width = float(self.fig_width.get())
        height = float(self.fig_height.get())
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.set_facecolor(self.colors['primary'])
        
        # Veriler
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        triggered = self.data['test_results']['triggered_rules']
        not_tested = self.data['test_results']['not_tested']
        failed = tested - triggered
        
        # Ana pasta grafik
        sizes = [tested, not_tested]
        labels = [f'Test Edilmiş\n{tested} kural\n(%{tested/total*100:.1f})', 
                 f'Test Edilmemiş\n{not_tested} kural\n(%{not_tested/total*100:.1f})']
        colors = [self.colors['accent_secondary'], self.colors['gray']]
        explode = (0.05, 0)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          explode=explode, autopct='',
                                          startangle=90, shadow=True,
                                          textprops={'fontsize': 11, 'color': self.colors['light']})
        
        # İç detay çemberi
        centre_circle = plt.Circle((0, 0), 0.70, fc=self.colors['primary'], 
                                  linewidth=2, edgecolor=self.colors['accent'])
        ax.add_artist(centre_circle)
        
        # Merkez metin
        ax.text(0, 0.15, str(total), ha='center', va='center', 
               fontsize=42, fontweight='bold', color=self.colors['accent'])
        ax.text(0, -0.1, 'Toplam Kural', ha='center', va='center', 
               fontsize=14, color=self.colors['gray'])
        ax.text(0, -0.25, f'Başarı: %{self.data["test_results"]["success_rate"]:.1f}', 
               ha='center', va='center', fontsize=12, fontweight='bold',
               color=self.colors['success'] if self.data["test_results"]["success_rate"] >= 70 else self.colors['warning'])
        
        # Mini istatistikler
        stats_text = f"""
Test Edilen: {tested}
Tetiklenen: {triggered}
Başarısız: {failed}
Test Edilmeyen: {not_tested}
        """
        ax.text(1.2, 0.5, stats_text.strip(), transform=ax.transAxes,
               fontsize=10, color=self.colors['light'],
               bbox=dict(boxstyle='round', facecolor=self.colors['secondary'], alpha=0.8))
        
        # Başlık
        ax.set_title('Figure 1: Analiz Edilen Korelasyonların Test Uygunluk Grafiği',
                    fontsize=16, fontweight='bold', color=self.colors['light'], pad=20)
        
        # Alt bilgi
        fig.text(0.5, 0.02, f'{self.data["general"]["company_name"]} - {self.data["general"]["report_date"]} - {self.data["general"]["report_id"]}',
                ha='center', fontsize=9, color=self.colors['gray'], style='italic')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_figure2(self, filepath):
        """Figure 2 - Test Durumu"""
        width = float(self.fig_width.get())
        height = float(self.fig_height.get())
        dpi = int(self.fig_dpi.get())
        
        fig = plt.figure(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        
        # Sol grafik - Test sonuçları
        ax1 = plt.subplot(1, 2, 1)
        ax1.set_facecolor(self.colors['primary'])
        
        triggered = self.data['test_results']['triggered_rules']
        failed = self.data['test_results']['failed_rules']
        
        categories = ['Tetiklenen\nKurallar', 'Başarısız\nKurallar']
        values = [triggered, failed]
        colors_bar = [self.colors['success'], self.colors['danger']]
        
        bars = ax1.bar(categories, values, color=colors_bar, width=0.6,
                      edgecolor=self.colors['accent'], linewidth=2)
        
        # Değer etiketleri
        for bar, val in zip(bars, values):
            height = bar.get_height()
            percentage = (val/self.data['test_results']['tested_rules']*100) if self.data['test_results']['tested_rules'] > 0 else 0
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.02,
                    f'{val}\n(%{percentage:.1f})',
                    ha='center', va='bottom', fontweight='bold', fontsize=11,
                    color=self.colors['light'])
        
        ax1.set_ylim(0, max(values) * 1.2 if values else 1)
        ax1.set_ylabel('Kural Sayısı', fontsize=12, color=self.colors['light'])
        ax1.set_title('Test Sonuç Dağılımı', fontsize=14, fontweight='bold', color=self.colors['light'])
        ax1.grid(axis='y', alpha=0.3, linestyle='--', color=self.colors['gray'])
        ax1.tick_params(colors=self.colors['gray'])
        
        # Sağ grafik - En düşük performanslı taktikler
        ax2 = plt.subplot(1, 2, 2)
        ax2.set_facecolor(self.colors['primary'])
        
        if self.data['mitre_tactics']:
            # En düşük 6 taktiği bul
            tactics_sorted = sorted(self.data['mitre_tactics'].items(), 
                                  key=lambda x: x[1]['rate'])[:6]
            
            tactics = [t[0] for t in tactics_sorted]
            rates = [t[1]['rate'] for t in tactics_sorted]
            
            # Renk skalası
            colors_gradient = []
            for rate in rates:
                if rate < 40:
                    colors_gradient.append(self.colors['danger'])
                elif rate < 60:
                    colors_gradient.append(self.colors['warning'])
                else:
                    colors_gradient.append(self.colors['success'])
            
            y_pos = np.arange(len(tactics))
            bars2 = ax2.barh(y_pos, rates, color=colors_gradient,
                           edgecolor=self.colors['accent'], linewidth=1)
            
            # Değer etiketleri
            for bar, val in zip(bars2, rates):
                ax2.text(val + 1, bar.get_y() + bar.get_height()/2.,
                        f'%{val:.1f}', va='center', fontweight='bold', 
                        fontsize=10, color=self.colors['light'])
            
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(tactics, fontsize=10, color=self.colors['light'])
            ax2.set_xlabel('Başarı Oranı (%)', fontsize=12, color=self.colors['light'])
            ax2.set_xlim(0, 100)
            ax2.set_title('En Düşük Performanslı Taktikler', fontsize=14, fontweight='bold', color=self.colors['light'])
            ax2.grid(axis='x', alpha=0.3, linestyle='--', color=self.colors['gray'])
            
            # Hedef çizgileri
            ax2.axvline(x=50, color=self.colors['warning'], linestyle='--', linewidth=2,
                       alpha=0.5, label='Minimum Hedef %50')
            ax2.axvline(x=70, color=self.colors['success'], linestyle='--', linewidth=2,
                       alpha=0.5, label='İdeal Hedef %70')
            ax2.legend(loc='lower right', framealpha=0.9, fontsize=9)
        
        ax2.tick_params(colors=self.colors['gray'])
        
        # Ana başlık
        fig.suptitle('Figure 2: Test Edilen Korelasyonların Durumu',
                    fontsize=16, fontweight='bold', color=self.colors['light'], y=0.98)
        
        # Alt bilgi
        fig.text(0.5, 0.02, f'{self.data["general"]["company_name"]} - {self.data["general"]["prepared_by"]}',
                ha='center', fontsize=9, color=self.colors['gray'], style='italic')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table1(self, filepath):
        """Table 1 - Sonuç Değerlendirme Tablosu"""
        width = float(self.fig_width.get())
        height = 6  # Sabit yükseklik
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Kritik taktiklerin ortalaması
        critical_tactics = ['Initial Access', 'Execution', 'Privilege Escalation']
        critical_rates = []
        for tactic in critical_tactics:
            if tactic in self.data['mitre_tactics']:
                critical_rates.append(self.data['mitre_tactics'][tactic]['rate'])
        critical_avg = np.mean(critical_rates) if critical_rates else 0
        
        # Tablo verileri
        total = self.data['test_results']['total_rules']
        tested = self.data['test_results']['tested_rules']
        triggered = self.data['test_results']['triggered_rules']
        not_tested = self.data['test_results']['not_tested']
        success_rate = self.data['test_results']['success_rate']
        
        table_data = [
            ['Metrik', 'Değer', 'Hedef', 'Durum', 'Açıklama'],
            ['Toplam Kural Sayısı', str(total), '300+',
             '✅' if total >= 300 else '⚠️' if total >= 200 else '❌',
             'Kural kapsam değerlendirmesi'],
            ['Test Edilen Kural', str(tested), '200+',
             '✅' if tested >= 200 else '⚠️' if tested >= 100 else '❌',
             'Test kapsam değerlendirmesi'],
            ['Başarı Oranı', f'%{success_rate:.1f}', '%70+',
             '✅' if success_rate >= 70 else '⚠️' if success_rate >= 50 else '❌',
             'Genel tespit yeteneği'],
            ['Test Edilmeyen', str(not_tested), '<50',
             '✅' if not_tested < 50 else '⚠️' if not_tested < 100 else '❌',
             'Kapsam dışı kural sayısı'],
            ['Kritik Taktik Ortalaması', f'%{critical_avg:.1f}', '%60+',
             '✅' if critical_avg >= 60 else '⚠️' if critical_avg >= 40 else '❌',
             'IA, EX, PE ortalaması']
        ]
        
        # Renk şeması
        cell_colors = []
        for i, row in enumerate(table_data):
            if i == 0:  # Başlık
                cell_colors.append([self.colors['accent_secondary']] * 5)
            else:
                row_colors = [self.colors['secondary']] * 5
                # Durum sütunu renklendirme
                if '✅' in row[3]:
                    row_colors[3] = self.colors['success']
                elif '⚠️' in row[3]:
                    row_colors[3] = self.colors['warning']
                elif '❌' in row[3]:
                    row_colors[3] = self.colors['danger']
                cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors, colWidths=[0.25, 0.12, 0.12, 0.1, 0.31])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 2.2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
            cell.set_height(0.12)
        
        # Veri satırları
        for i in range(1, len(table_data)):
            for j in range(5):
                cell = table[(i, j)]
                if j == 3:  # Durum sütunu
                    cell.set_text_props(weight='bold', fontsize=14)
                cell.set_height(0.1)
        
        ax.set_title('Table 1: Sonuç Değerlendirme Tablosu',
                    fontsize=16, fontweight='bold', pad=20)
        
        # Alt bilgiler
        fig.text(0.5, 0.08, f'{self.data["general"]["company_name"]} - {self.data["general"]["report_date"]}',
                ha='center', fontsize=10, color=self.colors['gray'])
        fig.text(0.5, 0.04, '✅ Başarılı | ⚠️ Dikkat Gerekli | ❌ Kritik',
                ha='center', fontsize=9, style='italic', color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table2(self, filepath):
        """Table 2 - MITRE ATT&CK Kapsama Analizi"""
        if not self.data['mitre_tactics']:
            return
        
        width = float(self.fig_width.get())
        height = max(8, len(self.data['mitre_tactics']) * 0.6)
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['Taktik', 'Test Edilen', 'Tetiklenen', 'Başarı %', 'Kritiklik']
        rows = []
        
        # Taktikleri başarı oranına göre sırala (düşükten yükseğe)
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
        cell_colors.append([self.colors['accent_secondary']] * 5)  # Başlık
        
        for row in rows:
            row_colors = [self.colors['secondary']] * 5
            success_rate = float(row[3].strip('%'))
            if success_rate < 40:
                row_colors[3] = self.colors['danger']
                row_colors[4] = self.colors['danger']
            elif success_rate < 60:
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
            cell.set_height(0.08)
        
        # Veri satırları
        for i in range(1, len(table_data)):
            for j in range(5):
                cell = table[(i, j)]
                if j == 3:  # Başarı yüzdesi
                    cell.set_text_props(weight='bold')
                cell.set_height(0.06)
        
        ax.set_title('Table 2: MITRE ATT&CK Kapsama Analizi',
                    fontsize=16, fontweight='bold', pad=20)
        
        # Özet istatistikler
        avg_success = np.mean([v['rate'] for v in self.data['mitre_tactics'].values()])
        total_test = sum([v['test'] for v in self.data['mitre_tactics'].values()])
        total_success = sum([v['triggered'] for v in self.data['mitre_tactics'].values()])
        
        fig.text(0.5, 0.05,
                f'Ortalama Başarı: %{avg_success:.1f} | Toplam Test: {total_test} | Toplam Başarılı: {total_success}',
                ha='center', fontsize=10, color=self.colors['light'])
        fig.text(0.5, 0.02,
                f'{self.data["general"]["company_name"]} | Kritik: <%40 | Orta: %40-60 | İyi: >%60',
                ha='center', fontsize=9, style='italic', color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table3(self, filepath):
        """Table 3 - Tetiklenen Korelasyon Kuralları"""
        if not self.data['triggered_rules']:
            return
        
        width = float(self.fig_width.get())
        height = max(6, min(12, len(self.data['triggered_rules']) * 0.5))
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['ID', 'Kural Adı', 'MITRE Teknik', 'Taktik', 'Güven Skoru']
        rows = []
        
        for i, rule in enumerate(self.data['triggered_rules'][:20], 1):  # Max 20 kural
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
            cell.set_height(0.08)
        
        ax.set_title('Table 3: Tetiklenen Korelasyon Kuralları Listesi',
                    fontsize=16, fontweight='bold', pad=20)
        
        # Alt bilgi
        avg_confidence = np.mean([int(r['confidence']) for r in self.data['triggered_rules']])
        fig.text(0.5, 0.02,
                f'Toplam {len(self.data["triggered_rules"])} kural | Ortalama Güven: %{avg_confidence:.1f} | {self.data["general"]["company_name"]}',
                ha='center', fontsize=9, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table4(self, filepath):
        """Table 4 - Algılanamayan MITRE Teknikleri"""
        if not self.data['undetected_techniques']:
            return
        
        width = float(self.fig_width.get())
        height = max(6, min(12, len(self.data['undetected_techniques']) * 0.5))
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Tablo verileri
        headers = ['MITRE Teknik ID', 'Teknik Adı', 'Taktik', 'Kritiklik Seviyesi', 'Öncelik']
        rows = []
        
        # Kritiklik sırasına göre sırala
        kritiklik_order = {'Kritik': 0, 'Yüksek': 1, 'Orta': 2, 'Düşük': 3}
        sorted_techniques = sorted(self.data['undetected_techniques'],
                                 key=lambda x: kritiklik_order.get(x['criticality'], 4))
        
        for i, tech in enumerate(sorted_techniques[:20], 1):  # Max 20 teknik
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
                        colWidths=[0.15, 0.33, 0.2, 0.15, 0.1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
            cell.set_height(0.1)
        
        ax.set_title('Table 4: Algılanamayan MITRE Teknikleri Listesi',
                    fontsize=16, fontweight='bold', pad=20)
        
        # Uyarı notu
        kritik_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Kritik')
        yuksek_count = sum(1 for t in self.data['undetected_techniques'] if t['criticality'] == 'Yüksek')
        
        fig.text(0.5, 0.02,
                f'⚠️ {kritik_count} Kritik, {yuksek_count} Yüksek seviyeli teknik için acil kural yazılması gerekmektedir',
                ha='center', fontsize=10, weight='bold', color=self.colors['warning'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()
    
    def generate_table5(self, filepath):
        """Table 5 - Yazılması Gereken Korelasyon Kurallarının Öneri Listesi"""
        if not self.data['recommendations']:
            return
        
        width = float(self.fig_width.get())
        height = max(6, min(12, len(self.data['recommendations']) * 0.6))
        dpi = int(self.fig_dpi.get())
        
        fig, ax = plt.subplots(figsize=(width, height), dpi=100)
        fig.patch.set_facecolor(self.colors['dark'])
        ax.axis('tight')
        ax.axis('off')
        
        # Öneri verileri
        headers = ['Öncelik', 'Kategori', 'Öneri', 'Beklenen Etki', 'Tahmini Süre']
        rows = []
        
        for i, rec in enumerate(self.data['recommendations'][:15], 1):  # Max 15 öneri
            # Otomatik etki ve süre tahmini
            if i <= 2:
                etki = 'Çok Yüksek'
                sure = f'{i*2} hafta'
            elif i <= 5:
                etki = 'Yüksek'
                sure = f'{i+2} hafta'
            elif i <= 8:
                etki = 'Orta'
                sure = f'{i+4} hafta'
            else:
                etki = 'Normal'
                sure = f'{i+6} hafta'
            
            rows.append([
                rec['priority'],
                rec['category'],
                rec['text'][:50] + '...' if len(rec['text']) > 50 else rec['text'],
                etki,
                sure
            ])
        
        table_data = [headers] + rows
        
        # Renk kodlaması
        cell_colors = []
        cell_colors.append([self.colors['accent_secondary']] * 5)
        
        for i, row in enumerate(rows):
            row_colors = [self.colors['secondary']] * 5
            if i < 2:  # İlk 2 öneri
                row_colors[0] = self.colors['danger']
                row_colors[3] = self.colors['success']
            elif i < 5:  # Sonraki 3 öneri
                row_colors[0] = self.colors['warning']
                row_colors[3] = self.colors['warning']
            cell_colors.append(row_colors)
        
        # Tablo oluştur
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors,
                        colWidths=[0.1, 0.18, 0.38, 0.15, 0.12])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Başlık satırı
        for i in range(5):
            cell = table[(0, i)]
            cell.set_text_props(weight='bold', color='white')
            cell.set_height(0.08)
        
        # Veri satırları
        for i in range(1, len(table_data)):
            for j in range(5):
                cell = table[(i, j)]
                if j == 0:  # Öncelik sütunu
                    cell.set_text_props(weight='bold')
                cell.set_height(0.08)
        
        ax.set_title('Table 5: Yazılması Gereken Korelasyon Kurallarının Öneri Listesi',
                    fontsize=16, fontweight='bold', pad=20)
        
        # Özet bilgi
        fig.text(0.5, 0.03,
                f'Toplam {len(self.data["recommendations"])} öneri | Tüm önerilerin uygulanması durumunda başarı oranının %70+ seviyesine çıkması beklenmektedir',
                ha='center', fontsize=9, style='italic', color=self.colors['success'])
        fig.text(0.5, 0.005,
                f'{self.data["general"]["company_name"]} - {self.data["general"]["prepared_by"]}',
                ha='center', fontsize=8, color=self.colors['gray'])
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, facecolor=self.colors['dark'], bbox_inches='tight')
        plt.close()

def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    app = IDCAFinalVersion(root)
    
    # Pencereyi ortala
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y-30}')
    
    root.mainloop()

if __name__ == "__main__":
    main()