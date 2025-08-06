"""
IDCA Security Assessment - Theme and Color Configuration
========================================================
This module contains all theme and color definitions for the application.
"""

class ThemeManager:
    """Manages themes and color schemes for the IDCA application"""
    
    def __init__(self):
        self.current_theme = 'Varsayılan'
        
        # Define all available themes
        self.themes = {
            'Varsayılan': {
                'primary': '#0F172A',
                'secondary': '#1E293B', 
                'accent': '#00D9FF',
                'accent_secondary': '#7C3AED',
                'success': '#10B981',
                'warning': '#F59E0B',
                'danger': '#EF4444',
                'dark': '#020617',
                'light': '#F8FAFC',
                'gray': '#64748B',
                'text': '#FFFFFF',
                'text_secondary': '#CBD5E1'
            },
            'Profesyonel': {
                'primary': '#1a1a2e',
                'secondary': '#16213e',
                'accent': '#0f3460',
                'accent_secondary': '#533483',
                'success': '#53c653',
                'warning': '#e94560',
                'danger': '#ff1744',
                'dark': '#0f0f0f',
                'light': '#eaeaea',
                'gray': '#7a7a7a',
                'text': '#FFFFFF',
                'text_secondary': '#CCCCCC'
            },
            'Modern': {
                'primary': '#2d3436',
                'secondary': '#636e72',
                'accent': '#00b894',
                'accent_secondary': '#6c5ce7',
                'success': '#55efc4',
                'warning': '#fdcb6e',
                'danger': '#ff7675',
                'dark': '#2d3436',
                'light': '#dfe6e9',
                'gray': '#b2bec3',
                'text': '#FFFFFF',
                'text_secondary': '#DFE6E9'
            },
            'Klasik': {
                'primary': '#2c3e50',
                'secondary': '#34495e',
                'accent': '#3498db',
                'accent_secondary': '#9b59b6',
                'success': '#2ecc71',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'dark': '#1a1a1a',
                'light': '#ecf0f1',
                'gray': '#95a5a6',
                'text': '#FFFFFF',
                'text_secondary': '#ECF0F1'
            },
            'Açık': {
                'primary': '#ffffff',
                'secondary': '#f5f5f5',
                'accent': '#2196F3',
                'accent_secondary': '#673AB7',
                'success': '#4CAF50',
                'warning': '#FF9800',
                'danger': '#F44336',
                'dark': '#ffffff',
                'light': '#212121',
                'gray': '#757575',
                'text': '#212121',
                'text_secondary': '#757575'
            },
            'Koyu Mavi': {
                'primary': '#0c1a2b',
                'secondary': '#1e3a8a',
                'accent': '#3b82f6',
                'accent_secondary': '#8b5cf6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'dark': '#030712',
                'light': '#f1f5f9',
                'gray': '#64748b',
                'text': '#FFFFFF',
                'text_secondary': '#CBD5E1'
            },
            'Yeşil Tema': {
                'primary': '#0f2419',
                'secondary': '#166534',
                'accent': '#22c55e',
                'accent_secondary': '#84cc16',
                'success': '#15803d',
                'warning': '#f59e0b',
                'danger': '#dc2626',
                'dark': '#052e16',
                'light': '#f0fdf4',
                'gray': '#6b7280',
                'text': '#FFFFFF',
                'text_secondary': '#D1FAE5'
            }
        }
        
        # Set default colors
        self.colors = self.themes[self.current_theme].copy()
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.colors = self.themes[theme_name].copy()
            return True
        return False
    
    def get_current_colors(self):
        """Get current theme colors"""
        return self.colors.copy()
    
    def get_current_theme_name(self):
        """Get current theme name"""
        return self.current_theme
    
    def get_color_for_state(self, state):
        """Get appropriate color for different states"""
        color_mapping = {
            'excellent': self.colors['success'],
            'good': self.colors['accent'],
            'warning': self.colors['warning'],
            'critical': self.colors['danger'],
            'info': self.colors['accent_secondary'],
            'neutral': self.colors['gray']
        }
        return color_mapping.get(state, self.colors['gray'])
    
    def get_performance_color(self, percentage):
        """Get color based on performance percentage"""
        if percentage >= 80:
            return self.colors['success']
        elif percentage >= 60:
            return self.colors['accent']
        elif percentage >= 40:
            return self.colors['warning']
        else:
            return self.colors['danger']