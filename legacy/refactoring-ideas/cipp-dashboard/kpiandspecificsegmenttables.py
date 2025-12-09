"""
Helper functions for lifecycle-driven tables and KPIs.
"""

from typing import Dict, Any, List, Tuple


def compute_potential_issues_kpi(processor) -> Tuple[int, float]:
    """
    Returns (count, total_feet) for segments where:
    Prep Complete == True AND Ready to Line == False.
    """
    issues = processor.get_potential_issues()
    count = len(issues)
    total_feet = sum(row["Map_Length_ft"] for row in issues)
    return count, total_feet


def build_potential_issues_table(processor) -> List[Dict[str, Any]]:
    """
    Thin wrapper so Dash can just call this and feed the rows into a DataTable.
    """
    return processor.get_potential_issues()


def build_lifecycle_tables_for_dash(processor) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns the lifecycle segment tables in a format that Dash can easily map:
    {
      "Not Started": [...],
      "Ready to Line": [...],
      "Lined": [...],
      "Post TV Complete": [...],
      "Wet Out": [...],
    }
    """
    return processor.get_lifecycle_segment_tables()
