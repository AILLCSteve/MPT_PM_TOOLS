"""
Flask web application for CIPP Dashboard Generator.
Allows file upload, processing, and interactive web-based visualization.
"""

from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from data_processor import CIPPDataProcessor
from excel_generator import ExcelDashboardGenerator

app = Flask(__name__)
app.secret_key = 'cipp-dashboard-secret-key-2025'  # Change in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Store processed data in memory (use Redis/DB in production)
processed_data = {}


@app.route('/')
def index():
    """Main upload page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Only .xlsx files are supported'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Process data
        processor = CIPPDataProcessor(filepath)
        processor.load_data()

        # Get all tables
        tables = processor.get_all_tables()

        # Store in session
        session_id = timestamp
        processed_data[session_id] = {
            'processor': processor,
            'tables': tables,
            'filepath': filepath,
            'filename': filename
        }

        # Generate Excel files with all 3 approaches
        generator = ExcelDashboardGenerator(processor)

        output_files = {
            'approach1': os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_approach1.xlsx"),
            'approach2': os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_approach2.xlsx"),
            'approach3': os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}_approach3.xlsx")
        }

        try:
            generator.generate_approach_1(output_files['approach1'])
        except Exception as e:
            print(f"Approach 1 failed: {e}")
            output_files['approach1'] = None

        try:
            generator.generate_approach_2(output_files['approach2'])
        except Exception as e:
            print(f"Approach 2 failed: {e}")
            output_files['approach2'] = None

        try:
            generator.generate_approach_3(output_files['approach3'])
        except Exception as e:
            print(f"Approach 3 failed: {e}")
            output_files['approach3'] = None

        processed_data[session_id]['output_files'] = output_files

        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_segments': len(processor.segments),
            'total_footage': processor.total_footage,
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Display interactive dashboard."""
    if session_id not in processed_data:
        return "Session not found. Please upload a file first.", 404

    data = processed_data[session_id]
    return render_template('dashboard.html',
                           session_id=session_id,
                           filename=data['filename'],
                           total_segments=len(data['processor'].segments),
                           total_footage=data['processor'].total_footage)


