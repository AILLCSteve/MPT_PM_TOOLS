"""
Executive Excel Dashboard Generator - 3-Sheet Format
Professional formatting with openpyxl for CIPP Analysis Results

Sheet 1: Summary - Statistics and section breakdown
Sheet 2: Detailed Results - All questions with answers in unified table
Sheet 3: By Section - Questions grouped by section with styling
"""
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter


class ExcelDashboardGenerator:
    """Generate executive-ready Excel dashboards with 3 professional sheets"""

    # Professional color scheme - Municipal Pipe Tool branding (purple)
    HEADER_FILL = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
    HEADER_FONT = Font(name='Calibri', size=12, bold=True, color="FFFFFF")

    SUBHEADER_FILL = PatternFill(start_color="764ba2", end_color="764ba2", fill_type="solid")
    SUBHEADER_FONT = Font(name='Calibri', size=11, bold=True, color="FFFFFF")

    SECTION_FILL = PatternFill(start_color="f0f4ff", end_color="f0f4ff", fill_type="solid")
    SECTION_FONT = Font(name='Calibri', size=11, bold=True, color="667eea")

    DATA_FONT = Font(name='Calibri', size=11)
    DATA_FONT_BOLD = Font(name='Calibri', size=11, bold=True)

    ANSWERED_FILL = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
    UNANSWERED_FILL = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
    ALT_ROW_FILL = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")

    BORDER_THIN = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC')
    )

    def __init__(self, analysis_result, is_partial=False):
        """
        Initialize dashboard generator

        Args:
            analysis_result: Dict with structure:
                {
                    'sections': [
                        {
                            'section_name': str,
                            'questions': [
                                {'question': str, 'answer': str, 'page_citations': [int], 'footnote': str}
                            ]
                        }
                    ]
                }
            is_partial: Boolean flag indicating if this is a partial/stopped analysis
        """
        self.result = analysis_result
        self.is_partial = is_partial
        self.wb = Workbook()

    def generate(self):
        """Generate complete 3-sheet dashboard workbook"""
        # Remove default sheet
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        # Create all 3 sheets (streamlined format)
        self._create_summary_sheet()         # Sheet 1: Summary with stats
        self._create_detailed_results_sheet() # Sheet 2: Detailed Results (unified table)
        self._create_by_section_sheet()       # Sheet 3: By Section (grouped)

        # Save to bytes
        output = io.BytesIO()
        self.wb.save(output)
        output.seek(0)
        return output

    def _create_summary_sheet(self):
        """Sheet 1: Summary - Statistics and overview"""
        ws = self.wb.create_sheet('Summary', 0)

        # Title
        ws['A1'] = 'CIPP DOCUMENT ANALYSIS'
        ws['A1'].font = Font(name='Calibri', size=20, bold=True, color="667eea")
        ws.merge_cells('A1:D1')

        ws['A2'] = f'Generated: {self._get_timestamp()}'
        ws['A2'].font = Font(name='Calibri', size=11, italic=True, color="666666")
        ws.merge_cells('A2:D2')

        # Partial Results Banner (if applicable)
        row = 3
        if self.is_partial:
            row += 1
            ws[f'A{row}'] = 'PARTIAL RESULTS - Analysis was stopped before completion'
            ws[f'A{row}'].font = Font(name='Calibri', size=12, bold=True, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells(f'A{row}:D{row}')
            ws.row_dimensions[row].height = 25

        # Statistics Section
        stats = self._calculate_statistics()
        row += 2

        ws[f'A{row}'] = 'ANALYSIS STATISTICS'
        ws[f'A{row}'].font = self.SUBHEADER_FONT
        ws[f'A{row}'].fill = self.SUBHEADER_FILL
        ws.merge_cells(f'A{row}:B{row}')

        row += 1
        self._add_stat_row(ws, row, 'Total Questions:', stats['total'])
        row += 1
        self._add_stat_row(ws, row, 'Questions Answered:', stats['answered'], fill=self.ANSWERED_FILL)
        row += 1
        self._add_stat_row(ws, row, 'Not Found:', stats['unanswered'], fill=self.UNANSWERED_FILL)
        row += 1
        self._add_stat_row(ws, row, 'Answer Rate:', f"{stats['answer_rate']:.1f}%", bold=True)

        # Section Breakdown Table
        row += 2
        ws[f'A{row}'] = 'BREAKDOWN BY SECTION'
        ws[f'A{row}'].font = self.SUBHEADER_FONT
        ws[f'A{row}'].fill = self.SUBHEADER_FILL
        ws.merge_cells(f'A{row}:D{row}')

        row += 1
        headers = ['Section', 'Answered', 'Total', 'Rate']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = self.BORDER_THIN

        for section in self.result.get('sections', []):
            row += 1
            total = len(section.get('questions', []))
            answered = sum(1 for q in section.get('questions', []) if q.get('answer'))
            rate = (answered / total * 100) if total > 0 else 0

            ws.cell(row, 1, section.get('section_name', 'Unknown')).font = self.DATA_FONT
            ws.cell(row, 2, answered).font = self.DATA_FONT
            ws.cell(row, 3, total).font = self.DATA_FONT
            ws.cell(row, 4, f"{rate:.0f}%").font = self.DATA_FONT_BOLD

            for col in range(1, 5):
                cell = ws.cell(row, col)
                cell.border = self.BORDER_THIN
                cell.alignment = Alignment(horizontal='left' if col == 1 else 'center', vertical='center')
                if rate == 100:
                    cell.fill = self.ANSWERED_FILL

        # Column widths
        ws.column_dimensions['A'].width = 45
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 10

    def _create_detailed_results_sheet(self):
        """Sheet 2: Detailed Results - All Q&A in unified table"""
        ws = self.wb.create_sheet('Detailed Results')

        # Headers
        headers = ['#', 'Section', 'Question', 'Answer', 'PDF Pages', 'Status']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(1, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        row = 2
        question_num = 1
        for section in self.result.get('sections', []):
            for q in section.get('questions', []):
                answer_text = q.get('answer') or ''
                has_answer = bool(answer_text and answer_text.strip())
                pages = q.get('page_citations', [])
                pages_str = ', '.join(map(str, pages)) if pages else '-'

                # Question number
                ws.cell(row, 1, question_num).font = self.DATA_FONT
                ws.cell(row, 1).alignment = Alignment(horizontal='center', vertical='top')

                # Section
                ws.cell(row, 2, section.get('section_name', '')).font = self.DATA_FONT

                # Question
                ws.cell(row, 3, q.get('question', '')).font = self.DATA_FONT

                # Answer
                answer_cell = ws.cell(row, 4, answer_text if has_answer else 'Not found in document')
                answer_cell.font = self.DATA_FONT if has_answer else Font(name='Calibri', size=11, italic=True, color="999999")

                # PDF Pages
                pages_cell = ws.cell(row, 5, pages_str)
                pages_cell.font = self.DATA_FONT_BOLD if has_answer else self.DATA_FONT
                pages_cell.alignment = Alignment(horizontal='center', vertical='top')

                # Status
                status_cell = ws.cell(row, 6, 'Answered' if has_answer else 'Not Found')
                status_cell.font = Font(name='Calibri', size=11, bold=True)
                status_cell.fill = self.ANSWERED_FILL if has_answer else self.UNANSWERED_FILL
                status_cell.alignment = Alignment(horizontal='center', vertical='top')

                # Apply borders and alternating row color
                for col in range(1, 7):
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    cell.alignment = Alignment(horizontal='left' if col in [2, 3, 4] else 'center', vertical='top', wrap_text=True)
                    if row % 2 == 0 and col != 6:
                        cell.fill = self.ALT_ROW_FILL

                row += 1
                question_num += 1

        # Column widths
        ws.column_dimensions['A'].width = 5    # #
        ws.column_dimensions['B'].width = 28   # Section
        ws.column_dimensions['C'].width = 50   # Question
        ws.column_dimensions['D'].width = 70   # Answer
        ws.column_dimensions['E'].width = 12   # PDF Pages
        ws.column_dimensions['F'].width = 12   # Status

        # Row heights
        for r in range(2, row):
            ws.row_dimensions[r].height = 60

    def _create_by_section_sheet(self):
        """Sheet 3: By Section - Questions grouped with section headers"""
        ws = self.wb.create_sheet('By Section')

        row = 1
        for section in self.result.get('sections', []):
            # Section header
            ws.cell(row, 1, section.get('section_name', 'Unknown Section')).font = self.SECTION_FONT
            ws.cell(row, 1).fill = self.SECTION_FILL
            ws.merge_cells(f'A{row}:E{row}')
            ws.row_dimensions[row].height = 25
            row += 1

            # Column headers for this section
            headers = ['#', 'Question', 'Answer', 'Pages', 'Status']
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row, col, header)
                cell.font = self.SUBHEADER_FONT
                cell.fill = self.SUBHEADER_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = self.BORDER_THIN
            row += 1

            # Questions in this section
            for idx, q in enumerate(section.get('questions', []), start=1):
                answer_text = q.get('answer') or ''
                has_answer = bool(answer_text and answer_text.strip())
                pages = q.get('page_citations', [])
                pages_str = ', '.join(map(str, pages)) if pages else '-'

                ws.cell(row, 1, idx).font = self.DATA_FONT
                ws.cell(row, 1).alignment = Alignment(horizontal='center', vertical='top')

                ws.cell(row, 2, q.get('question', '')).font = self.DATA_FONT

                answer_cell = ws.cell(row, 3, answer_text if has_answer else 'Not found')
                answer_cell.font = self.DATA_FONT if has_answer else Font(name='Calibri', size=11, italic=True, color="999999")

                ws.cell(row, 4, pages_str).font = self.DATA_FONT_BOLD
                ws.cell(row, 4).alignment = Alignment(horizontal='center', vertical='top')

                status_cell = ws.cell(row, 5, 'Yes' if has_answer else 'No')
                status_cell.font = Font(name='Calibri', size=11, bold=True)
                status_cell.fill = self.ANSWERED_FILL if has_answer else self.UNANSWERED_FILL
                status_cell.alignment = Alignment(horizontal='center', vertical='top')

                for col in range(1, 6):
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    cell.alignment = Alignment(horizontal='left' if col in [2, 3] else 'center', vertical='top', wrap_text=True)

                row += 1

            # Add spacing after section
            row += 1

        # Column widths
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 70
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 10


    def _add_stat_row(self, ws, row, label, value, fill=None, bold=False):
        """Add a statistics row with consistent styling"""
        ws.cell(row, 1, label).font = self.DATA_FONT_BOLD
        value_cell = ws.cell(row, 2, value)
        value_cell.font = self.DATA_FONT_BOLD if bold else self.DATA_FONT
        value_cell.alignment = Alignment(horizontal='right')
        if fill:
            value_cell.fill = fill

    def _calculate_statistics(self):
        """Calculate overall statistics"""
        all_questions = []
        for section in self.result.get('sections', []):
            all_questions.extend(section.get('questions', []))

        total = len(all_questions)
        answered = sum(1 for q in all_questions if q.get('answer'))
        unanswered = total - answered
        answer_rate = (answered / total * 100) if total > 0 else 0

        return {
            'total': total,
            'answered': answered,
            'unanswered': unanswered,
            'answer_rate': answer_rate
        }

    def _get_timestamp(self):
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%B %d, %Y at %I:%M %p')
