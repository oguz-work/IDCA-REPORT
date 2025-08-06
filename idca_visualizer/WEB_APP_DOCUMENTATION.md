# IDCA Visualizer Web Application Documentation

## Overview

The IDCA Visualizer Web Application is a modern, web-based interface for the IDCA Security Assessment Report Visualizer. It provides a complete solution for managing security assessment data, importing/exporting CSV files, and generating visualizations without requiring a desktop GUI.

## Features

### 1. **Web-Based Interface**
- Modern, responsive design using Bootstrap 5
- Tab-based navigation for different data sections
- Real-time validation and feedback
- Dark mode support

### 2. **Data Management**
- **General Information**: Company details, report metadata
- **Test Results**: Overall testing statistics with automatic coverage calculations
- **MITRE ATT&CK Tactics**: Track testing coverage across MITRE tactics
- **Triggered Rules**: Document detected security rules
- **Undetected Techniques**: Track gaps in detection coverage
- **Recommendations**: Prioritized security improvement suggestions

### 3. **CSV Import/Export**
- **Smart CSV Import**: 
  - Auto-detection of CSV delimiters
  - Intelligent field mapping suggestions
  - Visual mapping interface
  - Support for multiple CSV formats
- **Multi-file Export**: 
  - Separate CSV files for each data category
  - ZIP archive download
  - Preserves data structure and relationships

### 4. **Data Validation**
- MITRE ID format validation (T####, TA####)
- Numeric field validation
- Cross-field validation (e.g., triggered ≤ tested)
- Real-time success rate calculations
- Visual error indicators

### 5. **Visualizations**
- Test Coverage Chart
- MITRE ATT&CK Heatmap
- Severity Distribution
- Top Detection Gaps
- Summary Dashboard

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd idca_visualizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install flask
   ```

3. **Run the application**:
   ```bash
   python web_app.py
   ```

4. **Access the application**:
   - Open your browser and navigate to `http://localhost:5000`

## Usage Guide

### Data Entry

1. **General Information Tab**:
   - Enter company name, report date, and personnel information
   - All fields are optional but recommended for complete reports

2. **Test Results**:
   - Enter total number of security rules
   - Enter how many were tested
   - Enter how many triggered alerts
   - Coverage and success rates calculate automatically

3. **MITRE ATT&CK Tab**:
   - Click "Add Tactic" to add a new row
   - Enter tactic name, test count, and triggered count
   - Success rate calculates automatically
   - Color coding: Green (≥70%), Orange (40-69%), Red (<40%)

4. **Triggered Rules Tab**:
   - Add rules that successfully detected threats
   - Enter MITRE ID (format: T#### or T####.###)
   - Provide rule name and severity level

5. **Undetected Techniques Tab**:
   - Document techniques that weren't detected
   - Enter MITRE ID, technique name, and description

6. **Recommendations Tab**:
   - Add prioritized recommendations
   - Select priority level (Critical/High/Medium/Low)
   - Provide detailed description

### CSV Import

1. **Click "Import CSV" button** in the navigation bar

2. **Upload your CSV file**:
   - Drag and drop or browse for file
   - Supports comma, semicolon, tab, and pipe delimiters

3. **Map CSV columns**:
   - System suggests mappings automatically
   - Adjust mappings using dropdown menus
   - Select appropriate columns for each field

4. **Import data**:
   - Click "Import Data" to process
   - Data validates automatically
   - Existing data can be overwritten or appended

### CSV Export

1. **Click "Export CSV" button**
2. **Download ZIP file** containing:
   - `mitre_tactics.csv`: MITRE tactics with success rates
   - `triggered_rules.csv`: Detected security rules
   - `undetected_techniques.csv`: Coverage gaps
   - `recommendations.csv`: Improvement suggestions

### Visualizations

1. **Navigate to Visualizations tab**
2. **Select visualization type**:
   - **Test Coverage**: Pie chart of tested vs untested rules
   - **MITRE Heatmap**: Visual representation of tactic coverage
   - **Severity Distribution**: Bar chart of rule severities
   - **Top Gaps**: Most critical undetected techniques
   - **Summary Dashboard**: Complete overview

## API Reference

### Endpoints

#### `GET /api/data`
Retrieve all current data

#### `POST /api/data`
Update data (JSON format)

#### `POST /api/import/csv`
Import CSV file (multipart/form-data)

#### `GET /api/export/csv`
Export data as ZIP archive

#### `GET /api/visualizations/<type>`
Generate visualization (returns base64 image)

#### `POST /api/validate`
Validate specific field value

## Architecture

### Components

1. **Flask Backend** (`web_app.py`):
   - RESTful API endpoints
   - Data management
   - CSV processing
   - Visualization generation

2. **HTML/JavaScript Frontend** (`templates/index.html`):
   - Single-page application
   - Bootstrap UI components
   - AJAX data communication
   - Real-time validation

3. **CSV Handler** (`utils/csv_handler_web.py`):
   - CSV parsing and generation
   - Field mapping logic
   - Data validation

4. **Data Models** (`data/models.py`):
   - Structured data classes
   - Business logic
   - Validation rules

5. **Visualization Generator** (`core/visualizations.py`):
   - Matplotlib-based charts
   - Multiple visualization types
   - Theme support

## Troubleshooting

### Common Issues

1. **Import errors**:
   - Ensure Python path includes project directory
   - Check all dependencies are installed

2. **CSV import fails**:
   - Verify CSV format and encoding (UTF-8)
   - Check column headers match expected patterns
   - Ensure numeric fields contain valid numbers

3. **Visualizations not loading**:
   - Check matplotlib is installed
   - Verify data exists before generating
   - Check browser console for errors

4. **Data not saving**:
   - Ensure all required fields are filled
   - Check validation errors in UI
   - Verify server is running

### Debug Mode

Run with debug enabled:
```bash
python web_app.py
```

Check logs in `web_app.log` if running in background.

## Best Practices

1. **Data Entry**:
   - Complete all sections for comprehensive reports
   - Use consistent MITRE ID formats
   - Provide descriptive rule names

2. **CSV Import**:
   - Use header names that match field patterns
   - Ensure data types are correct
   - Validate data before import

3. **Performance**:
   - Limit table rows to reasonable numbers
   - Export large datasets in separate files
   - Use modern browsers for best experience

## Security Considerations

1. **Production Deployment**:
   - Change SECRET_KEY in web_app.py
   - Use HTTPS in production
   - Implement authentication if needed
   - Sanitize file uploads

2. **Data Protection**:
   - No data persists between sessions by default
   - Consider database for permanent storage
   - Implement access controls as needed

## Future Enhancements

- Database backend for data persistence
- User authentication and multi-tenancy
- Advanced filtering and search
- Report PDF generation
- API authentication
- Real-time collaboration features

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in browser console
3. Check server logs
4. Submit issues to project repository