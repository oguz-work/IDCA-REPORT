#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDCA Security Assessment Report Visualizer - Main Application
Version 6.0 - Modular and Improved
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from pathlib import Path
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import project modules
from core.config import *
from themes.theme_manager import ThemeManager
from data.models import (
    IDCAData, GeneralInfo, TestResults, MitreTactic,
    TriggeredRule, UndetectedTechnique, Recommendation
)
from ui.widgets import ValidatedEntry, EnhancedTable, CollapsibleFrame, StatusBar
from utils.validators import InputValidator, CrossFieldValidator
from core.visualizations import VisualizationGenerator


class IDCAVisualizerApp:
    """Main application class"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        
        # Initialize components
        self.theme_manager = ThemeManager()
        self.data = IDCAData()
        self.visualization_generator = VisualizationGenerator(self.theme_manager)
        
        # Settings
        self.transparent_bg = tk.BooleanVar(value=True)
        self.output_dir = OUTPUT_DIR
        
        # Apply matplotlib settings
        for key, value in MATPLOTLIB_PARAMS.items():
            plt.rcParams[key] = value
        
        # Setup window
        self._setup_window()
        
        # Initialize UI
        self._create_ui()
        
        # Show welcome
        self._show_welcome()
        
        # Update status
        self._update_data_status()
    
    def _setup_window(self):
        """Configure main window"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size
        window_width = min(DEFAULT_WINDOW_WIDTH, screen_width - 100)
        window_height = min(DEFAULT_WINDOW_HEIGHT, screen_height - 100)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Set icon if available
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
    
    def _create_ui(self):
        """Create main UI layout"""
        # Configure styles
        self._configure_styles()
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        self._create_toolbar(main_frame)
        
        # Content area with paned window
        self.paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left panel - Data entry
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=3)
        self._create_data_panel(left_frame)
        
        # Right panel - Preview
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=2)
        self._create_preview_panel(right_frame)
        
        # Status bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def _configure_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for validation feedback
        style.configure('Error.TEntry', fieldbackground='#fee2e2')
        style.configure('Success.TEntry', fieldbackground='#dcfce7')
        
        # Configure button styles
        style.configure('Success.TButton', foreground='green')
        style.configure('Warning.TButton', foreground='orange')
        style.configure('Danger.TButton', foreground='red')
    
    def _create_toolbar(self, parent):
        """Create toolbar with main actions"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Button definitions
        buttons = [
            ("📖 Guide", self._show_guide, None),
            ("📁 Load", self._load_data, None),
            ("💾 Save", self._save_data, None),
            ("📊 Sample Data", self._load_sample_data, None),
            ("🎨 GENERATE VISUALS", self._generate_all_visuals, 'Success.TButton'),
            ("🔄 Refresh", self._refresh_preview, None),
            ("🗑️ Clear All", self._clear_all_data, 'Danger.TButton')
        ]
        
        for text, command, style in buttons:
            btn = ttk.Button(toolbar, text=text, command=command)
            if style:
                btn.configure(style=style)
            btn.pack(side=tk.LEFT, padx=2)
    
    def _create_data_panel(self, parent):
        """Create data entry panel with tabs"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_general_tab()
        self._create_test_results_tab()
        self._create_mitre_tab()
        self._create_rules_tab()
        self._create_recommendations_tab()
        self._create_settings_tab()
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _create_general_tab(self):
        """Create general information tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. General Info")
        
        # Scrollable content
        canvas = tk.Canvas(tab, bg='white')
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content
        content = CollapsibleFrame(scrollable_frame, "Report Information", expanded=True)
        content.pack(fill=tk.X, padx=10, pady=10)
        
        frame = content.get_content_frame()
        
        # Info label
        info = ttk.Label(frame, text=f"{STATUS_ICONS['info']} All fields support Turkish characters",
                        foreground='blue', font=('Arial', 9))
        info.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky='w')
        
        # Form fields
        self.general_widgets = {}
        fields = [
            ("Company/Organization*:", "company_name", "e.g., Technology Corp.", 
             lambda v: InputValidator.validate_required_text(v, "Company name")),
            ("Report Date*:", "report_date", "e.g., January 2025",
             InputValidator.validate_date),
            ("Prepared By:", "prepared_by", "e.g., Security Team", None),
            ("Report ID:", "report_id", "e.g., IDCA-2025-001", None),
            ("Report Title:", "report_title", "e.g., Security Assessment", None),
            ("Classification:", "classification", "e.g., Confidential", None)
        ]
        
        for i, (label, key, hint, validator) in enumerate(fields, 1):
            ttk.Label(frame, text=label, font=('Arial', 10)).grid(
                row=i, column=0, sticky='w', pady=5, padx=(0, 10))
            
            # Error label
            error_var = tk.StringVar()
            
            # Entry widget
            entry = ValidatedEntry(frame, validator=validator, error_var=error_var,
                                 width=35, font=('Arial', 10))
            entry.grid(row=i, column=1, pady=5, sticky='ew')
            
            # Hint label
            ttk.Label(frame, text=hint, foreground='gray',
                     font=('Arial', 8, 'italic')).grid(
                row=i, column=2, sticky='w', padx=(10, 0))
            
            # Error display
            error_label = ttk.Label(frame, textvariable=error_var,
                                   foreground='red', font=('Arial', 8))
            error_label.grid(row=i+10, column=1, sticky='w', pady=(0, 5))
            
            self.general_widgets[key] = entry
        
        frame.grid_columnconfigure(1, weight=1)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_test_results_tab(self):
        """Create test results tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Test Results")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Information section
        info_frame = CollapsibleFrame(main_frame, "Information", expanded=True)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """• Total Rules: All rules in the system
• Tested Rules: Rules included in testing
• Triggered Rules: Rules that successfully generated alerts
• Other values are calculated automatically"""
        
        ttk.Label(info_frame.get_content_frame(), text=info_text,
                 font=('Arial', 9)).pack(padx=10, pady=5)
        
        # Data entry section
        entry_frame = CollapsibleFrame(main_frame, "Test Data Entry", expanded=True)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        content = entry_frame.get_content_frame()
        
        # Form fields
        self.test_widgets = {}
        fields = [
            ("Total Rules:", "total_rules", 
             lambda v: InputValidator.validate_integer(v, 1, 10000)),
            ("Tested Rules:", "tested_rules",
             lambda v: InputValidator.validate_integer(v, 0, 10000)),
            ("Triggered Rules:", "triggered_rules",
             lambda v: InputValidator.validate_integer(v, 0, 10000))
        ]
        
        for i, (label, key, validator) in enumerate(fields):
            ttk.Label(content, text=label, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky='w', pady=8, padx=(10, 0))
            
            error_var = tk.StringVar()
            entry = ValidatedEntry(content, validator=validator, error_var=error_var,
                                 width=15, font=('Arial', 11))
            entry.grid(row=i, column=1, pady=8, padx=10)
            entry.bind('<KeyRelease>', lambda e: self._calculate_test_stats())
            
            error_label = ttk.Label(content, textvariable=error_var,
                                   foreground='red', font=('Arial', 8))
            error_label.grid(row=i, column=2, sticky='w', padx=5)
            
            self.test_widgets[key] = entry
        
        # Calculated values section
        calc_frame = CollapsibleFrame(main_frame, "Calculated Values", expanded=True)
        calc_frame.pack(fill=tk.X)
        
        calc_content = calc_frame.get_content_frame()
        
        self.calc_labels = {}
        calcs = [
            ("Not Tested:", "not_tested", "Rules not included in testing"),
            ("Failed:", "failed", "Rules that didn't trigger"),
            ("Success Rate:", "success_rate", "Percentage of triggered rules"),
            ("Coverage:", "coverage_rate", "Percentage of tested rules")
        ]
        
        for i, (label, key, desc) in enumerate(calcs):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(calc_content, text=label, font=('Arial', 10)).grid(
                row=row, column=col, sticky='w', pady=5, padx=(10, 5))
            
            value_label = ttk.Label(calc_content, text="0",
                                   font=('Arial', 12, 'bold'), foreground='blue')
            value_label.grid(row=row, column=col+1, pady=5, padx=5)
            
            ttk.Label(calc_content, text=desc, font=('Arial', 8, 'italic'),
                     foreground='gray').grid(row=row, column=col+2, sticky='w', padx=5)
            
            self.calc_labels[key] = value_label
    
    def _create_mitre_tab(self):
        """Create MITRE ATT&CK tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. MITRE ATT&CK")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info
        info = ttk.Label(main_frame,
                        text="Enter test and triggered counts for each tactic. Success rates are calculated automatically.",
                        font=('Arial', 9), foreground='blue')
        info.pack(pady=5)
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="MITRE Tactics", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create enhanced table
        columns = ['Tactic Name', 'Tested', 'Triggered', 'Success %']
        self.mitre_table = EnhancedTable(table_frame, columns, rows=0,
                                        column_widths=[25, 12, 12, 12])
        self.mitre_table.pack(fill=tk.BOTH, expand=True)
        
        # Add default tactics
        for tactic in MITRE_TACTICS:
            self.mitre_table.add_row([tactic, '', '', ''])
        
        # Make tactic names read-only and bind calculation
        for i, row in enumerate(self.mitre_table.entries):
            row[0].config(state='readonly')
            row[1].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
            row[2].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
            row[3].config(state='readonly')
    
    def _create_rules_tab(self):
        """Create rules tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4. Rules")
        
        # Sub-tabs
        rules_notebook = ttk.Notebook(tab)
        rules_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Triggered rules tab
        triggered_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(triggered_tab, text=f"{STATUS_ICONS['success']} Triggered Rules")
        
        ttk.Label(triggered_tab, text="Successfully triggered rules",
                 font=('Arial', 9), foreground='green').pack(pady=5)
        
        columns = ['Rule Name', 'MITRE ID', 'Tactic', 'Confidence %']
        self.triggered_table = EnhancedTable(triggered_tab, columns, rows=5,
                                           column_widths=[30, 15, 20, 12])
        self.triggered_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Undetected techniques tab
        undetected_tab = ttk.Frame(rules_notebook)
        rules_notebook.add(undetected_tab, text=f"{STATUS_ICONS['error']} Undetected")
        
        ttk.Label(undetected_tab, text="Techniques not detected",
                 font=('Arial', 9), foreground='red').pack(pady=5)
        
        columns = ['MITRE ID', 'Technique Name', 'Tactic', 'Criticality']
        self.undetected_table = EnhancedTable(undetected_tab, columns, rows=5,
                                            column_widths=[15, 30, 20, 12])
        self.undetected_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add criticality dropdowns
        self._add_criticality_dropdowns()
    
    def _add_criticality_dropdowns(self):
        """Add criticality dropdown to undetected techniques"""
        # This will be called after table rows are created
        pass
    
    def _create_recommendations_tab(self):
        """Create recommendations tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="5. Recommendations")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Recommendation list for improving detection",
                 font=('Arial', 9), foreground='blue').pack(pady=5)
        
        columns = ['Priority', 'Category', 'Recommendation Text']
        self.recommendations_table = EnhancedTable(main_frame, columns, rows=5,
                                                 column_widths=[10, 20, 50])
        self.recommendations_table.pack(fill=tk.BOTH, expand=True)
        
        # Set up priority numbering
        self._setup_recommendation_priorities()
    
    def _setup_recommendation_priorities(self):
        """Set up automatic priority numbering"""
        for i, row in enumerate(self.recommendations_table.entries):
            row[0].insert(0, f"P{i+1}")
            row[0].config(state='readonly')
    
    def _create_settings_tab(self):
        """Create settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Settings")
        
        # Visual settings
        visual_frame = CollapsibleFrame(tab, "Visual Settings", expanded=True)
        visual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        visual_content = visual_frame.get_content_frame()
        
        # Dimension settings
        settings = [
            ("Figure Width (inch):", "fig_width", DEFAULT_FIG_WIDTH, 8, 20),
            ("Figure Height (inch):", "fig_height", DEFAULT_FIG_HEIGHT, 6, 15),
            ("DPI (Resolution):", "fig_dpi", DEFAULT_DPI, MIN_DPI, MAX_DPI)
        ]
        
        self.visual_settings = {}
        for i, (label, key, default, min_val, max_val) in enumerate(settings):
            ttk.Label(visual_content, text=label).grid(row=i, column=0, sticky='w', pady=5)
            
            spinbox = ttk.Spinbox(visual_content, from_=min_val, to=max_val, width=10)
            spinbox.set(default)
            spinbox.grid(row=i, column=1, pady=5, padx=10)
            
            self.visual_settings[key] = spinbox
        
        # Transparent background option
        ttk.Checkbutton(visual_content, text="Transparent Background (recommended for Word)",
                       variable=self.transparent_bg,
                       command=self._update_preview).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Theme settings
        theme_frame = CollapsibleFrame(tab, "Theme Settings", expanded=True)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        theme_content = theme_frame.get_content_frame()
        
        # Theme selection
        ttk.Label(theme_content, text="Select Theme:").grid(row=0, column=0, sticky='w', pady=5)
        
        self.theme_combo = ttk.Combobox(theme_content, 
                                       values=self.theme_manager.get_theme_names(),
                                       width=25)
        self.theme_combo.set(self.theme_manager.current_theme.name)
        self.theme_combo.grid(row=0, column=1, padx=10, pady=5)
        self.theme_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_theme())
        
        ttk.Button(theme_content, text="Apply Theme",
                  command=self._apply_theme).grid(row=0, column=2, padx=5)
        
        # Theme preview
        self._create_theme_preview(theme_content)
        
        # Output settings
        output_frame = CollapsibleFrame(tab, "Output Settings", expanded=True)
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_content = output_frame.get_content_frame()
        
        ttk.Label(output_content, text="Output Directory:").grid(row=0, column=0, sticky='w')
        
        self.output_path_var = tk.StringVar(value=str(self.output_dir))
        entry = ttk.Entry(output_content, textvariable=self.output_path_var, width=50)
        entry.grid(row=0, column=1, padx=10)
        
        ttk.Button(output_content, text="📁 Browse",
                  command=self._select_output_dir).grid(row=0, column=2)
    
    def _create_theme_preview(self, parent):
        """Create theme color preview"""
        preview_frame = ttk.LabelFrame(parent, text="Theme Colors", padding=10)
        preview_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky='ew')
        
        self.color_labels = {}
        color_items = [
            ('Primary', 'primary'), ('Secondary', 'secondary'), 
            ('Accent', 'accent'), ('Success', 'success'),
            ('Warning', 'warning'), ('Danger', 'danger')
        ]
        
        for i, (name, key) in enumerate(color_items):
            row = i // 3
            col = (i % 3) * 2
            
            ttk.Label(preview_frame, text=f"{name}:").grid(
                row=row, column=col, sticky='w', padx=5, pady=3)
            
            color_label = tk.Label(preview_frame, text="   ", 
                                  bg=self.theme_manager.get_color(key), 
                                  width=10, relief='solid', borderwidth=1)
            color_label.grid(row=row, column=col+1, padx=5, pady=3)
            self.color_labels[key] = color_label
    
    def _create_preview_panel(self, parent):
        """Create preview panel"""
        # Header
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header, text="Preview", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Visual selection
        self.preview_combo = ttk.Combobox(header, values=[
            'Figure 1 - Test Coverage',
            'Figure 2 - Test Status',
            'Table 1 - Summary',
            'Table 2 - MITRE Coverage',
            'Table 3 - Triggered Rules',
            'Table 4 - Undetected Techniques',
            'Table 5 - Recommendations'
        ], width=25)
        self.preview_combo.pack(side=tk.LEFT, padx=10)
        self.preview_combo.current(0)
        self.preview_combo.bind('<<ComboboxSelected>>', lambda e: self._update_preview())
        
        ttk.Button(header, text="🔄", command=self._update_preview, width=3).pack(side=tk.LEFT)
        
        # Preview area
        self.preview_frame = ttk.LabelFrame(parent, text="", padding=5)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Event handlers and methods
    
    def _on_tab_changed(self, event):
        """Handle tab change event"""
        self._update_data_status()
    
    def _calculate_test_stats(self):
        """Calculate test statistics"""
        try:
            total = int(self.test_widgets['total_rules'].get() or 0)
            tested = int(self.test_widgets['tested_rules'].get() or 0)
            triggered = int(self.test_widgets['triggered_rules'].get() or 0)
            
            # Validate
            is_valid, error = CrossFieldValidator.validate_test_results(total, tested, triggered)
            if not is_valid:
                self.status_bar.set_status(error, 'error')
                return
            
            # Calculate
            not_tested = total - tested
            failed = tested - triggered
            success_rate = (triggered / tested * 100) if tested > 0 else 0
            coverage_rate = (tested / total * 100) if total > 0 else 0
            
            # Update labels
            self.calc_labels['not_tested'].config(text=str(not_tested))
            self.calc_labels['failed'].config(text=str(failed))
            self.calc_labels['success_rate'].config(text=f"{success_rate:.1f}%")
            self.calc_labels['coverage_rate'].config(text=f"{coverage_rate:.1f}%")
            
            # Color coding
            if success_rate >= 70:
                color = 'green'
            elif success_rate >= 50:
                color = 'orange'
            else:
                color = 'red'
            self.calc_labels['success_rate'].config(foreground=color)
            
            self.status_bar.set_status("Statistics calculated", 'success')
            
        except ValueError:
            pass
    
    def _calculate_mitre_rates(self):
        """Calculate MITRE success rates"""
        for row in self.mitre_table.entries:
            try:
                test = int(row[1].get() or 0)
                triggered = int(row[2].get() or 0)
                
                is_valid, error = CrossFieldValidator.validate_mitre_tactic(test, triggered)
                if not is_valid:
                    row[3].delete(0, tk.END)
                    row[3].insert(0, "Error")
                    row[3].config(foreground='red')
                    continue
                
                if test > 0:
                    rate = (triggered / test) * 100
                    row[3].delete(0, tk.END)
                    row[3].insert(0, f"{rate:.1f}")
                    
                    # Color coding
                    if rate >= 70:
                        row[3].config(foreground='green')
                    elif rate >= 40:
                        row[3].config(foreground='orange')
                    else:
                        row[3].config(foreground='red')
                else:
                    row[3].delete(0, tk.END)
                    row[3].insert(0, "0.0")
                    row[3].config(foreground='gray')
            except:
                pass
        
        self.status_bar.set_status("MITRE rates calculated", 'success')
    
    def _apply_theme(self):
        """Apply selected theme"""
        theme_name = self.theme_combo.get()
        if self.theme_manager.set_current_theme(theme_name):
            # Update color preview
            for key, label in self.color_labels.items():
                label.config(bg=self.theme_manager.get_color(key))
            
            # Update preview
            self._update_preview()
            
            self.status_bar.set_status(f"Theme '{theme_name}' applied", 'success')
        else:
            self.status_bar.set_status(f"Failed to apply theme '{theme_name}'", 'error')
    
    def _update_preview(self):
        """Update visualization preview"""
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        try:
            # Collect current data
            self._collect_data()
            
            # Create figure
            fig = plt.figure(figsize=(5, 4), dpi=80)
            
            # Apply theme
            self.theme_manager.apply_to_matplotlib(self.transparent_bg.get())
            
            # Set background
            if self.transparent_bg.get():
                fig.patch.set_facecolor('none')
                fig.patch.set_alpha(0)
            else:
                fig.patch.set_facecolor(self.theme_manager.get_color('background'))
            
            # Generate preview based on selection
            selected = self.preview_combo.get()
            
            if 'Figure 1' in selected:
                self._preview_figure1(fig)
            elif 'Figure 2' in selected:
                self._preview_figure2(fig)
            else:
                self._preview_table(fig, selected)
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.preview_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            error_label = ttk.Label(self.preview_frame,
                                   text=f"Preview error:\n{str(e)}",
                                   font=('Arial', 10))
            error_label.pack(expand=True)
    
    def _preview_figure1(self, fig):
        """Preview Figure 1"""
        ax = fig.add_subplot(111)
        
        # Apply theme
        if self.transparent_bg.get():
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            ax.set_facecolor(self.theme_manager.get_color('surface'))
        
        # Sample data
        total = self.data.test_results.total_rules or 100
        tested = self.data.test_results.tested_rules or 60
        not_tested = total - tested
        
        # Pie chart
        sizes = [tested, not_tested]
        labels = ['Tested', 'Not Tested']
        colors = [self.theme_manager.get_color('accent'),
                 self.theme_manager.get_color('gray')]
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'color': self.theme_manager.get_color('text_primary')})
        
        ax.set_title('Test Coverage Preview', fontsize=11,
                    color=self.theme_manager.get_color('text_primary'))
    
    def _preview_figure2(self, fig):
        """Preview Figure 2"""
        ax = fig.add_subplot(111)
        
        # Apply theme
        if self.transparent_bg.get():
            ax.set_facecolor('none')
            ax.patch.set_alpha(0)
        else:
            ax.set_facecolor(self.theme_manager.get_color('surface'))
        
        # Sample data
        triggered = self.data.test_results.triggered_rules or 30
        failed = self.data.test_results.failed or 20
        
        # Bar chart
        ax.bar(['Triggered', 'Failed'], [triggered, failed],
               color=[self.theme_manager.get_color('success'),
                     self.theme_manager.get_color('danger')])
        
        ax.set_title('Test Status Preview', fontsize=11,
                    color=self.theme_manager.get_color('text_primary'))
        ax.tick_params(colors=self.theme_manager.get_color('text_secondary'))
    
    def _preview_table(self, fig, selected):
        """Preview table visualization"""
        ax = fig.add_subplot(111)
        ax.axis('tight')
        ax.axis('off')
        
        # Sample table
        table_data = [
            ['Header 1', 'Header 2', 'Header 3'],
            ['Data 1', 'Data 2', 'Data 3'],
            ['Data 4', 'Data 5', 'Data 6']
        ]
        
        # Colors
        cell_colors = []
        cell_colors.append([self.theme_manager.get_color('accent_secondary')] * 3)
        cell_colors.append([self.theme_manager.get_color('secondary')] * 3)
        cell_colors.append([self.theme_manager.get_color('secondary')] * 3)
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        cellColours=cell_colors)
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        ax.set_title(selected + ' Preview', fontsize=11,
                    color=self.theme_manager.get_color('text_primary'))
    
    def _collect_data(self):
        """Collect all data from forms"""
        # General info
        for key, widget in self.general_widgets.items():
            setattr(self.data.general, key, widget.get())
        
        # Test results
        try:
            self.data.test_results.total_rules = int(self.test_widgets['total_rules'].get() or 0)
            self.data.test_results.tested_rules = int(self.test_widgets['tested_rules'].get() or 0)
            self.data.test_results.triggered_rules = int(self.test_widgets['triggered_rules'].get() or 0)
            self.data.test_results.calculate_derived_values()
        except:
            pass
        
        # MITRE tactics
        self.data.mitre_tactics.clear()
        for row in self.mitre_table.get_data():
            if len(row) >= 4 and row[0]:
                try:
                    tactic = MitreTactic(
                        name=row[0],
                        test_count=int(row[1] or 0),
                        triggered_count=int(row[2] or 0)
                    )
                    tactic.calculate_success_rate()
                    self.data.mitre_tactics[row[0]] = tactic
                except:
                    pass
        
        # Triggered rules
        self.data.triggered_rules.clear()
        for row in self.triggered_table.get_data():
            if len(row) >= 4 and row[0]:
                try:
                    rule = TriggeredRule(
                        name=row[0],
                        mitre_id=row[1],
                        tactic=row[2],
                        confidence=int(row[3].replace('%', '') or 0)
                    )
                    self.data.triggered_rules.append(rule)
                except:
                    pass
        
        # Undetected techniques
        self.data.undetected_techniques.clear()
        for row in self.undetected_table.get_data():
            if len(row) >= 4 and row[0]:
                try:
                    tech = UndetectedTechnique(
                        mitre_id=row[0],
                        name=row[1],
                        tactic=row[2],
                        criticality=row[3]
                    )
                    self.data.undetected_techniques.append(tech)
                except:
                    pass
        
        # Recommendations
        self.data.recommendations.clear()
        for row in self.recommendations_table.get_data():
            if len(row) >= 3 and row[2]:
                try:
                    rec = Recommendation(
                        priority=row[0],
                        category=row[1],
                        text=row[2]
                    )
                    self.data.recommendations.append(rec)
                except:
                    pass
    
    def _update_data_status(self):
        """Update data status in status bar"""
        self._collect_data()
        
        # Count filled sections
        sections = []
        if self.data.general.company_name:
            sections.append("General")
        if self.data.test_results.total_rules > 0:
            sections.append("Tests")
        if self.data.mitre_tactics:
            sections.append("MITRE")
        if self.data.triggered_rules:
            sections.append("Rules")
        if self.data.recommendations:
            sections.append("Recommendations")
        
        if sections:
            self.status_bar.set_data_status(f"Data: {', '.join(sections)}")
        else:
            self.status_bar.set_data_status("No data entered")
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome = f"""Welcome to {APP_NAME} v{APP_VERSION}

✅ Turkish character support
✅ Enhanced data entry with validation
✅ 6 professional themes
✅ Transparent background support
✅ Real-time preview

Current Theme: {self.theme_manager.current_theme.name}
Background: {'Transparent' if self.transparent_bg.get() else 'Opaque'}

Get started by entering your data in the tabs!"""
        
        self.status_bar.set_status("Ready to begin. Click 'Guide' for help.", 'info')
    
    def _show_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("📖 User Guide")
        guide_window.geometry("800x600")
        
        # Make it modal
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # Create scrolled text
        text = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, font=('Arial', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guide_text = f"""
{APP_NAME} USER GUIDE
{'='*50}

🎯 PURPOSE
This tool converts IDCA test results into professional visualizations for Word reports.

📊 GENERATED VISUALIZATIONS
• Figure 1: Test Coverage Analysis
• Figure 2: Test Status Overview
• Table 1: Assessment Summary
• Table 2: MITRE ATT&CK Coverage
• Table 3: Triggered Rules List
• Table 4: Undetected Techniques
• Table 5: Recommendations

📝 DATA ENTRY

1. GENERAL INFORMATION
   - Company name and report date are required
   - All fields support Turkish characters (ç, ğ, ı, ö, ş, ü)
   - Fields with * are mandatory

2. TEST RESULTS
   - Enter total, tested, and triggered rule counts
   - Other values are calculated automatically
   - Real-time validation ensures data integrity

3. MITRE ATT&CK
   - Enter test and triggered counts for each tactic
   - Success rates are calculated automatically
   - Color coding: Green (≥70%), Orange (40-69%), Red (<40%)

4. RULES
   - List triggered rules with confidence scores
   - List undetected techniques with criticality levels
   - Use the table controls to add/remove rows

5. RECOMMENDATIONS
   - Priorities are auto-numbered
   - Select categories from dropdowns
   - Enter clear, actionable recommendation text

💡 TIPS

• VALIDATION: Red borders indicate validation errors
• TABLES: Use "Add Row" to add more entries
• PREVIEW: Select different visualizations to preview
• THEMES: Try different themes for various report styles
• SAVE: Use JSON format to save and resume work

📁 GENERATING VISUALS

1. Complete all required data fields
2. Click "GENERATE VISUALS" button
3. Select output directory if needed
4. All images are saved as high-quality PNG files

📋 ADDING TO WORD

1. Insert PNG files into Word document
2. Use "In Line with Text" layout option
3. Disable compression for best quality (300 DPI)

⚙️ SETTINGS

• Figure dimensions: Adjust for your document layout
• DPI: Higher values = better quality but larger files
• Transparent background: Recommended for Word
• Themes: Choose based on your report style

⚠️ IMPORTANT NOTES

• Numeric fields accept only numbers
• Test rules ≤ Total rules
• Triggered rules ≤ Test rules
• Confidence scores: 0-100
• Save frequently to avoid data loss

For support or bug reports, contact your IT administrator.

Happy reporting! 🚀
"""
        
        text.insert(tk.END, guide_text)
        text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(guide_window, text="Close", 
                  command=guide_window.destroy).pack(pady=10)
    
    def _load_sample_data(self):
        """Load sample data for testing"""
        sample = {
            'general': {
                'company_name': 'Example Corporation',
                'report_date': 'January 2025',
                'prepared_by': 'Security Team',
                'report_id': 'IDCA-2025-001',
                'report_title': 'Security Assessment Report',
                'classification': 'Confidential'
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
                {'name': 'Suspicious PowerShell Command', 'mitre': 'T1059.001',
                 'tactic': 'Execution', 'confidence': '95'},
                {'name': 'Brute Force Attack Detected', 'mitre': 'T1110',
                 'tactic': 'Credential Access', 'confidence': '88'}
            ],
            'undetected_techniques': [
                {'id': 'T1566.001', 'name': 'Spearphishing Attachment',
                 'tactic': 'Initial Access', 'criticality': 'Critical'},
                {'id': 'T1548.002', 'name': 'Bypass UAC',
                 'tactic': 'Privilege Escalation', 'criticality': 'High'}
            ],
            'recommendations': [
                {'priority': 'P1', 'category': 'Log Sources',
                 'text': 'Enable Windows Security event logging on all critical servers'},
                {'priority': 'P2', 'category': 'Rule Optimization',
                 'text': 'Adjust threshold values for failed authentication rules'}
            ]
        }
        
        try:
            self.data = IDCAData.from_dict(sample)
            self._populate_forms()
            
            messagebox.showinfo("Success", "Sample data loaded successfully!")
            self.status_bar.set_status("Sample data loaded", 'success')
            self._update_data_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sample data: {str(e)}")
            self.status_bar.set_status("Failed to load sample data", 'error')
    
    def _populate_forms(self):
        """Populate forms with current data"""
        # General info
        for key, widget in self.general_widgets.items():
            value = getattr(self.data.general, key, '')
            widget.delete(0, tk.END)
            widget.insert(0, value)
        
        # Test results
        self.test_widgets['total_rules'].delete(0, tk.END)
        self.test_widgets['total_rules'].insert(0, str(self.data.test_results.total_rules))
        self.test_widgets['tested_rules'].delete(0, tk.END)
        self.test_widgets['tested_rules'].insert(0, str(self.data.test_results.tested_rules))
        self.test_widgets['triggered_rules'].delete(0, tk.END)
        self.test_widgets['triggered_rules'].insert(0, str(self.data.test_results.triggered_rules))
        
        self._calculate_test_stats()
        
        # MITRE tactics
        mitre_data = []
        for tactic in MITRE_TACTICS:
            if tactic in self.data.mitre_tactics:
                t = self.data.mitre_tactics[tactic]
                mitre_data.append([tactic, str(t.test_count), str(t.triggered_count), f"{t.success_rate:.1f}"])
            else:
                mitre_data.append([tactic, '', '', ''])
        
        self.mitre_table.set_data(mitre_data)
        
        # Re-apply read-only and bindings
        for i, row in enumerate(self.mitre_table.entries):
            row[0].config(state='readonly')
            row[1].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
            row[2].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
            row[3].config(state='readonly')
        
        # Triggered rules
        triggered_data = []
        for rule in self.data.triggered_rules:
            triggered_data.append([rule.name, rule.mitre_id, rule.tactic, str(rule.confidence)])
        self.triggered_table.set_data(triggered_data)
        
        # Undetected techniques
        undetected_data = []
        for tech in self.data.undetected_techniques:
            undetected_data.append([tech.mitre_id, tech.name, tech.tactic, tech.criticality])
        self.undetected_table.set_data(undetected_data)
        
        # Recommendations
        rec_data = []
        for rec in self.data.recommendations:
            rec_data.append([rec.priority, rec.category, rec.text])
        self.recommendations_table.set_data(rec_data)
        
        # Re-apply priority numbering
        for i, row in enumerate(self.recommendations_table.entries):
            if row and row[0].winfo_exists():
                row[0].config(state='normal')
                row[0].delete(0, tk.END)
                row[0].insert(0, f"P{i+1}")
                row[0].config(state='readonly')
    
    def _save_data(self):
        """Save data to JSON file"""
        self._collect_data()
        
        # Validate
        errors = self.data.validate()
        if errors:
            messagebox.showwarning("Validation Errors", 
                                 "The following issues were found:\n\n" + "\n".join(errors[:5]))
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"IDCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                self.data.save_to_json(filename)
                messagebox.showinfo("Success", "Data saved successfully!")
                self.status_bar.set_status(f"Saved to {Path(filename).name}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")
                self.status_bar.set_status("Save failed", 'error')
    
    def _load_data(self):
        """Load data from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.data = IDCAData.load_from_json(filename)
                self._populate_forms()
                messagebox.showinfo("Success", "Data loaded successfully!")
                self.status_bar.set_status(f"Loaded {Path(filename).name}", 'success')
                self._update_data_status()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                self.status_bar.set_status("Load failed", 'error')
    
    def _clear_all_data(self):
        """Clear all data after confirmation"""
        if messagebox.askyesno("Confirm Clear", 
                              "Are you sure you want to clear all data?\nThis cannot be undone."):
            # Clear forms
            for widget in self.general_widgets.values():
                widget.delete(0, tk.END)
            
            for widget in self.test_widgets.values():
                widget.delete(0, tk.END)
            
            for label in self.calc_labels.values():
                label.config(text="0")
            
            # Clear tables
            self.mitre_table.clear()
            self.triggered_table.clear()
            self.undetected_table.clear()
            self.recommendations_table.clear()
            
            # Reset data
            self.data = IDCAData()
            
            # Re-add default MITRE tactics
            for tactic in MITRE_TACTICS:
                self.mitre_table.add_row([tactic, '', '', ''])
            
            # Re-apply settings
            for i, row in enumerate(self.mitre_table.entries):
                row[0].config(state='readonly')
                row[1].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
                row[2].bind('<KeyRelease>', lambda e: self._calculate_mitre_rates())
                row[3].config(state='readonly')
            
            self.status_bar.set_status("All data cleared", 'warning')
            self._update_data_status()
    
    def _refresh_preview(self):
        """Refresh the preview"""
        self._update_preview()
        self.status_bar.set_status("Preview refreshed", 'success')
    
    def _select_output_dir(self):
        """Select output directory"""
        folder = filedialog.askdirectory(initialdir=self.output_dir)
        if folder:
            self.output_dir = Path(folder)
            self.output_path_var.set(str(self.output_dir))
            self.status_bar.set_status(f"Output directory set to {self.output_dir.name}", 'success')
    
    def _generate_all_visuals(self):
        """Generate all visualizations"""
        # Collect and validate data
        self._collect_data()
        self.data.calculate_all_derived_values()
        
        errors = self.data.validate()
        if errors:
            response = messagebox.askyesnocancel(
                "Validation Issues",
                f"Found {len(errors)} validation issues:\n\n" + 
                "\n".join(errors[:5]) + 
                ("\n..." if len(errors) > 5 else "") +
                "\n\nContinue anyway?"
            )
            if response != True:
                return
        
        # Check minimum requirements
        if not self.data.general.company_name:
            messagebox.showwarning("Missing Data", "Please enter at least the company name.")
            return
        
        if self.data.test_results.total_rules == 0:
            messagebox.showwarning("Missing Data", "Please enter test results data.")
            return
        
        # Create output directory
        self.output_dir = Path(self.output_path_var.get())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress window
        progress = tk.Toplevel(self.root)
        progress.title("Generating Visualizations")
        progress.geometry("500x300")
        progress.transient(self.root)
        
        # Center the progress window
        progress.update_idletasks()
        x = (progress.winfo_screenwidth() - progress.winfo_width()) // 2
        y = (progress.winfo_screenheight() - progress.winfo_height()) // 2
        progress.geometry(f"+{x}+{y}")
        
        # Theme info
        theme_info = ttk.Label(progress,
                              text=f"Theme: {self.theme_manager.current_theme.name} | " +
                                   f"Background: {'Transparent' if self.transparent_bg.get() else 'Opaque'}",
                              font=('Arial', 10, 'italic'), foreground='blue')
        theme_info.pack(pady=10)
        
        # Progress label
        label = ttk.Label(progress, text="Starting...", font=('Arial', 12))
        label.pack(pady=10)
        
        # Progress bar
        pbar = ttk.Progressbar(progress, length=400, mode='determinate')
        pbar.pack(pady=20)
        
        # Details
        details = ttk.Label(progress, text="", font=('Arial', 9), foreground='gray')
        details.pack(pady=5)
        
        # Results text
        results_frame = ttk.Frame(progress)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        results_text = scrolledtext.ScrolledText(results_frame, height=8, width=50,
                                                font=('Courier', 9))
        results_text.pack(fill=tk.BOTH, expand=True)
        
        # Update visualization settings
        try:
            width = float(self.visual_settings['fig_width'].get())
            height = float(self.visual_settings['fig_height'].get())
            dpi = int(self.visual_settings['fig_dpi'].get())
            
            self.visualization_generator.set_dimensions(width, height, dpi)
            self.visualization_generator.set_transparent(self.transparent_bg.get())
        except:
            pass
        
        # Generate visualizations
        visualizations = [
            'Figure_1_Test_Coverage',
            'Figure_2_Test_Status',
            'Table_1_Summary',
            'Table_2_MITRE_Coverage',
            'Table_3_Triggered_Rules',
            'Table_4_Undetected_Techniques',
            'Table_5_Recommendations'
        ]
        
        pbar['maximum'] = len(visualizations)
        
        # Process
        success_count = 0
        for i, visual_name in enumerate(visualizations):
            label.config(text=f"Generating: {visual_name}")
            details.config(text=f"({i+1}/{len(visualizations)}) {visual_name}.png")
            pbar['value'] = i
            progress.update()
            
            try:
                # Generate individual visualization
                if visual_name == 'Figure_1_Test_Coverage':
                    filepath = self.output_dir / f"{visual_name}.png"
                    self.visualization_generator.generate_figure1(self.data, filepath)
                elif visual_name == 'Figure_2_Test_Status':
                    filepath = self.output_dir / f"{visual_name}.png"
                    self.visualization_generator.generate_figure2(self.data, filepath)
                elif visual_name == 'Table_1_Summary':
                    filepath = self.output_dir / f"{visual_name}.png"
                    self.visualization_generator.generate_table1(self.data, filepath)
                elif visual_name == 'Table_2_MITRE_Coverage':
                    if self.data.mitre_tactics:
                        filepath = self.output_dir / f"{visual_name}.png"
                        self.visualization_generator.generate_table2(self.data, filepath)
                    else:
                        raise Exception("No MITRE data")
                elif visual_name == 'Table_3_Triggered_Rules':
                    if self.data.triggered_rules:
                        filepath = self.output_dir / f"{visual_name}.png"
                        self.visualization_generator.generate_table3(self.data, filepath)
                    else:
                        raise Exception("No triggered rules data")
                elif visual_name == 'Table_4_Undetected_Techniques':
                    if self.data.undetected_techniques:
                        filepath = self.output_dir / f"{visual_name}.png"
                        self.visualization_generator.generate_table4(self.data, filepath)
                    else:
                        raise Exception("No undetected techniques data")
                elif visual_name == 'Table_5_Recommendations':
                    if self.data.recommendations:
                        filepath = self.output_dir / f"{visual_name}.png"
                        self.visualization_generator.generate_table5(self.data, filepath)
                    else:
                        raise Exception("No recommendations data")
                
                results_text.insert(tk.END, f"✅ {visual_name}.png\n")
                success_count += 1
                
            except Exception as e:
                results_text.insert(tk.END, f"❌ {visual_name}.png - {str(e)}\n")
            
            results_text.see(tk.END)
        
        pbar['value'] = len(visualizations)
        label.config(text=f"✅ Completed! {success_count}/{len(visualizations)} visuals generated")
        details.config(text=f"Output directory: {self.output_dir}")
        
        # Add background info
        if self.transparent_bg.get():
            info_label = ttk.Label(progress,
                                  text=f"{STATUS_ICONS['info']} Images saved with transparent background (ideal for Word)",
                                  font=('Arial', 9), foreground='green')
            info_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(progress)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Open Folder",
                  command=lambda: self._open_folder(self.output_dir)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close",
                  command=progress.destroy).pack(side=tk.LEFT, padx=5)
        
        self.status_bar.set_status(f"Generated {success_count} visualizations", 'success')
    
    def _open_folder(self, folder_path: Path):
        """Open folder in file explorer"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(str(folder_path))
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{folder_path}"')
            else:
                os.system(f'xdg-open "{folder_path}"')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set encoding for Turkish characters
    try:
        root.tk.call('encoding', 'system', 'utf-8')
    except:
        pass
    
    # Create and run application
    app = IDCAVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()