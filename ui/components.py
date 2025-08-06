"""
IDCA Security Assessment - UI Components
========================================
Reusable UI components for the IDCA application.
"""

import tkinter as tk
from tkinter import ttk
import re

class ImprovedTableEntry(ttk.Frame):
    """Enhanced table widget with better UX for data entry"""
    
    def __init__(self, parent, columns, rows=10, validation_rules=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.columns = columns
        self.rows = rows
        self.entries = []
        self.validation_rules = validation_rules or {}
        self.header_labels = []
        
        self.create_table()
        self.setup_navigation()
        
    def create_table(self):
        """Create the table structure with headers and entries"""
        # Header frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Headers with better styling
        for j, col in enumerate(self.columns):
            label = ttk.Label(header_frame, text=col, font=('Arial', 10, 'bold'),
                            background='#34495e', foreground='white',
                            padding=(5, 8))
            label.grid(row=0, column=j, sticky='ew', padx=1)
            self.header_labels.append(label)
            header_frame.grid_columnconfigure(j, weight=1)
        
        # Scrollable content frame
        canvas = tk.Canvas(self, height=300)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create entry rows
        for i in range(self.rows):
            self.add_row_internal(i)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="➕ Satır Ekle", 
                  command=self.add_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🗑️ Son Satırı Sil", 
                  command=self.remove_last_row).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📋 Excel'den Yapıştır", 
                  command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🧹 Temizle", 
                  command=self.clear).pack(side=tk.RIGHT, padx=2)
    
    def add_row_internal(self, row_index):
        """Add a single row internally"""
        row_entries = []
        
        for j in range(len(self.columns)):
            # Create entry with validation
            entry = ttk.Entry(self.scrollable_frame, font=('Arial', 10), width=15)
            entry.grid(row=row_index, column=j, sticky='ew', padx=1, pady=1)
            
            # Add validation if specified
            col_name = self.columns[j]
            if col_name in self.validation_rules:
                self.add_validation(entry, self.validation_rules[col_name])
            
            # Add context menu
            self.add_context_menu(entry)
            
            row_entries.append(entry)
        
        # Configure column weights
        for j in range(len(self.columns)):
            self.scrollable_frame.grid_columnconfigure(j, weight=1)
        
        if len(self.entries) > row_index:
            self.entries[row_index] = row_entries
        else:
            self.entries.append(row_entries)
    
    def add_validation(self, entry, validation_type):
        """Add validation to an entry widget"""
        def validate_input(event):
            value = entry.get()
            if validation_type == 'numeric':
                if value and not value.isdigit():
                    entry.configure(style='Invalid.TEntry')
                    return False
                else:
                    entry.configure(style='TEntry')
            elif validation_type == 'percentage':
                if value and not (value.replace('%', '').replace('.', '').isdigit()):
                    entry.configure(style='Invalid.TEntry')
                    return False
                else:
                    entry.configure(style='TEntry')
            return True
        
        entry.bind('<KeyRelease>', validate_input)
    
    def add_context_menu(self, entry):
        """Add right-click context menu to entry"""
        context_menu = tk.Menu(entry, tearoff=0)
        context_menu.add_command(label="Kes", command=lambda: entry.event_generate("<<Cut>>"))
        context_menu.add_command(label="Kopyala", command=lambda: entry.event_generate("<<Copy>>"))
        context_menu.add_command(label="Yapıştır", command=lambda: entry.event_generate("<<Paste>>"))
        context_menu.add_separator()
        context_menu.add_command(label="Temizle", command=lambda: entry.delete(0, tk.END))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        entry.bind("<Button-3>", show_context_menu)  # Right click
    
    def setup_navigation(self):
        """Set up keyboard navigation between cells"""
        def on_tab(event):
            # Find current widget
            current = event.widget
            for i, row in enumerate(self.entries):
                for j, entry in enumerate(row):
                    if entry == current:
                        # Move to next cell
                        if j < len(row) - 1:
                            row[j + 1].focus()
                        elif i < len(self.entries) - 1:
                            self.entries[i + 1][0].focus()
                        return "break"
        
        def on_shift_tab(event):
            # Find current widget and move to previous cell
            current = event.widget
            for i, row in enumerate(self.entries):
                for j, entry in enumerate(row):
                    if entry == current:
                        if j > 0:
                            row[j - 1].focus()
                        elif i > 0:
                            self.entries[i - 1][-1].focus()
                        return "break"
        
        def on_enter(event):
            # Move to next row, same column
            current = event.widget
            for i, row in enumerate(self.entries):
                for j, entry in enumerate(row):
                    if entry == current and i < len(self.entries) - 1:
                        self.entries[i + 1][j].focus()
                        return "break"
        
        # Bind navigation events
        for row in self.entries:
            for entry in row:
                entry.bind('<Tab>', on_tab)
                entry.bind('<Shift-Tab>', on_shift_tab)
                entry.bind('<Return>', on_enter)
    
    def get_data(self):
        """Get table data as list of lists"""
        data = []
        for row in self.entries:
            row_data = [entry.get().strip() for entry in row]
            if any(row_data):  # Include row if any cell has data
                data.append(row_data)
        return data
    
    def set_data(self, data):
        """Set table data from list of lists"""
        # Clear existing data
        self.clear()
        
        # Add more rows if needed
        while len(self.entries) < len(data):
            self.add_row()
        
        # Fill data
        for i, row_data in enumerate(data):
            if i < len(self.entries):
                for j, value in enumerate(row_data):
                    if j < len(self.entries[i]):
                        self.entries[i][j].delete(0, tk.END)
                        self.entries[i][j].insert(0, str(value))
    
    def clear(self):
        """Clear all data in the table"""
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)
    
    def add_row(self):
        """Add a new row to the table"""
        new_row_index = len(self.entries)
        self.add_row_internal(new_row_index)
        
        # Update navigation bindings
        self.setup_navigation()
    
    def remove_last_row(self):
        """Remove the last row from the table"""
        if len(self.entries) > 1:
            # Destroy widgets in last row
            for entry in self.entries[-1]:
                entry.destroy()
            # Remove from entries list
            self.entries.pop()
    
    def paste_from_clipboard(self):
        """Paste tab-separated data from clipboard"""
        try:
            clipboard_data = self.clipboard_get()
            lines = clipboard_data.strip().split('\n')
            
            # Add more rows if needed
            while len(self.entries) < len(lines):
                self.add_row()
            
            # Parse and fill data
            for i, line in enumerate(lines):
                if i < len(self.entries):
                    cells = line.split('\t')
                    for j, cell_value in enumerate(cells):
                        if j < len(self.entries[i]):
                            self.entries[i][j].delete(0, tk.END)
                            self.entries[i][j].insert(0, cell_value.strip())
            
        except tk.TclError:
            pass  # Clipboard is empty or invalid


