"""
CIPP Dashboard - Visual Project Summary Module
Transforms CIPP shot schedules into comprehensive visual dashboards
"""

from .data_processor import CIPPDataProcessor
from .excel_generator_v2 import ExcelDashboardGeneratorV2

__all__ = ['CIPPDataProcessor', 'ExcelDashboardGeneratorV2']
