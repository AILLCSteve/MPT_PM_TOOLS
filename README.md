# PM Tools Suite - Project Management Tools

A comprehensive suite of professional tools for construction and infrastructure project management.

## 🚀 Features

### Available Tools

1. **CIPP Spec Analyzer** 🏗️
   - AI-powered analysis of CIPP (Cured-In-Place Pipe) project specifications
   - PDF text extraction and processing
   - Automated bid requirement identification
   - Project scope summarization

2. **Sewer Jetting Production Estimator** 📊
   - Calculate production rates for sewer cleaning/jetting operations
   - Advanced recycler efficiency modeling
   - Realization factor analysis with site-specific conditions
   - Time and cost savings projections

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Adding New Tools](#adding-new-tools)
- [Branding Customization](#branding-customization)
- [Troubleshooting](#troubleshooting)

## 🏁 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MPT_PM_TOOLS.git
   cd MPT_PM_TOOLS
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
PM Tools Buildout/
├── app.py                      # Main Flask application
├── gunicorn_config.py          # Production server config
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── claude.md                   # Engineering playbook
│
├── services/                   # Live microservices
│   ├── hotdog/                 # HOTDOG AI document analysis orchestrator
│   ├── cipp_dashboard/         # CIPP dashboard service with Dash/Plotly
│   ├── document_extractor.py   # Document extraction utilities
│   ├── excel_dashboard.py      # Excel dashboard generator
│   └── pdf_extractor.py        # PDF processing utilities
│
├── config/                     # Runtime configuration
│   ├── cipp_questions_default.json
│   └── model_config.json
│
├── shared/                     # Branding assets and shared resources
├── images/                     # Image assets
│
├── docs/                       # Documentation (organized)
│   ├── README.md               # Documentation index
│   ├── architecture/           # System architecture docs
│   ├── deployment/             # Deployment guides
│   ├── research/               # Research and analysis
│   └── sessions/               # Session summaries
│
├── scripts/                    # Utility scripts
├── outputs/                    # Runtime outputs (logs, spec files)
└── legacy/                     # Archived code (see legacy/LEGACY.md)
```

For detailed documentation, see [docs/README.md](docs/README.md).

## 💻 Local Development

### Running in Development Mode

```bash
# Enable debug mode
export DEBUG=true  # macOS/Linux
set DEBUG=true     # Windows

python app.py
```

### Testing Individual Tools

Each tool can be accessed directly:

- **Landing Page**: http://localhost:5000/
- **CIPP Analyzer**: http://localhost:5000/cipp-analyzer
- **Progress Estimator**: http://localhost:5000/progress-estimator
- **Health Check**: http://localhost:5000/health

### Code Quality

The codebase follows principles outlined in `claude.md`:
- **SOLID Principles** for maintainable architecture
- **Clean Code** practices with meaningful names and small functions
- **DRY** (Don't Repeat Yourself) to minimize duplication
- **KISS** (Keep It Simple, Stupid) for clarity
- **YAGNI** (You Aren't Gonna Need It) avoiding premature optimization

## 🌐 Deployment

### Deploying to Render

This application is configured for easy deployment to [Render.com](https://render.com).

#### Step 1: Prepare Repository

1. Initialize git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Push to GitHub/GitLab:
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

#### Step 2: Deploy on Render

1. Log in to [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Render will auto-detect the `render.yaml` configuration
5. Review and click "Create Web Service"

#### Step 3: Configure Environment

Set environment variables in Render dashboard:
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `SECRET_KEY` (auto-generated by Render)

#### Step 4: Deploy

- Render will automatically build and deploy
- Access your app at: `https://your-app-name.onrender.com`

### Alternative Deployment Options

#### Heroku
```bash
# Create Procfile
echo "web: gunicorn --bind 0.0.0.0:\$PORT app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### Docker
```bash
# Build image
docker build -t pm-tools-suite .

# Run container
docker run -p 5000:5000 pm-tools-suite
```

## 📁 Project Structure

```
PM Tools Buildout/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment config
├── index.html                      # Landing page
├── claude.md                       # Code quality guidelines
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── shared/                         # Shared assets
│   ├── assets/
│   │   ├── css/
│   │   │   └── common.css         # Shared styles
│   │   ├── images/
│   │   │   └── logo-placeholder.svg
│   │   └── js/
│   └── BRANDING_README.md         # Branding guide
│
├── Bid-Spec Analysis for CIPP/    # CIPP Analyzer tool
│   ├── cipp_analyzer_main.py      # Original version
│   ├── cipp_analyzer_complete.html
│   └── refactored/                # Improved version (SOLID principles)
│       ├── app.py
│       ├── config.py
│       ├── services/
│       │   └── pdf_extractor.py
│       ├── routes/
│       │   └── api.py
│       └── templates/
│
└── Progress Estimator/            # Progress Estimator tool
    ├── CleaningEstimateProto.html
    ├── script.js                  # Original version
    ├── styles.css                 # Original version
    ├── script_improved.js         # Enhanced with validation
    └── styles_improved.css        # Enhanced with CSS variables
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug mode | `false` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `SECRET_KEY` | Flask secret key for sessions | - | Yes (Production) |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `5000` | No |

### Customization

#### Update Configuration

Edit `app.py` Config class:
```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    # Add more configuration...
```

## 🔧 Adding New Tools

To add a new tool to the suite:

### 1. Create Tool Directory

```bash
mkdir "Your New Tool"
cd "Your New Tool"
```

### 2. Build Your Tool

Create your tool's files (HTML, CSS, JS, or Python backend).

### 3. Register Route in `app.py`

```python
@app.route('/your-new-tool')
def your_new_tool():
    """Serve Your New Tool application."""
    return send_from_directory(config.YOUR_TOOL_DIR, 'index.html')
```

### 4. Update Landing Page

Edit `index.html` to add a new tool card:

```html
<div class="tool-card">
    <div class="tool-icon">🔧</div>
    <span class="status-badge">✓ Available</span>
    <h2 class="tool-title">Your New Tool</h2>
    <p class="tool-description">Description of your tool...</p>
    <div class="tool-actions">
        <a href="/your-new-tool" class="btn btn-primary btn-lg">Launch Tool</a>
    </div>
</div>
```

### 5. Update Health Check

Add your tool to the health check endpoint in `app.py`:

```python
'tools': {
    'cipp_analyzer': 'available',
    'progress_estimator': 'available',
    'your_new_tool': 'available'
}
```

## 🎨 Branding Customization

### Update Logo

1. Replace `shared/assets/images/logo-placeholder.svg` with your logo
2. Supported formats: SVG (recommended), PNG with transparency
3. Recommended size: 200x60px or similar aspect ratio

### Update Colors

Edit `shared/assets/css/common.css`:

```css
:root {
    --brand-primary: #YourColor;
    --brand-secondary: #YourColor;
    --brand-accent: #YourColor;
}
```

### Update Company Name

Search and replace "PM Tools Suite" with your company name in:
- `index.html`
- `app.py`
- `README.md`

See `shared/BRANDING_README.md` for detailed branding guidelines.

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Change port in .env or command line
PORT=8000 python app.py
```

#### PDF Extraction Fails

Ensure PDF processing libraries are installed:
```bash
pip install PyPDF2 pdfplumber pdfminer.six
```

#### Static Files Not Loading

Check file paths match the directory structure. Verify:
- `static_folder` is correctly set in `app.py`
- Files exist in the expected locations

#### Import Errors

Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Logs

View application logs:
```bash
# Set log level
export LOG_LEVEL=DEBUG

# Run with verbose output
python app.py
```

### Health Check

Test application health:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "PM Tools Suite",
  "version": "1.0.0",
  "tools": {
    "cipp_analyzer": "available",
    "progress_estimator": "available"
  }
}
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Render Deployment Guide](https://render.com/docs)
- [SOLID Principles](claude.md) (included in this project)

## 🤝 Contributing

1. Follow code quality guidelines in `claude.md`
2. Write clean, documented code
3. Test locally before deploying
4. Use meaningful commit messages

## 📄 License

Copyright © 2025. All rights reserved.

## 📧 Support

For support, contact: support@example.com

---

**Built with ❤️ for project management professionals**
