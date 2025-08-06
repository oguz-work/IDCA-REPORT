#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom UI widgets for IDCA Visualizer
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional, Dict, Any
import tkinter.font as tkFont


class ValidatedEntry(ttk.Entry):
    """Entry widget with validation support"""
    
    def __init__(self, parent, validator: Callable = None, error_var: tk.StringVar = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.validator = validator
        self.error_var = error_var or tk.StringVar()
        self.is_valid = True
        
        # Set up validation
        self.configure(validate='focusout', validatecommand=self.validate_input)
        self.bind('<FocusOut>', lambda e: self.validate_input())
        self.bind('<KeyRelease>', lambda e: self.on_key_release())
        
        # Visual feedback
        self.default_style = self['style'] or 'TEntry'
        self.error_style = 'Error.TEntry'
        self.success_style = 'Success.TEntry'
    
    def validate_input(self) -> bool:
        """Validate the input"""
        if not self.validator:
            return True
        
        value = self.get()
        is_valid, _, error_msg = self.validator(value)
        
        self.is_valid = is_valid
        self.error_var.set(error_msg if not is_valid else "")
        
        # Update visual style
        if not value:
            self['style'] = self.default_style
        elif is_valid:
            self['style'] = self.success_style
        else:
            self['style'] = self.error_style
        
        return is_valid
    
    def on_key_release(self):
        """Clear error on typing"""
        if self.error_var.get():
            self.error_var.set("")
            self['style'] = self.default_style
    
    def get_validated_value(self) -> Any:
        """Get the validated and converted value"""
        if not self.validator:
            return self.get()
        
        value = self.get()
        is_valid, converted_value, _ = self.validator(value)
        
        return converted_value if is_valid else None


class EnhancedTable(ttk.Frame):
    """Enhanced table widget with better UX"""
    
    def __init__(self, parent, columns: List[str], rows: int = 10, 
                 column_widths: List[int] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.initial_rows = rows
        self.entries = []
        self.column_widths = column_widths or [15] * len(columns)
        
        # Create UI
        self._create_header()
        self._create_scrollable_area()
        self._create_initial_rows()
        self._create_controls()
        
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def _create_header(self):
        """Create table header"""
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky='ew', padx=1)
        
        for j, (col, width) in enumerate(zip(self.columns, self.column_widths)):
            label = ttk.Label(header_frame, text=col, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=j, sticky='ew', padx=2, pady=5)
            header_frame.grid_columnconfigure(j, weight=1, minsize=width*8)
    
    def _create_scrollable_area(self):
        """Create scrollable area for table rows"""
        # Create canvas and scrollbar
        canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        canvas.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.canvas = canvas
    
    def _create_initial_rows(self):
        """Create initial empty rows"""
        for _ in range(self.initial_rows):
            self.add_row()
    
    def _create_controls(self):
        """Create control buttons"""
        control_frame = ttk.Frame(self)
        control_frame.grid(row=2, column=0, sticky='ew', pady=5)
        
        ttk.Button(control_frame, text="➕ Add Row", 
                  command=self.add_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🗑️ Clear All", 
                  command=self.clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🧹 Remove Empty", 
                  command=self.remove_empty_rows).pack(side=tk.LEFT, padx=5)
    
    def add_row(self, data: List[str] = None):
        """Add a new row to the table"""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill='x', padx=1, pady=1)
        
        row_entries = []
        for j, width in enumerate(self.column_widths):
            entry = ttk.Entry(row_frame, width=width)
            entry.grid(row=0, column=j, sticky='ew', padx=2)
            
            if data and j < len(data):
                entry.insert(0, str(data[j]))
            
            row_entries.append(entry)
            row_frame.grid_columnconfigure(j, weight=1)
        
        # Add remove button
        remove_btn = ttk.Button(row_frame, text="❌", width=3,
                               command=lambda: self.remove_row(row_frame, row_entries))
        remove_btn.grid(row=0, column=len(self.columns), padx=2)
        
        self.entries.append(row_entries)
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def remove_row(self, row_frame: ttk.Frame, row_entries: List[ttk.Entry]):
        """Remove a specific row"""
        row_frame.destroy()
        if row_entries in self.entries:
            self.entries.remove(row_entries)
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def remove_empty_rows(self):
        """Remove all empty rows"""
        rows_to_remove = []
        
        for row_entries in self.entries:
            if all(not entry.get().strip() for entry in row_entries):
                rows_to_remove.append(row_entries)
        
        for row in rows_to_remove:
            # Find and destroy the parent frame
            if row and row[0].winfo_exists():
                row[0].master.destroy()
            self.entries.remove(row)
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def get_data(self) -> List[List[str]]:
        """Get all non-empty table data"""
        data = []
        for row in self.entries:
            if any(entry.winfo_exists() for entry in row):
                row_data = [entry.get().strip() if entry.winfo_exists() else "" 
                           for entry in row]
                if any(row_data):  # Only include non-empty rows
                    data.append(row_data)
        return data
    
    def set_data(self, data: List[List[str]]):
        """Set table data"""
        self.clear()
        for row_data in data:
            self.add_row(row_data)
    
    def clear(self):
        """Clear all rows"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        
        # Update scroll region
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class CollapsibleFrame(ttk.Frame):
    """A collapsible frame widget"""
    
    def __init__(self, parent, title: str, expanded: bool = True, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.expanded = tk.BooleanVar(value=expanded)
        
        # Header
        self.header = ttk.Frame(self)
        self.header.pack(fill='x', padx=5, pady=2)
        
        # Toggle button
        self.toggle_btn = ttk.Button(self.header, text="▼" if expanded else "▶",
                                    width=3, command=self.toggle)
        self.toggle_btn.pack(side=tk.LEFT)
        
        # Title
        self.title_label = ttk.Label(self.header, text=title, 
                                    font=('Arial', 11, 'bold'))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Content frame
        self.content_frame = ttk.Frame(self)
        if expanded:
            self.content_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def toggle(self):
        """Toggle the frame expansion"""
        if self.expanded.get():
            self.content_frame.pack_forget()
            self.toggle_btn.config(text="▶")
            self.expanded.set(False)
        else:
            self.content_frame.pack(fill='both', expand=True, padx=5, pady=5)
            self.toggle_btn.config(text="▼")
            self.expanded.set(True)
    
    def get_content_frame(self) -> ttk.Frame:
        """Get the content frame for adding widgets"""
        return self.content_frame


class StatusBar(ttk.Frame):
    """Enhanced status bar with multiple sections"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Left section - Main status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var,
                                     font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Separator
        ttk.Separator(self, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        
        # Center section - Progress
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(self, textvariable=self.progress_var,
                                       font=('Arial', 9))
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Right section - Data status
        self.data_var = tk.StringVar()
        self.data_label = ttk.Label(self, textvariable=self.data_var,
                                   font=('Arial', 9))
        self.data_label.pack(side=tk.RIGHT, padx=10)
    
    def set_status(self, message: str, type: str = "info"):
        """Set main status message with type-based styling"""
        self.status_var.set(message)
        
        # Color based on type
        colors = {
            'info': '#000000',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        
        self.status_label.config(foreground=colors.get(type, '#000000'))
    
    def set_progress(self, message: str):
        """Set progress message"""
        self.progress_var.set(message)
    
    def set_data_status(self, message: str):
        """Set data status message"""
        self.data_var.set(message)
    
    def clear(self):
        """Clear all status messages"""
        self.status_var.set("Ready")
        self.progress_var.set("")
        self.data_var.set("")