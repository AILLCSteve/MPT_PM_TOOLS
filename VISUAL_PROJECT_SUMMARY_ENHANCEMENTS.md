# Visual Project Summary - Enhancement Implementation Guide

## COMPLETED: Cumulative Lifecycle Stage Tracking ✅

**Commit:** ea405ab - "feat(dashboard): Implement CUMULATIVE LIFECYCLE stage tracking"

### What Was Changed:
The data processor now tracks segments cumulatively through their lifecycle instead of treating stages as mutually exclusive.

**Before (Mutually Exclusive):**
- A segment at "Lined" was NOT counted as "Ready to Line"
- Metrics showed "how many are stuck at each stage"
- Inaccurate progress representation

**After (Cumulative):**
- A segment at "Lined" IS counted in: Prep Complete ✓, Ready to Line ✓, Lined ✓
- Metrics show "how much has passed through each lifecycle gate"
- Accurate progress tracking for PM

### Implementation Details:
- `_compute_achieved_stages()` - Returns list of ALL achieved stages
- `get_stage_footage_summary()` - Uses cumulative counting
- `get_stage_by_pipe_size()` - Cumulative progress by diameter
- 10+ filtering functions for breakout tables

---

## NEXT STEPS: Interactive Breakout Tables & Clickable Visualizations

### Requirements Summary:

1. **Instant Breakout Tables** - Display immediately on dashboard:
   - Ready to Line segments
   - CCTV Posted (Post TV Complete) segments
   - Flagged Issues segments
   - Easement segments
   - Traffic Control segments
   - Each pipe size breakout

2. **Clickable Visualizations** → Jump to filtered tables:
   - Click "Ready to Line" in progress chart → show Ready to Line table
   - Click "Easement Yes" → show easement segments table
   - Click "15" pipe size → show all 15" segments table
   - Click length bin → show segments in that range

3. **Hover Behavior**:
   - What was on-click now shows on-hover
   - Click navigates to breakout table
   - Hover shows detailed tooltip with metrics

---

## Implementation Plan for dash_app.py

### Step 1: Add Breakout Tables Section to Layout

Add after the "Summary Tables" section (around line 300):

```python
# Breakout Tables Section - Instant Filtered Views
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader(html.H5([
                html.I(className="fas fa-filter me-2"),
                "Breakout Tables - Filtered Segment Views"
            ])),
            dbc.CardBody([
                # Tabs for different breakouts
                dbc.Tabs([
                    dbc.Tab(label="Ready to Line", tab_id="breakout-ready"),
                    dbc.Tab(label="CCTV Posted", tab_id="breakout-cctv"),
                    dbc.Tab(label="Flagged Issues", tab_id="breakout-flagged"),
                    dbc.Tab(label="Easement", tab_id="breakout-easement"),
                    dbc.Tab(label="Traffic Control", tab_id="breakout-traffic"),
                    dbc.Tab(label="By Pipe Size", tab_id="breakout-pipe"),
                    dbc.Tab(label="By Length", tab_id="breakout-length"),
                    dbc.Tab(label="Custom Filter", tab_id="breakout-custom"),
                ], id="breakout-tabs", active_tab="breakout-ready"),
                html.Div(id='breakout-table-content', className='mt-3')
            ])
        ], className='shadow-sm')
    ], width=12)
], className='mb-4'),

# Store for click navigation
dcc.Store(id='breakout-nav-store'),
```

### Step 2: Add Callback for Breakout Tables