@app.route('/api/charts/<session_id>/<approach>')
def get_charts(session_id, approach):
    """Generate charts for web display based on selected approach."""
    if session_id not in processed_data:
        return jsonify({'error': 'Session not found'}), 404

    data = processed_data[session_id]
    processor = data['processor']
    tables = data['tables']

    try:
        if approach == 'plotly':
            charts = generate_plotly_charts(processor, tables)
        elif approach == 'chartjs':
            charts = generate_chartjs_data(processor, tables)
        else:
            charts = generate_plotly_charts(processor, tables)

        return jsonify(charts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables/<session_id>')
def get_tables(session_id):
    """Get all table data."""
    if session_id not in processed_data:
        return jsonify({'error': 'Session not found'}), 404

    data = processed_data[session_id]
    return jsonify(data['tables'])


@app.route('/download/<session_id>/<approach>')
def download_file(session_id, approach):
    """Download generated Excel file."""
    if session_id not in processed_data:
        return "Session not found", 404

    data = processed_data[session_id]
    output_files = data.get('output_files', {})

    filepath = output_files.get(approach)
    if not filepath or not os.path.exists(filepath):
        return f"File for {approach} not available", 404

    return send_file(filepath, as_attachment=True,
                     download_name=f"CIPP_Dashboard_{approach}.xlsx")


def generate_plotly_charts(processor, tables):
    """Generate Plotly charts (Approach 3 - Interactive Web)."""
    charts = {}

    # Chart 1: Overall Progress
    table1 = tables["stage_footage_summary"]
    fig1 = go.Figure(data=[
        go.Bar(
            x=[r["Stage"] for r in table1],
            y=[r["Total_Feet"] for r in table1],
            text=[f"{r['Pct_of_Total_Feet']*100:.1f}%" for r in table1],
            textposition='auto',
            marker_color='#4472C4',
            hovertemplate='<b>%{x}</b><br>Feet: %{y:,.0f}<br>Percentage: %{text}<extra></extra>'
        )
    ])
    fig1.update_layout(
        title="Overall Progress by Stage",
        xaxis_title="Stage",
        yaxis_title="Total Feet",
        template="plotly_white",
        height=400,
        hovermode='closest'
    )
    charts['chart1'] = json.loads(json.dumps(fig1, cls=PlotlyJSONEncoder))

    # Chart 2: Progress by Pipe Size (stacked)
    table2 = tables["stage_by_pipe_size"]
    fig2 = go.Figure()

    colors = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5', '#70AD47']
    for idx, stage in enumerate(processor.STAGES):
        fig2.add_trace(go.Bar(
            name=stage,
            y=[str(r["Pipe Size"]) for r in table2],
            x=[r[stage] for r in table2],
            orientation='h',
            marker_color=colors[idx % len(colors)],
            hovertemplate=f'<b>{stage}</b><br>Feet: %{{x:,.0f}}<extra></extra>'
        ))

    fig2.update_layout(
        barmode='stack',
        title="Progress by Pipe Size",
        xaxis_title="Feet",
        yaxis_title="Pipe Size",
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    charts['chart2'] = json.loads(json.dumps(fig2, cls=PlotlyJSONEncoder))

    # Chart 3: Pipe Size Mix
    table3 = tables["pipe_size_mix"]
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        name='Segment Count',
        x=[str(r["Pipe Size"]) for r in table3],
        y=[r["Segment_Count"] for r in table3],
        marker_color='#4472C4',
        hovertemplate='<b>Count</b><br>Segments: %{y}<extra></extra>'
    ))

    fig3.add_trace(go.Bar(
        name='Total Feet',
        x=[str(r["Pipe Size"]) for r in table3],
        y=[r["Total_Feet"] for r in table3],
        marker_color='#ED7D31',
        hovertemplate='<b>Footage</b><br>Feet: %{y:,.0f}<extra></extra>'
    ))

    fig3.update_layout(
        barmode='group',
        title="Pipe Size Mix",
        xaxis_title="Pipe Size",
        yaxis_title="Count / Footage",
        template="plotly_white",
        height=400
    )
    charts['chart3'] = json.loads(json.dumps(fig3, cls=PlotlyJSONEncoder))

    # Chart 4: Length Distribution
    table4 = tables["length_bins"]
    fig4 = go.Figure(data=[
        go.Bar(
            x=[r["Length_Bin_Label"] for r in table4],
            y=[r["Total_Feet"] for r in table4],
            text=[f"{r['Total_Feet']:,.0f}" for r in table4],
            textposition='auto',
            marker_color='#70AD47',
            hovertemplate='<b>%{x}</b><br>Feet: %{y:,.0f}<br>Segments: %{customdata}<extra></extra>',
            customdata=[r["Segment_Count"] for r in table4]
        )
    ])

    fig4.update_layout(
        title="Length Distribution",
        xaxis_title="Length Bin (feet)",
        yaxis_title="Total Feet",
        template="plotly_white",
        height=400
    )
    charts['chart4'] = json.loads(json.dumps(fig4, cls=PlotlyJSONEncoder))

    # Chart 5: Easement & Traffic
    table5 = tables["easement_traffic_summary"]
    fig5 = go.Figure(data=[
        go.Bar(
            x=[f"{r['Category']}<br>{r['Flag']}" for r in table5],
            y=[r["Total_Feet"] for r in table5],
            text=[f"{r['Pct_of_Total_Feet']*100:.1f}%" for r in table5],
            textposition='auto',
            marker_color=['#E7E6E6' if r['Flag'] == 'No' else '#FFC000' for r in table5],
            hovertemplate='<b>%{x}</b><br>Feet: %{y:,.0f}<br>Percentage: %{text}<extra></extra>'
        )
    ])

    fig5.update_layout(
        title="Easement & Traffic Control Distribution",
        xaxis_title="Category",
        yaxis_title="Total Feet",
        template="plotly_white",
        height=400
    )
    charts['chart5'] = json.loads(json.dumps(fig5, cls=PlotlyJSONEncoder))

    return charts


def generate_chartjs_data(processor, tables):
    """Generate Chart.js compatible data (Alternative approach)."""
    charts = {}

    # Chart 1: Overall Progress
    table1 = tables["stage_footage_summary"]
    charts['chart1'] = {
        'type': 'bar',
        'data': {
            'labels': [r["Stage"] for r in table1],
            'datasets': [{
                'label': 'Total Feet',
                'data': [r["Total_Feet"] for r in table1],
                'backgroundColor': '#4472C4'
            }]
        }
    }

    # Add more charts...
    # (Similar structure for other charts)

    return charts


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
