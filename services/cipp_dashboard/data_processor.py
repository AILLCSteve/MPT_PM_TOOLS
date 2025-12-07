"""
Core data processing module for CIPP shot schedule analysis.
Handles reading Excel data, computing stages, and building summary tables.
"""

from openpyxl import load_workbook
from typing import List, Dict, Any, Optional
from collections import defaultdict


class CIPPDataProcessor:
    """Process CIPP shot schedule data and generate summary tables."""

    STAGES = [
        "Not Started",
        "Prep Complete",
        "Ready to Line",
        "Lined",
        "Post TV Complete"
    ]

    LENGTH_BINS = [
        {"label": "0–50", "min": 0, "max": 50},
        {"label": "51–150", "min": 51, "max": 150},
        {"label": "151–250", "min": 151, "max": 250},
        {"label": "251–350", "min": 251, "max": 350},
        {"label": "351+", "min": 351, "max": None},
    ]

    def __init__(self, file_path: str, sheet_name: str = "WEST DES MOINES, IA Shot Schedu"):
        """Initialize processor with Excel file path."""
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.segments = []
        self.total_footage = 0

    def load_data(self) -> List[Dict[str, Any]]:
        """Load and validate data from Excel file."""
        wb = load_workbook(self.file_path, data_only=True)

        # Try to find the sheet
        if self.sheet_name not in wb.sheetnames:
            # Try to find sheet with similar name
            for sheet in wb.sheetnames:
                if "MOINES" in sheet.upper() or "SHOT" in sheet.upper():
                    self.sheet_name = sheet
                    break
            else:
                raise ValueError(f"Sheet '{self.sheet_name}' not found. Available: {wb.sheetnames}")

        ws = wb[self.sheet_name]

        # Get headers from row 1
        headers = {}
        for col_idx, cell in enumerate(ws[1], start=1):
            if cell.value:
                headers[str(cell.value).strip()] = col_idx

        # Process data rows
        segments = []
        for row_idx in range(2, ws.max_row + 1):
            row = ws[row_idx]

            # Get VIDEO ID and Map Length
            video_id = self._get_cell_value(row, headers.get("VIDEO ID"))
            map_length = self._get_cell_value(row, headers.get("Map Length"))

            # Validate segment
            if not self._is_valid_segment(video_id, map_length):
                continue

            # Extract segment data
            segment = {
                "video_id": video_id,
                "line_segment": self._get_cell_value(row, headers.get("Line Segment")),
                "pipe_size": self._get_cell_value(row, headers.get("Pipe Size")),
                "map_length": float(map_length),
                "prep_complete": self._is_truthy(self._get_cell_value(row, headers.get("Prep Complete"))),
                "ready_to_line": self._is_truthy(self._get_cell_value(row, headers.get("Ready to Line - Certified by Prep Crew Lead"))),
                "lining_date": self._get_cell_value(row, headers.get("Lining Date")),
                "final_post_tv_date": self._get_cell_value(row, headers.get("Final Post TV Date")),
                "grout_state_date": self._get_cell_value(row, headers.get("Grout State Date")),
                "easement": self._is_truthy(self._get_cell_value(row, headers.get("Easement"))),
                "traffic_control": self._is_truthy(self._get_cell_value(row, headers.get("Traffic Control"))),
            }

            # Compute stage
            segment["stage"] = self._compute_stage(segment)
            segments.append(segment)

        self.segments = segments
        self.total_footage = sum(s["map_length"] for s in segments)
        return segments

    def _get_cell_value(self, row, col_idx):
        """Get cell value safely."""
        if col_idx is None or col_idx < 1:
            return None
        try:
            return row[col_idx - 1].value
        except (IndexError, AttributeError):
            return None

    def _is_valid_segment(self, video_id, map_length) -> bool:
        """Check if segment is valid."""
        try:
            video_id_num = float(video_id) if video_id is not None else 0
            map_length_num = float(map_length) if map_length is not None else 0
            return video_id_num >= 1 and map_length_num > 0
        except (ValueError, TypeError):
            return False

    def _is_truthy(self, value) -> bool:
        """Check if value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.upper() in ["TRUE", "YES", "Y", "1"]
        return bool(value)

    def _compute_stage(self, segment: Dict[str, Any]) -> str:
        """Compute stage based on priority logic."""
        if segment["final_post_tv_date"] is not None:
            return "Post TV Complete"
        elif segment["lining_date"] is not None:
            return "Lined"
        elif segment["ready_to_line"]:
            return "Ready to Line"
        elif segment["prep_complete"]:
            return "Prep Complete"
        else:
            return "Not Started"

    def get_stage_footage_summary(self) -> List[Dict[str, Any]]:
        """Table 1: Stage_Footage_Summary (overall progress)."""
        stage_data = defaultdict(lambda: {"count": 0, "footage": 0})

        for segment in self.segments:
            stage = segment["stage"]
            stage_data[stage]["count"] += 1
            stage_data[stage]["footage"] += segment["map_length"]

        result = []
        for stage in self.STAGES:
            data = stage_data[stage]
            result.append({
                "Stage": stage,
                "Segment_Count": data["count"],
                "Total_Feet": round(data["footage"], 2),
                "Pct_of_Total_Feet": round(data["footage"] / self.total_footage, 4) if self.total_footage > 0 else 0
            })

        return result

    def get_stage_by_pipe_size(self) -> List[Dict[str, Any]]:
        """Table 2: Stage_by_PipeSize (progress by diameter)."""
        # Collect unique pipe sizes
        pipe_sizes = sorted(set(s["pipe_size"] for s in self.segments if s["pipe_size"] is not None))

        result = []
        for pipe_size in pipe_sizes:
            row = {"Pipe Size": pipe_size}
            total = 0

            for stage in self.STAGES:
                footage = sum(
                    s["map_length"]
                    for s in self.segments
                    if s["pipe_size"] == pipe_size and s["stage"] == stage
                )
                row[stage] = round(footage, 2)
                total += footage

            row["Total_Feet"] = round(total, 2)
            result.append(row)

        return result

    def get_pipe_size_mix(self) -> List[Dict[str, Any]]:
        """Table 3: Pipe_Size_Mix (how much of each diameter)."""
        pipe_sizes = sorted(set(s["pipe_size"] for s in self.segments if s["pipe_size"] is not None))

        result = []
        for pipe_size in pipe_sizes:
            segments_for_size = [s for s in self.segments if s["pipe_size"] == pipe_size]
            count = len(segments_for_size)
            footage = sum(s["map_length"] for s in segments_for_size)

            result.append({
                "Pipe Size": pipe_size,
                "Segment_Count": count,
                "Total_Feet": round(footage, 2),
                "Avg_Length_ft": round(footage / count, 2) if count > 0 else 0,
                "Pct_of_Total_Feet": round(footage / self.total_footage, 4) if self.total_footage > 0 else 0
            })

        return result

    def get_length_bins(self) -> List[Dict[str, Any]]:
        """Table 4: Length_Bins (distribution of run lengths)."""
        result = []

        for bin_def in self.LENGTH_BINS:
            segments_in_bin = []
            for segment in self.segments:
                length = segment["map_length"]
                min_len = bin_def["min"]
                max_len = bin_def["max"]

                if max_len is None:
                    # Open-ended bin
                    if length >= min_len:
                        segments_in_bin.append(segment)
                else:
                    if min_len <= length <= max_len:
                        segments_in_bin.append(segment)

            count = len(segments_in_bin)
            footage = sum(s["map_length"] for s in segments_in_bin)

            result.append({
                "Length_Bin_Label": bin_def["label"],
                "Min_Length_ft": bin_def["min"],
                "Max_Length_ft": bin_def["max"] if bin_def["max"] is not None else "",
                "Segment_Count": count,
                "Total_Feet": round(footage, 2),
                "Pct_of_Total_Feet": round(footage / self.total_footage, 4) if self.total_footage > 0 else 0
            })

        return result

    def get_easement_traffic_summary(self) -> List[Dict[str, Any]]:
        """Table 5: Easement_Traffic_Summary."""
        result = []

        # Easement Yes
        easement_yes = [s for s in self.segments if s["easement"]]
        result.append({
            "Category": "Easement",
            "Flag": "Yes",
            "Segment_Count": len(easement_yes),
            "Total_Feet": round(sum(s["map_length"] for s in easement_yes), 2),
            "Pct_of_Total_Feet": round(sum(s["map_length"] for s in easement_yes) / self.total_footage, 4) if self.total_footage > 0 else 0
        })

        # Easement No
        easement_no = [s for s in self.segments if not s["easement"]]
        result.append({
            "Category": "Easement",
            "Flag": "No",
            "Segment_Count": len(easement_no),
            "Total_Feet": round(sum(s["map_length"] for s in easement_no), 2),
            "Pct_of_Total_Feet": round(sum(s["map_length"] for s in easement_no) / self.total_footage, 4) if self.total_footage > 0 else 0
        })

        # Traffic Control Yes
        traffic_yes = [s for s in self.segments if s["traffic_control"]]
        result.append({
            "Category": "Traffic Control",
            "Flag": "Yes",
            "Segment_Count": len(traffic_yes),
            "Total_Feet": round(sum(s["map_length"] for s in traffic_yes), 2),
            "Pct_of_Total_Feet": round(sum(s["map_length"] for s in traffic_yes) / self.total_footage, 4) if self.total_footage > 0 else 0
        })

        # Traffic Control No
        traffic_no = [s for s in self.segments if not s["traffic_control"]]
        result.append({
            "Category": "Traffic Control",
            "Flag": "No",
            "Segment_Count": len(traffic_no),
            "Total_Feet": round(sum(s["map_length"] for s in traffic_no), 2),
            "Pct_of_Total_Feet": round(sum(s["map_length"] for s in traffic_no) / self.total_footage, 4) if self.total_footage > 0 else 0
        })

        return result

    def get_all_tables(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all 5 summary tables."""
        return {
            "stage_footage_summary": self.get_stage_footage_summary(),
            "stage_by_pipe_size": self.get_stage_by_pipe_size(),
            "pipe_size_mix": self.get_pipe_size_mix(),
            "length_bins": self.get_length_bins(),
            "easement_traffic_summary": self.get_easement_traffic_summary()
        }
