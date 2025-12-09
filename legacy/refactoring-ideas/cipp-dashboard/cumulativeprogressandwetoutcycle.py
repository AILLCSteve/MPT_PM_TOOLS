"""
Example: use cumulative lifecycle milestones in Dash 'Overall Project Progress' chart.
"""

from dash import Output, Input
import plotly.graph_objects as go

from services.cipp_dashboard.data_processor_lifecycle_v2 import CIPPDataProcessorLifecycleV2

COLORS = {
    "Not Started": "#E0E0E0",
    "Prep Complete": "#FF6B35",
    "Ready to Line": "#F7B801",
    "Wet Out": "#00A6A6",
    "Lined": "#004E89",
    "Post TV Complete": "#6A0572",
}

# Lifecycle view EXCLUDES Prep Complete if you want a tighter story:
LIFECYCLE_STAGES = [
    "Ready to Line",
    "Wet Out",
    "Lined",
    "Post TV Complete",
]


def build_overall_progress_figure(processor: CIPPDataProcessorLifecycleV2) -> go.Figure:
    tables = processor.get_all_tables()
    lifecycle_rows = tables["lifecycle_milestones"]
    total_segments = len(processor.segments)

    row_map = {r["Stage"]: r for r in lifecycle_rows}

    fig = go.Figure()

    # === PROJECT LIFECYCLE (stacked bar) ===
    for stage in LIFECYCLE_STAGES:
        data = row_map.get(
            stage,
            {
                "Cumulative_Feet": 0,
                "Cumulative_Pct_of_Total_Feet": 0,
                "Delta_Pct_of_Total_Feet": 0,
            },
        )

        pct_cum = data["Cumulative_Pct_of_Total_Feet"] * 100
        pct_delta = data["Delta_Pct_of_Total_Feet"] * 100
        feet = data["Cumulative_Feet"]

        if pct_delta <= 0:
            continue

        text_display = (
            f"{stage}<br>{pct_cum:.1f}%"
            if pct_delta >= 5  # visibility threshold
            else ""
        )

        fig.add_trace(
            go.Bar(
                y=["Project Lifecycle"],
                x=[pct_delta],
                name=stage,
                orientation="h",
                marker_color=COLORS.get(stage, "#999999"),
                text=text_display,
                textposition="inside",
                hovertemplate=(
                    f"<b>{stage}</b><br>"
                    f"Cumulative: {pct_cum:.1f}% ({feet:,.0f} ft)<extra></extra>"
                ),
                legendgroup="lifecycle",
            )
        )

    # === CIPP Lining Completion by segment count (unchanged idea) ===
    lined_or_better = [
        s for s in processor.segments if s.get("lining_date") is not None
    ]
    lining_complete_count = len(lined_or_better)
    lining_complete_pct = (
        lining_complete_count / total_segments * 100 if total_segments else 0
    )
    lining_incomplete_pct = 100 - lining_complete_pct

    if lining_complete_pct > 0:
        fig.add_trace(
            go.Bar(
                y=["CIPP Lining Status"],
                x=[lining_complete_pct],
                name="Lining Complete",
                orientation="h",
                marker_color="#27AE60",
                text=(
                    f"Lining Complete<br>{lining_complete_pct:.1f}%"
                    if lining_complete_pct >= 5
                    else ""
                ),
                textposition="inside",
                hovertemplate=(
                    f"<b>Lining Complete</b><br>"
                    f"{lining_complete_pct:.1f}% ({lining_complete_count} segments)"
                    "<extra></extra>"
                ),
                legendgroup="lining",
                showlegend=False,
            )
        )

    if lining_incomplete_pct > 0:
        fig.add_trace(
            go.Bar(
                y=["CIPP Lining Status"],
                x=[lining_incomplete_pct],
                name="Lining Not Complete",
                orientation="h",
                marker_color="#E0E0E0",
                text=(
                    f"Lining Not Complete<br>{lining_incomplete_pct:.1f}%"
                    if lining_incomplete_pct >= 5
                    else ""
                ),
                textposition="inside",
                hovertemplate=(
                    f"<b>Lining Not Complete</b><br>"
                    f"{lining_incomplete_pct:.1f}% ({total_segments - lining_complete_count} segments)"
                    "<extra></extra>"
                ),
                legendgroup="lining",
                showlegend=False,
            )
        )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        height=240,
        margin=dict(l=150, r=20, t=10, b=90),
        xaxis=dict(range=[0, 100], ticksuffix="%", fixedrange=True),
        yaxis=dict(categoryorder="array", categoryarray=["CIPP Lining Status", "Project Lifecycle"]),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig
