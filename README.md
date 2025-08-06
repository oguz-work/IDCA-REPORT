# IDCA Security Assessment - Enhanced Report Visualizer v6.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/)

## 🎯 Overview

The IDCA (Intelligent Detection Coverage Assessment) Enhanced Report Visualizer is a professional tool designed to transform IDCA test results into high-quality visualizations for security reports and presentations. This modular, user-friendly application generates publication-ready charts and tables suitable for Word documents and PowerPoint presentations.

## ✨ Key Features

### 🆕 Version 6.0 Improvements

- **🏗️ Modular Architecture**: Clean, maintainable code structure
- **🎨 7 Professional Themes**: From light to dark, including specialized themes
- **📊 Advanced Table Editor**: Excel-like navigation and clipboard support
- **🔍 Real-time Data Validation**: Instant error checking and feedback
- **🌐 Full Turkish Character Support**: Complete Unicode support
- **⚡ Enhanced Performance**: Optimized rendering and processing
- **🔧 Improved User Experience**: Intuitive interface with better workflows

### 📈 Generated Visualizations

1. **Figure 1**: Test Suitability Pie Chart with success metrics
2. **Figure 2**: Test Status and MITRE Performance dual charts
3. **Table 1**: Results Assessment Matrix with target comparisons
4. **Table 2**: MITRE ATT&CK Coverage Analysis
5. **Table 3**: Triggered Correlation Rules List
6. **Table 4**: Undetected MITRE Techniques (prioritized)
7. **Table 5**: Security Improvement Recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB RAM minimum
- 100MB disk space

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/idca-enhanced.git
   cd idca-enhanced
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python idca_app.py
   ```

### Alternative: Run Original Version
```bash
python idca-final.py  # Original monolithic version (not recommended)
```

## 📦 Dependencies

Create a `requirements.txt` file with these dependencies:

```
tkinter>=8.6  # Usually comes with Python
matplotlib>=3.5.0
pandas>=1.3.0
numpy>=1.21.0
```

## 🎨 Theme System

### Available Themes

| Theme | Best For | Primary Color | Accent |
|-------|----------|---------------|--------|
| **Varsayılan** | General use | Dark Blue | Cyan |
| **Profesyonel** | Corporate reports | Navy | Purple |
| **Modern** | Tech presentations | Charcoal | Green |
| **Klasik** | Traditional docs | Blue-gray | Blue |
| **Açık** | Light backgrounds | White | Blue |
| **Koyu Mavi** | Technical reports | Deep Blue | Light Blue |
| **Yeşil Tema** | Security focus | Dark Green | Lime |

### Theme Features

- **Real-time Preview**: See changes instantly
- **Transparent Backgrounds**: Perfect for Word documents
- **Color-coded Performance**: Automatic success/warning/danger indicators
- **Consistent Typography**: Professional font hierarchy

## 📊 Data Entry Guide

### 1. General Information Tab 🏢
- **Required fields** marked with *
- Company name, report date, prepared by
- Full Turkish character support
- Auto-generated report IDs

### 2. Test Results Tab 📊
- **Automatic calculations** for derived metrics
- **Real-time validation** prevents invalid entries
- Visual indicators for success rates
- Performance benchmarking

### 3. MITRE ATT&CK Tab 🎯
- **Pre-loaded tactics** from MITRE framework
- Excel-like table navigation
- Auto-calculated success percentages
- Color-coded performance indicators

### 4. Rules Tab 📋
Two sub-tabs for comprehensive coverage:

#### ✅ Triggered Rules
- Rule name, MITRE technique, confidence scores
- Automatic confidence level color coding
- Supports up to 20 detailed entries

#### ❌ Undetected Techniques  
- MITRE ID, technique details, criticality levels
- Priority-based sorting
- Risk assessment integration

### 5. Recommendations Tab 💡
- **Auto-numbered priorities** (P1, P2, ...)
- Category selection from dropdown
- **Expandable rows** for detailed recommendations
- Impact level assessment

## 🔧 Advanced Features

### Table Editor Capabilities

#### Navigation
- **Tab**: Next cell
- **Shift+Tab**: Previous cell
- **Enter**: Same column, next row
- **Right-click**: Context menu

#### Data Management
- **Excel Integration**: Copy-paste from spreadsheets
- **Clipboard Support**: Tab-separated value import
- **Row Management**: Add/remove rows dynamically
- **Data Validation**: Real-time input checking

### Export Options

#### Visual Settings
- **Size**: 8-20 inches width/height
- **Resolution**: 100-600 DPI
- **Background**: Transparent or themed
- **Format**: PNG with lossless quality

#### File Management
- **JSON Storage**: Save/load complete sessions
- **Auto-backup**: Timestamp-based file naming
- **Metadata**: Version and creation info
- **Validation**: Data integrity checking

## 🖥️ User Interface

### Layout
- **Resizable Panels**: Adjust data entry vs preview ratio
- **Tabbed Interface**: Organized workflow
- **Status Indicators**: Real-time feedback
- **Progress Tracking**: Visual generation progress

### Accessibility
- **Keyboard Shortcuts**: Full keyboard navigation
- **High Contrast**: Support for accessibility needs
- **Scalable UI**: Responsive to different screen sizes
- **Multi-monitor**: Optimized for extended displays

## 📁 Project Structure

```
idca-enhanced/
├── config/
│   ├── __init__.py
│   └── themes.py           # Theme management
├── core/
│   ├── __init__.py
│   └── data_manager.py     # Data validation & storage
├── ui/
│   ├── __init__.py
│   └── components.py       # Enhanced UI components
├── visualization/
│   ├── __init__.py
│   └── chart_generator.py  # Chart & table generation
├── idca_app.py            # Main application (modular)
├── idca-final.py          # Original version (legacy)
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## 🔄 Migration from v5.0

