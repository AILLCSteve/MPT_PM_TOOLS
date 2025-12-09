"""
Script to create a branded version of CIPP analyzer with MPT styling.
"""

def brand_cipp_analyzer():
    input_file = r"C:\Users\pr0ph\Documents\AI LLC\Doc Analysis Projects\DeployedDocAnalysisForMPT\PM Tools Buildout\Bid-Spec Analysis for CIPP\cipp_analyzer_complete.html"
    output_file = r"C:\Users\pr0ph\Documents\AI LLC\Doc Analysis Projects\DeployedDocAnalysisForMPT\PM Tools Buildout\Bid-Spec Analysis for CIPP\cipp_analyzer_branded.html"

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace purple gradient with MPT brand colors
    content = content.replace('#667eea', '#5B7FCC')  # Accent blue
    content = content.replace('#764ba2', '#1E3A8A')  # Deep blue

    # Update the title
    content = content.replace('<title>CIPP Spec Analyzer - Complete</title>',
                            '<title>CIPP Analyzer - MPT Tools</title>')

    # Add MPT navbar CSS (insert before existing styles close)
    navbar_css = """
        /* MPT Navbar */
        .mpt-navbar {
            background: linear-gradient(135deg, #1E3A8A, #5B7FCC);
            padding: 15px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            margin-bottom: 20px;
        }

        .mpt-navbar .logo-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .mpt-navbar img {
            height: 40px;
            width: auto;
        }

        .mpt-navbar .app-title {
            color: white;
            font-size: 1.2rem;
            font-weight: 600;
        }

        .mpt-navbar .home-link {
            color: white;
            text-decoration: none;
            padding: 8px 20px;
            border: 2px solid white;
            border-radius: 5px;
            transition: all 0.3s;
            font-weight: 500;
        }

        .mpt-navbar .home-link:hover {
            background-color: white;
            color: #1E3A8A;
        }

        /* Update body to remove centering since we have navbar */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #5B7FCC 0%, #1E3A8A 100%);
            min-height: 100vh;
            padding: 0;
        }

        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 1000px;
            width: calc(100% - 40px);
            min-height: 600px;
            margin: 20px auto;
        }
"""

    # Insert navbar CSS before the closing </style> tag
    content = content.replace('    </style>', navbar_css + '    </style>')

    # Add MPT navbar HTML right after <body> tag
    navbar_html = """    <!-- MPT Navigation Bar -->
    <nav class="mpt-navbar">
        <div class="logo-container">
            <img src="/shared/assets/images/logo.png" alt="Municipal Pipe Tool">
            <span class="app-title">CIPP Analyzer</span>
        </div>
        <a href="/" class="home-link">← Home</a>
    </nav>

"""

    content = content.replace('<body>\n    <div class="container">', '<body>\n' + navbar_html + '    <div class="container">')

    # Write the branded version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Branded CIPP analyzer created at: {output_file}")
    print(f"   - Updated colors to MPT brand (#5B7FCC, #1E3A8A)")
    print(f"   - Added MPT navbar with logo and home button")
    print(f"   - Updated title to 'CIPP Analyzer - MPT Tools'")

if __name__ == '__main__':
    brand_cipp_analyzer()
