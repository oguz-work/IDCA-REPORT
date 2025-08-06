# IDCA Security Assessment Report Visualizer

## Version 6.0 - Modular and Improved

A professional tool for converting IDCA (Incident Detection Capability Assessment) test results into high-quality visualizations for Word reports.

## Features

### 🎯 Core Features
- **Turkish Character Support**: Full support for Turkish characters (ç, ğ, ı, ö, ş, ü)
- **Professional Visualizations**: Generates 7 different charts and tables
- **Real-time Preview**: See your visualizations before generating
- **Data Validation**: Comprehensive input validation with helpful error messages
- **Modular Architecture**: Clean, maintainable code structure

### 🎨 Visual Features
- **6 Professional Themes**: Dark Professional, Light Modern, Blue Ocean, Purple Night, Green Forest, High Contrast
- **Transparent Background**: Perfect for Word documents
- **Customizable Dimensions**: Adjust figure size and DPI
- **Color-coded Results**: Automatic color coding based on performance

### 💾 Data Management
- **JSON Import/Export**: Save and load your work
- **Sample Data**: Quick start with example data
- **Auto-calculation**: Automatic calculation of derived values
- **Cross-field Validation**: Ensures data consistency

### 🔧 User Experience
- **Enhanced Tables**: Easy data entry with add/remove row functionality
- **Collapsible Sections**: Organized interface with expandable panels
- **Status Bar**: Real-time feedback and data status
- **Comprehensive Guide**: Built-in user manual

## Installation

### Requirements
- Python 3.8 or higher
- Operating System: Windows, macOS, or Linux

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- tkinter (usually comes with Python)
- matplotlib >= 3.5.0
- pandas >= 1.3.0
- numpy >= 1.21.0

### Quick Start

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### 1. General Information
Enter basic report information:
- Company/Organization name (required)
- Report date (required)
- Prepared by
- Report ID
- Report title
- Classification level

### 2. Test Results
Enter your test statistics:
- Total rules in the system
- Rules tested
- Rules that triggered alerts

The application automatically calculates:
- Not tested rules
- Failed rules
- Success rate
- Coverage rate

### 3. MITRE ATT&CK Mapping
For each MITRE tactic:
- Enter number of tests performed
- Enter number of successful triggers
- Success rates are calculated automatically

### 4. Rules Details
**Triggered Rules:**
- Rule name
- MITRE technique ID
- Associated tactic
- Confidence score (0-100%)

**Undetected Techniques:**
- MITRE technique ID
- Technique name
- Associated tactic
- Criticality level (Critical/High/Medium/Low)

### 5. Recommendations
Add actionable recommendations:
- Priority (auto-numbered)
- Category (dropdown selection)
- Recommendation text

### 6. Settings
**Visual Settings:**
- Figure width and height (inches)
- DPI (resolution)
- Transparent background option

**Theme Settings:**
- Choose from 6 professional themes
- Real-time color preview

**Output Settings:**
- Select output directory for generated images

## Generated Visualizations

1. **Figure 1 - Test Coverage Analysis**
   - Donut chart showing tested vs. not tested rules
   - Central display of total rules and success rate

2. **Figure 2 - Test Status Overview**
   - Bar chart of triggered vs. failed rules
   - Horizontal bar chart of lowest performing MITRE tactics

3. **Table 1 - Assessment Summary**
   - Key metrics with status indicators
   - Color-coded performance evaluation

4. **Table 2 - MITRE ATT&CK Coverage**
   - Detailed breakdown by tactic
   - Success rates and risk levels

5. **Table 3 - Triggered Rules List**
   - Successfully detected attack patterns
   - Confidence scores with color coding

6. **Table 4 - Undetected Techniques**
   - Critical gaps in detection
   - Priority-based sorting

7. **Table 5 - Recommendations**
   - Prioritized improvement suggestions
   - Categorized by type

## Tips for Best Results

### Data Entry
- Use Tab key to navigate between fields
- Validation errors appear in red below fields
- Save your work frequently using JSON export

### For Word Documents
1. Use transparent background option
2. Set DPI to 300 for print quality
3. Insert images as "In Line with Text"
4. Disable image compression in Word

### Theme Selection
- **Dark Professional**: Best for presentations
- **Light Modern**: Ideal for printed reports
- **Blue Ocean**: Corporate style
- **Purple Night**: Modern tech look
- **Green Forest**: Environmental reports
- **High Contrast**: Accessibility

## Project Structure

```
idca_visualizer/
├── main.py                 # Main application entry point
├── core/                   # Core functionality
│   ├── config.py          # Configuration and constants
│   └── visualizations.py  # Chart generation logic
├── data/                   # Data models and management
│   └── models.py          # Data structures with validation
├── themes/                 # Theme management
│   └── theme_manager.py   # Theme system
├── ui/                     # User interface components
│   └── widgets.py         # Custom UI widgets
├── utils/                  # Utility functions
│   └── validators.py      # Input validation
└── README.md              # This file
```

## Troubleshooting

### Common Issues

**Turkish characters not displaying:**
- Ensure your system locale supports Turkish
- The application automatically configures encoding

**Import errors:**
- Make sure all dependencies are installed
- Check Python version (3.8+)

**Visualization errors:**
- Verify all required data fields are filled
- Check for validation errors in red

**Memory issues with large datasets:**
- Close other applications
- Reduce DPI if needed

### Error Messages

- "Tested rules cannot exceed total rules" - Check your numbers
- "MITRE ID format invalid" - Use format like T1059.001
- "Confidence must be between 0 and 100" - Enter percentage without % sign

## Support

For bug reports or feature requests, please contact your IT administrator or the development team.

## License

This software is provided for authorized use only. All rights reserved.

## Changelog

### Version 6.0 (Current)
- Complete modular rewrite
- Enhanced UI with better widgets
- Improved theme system
- Better validation and error handling
- Fixed duplicate code issues
- Improved performance

### Version 5.0
- Added table-based data entry
- Turkish character support
- Multiple theme support
- Transparent background option

---

**Note**: This tool is designed specifically for IDCA security assessments. Ensure all data is handled according to your organization's security policies.