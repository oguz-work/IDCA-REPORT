#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme Manager for IDCA Visualizer
Handles color schemes and visual themes
"""

from typing import Dict, Any
import json
from pathlib import Path


class Theme:
    """Represents a visual theme with color definitions"""
    
    def __init__(self, name: str, colors: Dict[str, str], description: str = ""):
        self.name = name
        self.colors = colors
        self.description = description
    
    def get_color(self, key: str, default: str = "#000000") -> str:
        """Get a color value by key with fallback"""
        return self.colors.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary"""
        return {
            'name': self.name,
            'colors': self.colors,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """Create theme from dictionary"""
        return cls(
            name=data.get('name', 'Custom'),
            colors=data.get('colors', {}),
            description=data.get('description', '')
        )


class ThemeManager:
    """Manages application themes"""
    
    # Default themes with improved color schemes
    DEFAULT_THEMES = {
        'Dark Professional': Theme(
            name='Dark Professional',
            colors={
                'primary': '#1a1a1a',
                'secondary': '#2d2d2d',
                'accent': '#00a8ff',
                'accent_secondary': '#7c3aed',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#ef4444',
                'info': '#3b82f6',
                'dark': '#0a0a0a',
                'light': '#f3f4f6',
                'gray': '#6b7280',
                'border': '#374151',
                'text_primary': '#f3f4f6',
                'text_secondary': '#9ca3af',
                'background': '#111111',
                'surface': '#1f2937',
                'hover': '#374151'
            },
            description='Professional dark theme for reduced eye strain'
        ),
        
        'Light Modern': Theme(
            name='Light Modern',
            colors={
                'primary': '#ffffff',
                'secondary': '#f9fafb',
                'accent': '#2563eb',
                'accent_secondary': '#7c3aed',
                'success': '#16a34a',
                'warning': '#ea580c',
                'danger': '#dc2626',
                'info': '#0891b2',
                'dark': '#1f2937',
                'light': '#ffffff',
                'gray': '#6b7280',
                'border': '#e5e7eb',
                'text_primary': '#111827',
                'text_secondary': '#6b7280',
                'background': '#ffffff',
                'surface': '#f9fafb',
                'hover': '#f3f4f6'
            },
            description='Clean light theme for daytime use'
        ),
        
        'Blue Ocean': Theme(
            name='Blue Ocean',
            colors={
                'primary': '#0f172a',
                'secondary': '#1e293b',
                'accent': '#0ea5e9',
                'accent_secondary': '#06b6d4',
                'success': '#10b981',
                'warning': '#f59e0b',
                'danger': '#f43f5e',
                'info': '#6366f1',
                'dark': '#020617',
                'light': '#f1f5f9',
                'gray': '#64748b',
                'border': '#334155',
                'text_primary': '#f1f5f9',
                'text_secondary': '#94a3b8',
                'background': '#0f172a',
                'surface': '#1e293b',
                'hover': '#334155'
            },
            description='Ocean-inspired blue theme'
        ),
        
        'Purple Night': Theme(
            name='Purple Night',
            colors={
                'primary': '#1a1625',
                'secondary': '#2a2438',
                'accent': '#a855f7',
                'accent_secondary': '#c084fc',
                'success': '#22c55e',
                'warning': '#eab308',
                'danger': '#ef4444',
                'info': '#8b5cf6',
                'dark': '#0f0d15',
                'light': '#f5f3ff',
                'gray': '#9089a8',
                'border': '#3f3854',
                'text_primary': '#f5f3ff',
                'text_secondary': '#c4b5fd',
                'background': '#1a1625',
                'surface': '#2a2438',
                'hover': '#3f3854'
            },
            description='Elegant purple theme for night work'
        ),
        
        'Green Forest': Theme(
            name='Green Forest',
            colors={
                'primary': '#14532d',
                'secondary': '#166534',
                'accent': '#22c55e',
                'accent_secondary': '#4ade80',
                'success': '#16a34a',
                'warning': '#facc15',
                'danger': '#dc2626',
                'info': '#0891b2',
                'dark': '#052e16',
                'light': '#f0fdf4',
                'gray': '#86efac',
                'border': '#15803d',
                'text_primary': '#f0fdf4',
                'text_secondary': '#bbf7d0',
                'background': '#14532d',
                'surface': '#166534',
                'hover': '#15803d'
            },
            description='Nature-inspired green theme'
        ),
        
        'High Contrast': Theme(
            name='High Contrast',
            colors={
                'primary': '#000000',
                'secondary': '#1a1a1a',
                'accent': '#ffff00',
                'accent_secondary': '#00ffff',
                'success': '#00ff00',
                'warning': '#ff9500',
                'danger': '#ff0000',
                'info': '#0080ff',
                'dark': '#000000',
                'light': '#ffffff',
                'gray': '#808080',
                'border': '#ffffff',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'background': '#000000',
                'surface': '#1a1a1a',
                'hover': '#333333'
            },
            description='High contrast theme for accessibility'
        )
    }
    
    def __init__(self, themes_dir: Path = None):
        self.themes_dir = themes_dir or Path(__file__).parent
        self.themes = self.DEFAULT_THEMES.copy()
        self.current_theme = self.themes['Dark Professional']
        self._load_custom_themes()
    
    def _load_custom_themes(self):
        """Load custom themes from JSON files"""
        custom_themes_file = self.themes_dir / 'custom_themes.json'
        if custom_themes_file.exists():
            try:
                with open(custom_themes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for theme_data in data.get('themes', []):
                        theme = Theme.from_dict(theme_data)
                        self.themes[theme.name] = theme
            except Exception as e:
                print(f"Error loading custom themes: {e}")
    
    def save_custom_themes(self):
        """Save custom themes to JSON file"""
        custom_themes = {
            name: theme.to_dict() 
            for name, theme in self.themes.items() 
            if name not in self.DEFAULT_THEMES
        }
        
        custom_themes_file = self.themes_dir / 'custom_themes.json'
        try:
            with open(custom_themes_file, 'w', encoding='utf-8') as f:
                json.dump({'themes': list(custom_themes.values())}, f, indent=2)
        except Exception as e:
            print(f"Error saving custom themes: {e}")
    
    def get_theme(self, name: str) -> Theme:
        """Get a theme by name"""
        return self.themes.get(name, self.current_theme)
    
    def set_current_theme(self, name: str) -> bool:
        """Set the current theme"""
        if name in self.themes:
            self.current_theme = self.themes[name]
            return True
        return False
    
    def add_custom_theme(self, theme: Theme) -> bool:
        """Add a custom theme"""
        if theme.name not in self.DEFAULT_THEMES:
            self.themes[theme.name] = theme
            self.save_custom_themes()
            return True
        return False
    
    def remove_custom_theme(self, name: str) -> bool:
        """Remove a custom theme"""
        if name in self.themes and name not in self.DEFAULT_THEMES:
            del self.themes[name]
            self.save_custom_themes()
            return True
        return False
    
    def get_theme_names(self) -> list:
        """Get list of all theme names"""
        return list(self.themes.keys())
    
    def get_color(self, key: str, default: str = "#000000") -> str:
        """Get a color from the current theme"""
        return self.current_theme.get_color(key, default)
    
    def get_matplotlib_colors(self) -> Dict[str, Any]:
        """Get colors formatted for matplotlib"""
        return {
            'figure.facecolor': 'none',  # Transparent by default
            'axes.facecolor': 'none',
            'axes.edgecolor': self.get_color('border'),
            'axes.labelcolor': self.get_color('text_primary'),
            'text.color': self.get_color('text_primary'),
            'xtick.color': self.get_color('text_secondary'),
            'ytick.color': self.get_color('text_secondary'),
            'grid.color': self.get_color('gray'),
            'legend.facecolor': self.get_color('surface'),
            'legend.edgecolor': self.get_color('border')
        }
    
    def apply_to_matplotlib(self, transparent: bool = True):
        """Apply current theme to matplotlib"""
        import matplotlib.pyplot as plt
        
        colors = self.get_matplotlib_colors()
        if not transparent:
            colors['figure.facecolor'] = self.get_color('background')
            colors['axes.facecolor'] = self.get_color('surface')
        
        for key, value in colors.items():
            plt.rcParams[key] = value