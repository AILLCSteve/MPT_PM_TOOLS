"""
Visual Project Summary - Plotly Dash Application
Integrated into main Flask app as a sub-application
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
import io
import os
from datetime import datetime
from pathlib import Path

from services.cipp_dashboard.data_processor import CIPPDataProcessor
from services.cipp_dashboard.excel_generator_v2 import ExcelDashboardGeneratorV2

# Color scheme - vibrant, distinct colors for lifecycle stages
COLORS = {
    'Not Started': '#E0E0E0',  # Grey (not yet in pipeline)
    'Prep Complete': '#FF6B35',  # Vibrant orange
    'Ready to Line': '#F7B801',  # Vibrant yellow/gold
    'Lined': '#004E89',  # Deep blue
    'Post TV Complete': '#6A0572'  # Deep purple
}

STAGE_ORDER = ['Not Started', 'Prep Complete', 'Ready to Line', 'Lined', 'Post TV Complete']
LIFECYCLE_STAGES = ['Prep Complete', 'Ready to Line', 'Lined', 'Post TV Complete']  # Exclude Not Started


def create_dash_app(flask_app):
    """Create and configure Dash app to work with Flask"""

    # Initialize Dash app with Bootstrap theme and integrate with Flask
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/cipp-dashboard/',
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
        suppress_callback_exceptions=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"}
        ]
    )

    dash_app.title = "Visual Project Summary"

    # Create folders (use absolute paths relative to project root)
    base_dir = Path(__file__).parent
    uploads_dir = base_dir / 'uploads'
    outputs_dir = base_dir / 'outputs'
    uploads_dir.mkdir(exist_ok=True)
    outputs_dir.mkdir(exist_ok=True)

    # Store for processed data
    processed_data_store = {}

    # Layout
    dash_app.layout = dbc.Container(fluid=True, className="px-2 px-md-4", children=[
        # Header
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(html.I(className="fas fa-chart-line fa-2x me-3")),
                        dbc.Col(dbc.NavbarBrand("Visual Project Summary", className="fs-3 fw-bold")),
                    ], align="center"),
                    href="/",
                    style={"textDecoration": "none"}
                )
            ]),
            color="primary",
            dark=True,
            className="mb-4"
        ),

        # Upload Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fas fa-cloud-upload-alt me-2"), "Upload Project Schedule"])),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-file-excel fa-3x mb-3 text-success"),
                                html.H5('Drag and Drop or Click to Select Excel File'),
                                html.P('.xlsx files only', className='text-muted')
                            ], className='text-center p-5 border border-2 border-dashed rounded'),
                            multiple=False,
                            accept='.xlsx'
                        ),
                        html.Div(id='upload-status', className='mt-3')
                    ])
                ], className='shadow')
            ], width=12)
        ], className='mb-4', id='upload-section'),

        # Dashboard Section (hidden initially)
        html.Div([
            # KPIs
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-list fa-2x text-primary mb-2"),
                            html.H3(id='kpi-segments', className='fw-bold'),
                            html.P('Total Segments', className='text-muted mb-0')
                        ], className='text-center')
                    ], className='shadow-sm h-100')
                ], xs=12, sm=6, lg=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-clipboard-check fa-2x text-info mb-2"),
                            html.H3(id='kpi-ready-to-line', className='fw-bold'),
                            html.P('Ready to Line', className='text-muted mb-0')
                        ], className='text-center')
                    ], className='shadow-sm h-100')
                ], xs=12, sm=6, lg=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-ruler fa-2x text-success mb-2"),
                            html.H3(id='kpi-footage', className='fw-bold'),
                            html.P('Total Footage', className='text-muted mb-0')
                        ], className='text-center')
                    ], className='shadow-sm h-100')
                ], xs=12, sm=6, lg=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className="fas fa-calculator fa-2x text-warning mb-2"),
                            html.H3(id='kpi-avg-length', className='fw-bold'),
                            html.P('Avg Length (ft)', className='text-muted mb-0')
                        ], className='text-center')
                    ], className='shadow-sm h-100')
                ], xs=12, sm=6, lg=3)
            ], className='mb-4'),

            # Download Buttons
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6([html.I(className="fas fa-download me-2"), "Download Excel Files"], className='mb-3'),
                            dbc.ButtonGroup([
                                dbc.Button([html.I(className="fas fa-file-excel me-2"), "Approach 1: Native Charts"],
                                          id='download-btn-1', color='primary', outline=True, className='me-2 mb-2 mb-md-0'),
                                dbc.Button([html.I(className="fas fa-file-excel me-2"), "Approach 2: Enhanced"],
                                          id='download-btn-2', color='success', outline=True, className='me-2 mb-2 mb-md-0'),
                                dbc.Button([html.I(className="fas fa-file-excel me-2"), "Approach 3: Plotly Images"],
                                          id='download-btn-3', color='warning', outline=True, className='mb-2 mb-md-0')
                            ], className='w-100 flex-column flex-md-row'),
                            dcc.Download(id="download-file")
                        ])
                    ], className='shadow-sm')
                ], width=12)
            ], className='mb-4'),

            # Overall Progress Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H6("Overall Project Progress")),
                        dbc.CardBody([
                            dcc.Graph(id='overall-progress-chart', config={'displayModeBar': False, 'responsive': True})
                        ])
                    ], className='shadow-sm')
                ], width=12)
            ], className='mb-4'),

            # Stage Progress Bar
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H6("Stage Progress")),
                        dbc.CardBody([
                            dcc.Graph(id='progress-bar-chart', config={'displayModeBar': False, 'responsive': True})
                        ])
                    ], className='shadow-sm')
                ], width=12)
            ], className='mb-4'),

            # Pie charts row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H6("Pipe Size Distribution")),
                        dbc.CardBody([
                            dcc.Graph(id='pipe-size-chart')
                        ])
                    ], className='shadow-sm h-100')
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H6("Segment Type Distribution")),
                        dbc.CardBody([
                            dcc.Graph(id='easement-traffic-chart')
                        ])
                    ], className='shadow-sm h-100')
                ], md=6)
            ], className='mb-4'),

            # Data Tables
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5([html.I(className="fas fa-table me-2"), "Summary Tables"])),
                        dbc.CardBody([
                            dbc.Tabs([
                                dbc.Tab(label="Stage Summary", tab_id="tab-1"),
                                dbc.Tab(label="Stage by Pipe Size", tab_id="tab-2"),
                                dbc.Tab(label="Pipe Size Mix", tab_id="tab-3"),
                                dbc.Tab(label="Length Bins", tab_id="tab-4"),
                                dbc.Tab(label="Easement/Traffic", tab_id="tab-5"),
                            ], id="table-tabs", active_tab="tab-1"),
                            html.Div(id='table-content', className='mt-3')
                        ])
                    ], className='shadow-sm')
                ], width=12)
            ], className='mb-5'),

        ], id='dashboard-section', style={'display': 'none'}),

        # Store session data
        dcc.Store(id='session-data'),
    ])

    # ============================================================================
    # CALLBACKS
    # ============================================================================

    @dash_app.callback(
        [Output('upload-status', 'children'),
         Output('dashboard-section', 'style'),
         Output('session-data', 'data'),
         Output('kpi-segments', 'children'),
         Output('kpi-ready-to-line', 'children'),
         Output('kpi-footage', 'children'),
         Output('kpi-avg-length', 'children')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def process_upload(contents, filename):
        if contents is None:
            raise PreventUpdate

        try:
            # Decode uploaded file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            # Save file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = uploads_dir / f"{timestamp}_{filename}"

            with open(filepath, 'wb') as f:
                f.write(decoded)

            # Process data
            processor = CIPPDataProcessor(str(filepath))
            processor.load_data()

            # Store in global dict
            session_id = timestamp
            processed_data_store[session_id] = {
                'processor': processor,
                'filepath': str(filepath),
                'filename': filename
            }

            # Get Ready to Line count for KPI
            tables = processor.get_all_tables()
            stage_summary = tables['stage_footage_summary']

            ready_to_line_count = sum(
                r['Segment_Count'] for r in stage_summary
                if r['Stage'] == 'Ready to Line'
            )

            status = dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Success! Processed {len(processor.segments)} segments ({processor.total_footage:,.0f} feet)"
            ], color='success')

            return (
                status,
                {'display': 'block'},
                {'session_id': session_id},
                f"{len(processor.segments)}",
                f"{ready_to_line_count}",
                f"{processor.total_footage:,.0f} ft",
                f"{processor.total_footage / len(processor.segments):.1f} ft"
            )

        except Exception as e:
            error = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error: {str(e)}"
            ], color='danger')
            return error, {'display': 'none'}, {}, '', '', '', ''


    @dash_app.callback(
        Output('overall-progress-chart', 'figure'),
        Input('session-data', 'data')
    )
    def update_overall_progress(session_data):
        if not session_data:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        tables = processor.get_all_tables()
        stage_summary = tables['stage_footage_summary']

        # Build stage data map
        stage_data_map = {s['Stage']: s for s in stage_summary}

        fig = go.Figure()

        # Add lifecycle stages
        for stage in LIFECYCLE_STAGES:
            stage_info = stage_data_map.get(stage, {'Total_Feet': 0, 'Pct_of_Total_Feet': 0})
            pct = stage_info['Pct_of_Total_Feet'] * 100

            if pct > 0:
                fig.add_trace(go.Bar(
                    x=[pct],
                    y=['Progress'],
                    name=stage,
                    orientation='h',
                    marker_color=COLORS[stage],
                    text=f"{pct:.1f}%",
                    textposition='inside',
                    hovertemplate=f'<b>{stage}</b><br>{pct:.1f}%<extra></extra>'
                ))

        fig.update_layout(
            barmode='stack',
            height=150,
            margin=dict(l=100, r=20, t=20, b=40),
            xaxis=dict(range=[0, 100], showgrid=False),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
        )

        return fig


    @dash_app.callback(
        Output('progress-bar-chart', 'figure'),
        Input('session-data', 'data')
    )
    def update_progress_bar(session_data):
        if not session_data:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        tables = processor.get_all_tables()
        stage_summary = tables['stage_footage_summary']

        fig = go.Figure()

        for stage_info in stage_summary:
            stage = stage_info['Stage']
            if stage in LIFECYCLE_STAGES:
                fig.add_trace(go.Bar(
                    x=[stage_info['Total_Feet']],
                    y=[stage],
                    orientation='h',
                    marker_color=COLORS.get(stage, '#95A5A6'),
                    text=f"{stage_info['Total_Feet']:,.0f} ft",
                    textposition='inside',
                    hovertemplate=f'<b>{stage}</b><br>%{{x:,.0f}} ft<extra></extra>'
                ))

        fig.update_layout(
            barmode='overlay',
            height=250,
            margin=dict(l=150, r=20, t=20, b=40),
            showlegend=False
        )

        return fig


    @dash_app.callback(
        Output('pipe-size-chart', 'figure'),
        Input('session-data', 'data')
    )
    def update_pipe_size_chart(session_data):
        if not session_data:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        tables = processor.get_all_tables()
        pipe_mix = tables['pipe_size_mix']

        labels = [f"{r['Pipe Size']}\"" for r in pipe_mix]
        values = [r['Total_Feet'] for r in pipe_mix]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])

        fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=40))

        return fig


    @dash_app.callback(
        Output('easement-traffic-chart', 'figure'),
        Input('session-data', 'data')
    )
    def update_easement_traffic(session_data):
        if not session_data:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        segments = processor.segments

        easement_footage = sum(s['map_length'] for s in segments if s['easement'])
        traffic_footage = sum(s['map_length'] for s in segments if s['traffic_control'])
        regular_footage = sum(s['map_length'] for s in segments if not s['easement'] and not s['traffic_control'])

        labels = ['Easement', 'Traffic Control', 'Regular']
        values = [easement_footage, traffic_footage, regular_footage]
        colors = ['#FFC000', '#E74C3C', '#95A5A6']

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=40))

        return fig


    @dash_app.callback(
        Output('table-content', 'children'),
        [Input('table-tabs', 'active_tab'),
         Input('session-data', 'data')]
    )
    def render_table_content(active_tab, session_data):
        if not session_data:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        tables = processor.get_all_tables()

        table_map = {
            'tab-1': 'stage_footage_summary',
            'tab-2': 'stage_by_pipe_size',
            'tab-3': 'pipe_size_mix',
            'tab-4': 'length_bins',
            'tab-5': 'easement_traffic_summary'
        }

        table_data = tables[table_map[active_tab]]
        df = pd.DataFrame(table_data)

        # Format percentage columns
        for col in df.columns:
            if 'Pct' in col or '%' in col:
                df[col] = df[col].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "")
            elif df[col].dtype in ['float64', 'int64'] and col not in ['Pipe Size', 'Min_Length_ft', 'Max_Length_ft']:
                df[col] = df[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "")

        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(68, 114, 196)', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
        )


    @dash_app.callback(
        Output('download-file', 'data'),
        [Input('download-btn-1', 'n_clicks'),
         Input('download-btn-2', 'n_clicks'),
         Input('download-btn-3', 'n_clicks')],
        [State('session-data', 'data')],
        prevent_initial_call=True
    )
    def download_excel(btn1, btn2, btn3, session_data):
        if not session_data:
            raise PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        approach_map = {
            'download-btn-1': 'approach1',
            'download-btn-2': 'approach2',
            'download-btn-3': 'approach3'
        }

        approach = approach_map.get(button_id)
        if not approach:
            raise PreventUpdate

        session_id = session_data['session_id']
        processor = processed_data_store[session_id]['processor']
        original_filepath = processed_data_store[session_id]['filepath']

        # Generate Excel file
        generator = ExcelDashboardGeneratorV2(processor, original_filepath)

        output_path = outputs_dir / f"{session_id}_{approach}.xlsx"

        if approach == 'approach1':
            generator.generate_approach_1(str(output_path))
        elif approach == 'approach2':
            generator.generate_approach_2(str(output_path))
        elif approach == 'approach3':
            generator.generate_approach_3(str(output_path))

        return dcc.send_file(str(output_path))

    return dash_app