If you're upgrading from the previous version:

1. **Export your data** from v5.0 using JSON format
2. **Install v6.0** following the installation guide
3. **Import your data** using the improved file loader
4. **Verify themes** and adjust if needed
5. **Regenerate visuals** to benefit from improvements

## 🐛 Troubleshooting

### Common Issues

#### Matplotlib Font Errors
```bash
# Clear matplotlib cache
rm -rf ~/.matplotlib
# Or on Windows
del /Q %USERPROFILE%\.matplotlib\*
```

#### Turkish Character Issues
- Ensure system locale supports UTF-8
- Check Python encoding settings
- Verify font availability

#### Memory Issues
- Close other applications
- Use smaller datasets for testing
- Check available disk space

#### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

### Performance Optimization

- **Limit table rows** to <50 for optimal performance
- **Use preview mode** before final generation
- **Close unused applications** during generation
- **Save work frequently** to prevent data loss

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black idca_app.py
flake8 --max-line-length=88 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Credits

### Development Team
- **Lead Developer**: Security Visualization Team
- **UI/UX Design**: User Experience Division
- **Quality Assurance**: Testing & Validation Team

### Special Thanks
- MITRE Corporation for ATT&CK framework
- Python community for excellent libraries
- Security professionals for feedback and testing

## 📞 Support

### Documentation
- **User Guide**: Built-in help system (📖 Kılavuz button)
- **Video Tutorials**: Available on project website
- **FAQ**: Common questions and solutions

### Contact
- **Issues**: Use GitHub Issues for bug reports
- **Features**: Submit feature requests via GitHub
- **Security**: Report security issues privately
- **General**: Contact development team

## 🚀 Roadmap

### Upcoming Features (v6.1)
- [ ] **Cloud Integration**: Save/load from cloud storage
- [ ] **Template System**: Pre-configured report templates
- [ ] **Batch Processing**: Process multiple assessments
- [ ] **API Integration**: Connect to SIEM platforms

### Future Enhancements (v7.0)
- [ ] **Web Interface**: Browser-based version
- [ ] **Collaboration**: Multi-user editing
- [ ] **Advanced Analytics**: Trend analysis
- [ ] **Mobile Support**: Tablet/phone compatibility

---

**Version**: 6.0.0  
**Last Updated**: January 2025  
**Minimum Python**: 3.8+  
**Status**: Production Ready  

*Transform your security assessments into professional visualizations! 🛡️*