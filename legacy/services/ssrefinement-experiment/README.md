# CIPP Dashboard Generator

A comprehensive web application for generating CIPP (Cured-In-Place Pipe) project dashboards with multiple visualization approaches.

## Features

### 📊 5 Summary Tables
- **Stage Footage Summary**: Overall progress tracking
- **Stage by Pipe Size**: Progress breakdown by diameter
- **Pipe Size Mix**: Resource allocation analysis
- **Length Bins**: Distribution of run lengths
- **Easement/Traffic Summary**: Operational constraints

### 📈 5 Interactive Visualizations
1. Overall progress by stage (100% stacked column)
2. Progress by pipe size (stacked bar)
3. Pipe size mix (clustered column)
4. Length distribution (histogram)
5. Easement & traffic control distribution

### 🎨 Three Excel Generation Approaches

#### Approach 1: openpyxl Native Charts
- **Best for**: Standard Excel workflows
- **Features**: Native Excel charts, fully interactive
- **Use case**: Daily project tracking, team collaboration

#### Approach 2: xlsxwriter Enhanced Charts
- **Best for**: Professional presentations
- **Features**: Superior formatting, enhanced styling, gradients
- **Use case**: Client reports, executive dashboards

#### Approach 3: Plotly Images
- **Best for**: Publication-quality visuals
- **Features**: Beautiful static images, modern design
- **Use case**: Reports, documentation, presentations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create necessary folders** (automatic on first run):
   - `uploads/` - Stores uploaded Excel files
   - `outputs/` - Stores generated Excel files

## Usage

### Running the Web Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Upload your Excel file**:
   - Click "Select Excel File"
   - Choose your CIPP shot schedule (.xlsx)
   - Click "Upload & Generate Dashboard"

4. **View results**:
   - Interactive web dashboard with live charts
   - Download Excel files with embedded visualizations
   - View all summary tables

### Using as a Python Module

```python
from data_processor import CIPPDataProcessor
from excel_generator import ExcelDashboardGenerator

# Process data
processor = CIPPDataProcessor("your_file.xlsx")
processor.load_data()

# Generate Excel files
generator = ExcelDashboardGenerator(processor)

# Approach 1: openpyxl native charts
generator.generate_approach_1("output_approach1.xlsx")

# Approach 2: xlsxwriter enhanced charts
generator.generate_approach_2("output_approach2.xlsx")

# Approach 3: plotly images
generator.generate_approach_3("output_approach3.xlsx")
```

## Excel File Requirements

Your input Excel file should have:

### Required Sheet
- Sheet name containing: "MOINES" or "SHOT" (case-insensitive)
- Example: "WEST DES MOINES, IA Shot Schedu"

### Required Columns
- **VIDEO ID**: Numeric segment identifier (≥ 1)
- **Line Segment**: Segment name/identifier
- **Pipe Size**: Pipe diameter
- **Map Length**: Segment length in feet
- **Prep Complete**: Boolean (TRUE/FALSE)
- **Ready to Line - Certified by Prep Crew Lead**: Boolean
- **Lining Date**: Date or blank
- **Final Post TV Date**: Date or blank
- **Grout State Date**: Date or blank
- **Easement**: Boolean (TRUE/FALSE)
- **Traffic Control**: Boolean (TRUE/FALSE)

### Stage Determination Logic
The system automatically calculates stage based on:
1. Grout State Date present → "Grouted/Done"
2. Final Post TV Date present → "Post TV Complete"
3. Lining Date present → "Lined"
4. Ready to Line = TRUE → "Ready to Line"
5. Prep Complete = TRUE → "Prep Complete"
6. Otherwise → "Not Started"

## Project Structure

```
ssREFINEMENT/
├── app.py                      # Flask web application
├── data_processor.py           # Core data processing logic
├── excel_generator.py          # Excel generation with 3 approaches
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── CLAUDE.md                   # Engineering guidelines
├── excelrefinement.txt         # Original requirements
├── templates/
│   ├── index.html             # Upload page
│   └── dashboard.html         # Dashboard display page
├── static/
│   └── css/
│       └── style.css          # Custom styling
├── uploads/                   # Uploaded files (auto-created)
└── outputs/                   # Generated files (auto-created)
```

## API Endpoints

- `GET /` - Upload page
- `POST /upload` - Handle file upload and processing
- `GET /dashboard/<session_id>` - Display dashboard
- `GET /api/charts/<session_id>/<approach>` - Get chart data
- `GET /api/tables/<session_id>` - Get table data
- `GET /download/<session_id>/<approach>` - Download Excel file

## Customization

### Modifying Length Bins

Edit `data_processor.py`:
```python
LENGTH_BINS = [
    {"label": "0–50", "min": 0, "max": 50},
    {"label": "51–150", "min": 51, "max": 150},
    # Add your custom bins here
]
```

### Changing Chart Colors

Edit chart generation functions in `excel_generator.py` or `app.py`.

### Adding New Tables

1. Add method to `CIPPDataProcessor` class
2. Update `get_all_tables()` method
3. Add table rendering in templates

## Troubleshooting

### "Sheet not found" Error
- Ensure your sheet name contains "MOINES" or "SHOT"
- Or update `sheet_name` parameter in `CIPPDataProcessor`

### "No valid segments found"
- Check that VIDEO ID ≥ 1
- Check that Map Length > 0
- Verify column headers match exactly

### Kaleido Installation Issues (Plotly Images)
Windows:
```bash
pip install kaleido==0.2.1 --force-reinstall
```

Linux/Mac:
```bash
pip install kaleido
```

### Charts not displaying
- Ensure JavaScript is enabled
- Check browser console for errors
- Try different visualization approach

## Performance Notes

- **File size limit**: 16MB (configurable in `app.py`)
- **Processing time**: ~1-3 seconds for typical files
- **Memory usage**: Minimal for files <1000 rows

## Security Notes

For production deployment:
1. Change `app.secret_key` in `app.py`
2. Use environment variables for configuration
3. Add authentication/authorization
4. Use proper database instead of in-memory storage
5. Implement file upload validation
6. Use HTTPS

## License

This project is provided as-is for internal use.

## Support

For issues or questions:
1. Check troubleshooting section
2. Review example Excel file format
3. Check browser console for errors
4. Verify all dependencies installed correctly

## Version History

- **v1.0.0** (2025-12-06)
  - Initial release
  - Three visualization approaches
  - Web-based dashboard
  - Excel export functionality
