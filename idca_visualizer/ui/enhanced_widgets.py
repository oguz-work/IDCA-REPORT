#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced widgets for better data entry and visualization
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional, Tuple
import re


class MITRETable(ttk.Frame):
    """Enhanced table specifically for MITRE ATT&CK tactics with proper validation and symmetry"""
    
    def __init__(self, parent, tactics: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.tactics = tactics
        self.entries = []
        self.on_change_callback = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the table UI with proper alignment"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=2, pady=(0, 5))
        
        # Column headers with fixed widths
        headers = [
            ('Tactic Name', 250),
            ('Tested', 100),
            ('Triggered', 100),
            ('Success %', 100)
        ]
        
        for i, (header, width) in enumerate(headers):
            label = ttk.Label(header_frame, text=header, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=i, padx=5, sticky='w')
            header_frame.grid_columnconfigure(i, minsize=width)
        
        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=2)
        
        # Scrollable frame for rows
        self._create_scrollable_frame()
        
        # Add rows for each tactic
        for tactic in self.tactics:
            self._add_tactic_row(tactic)
    
    def _create_scrollable_frame(self):
        """Create scrollable area for table rows"""
        # Canvas and scrollbar
        canvas = tk.Canvas(self, bg='white', highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas = canvas
    
    def _add_tactic_row(self, tactic_name: str):
        """Add a row for a specific tactic"""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill='x', padx=2, pady=1)
        
        # Tactic name (read-only)
        name_label = ttk.Label(row_frame, text=tactic_name, width=30)
        name_label.grid(row=0, column=0, padx=5, sticky='w')
        
        # Test count entry
        test_var = tk.StringVar()
        test_entry = ttk.Entry(row_frame, textvariable=test_var, width=12, justify='center')
        test_entry.grid(row=0, column=1, padx=5)
        test_var.trace('w', lambda *args: self._validate_and_calculate(row_frame))
        
        # Triggered count entry
        triggered_var = tk.StringVar()
        triggered_entry = ttk.Entry(row_frame, textvariable=triggered_var, width=12, justify='center')
        triggered_entry.grid(row=0, column=2, padx=5)
        triggered_var.trace('w', lambda *args: self._validate_and_calculate(row_frame))
        
        # Success rate (read-only)
        rate_var = tk.StringVar(value="0.0")
        rate_entry = ttk.Entry(row_frame, textvariable=rate_var, width=12, 
                              state='readonly', justify='center')
        rate_entry.grid(row=0, column=3, padx=5)
        
        # Configure column weights for proper alignment
        row_frame.grid_columnconfigure(0, minsize=250)
        row_frame.grid_columnconfigure(1, minsize=100)
        row_frame.grid_columnconfigure(2, minsize=100)
        row_frame.grid_columnconfigure(3, minsize=100)
        
        # Store references
        row_data = {
            'frame': row_frame,
            'tactic': tactic_name,
            'test_var': test_var,
            'triggered_var': triggered_var,
            'rate_var': rate_var,
            'test_entry': test_entry,
            'triggered_entry': triggered_entry,
            'rate_entry': rate_entry
        }
        self.entries.append(row_data)
    
    def _validate_and_calculate(self, row_frame):
        """Validate inputs and calculate success rate"""
        # Find the row data
        row_data = None
        for entry in self.entries:
            if entry['frame'] == row_frame:
                row_data = entry
                break
        
        if not row_data:
            return
        
        try:
            # Get values
            test_str = row_data['test_var'].get().strip()
            triggered_str = row_data['triggered_var'].get().strip()
            
            # Validate numeric input
            test_count = int(test_str) if test_str else 0
            triggered_count = int(triggered_str) if triggered_str else 0
            
            # Validate logic
            if test_count < 0 or triggered_count < 0:
                row_data['rate_var'].set("Error")
                row_data['rate_entry'].configure(foreground='red')
                return
            
            if triggered_count > test_count:
                row_data['rate_var'].set("Error")
                row_data['rate_entry'].configure(foreground='red')
                row_data['triggered_entry'].configure(style='Error.TEntry')
                return
            else:
                row_data['triggered_entry'].configure(style='TEntry')
            
            # Calculate rate
            if test_count > 0:
                rate = (triggered_count / test_count) * 100
                row_data['rate_var'].set(f"{rate:.1f}")
                
                # Color coding
                if rate >= 70:
                    row_data['rate_entry'].configure(foreground='green')
                elif rate >= 40:
                    row_data['rate_entry'].configure(foreground='orange')
                else:
                    row_data['rate_entry'].configure(foreground='red')
            else:
                row_data['rate_var'].set("0.0")
                row_data['rate_entry'].configure(foreground='gray')
            
            # Trigger callback if set
            if self.on_change_callback:
                self.on_change_callback()
                
        except ValueError:
            # Non-numeric input
            if row_data['test_var'].get() or row_data['triggered_var'].get():
                row_data['rate_var'].set("---")
                row_data['rate_entry'].configure(foreground='gray')
    
    def get_data(self) -> List[Dict[str, any]]:
        """Get all table data"""
        data = []
        for entry in self.entries:
            try:
                test_count = int(entry['test_var'].get() or 0)
                triggered_count = int(entry['triggered_var'].get() or 0)
                success_rate = float(entry['rate_var'].get()) if entry['rate_var'].get() not in ['Error', '---', ''] else 0.0
            except:
                test_count = 0
                triggered_count = 0
                success_rate = 0.0
            
            data.append({
                'tactic': entry['tactic'],
                'test_count': test_count,
                'triggered_count': triggered_count,
                'success_rate': success_rate
            })
        
        return data
    
    def set_data(self, data: Dict[str, Dict]):
        """Set table data from dictionary"""
        for entry in self.entries:
            tactic_name = entry['tactic']
            if tactic_name in data:
                tactic_data = data[tactic_name]
                entry['test_var'].set(str(tactic_data.get('test_count', '')))
                entry['triggered_var'].set(str(tactic_data.get('triggered_count', '')))
    
    def clear(self):
        """Clear all data"""
        for entry in self.entries:
            entry['test_var'].set('')
            entry['triggered_var'].set('')
            entry['rate_var'].set('0.0')
            entry['rate_entry'].configure(foreground='gray')
    
    def set_on_change_callback(self, callback: Callable):
        """Set callback to be triggered on data change"""
        self.on_change_callback = callback