class StatusIndicator(ttk.Frame):
    """Status indicator with color coding and animation"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_label = ttk.Label(self, text="●", font=('Arial', 16))
        self.status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.text_label = ttk.Label(self, text="Hazır", font=('Arial', 10))
        self.text_label.pack(side=tk.LEFT)
        
    def set_status(self, status, text, color='gray'):
        """Set status with text and color"""
        self.status_label.configure(foreground=color)
        self.text_label.configure(text=text)
        
        # Add simple animation
        if status == 'working':
            self.animate_working()
    
    def animate_working(self):
        """Simple animation for working status"""
        current_text = self.status_label.cget('text')
        if current_text == "●":
            self.status_label.configure(text="○")
        else:
            self.status_label.configure(text="●")
        
        # Continue animation if still working
        if self.text_label.cget('text').startswith('İşleniyor'):
            self.after(500, self.animate_working)


class ProgressDialog(tk.Toplevel):
    """Enhanced progress dialog with better UX"""
    
    def __init__(self, parent, title="İşlem Yapılıyor", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title(title)
        self.geometry("500x300")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + (parent.winfo_width() // 2) - 250,
            parent.winfo_rooty() + (parent.winfo_height() // 2) - 150
        ))
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create progress dialog widgets"""
        # Header
        header_frame = ttk.Frame(self, padding=20)
        header_frame.pack(fill=tk.X)
        
        self.title_label = ttk.Label(header_frame, text="İşlem Başlıyor...", 
                                   font=('Arial', 14, 'bold'))
        self.title_label.pack()
        
        self.subtitle_label = ttk.Label(header_frame, text="", 
                                      font=('Arial', 10), foreground='gray')
        self.subtitle_label.pack(pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.Frame(self, padding=20)
        progress_frame.pack(fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", font=('Arial', 10))
        self.progress_label.pack()
        
        # Details section
        details_frame = ttk.LabelFrame(self, text="Detaylar", padding=15)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable text widget for details
        text_frame = ttk.Frame(details_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.details_text = tk.Text(text_frame, height=6, wrap=tk.WORD, 
                                   font=('Arial', 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                command=self.details_text.yview)
        
        self.details_text.configure(yscrollcommand=scrollbar.set)
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        button_frame = ttk.Frame(self, padding=20)
        button_frame.pack(fill=tk.X)
        
        self.close_button = ttk.Button(button_frame, text="Kapat", 
                                     command=self.destroy, state=tk.DISABLED)
        self.close_button.pack(side=tk.RIGHT)
        
    def update_progress(self, current, total, title="", detail=""):
        """Update progress bar and labels"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar['value'] = percentage
            self.progress_label.configure(text=f"{percentage:.1f}% ({current}/{total})")
        
        if title:
            self.title_label.configure(text=title)
        
        if detail:
            self.add_detail(detail)
        
        self.update()
    
    def add_detail(self, text):
        """Add detail text to the log"""
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.insert(tk.END, f"• {text}\n")
        self.details_text.see(tk.END)
        self.details_text.configure(state=tk.DISABLED)
    
    def set_complete(self, title="Tamamlandı!", enable_close=True):
        """Mark the operation as complete"""
        self.title_label.configure(text=title)
        self.progress_bar['value'] = 100
        self.progress_label.configure(text="100%")
        
        if enable_close:
            self.close_button.configure(state=tk.NORMAL)
    
    def set_error(self, error_message):
        """Mark the operation as failed"""
        self.title_label.configure(text="Hata Oluştu!")
        self.subtitle_label.configure(text=error_message, foreground='red')
        self.close_button.configure(state=tk.NORMAL)