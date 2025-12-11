"""
Executive Excel Dashboard Generator with Charts
Professional formatting with openpyxl for CIPP Analysis Results
"""
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter


class ExcelDashboardGenerator:
    """Generate executive-ready Excel dashboards with charts and professional styling"""

    # Professional color scheme
    HEADER_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    HEADER_FONT = Font(name='Calibri', size=15, bold=True, color="FFFFFF")

    SUBHEADER_FILL = PatternFill(start_color="5B7FCC", end_color="5B7FCC", fill_type="solid")
    SUBHEADER_FONT = Font(name='Calibri', size=14, bold=True, color="FFFFFF")

    DATA_FONT = Font(name='Calibri', size=15)
    DATA_FONT_BOLD = Font(name='Calibri', size=15, bold=True)

    ANSWERED_FILL = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
    UNANSWERED_FILL = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")

    BORDER_THIN = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000')
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
        """Generate complete dashboard workbook"""
        # Remove default sheet
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        # Create all sheets
        self._create_executive_summary()
        self._create_detailed_results()
        self._create_footnotes_sheet()
        self._create_unanswered_questions()
        self._create_page_citations_index()

        # Save to bytes
        output = io.BytesIO()
        self.wb.save(output)
        output.seek(0)
        return output

    def _create_executive_summary(self):
        """Sheet 1: Executive Summary with Charts"""
        ws = self.wb.create_sheet('Executive Summary', 0)

        # Title
        ws['A1'] = 'CIPP BID-SPEC ANALYSIS'
        ws['A1'].font = Font(name='Calibri', size=24, bold=True, color="1E3A8A")
        ws.merge_cells('A1:E1')

        ws['A2'] = 'Executive Dashboard Report'
        ws['A2'].font = Font(name='Calibri', size=16, color="5B7FCC")
        ws.merge_cells('A2:E2')

        ws['A3'] = f'Generated: {self._get_timestamp()}'
        ws['A3'].font = Font(name='Calibri', size=14, italic=True)
        ws.merge_cells('A3:E3')

        # Partial Results Banner (if applicable)
        row = 4
        if self.is_partial:
            ws[f'A{row}'] = '⚠️ PARTIAL RESULTS - ANALYSIS STOPPED'
            ws[f'A{row}'].font = Font(name='Calibri', size=16, bold=True, color="FFFFFF")
            ws[f'A{row}'].fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells(f'A{row}:E{row}')
            ws.row_dimensions[row].height = 25
            row += 1

        # Statistics Section
        row += 1
        ws[f'A{row}'] = 'ANALYSIS STATISTICS'
        ws[f'A{row}'].font = self.SUBHEADER_FONT
        ws[f'A{row}'].fill = self.SUBHEADER_FILL
        ws.merge_cells(f'A{row}:B{row}')

        stats = self._calculate_statistics()

        row += 1
        self._add_stat_row(ws, row, 'Total Questions:', stats['total'])
        row += 1
        self._add_stat_row(ws, row, 'Questions Answered:', stats['answered'], fill=self.ANSWERED_FILL)
        row += 1
        self._add_stat_row(ws, row, 'Unanswered:', stats['unanswered'], fill=self.UNANSWERED_FILL)
        row += 1
        self._add_stat_row(ws, row, 'Answer Rate:', f"{stats['answer_rate']:.1f}%", bold=True)

        # Section Breakdown Table
        row += 2
        ws[f'A{row}'] = 'SECTION BREAKDOWN'
        ws[f'A{row}'].font = self.SUBHEADER_FONT
        ws[f'A{row}'].fill = self.SUBHEADER_FILL
        ws.merge_cells(f'A{row}:D{row}')

        row += 1
        headers = ['Section Name', 'Answered', 'Total', 'Rate']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        section_data_start = row + 1
        for section in self.result['sections']:
            row += 1
            total = len(section['questions'])
            answered = sum(1 for q in section['questions'] if q.get('answer'))
            rate = (answered / total * 100) if total > 0 else 0

            ws.cell(row, 1, section['section_name']).font = self.DATA_FONT
            ws.cell(row, 2, answered).font = self.DATA_FONT
            ws.cell(row, 3, total).font = self.DATA_FONT
            ws.cell(row, 4, f"{rate:.1f}%").font = self.DATA_FONT

            # Apply borders and alignment
            for col in range(1, 5):
                cell = ws.cell(row, col)
                cell.border = self.BORDER_THIN
                cell.alignment = Alignment(horizontal='left' if col == 1 else 'center', vertical='center', wrap_text=True)

        section_data_end = row

        # Add Bar Chart for Section Performance
        chart = BarChart()
        chart.title = "Questions Answered by Section"
        chart.style = 10
        chart.height = 12
        chart.width = 20

        data = Reference(ws, min_col=2, min_row=section_data_start-1, max_row=section_data_end, max_col=2)
        categories = Reference(ws, min_col=1, min_row=section_data_start, max_row=section_data_end)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        chart.y_axis.title = "Questions Answered"
        chart.x_axis.title = "Section"

        ws.add_chart(chart, f'F5')

        # Add Pie Chart for Overall Answer Rate
        pie_row = row + 3
        ws[f'A{pie_row}'] = 'Answered'
        ws[f'B{pie_row}'] = stats['answered']
        ws[f'A{pie_row+1}'] = 'Unanswered'
        ws[f'B{pie_row+1}'] = stats['unanswered']

        pie = PieChart()
        pie.title = "Overall Answer Rate"
        pie.height = 12
        pie.width = 12

        labels = Reference(ws, min_col=1, min_row=pie_row, max_row=pie_row+1)
        data = Reference(ws, min_col=2, min_row=pie_row, max_row=pie_row+1)
        pie.add_data(data)
        pie.set_categories(labels)

        ws.add_chart(pie, f'F25')

        # Column widths
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15

    def _create_detailed_results(self):
        """Sheet 2: Detailed Q&A Results - Professionally Styled"""
        ws = self.wb.create_sheet('Detailed Results')

        # Headers (added "Inline Citations" and "Footnote" columns)
        headers = ['Section', 'Question', 'Answer', 'PDF Pages', 'Inline Citations', 'Footnote', 'Status']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(1, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        row = 2
        for section in self.result['sections']:
            for q in section['questions']:
                answer_text = q.get('answer', 'Not found in document')

                ws.cell(row, 1, section['section_name']).font = self.DATA_FONT
                ws.cell(row, 2, q['question']).font = self.DATA_FONT
                ws.cell(row, 3, answer_text).font = self.DATA_FONT
                ws.cell(row, 4, ', '.join(map(str, q.get('page_citations', [])))).font = self.DATA_FONT_BOLD

                # Extract inline citations (Section X.Y.Z references) from answer text
                inline_citations = self._extract_inline_citations(answer_text) if answer_text and answer_text != 'Not found in document' else []
                ws.cell(row, 5, '; '.join(inline_citations) if inline_citations else '-').font = self.DATA_FONT

                # Add footnote column (NEW)
                footnote_text = q.get('footnote', '') or '-'
                ws.cell(row, 6, footnote_text).font = self.DATA_FONT

                status_cell = ws.cell(row, 7, '✓ Answered' if q.get('answer') else '✗ Not Found')
                status_cell.font = Font(name='Calibri', size=15, bold=True)
                status_cell.fill = self.ANSWERED_FILL if q.get('answer') else self.UNANSWERED_FILL

                # Borders and wrapping
                for col in range(1, 8):  # Updated to include footnote column
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

                row += 1

        # Column widths (adjusted for footnote column)
        ws.column_dimensions['A'].width = 30   # Section
        ws.column_dimensions['B'].width = 60   # Question
        ws.column_dimensions['C'].width = 70   # Answer
        ws.column_dimensions['D'].width = 12   # PDF Pages (bold, smaller width)
        ws.column_dimensions['E'].width = 20   # Inline Citations
        ws.column_dimensions['F'].width = 45   # Footnote (NEW)
        ws.column_dimensions['G'].width = 15   # Status

        # Row heights for readability
        for r in range(2, row):
            ws.row_dimensions[r].height = 70  # Increased from 60 for wrapped text

    def _create_footnotes_sheet(self):
        """Sheet 3: Footnotes - PDF Pages & Section References"""
        ws = self.wb.create_sheet('Footnotes')

        # Title
        ws['A1'] = 'FOOTNOTES - PDF PAGES & SECTION REFERENCES'
        ws['A1'].font = Font(name='Calibri', size=18, bold=True, color="667eea")
        ws.merge_cells('A1:B1')

        ws['A2'] = 'Each footnote includes PDF page numbers (<PDF pg #>) and document section references'
        ws['A2'].font = Font(name='Calibri', size=12, italic=True, color="666666")
        ws.merge_cells('A2:B2')

        # Headers
        headers = ['#', 'Footnote']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(4, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        # Get footnotes from result
        footnotes = self.result.get('footnotes', [])

        if footnotes:
            row = 5
            for idx, footnote in enumerate(footnotes, start=1):
                # Number column
                num_cell = ws.cell(row, 1, idx)
                num_cell.font = Font(name='Calibri', size=14, bold=True)
                num_cell.alignment = Alignment(horizontal='center', vertical='top')
                num_cell.border = self.BORDER_THIN

                # Footnote text
                footnote_cell = ws.cell(row, 2, footnote)
                footnote_cell.font = self.DATA_FONT
                footnote_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                footnote_cell.border = self.BORDER_THIN

                row += 1

            # Column widths
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 120

            # Row heights for readability
            for r in range(5, row):
                ws.row_dimensions[r].height = 40
        else:
            ws.cell(5, 1, 'No footnotes generated - answers did not contain detailed section references.').font = Font(name='Calibri', size=14, italic=True, color="666666")
            ws.merge_cells('A5:B5')
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 120

    def _create_unanswered_questions(self):
        """Sheet 3: Unanswered Questions for Manual Review"""
        ws = self.wb.create_sheet('Unanswered Questions')

        # Title
        ws['A1'] = 'UNANSWERED QUESTIONS - MANUAL REVIEW REQUIRED'
        ws['A1'].font = Font(name='Calibri', size=18, bold=True, color="DC3545")
        ws.merge_cells('A1:C1')

        # Headers
        headers = ['Section', 'Question', 'Notes']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(3, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        row = 4
        for section in self.result['sections']:
            for q in section['questions']:
                if not q.get('answer'):
                    ws.cell(row, 1, section['section_name']).font = self.DATA_FONT
                    ws.cell(row, 2, q['question']).font = self.DATA_FONT
                    ws.cell(row, 3, 'Not found - requires manual document review').font = Font(name='Calibri', size=15, italic=True)

                    for col in range(1, 4):
                        cell = ws.cell(row, col)
                        cell.border = self.BORDER_THIN
                        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                        cell.fill = self.UNANSWERED_FILL

                    row += 1

        if row == 4:
            ws.cell(4, 1, 'All questions answered - no manual review needed!').font = Font(name='Calibri', size=15, bold=True, color="28A745")
            ws.merge_cells('A4:C4')

        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 80
        ws.column_dimensions['C'].width = 50

        for r in range(4, row):
            ws.row_dimensions[r].height = 50

    def _create_page_citations_index(self):
        """Sheet 4: Page Citations Index - Reverse Lookup"""
        ws = self.wb.create_sheet('Page Citations Index')

        # Title
        ws['A1'] = 'PAGE CITATIONS INDEX'
        ws['A1'].font = Font(name='Calibri', size=18, bold=True, color="1E3A8A")
        ws.merge_cells('A1:B1')

        # Headers
        headers = ['Page Number', 'Questions Citing This Page']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(3, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN

        # Build page map
        page_map = {}
        for section in self.result['sections']:
            for q in section['questions']:
                if q.get('page_citations'):
                    for page in q['page_citations']:
                        if page not in page_map:
                            page_map[page] = []
                        page_map[page].append(q['question'])

        # Sort by page number
        row = 4
        for page in sorted(page_map.keys(), key=lambda x: int(x) if str(x).isdigit() else 999999):
            ws.cell(row, 1, f"Page {page}").font = self.DATA_FONT_BOLD
            ws.cell(row, 2, ' | '.join(page_map[page])).font = self.DATA_FONT

            for col in range(1, 3):
                cell = ws.cell(row, col)
                cell.border = self.BORDER_THIN
                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

            row += 1

        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 120

        for r in range(4, row):
            ws.row_dimensions[r].height = 50

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
        for section in self.result['sections']:
            all_questions.extend(section['questions'])

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

    def _extract_inline_citations(self, answer_text):
        """
        Extract inline citations (Section X.Y.Z references) from answer text.

        Matches patterns like:
        - Section 3.2.1
        - Division 02, Section 02505
        - Part 3.2.1

        Returns:
            List of citation strings
        """
        import re

        if not answer_text:
            return []

        citations = []

        # Pattern 1: Section X.Y.Z or Section X.Y or Section X
        section_pattern = re.compile(r'Section\s+(\d+(?:\.\d+)*)', re.IGNORECASE)
        for match in section_pattern.finditer(answer_text):
            citation = f"Section {match.group(1)}"
            if citation not in citations:
                citations.append(citation)

        # Pattern 2: Division X, Section Y
        division_pattern = re.compile(r'Division\s+(\d+),?\s*Section\s+(\d+)', re.IGNORECASE)
        for match in division_pattern.finditer(answer_text):
            citation = f"Division {match.group(1)}, Section {match.group(2)}"
            if citation not in citations:
                citations.append(citation)

        # Pattern 3: Part X.Y.Z
        part_pattern = re.compile(r'Part\s+(\d+(?:\.\d+)*)', re.IGNORECASE)
        for match in part_pattern.finditer(answer_text):
            citation = f"Part {match.group(1)}"
            if citation not in citations:
                citations.append(citation)

        return citations