class AutoCompleteCombobox(ttk.Combobox):
    """Combobox with auto-complete functionality"""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._completion_list = values or []
        self.set_completion_list(self._completion_list)
        self._hits = []
        self._hit_index = 0
        self.bind('<KeyRelease>', self._handle_keyrelease)
    
    def set_completion_list(self, completion_list):
        """Set the list of possible completions"""
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
    
    def _handle_keyrelease(self, event):
        """Handle key release for auto-completion"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self._hits = []
            self._hit_index = 0
        
        if event.keysym == "Return":
            self.event_generate('<<ComboboxSelected>>')
            return
        
        if len(event.keysym) == 1:
            self._autocomplete()
    
    def _autocomplete(self):
        """Auto-complete the combobox value"""
        current_text = self.get()
        
        if not current_text:
            self._hits = []
            return
        
        # Find matching values
        self._hits = [item for item in self._completion_list 
                     if item.lower().startswith(current_text.lower())]
        
        if self._hits:
            self._hit_index = 0
            self.delete(0, tk.END)
            self.insert(0, self._hits[0])
            self.select_range(len(current_text), tk.END)


class NumericEntry(ttk.Entry):
    """Entry widget that only accepts numeric input"""
    
    def __init__(self, parent, allow_negative=False, allow_decimal=False, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.allow_negative = allow_negative
        self.allow_decimal = allow_decimal
        
        # Register validation
        vcmd = (self.register(self._validate), '%P')
        self.configure(validate='key', validatecommand=vcmd)
    
    def _validate(self, value):
        """Validate numeric input"""
        if value == "":
            return True
        
        # Check for negative sign
        if self.allow_negative and value == "-":
            return True
        
        # Build regex pattern
        pattern = r'^'
        if self.allow_negative:
            pattern += r'-?'
        pattern += r'\d+'
        if self.allow_decimal:
            pattern += r'(\.\d*)?'
        pattern += r'$'
        
        return bool(re.match(pattern, value))
    
    def get_value(self) -> Optional[float]:
        """Get numeric value or None if empty/invalid"""
        value = self.get().strip()
        if not value:
            return None
        
        try:
            return float(value) if self.allow_decimal else int(value)
        except ValueError:
            return None