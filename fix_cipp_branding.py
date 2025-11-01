"""
Script to properly brand CIPP analyzer with MPT styling - matching ProgEstimator approach.
"""

def fix_cipp_branding():
    input_file = r"C:\Users\pr0ph\Documents\AI LLC\Doc Analysis Projects\DeployedDocAnalysisForMPT\PM Tools Buildout\Bid-Spec Analysis for CIPP\cipp_analyzer_complete.html"
    output_file = r"C:\Users\pr0ph\Documents\AI LLC\Doc Analysis Projects\DeployedDocAnalysisForMPT\PM Tools Buildout\Bid-Spec Analysis for CIPP\cipp_analyzer_branded.html"

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update title
    content = content.replace(
        '<title>CIPP Spec Analyzer - Complete</title>',
        '<title>CIPP Bid-Spec Analyzer - MPT Tools</title>'
    )

    # 2. Replace purple colors with MPT brand colors
    content = content.replace('#667eea', '#5B7FCC')
    content = content.replace('#764ba2', '#1E3A8A')

    # 3. Update the header text
    content = content.replace(
        '<h1>🏗️ CIPP Spec Analyzer</h1>',
        '<h1>🏗️ CIPP Bid-Spec Analyzer</h1>'
    )
    content = content.replace(
        '<p>Complete Version - PDF Service + Stop Functionality + All Features</p>',
        '<p>Professional bid specification analysis powered by AI</p>'
    )

    # 4. Fix body styling - remove centering, add padding at top
    old_body_style = """        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #5B7FCC 0%, #1E3A8A 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }"""

    new_body_style = """        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #5B7FCC 0%, #1E3A8A 100%);
            min-height: 100vh;
            padding: 0;
        }"""

    content = content.replace(old_body_style, new_body_style)

    # 5. Update container to have margin instead of being centered by flexbox
    old_container_style = """        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 1000px;
            width: 100%;
            min-height: 600px;
        }"""

    new_container_style = """        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 1000px;
            width: calc(100% - 40px);
            min-height: 600px;
            margin: 20px auto;
        }"""

    content = content.replace(old_container_style, new_container_style)

    # 6. Add MPT navbar CSS before closing </style>
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
            margin-bottom: 0;
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

        /* Mobile responsive for navbar */
        @media (max-width: 768px) {
            .mpt-navbar {
                flex-direction: column;
                gap: 15px;
                padding: 15px;
            }
        }
"""

    content = content.replace('    </style>', navbar_css + '    </style>')

    # 7. Add navbar HTML after <body> tag
    navbar_html = """    <!-- MPT Navigation Bar -->
    <nav class="mpt-navbar">
        <div class="logo-container">
            <img src="/shared/assets/images/logo.png" alt="Municipal Pipe Tool">
            <span class="app-title">CIPP Bid-Spec Analyzer</span>
        </div>
        <a href="/" class="home-link">← Home</a>
    </nav>

"""

    content = content.replace('<body>\n    <div class="container">', '<body>\n' + navbar_html + '    <div class="container">')

    # 8. Set default API key in the JavaScript section
    api_key = ''  # User must provide their own OpenAI API key

    # Find and replace the API key placeholder
    content = content.replace(
        "let apiKey = '';",
        f"let apiKey = '{api_key}';"
    )

    # Write the branded version
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Branded CIPP Bid-Spec analyzer created successfully!")
    print("- Updated colors to MPT brand")
    print("- Added MPT navbar with logo and home button")
    print("- Fixed layout (no longer centered incorrectly)")
    print("- Updated title to 'CIPP Bid-Spec Analyzer - MPT Tools'")
    print("- Configured OpenAI API key")

if __name__ == '__main__':
    fix_cipp_branding()