```python
@dash_app.callback(
    Output('breakout-table-content', 'children'),
    [Input('breakout-tabs', 'active_tab'),
     Input('breakout-nav-store', 'data'),
     Input('session-data', 'data')]
)
def update_breakout_table(active_tab, nav_data, session_data):
    """Display filtered breakout tables based on tab or click navigation."""
    if not session_data:
        return html.P("Upload a file to see breakout tables", className='text-muted text-center p-5')

    processor = get_processor(session_data['filepath'])
    if not processor:
        return html.P("Error loading data", className='text-danger')

    # Determine filter based on tab or navigation
    filter_type = active_tab
    filter_value = None

    if nav_data:
        filter_type = nav_data.get('type', active_tab)
        filter_value = nav_data.get('value')

    # Get filtered segments
    if filter_type == 'breakout-ready':
        segments = processor.get_segments_ready_to_line()
        title = f"Ready to Line Segments ({len(segments)} total)"

    elif filter_type == 'breakout-cctv':
        segments = processor.get_segments_cctv_posted()
        title = f"CCTV Posted (Post TV Complete) Segments ({len(segments)} total)"

    elif filter_type == 'breakout-flagged':
        segments = processor.get_segments_flagged_for_issues()
        title = f"Flagged Issues ({len(segments)} segments with potential issues)"

    elif filter_type == 'breakout-easement':
        segments = processor.get_segments_by_easement(True)
        title = f"Easement Segments ({len(segments)} total)"

    elif filter_type == 'breakout-traffic':
        segments = processor.get_segments_by_traffic_control(True)
        title = f"Traffic Control Required ({len(segments)} segments)"

    elif filter_type == 'breakout-pipe':
        if filter_value:
            segments = processor.get_segments_by_pipe_size(filter_value)
            title = f"{filter_value}\" Pipe Segments ({len(segments)} total)"
        else:
            segments = []
            title = "Select a pipe size from the chart"

    elif filter_type == 'breakout-length':
        if filter_value and 'min' in filter_value:
            segments = processor.get_segments_by_length_bin(
                filter_value['min'],
                filter_value.get('max')
            )
            bin_label = filter_value.get('label', 'Selected Range')
            title = f"{bin_label} Segments ({len(segments)} total)"
        else:
            segments = []
            title = "Select a length bin from the chart"

    else:
        segments = processor.segments
        title = f"All Segments ({len(segments)} total)"

    # Format for table display
    if not segments:
        return html.Div([
            html.H6(title, className='mb-3'),
            html.P("No segments match this filter", className='text-muted text-center p-5')
        ])

    formatted = processor.format_segments_for_table(segments)
    df = pd.DataFrame(formatted)

    # Create footer with statistics
    total_footage = sum(s['map_length'] for s in segments)
    avg_length = total_footage / len(segments) if segments else 0

    footer = html.Div([
        dbc.Row([
            dbc.Col([
                html.Strong("Total Segments: "),
                html.Span(f"{len(segments)}")
            ], width=4),
            dbc.Col([
                html.Strong("Total Footage: "),
                html.Span(f"{total_footage:,.0f} ft")
            ], width=4),
            dbc.Col([
                html.Strong("Avg Length: "),
                html.Span(f"{avg_length:.1f} ft")
            ], width=4),
        ], className='mt-3 p-3 bg-light rounded')
    ])

    return html.Div([
        html.H6(title, className='mb-3'),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'minWidth': '100px'
            },
            style_header={
                'backgroundColor': '#1E3A8A',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            page_size=20,
            sort_action='native',
            filter_action='native',
            export_format='xlsx',
            export_headers='display'
        ),
        footer
    ])
```

### Step 3: Make Charts Clickable

Update chart creation callbacks to include click events:

```python
# Example for progress bar chart
@dash_app.callback(
    Output('breakout-nav-store', 'data'),
    [Input('progress-bar-chart', 'clickData'),
     Input('pipe-size-chart', 'clickData'),
     Input('easement-traffic-chart', 'clickData'),
     Input('length-distribution-chart', 'clickData')]
)
def handle_chart_clicks(progress_click, pipe_click, easement_click, length_click):
    """Handle clicks on charts to navigate to breakout tables."""
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'progress-bar-chart' and progress_click:
        stage = progress_click['points'][0]['y']  # Get clicked stage
        return {'type': 'breakout-stage', 'value': stage}

    elif trigger_id == 'pipe-size-chart' and pipe_click:
        pipe_size = pipe_click['points'][0]['x']  # Get clicked pipe size
        return {'type': 'breakout-pipe', 'value': pipe_size}

    elif trigger_id == 'easement-traffic-chart' and easement_click:
        category = easement_click['points'][0]['x']  # e.g., "Easement Yes"
        if "Easement" in category:
            return {'type': 'breakout-easement', 'value': "Yes" in category}
        else:
            return {'type': 'breakout-traffic', 'value': "Yes" in category}

    elif trigger_id == 'length-distribution-chart' and length_click:
        bin_label = length_click['points'][0]['x']
        # Parse bin label to get min/max
        # This requires the bin definition to be accessible
        return {'type': 'breakout-length', 'value': {'label': bin_label}}

    raise PreventUpdate
```

### Step 4: Update Chart Configs for Hover

Update each chart creation to set:

```python
config={'displayModeBar': True, 'responsive': True}

# And in the chart figure:
fig.update_traces(hovertemplate='<b>%{label}</b><br>' +
                                'Count: %{value}<br>' +
                                'Footage: %{customdata[0]:,.0f} ft<br>' +
                                'Percentage: %{customdata[1]:.1f}%<extra></extra>')
```

---

## Testing Checklist

- [ ] Upload Excel file - verify cumulative stage counting works
- [ ] Check Ready to Line count - should include Lined and Post TV segments
- [ ] Click on progress bar stage → verify navigation to breakout table
- [ ] Click on pipe size → verify filtered table shows only that size
- [ ] Click on easement chart → verify easement segments displayed
- [ ] Hover over charts → verify detailed tooltips appear
- [ ] Export breakout table to Excel → verify works
- [ ] Filter and sort breakout tables → verify functionality

---

## Files Modified

1. ✅ `services/cipp_dashboard/data_processor.py` - Cumulative lifecycle tracking
2. ⏳ `services/cipp_dashboard/dash_app.py` - Interactive breakout tables

---

## Key Benefits

1. **Accurate Metrics**: True progress through lifecycle gates
2. **Instant Insights**: Click any chart to see underlying segments
3. **Better PM**: Identify bottlenecks, easement segments, flagged issues instantly
4. **Flexible Filtering**: Multiple ways to slice and analyze project data
5. **Export Capability**: Export any filtered view to Excel

