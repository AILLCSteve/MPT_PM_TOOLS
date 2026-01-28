"""
Executive Excel Report Package - 4-Sheet Professional Format
Industry-grade formatting with openpyxl for Municipal Pipe Tool Analysis Results

Sheet 1: Executive Summary - Analysis statistics and key project requirements
Sheet 2: Detailed Results - All questions with answers in unified table
Sheet 3: By Section - Questions grouped by section with clear headers
Sheet 4: Footnotes - All footnotes and citation references
"""
import io
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelDashboardGenerator:
    """Generate executive-ready Excel report package with 4 professional sheets"""

    # Professional color scheme - Municipal Pipe Tool Purple branding
    PURPLE_DARK = "667EEA"
    PURPLE = "764BA2"
    PURPLE_LIGHT = "E9E4F0"
    GREEN = "22C55E"
    GREEN_LIGHT = "DCFCE7"
    RED = "EF4444"
    RED_LIGHT = "FEE2E2"
    ORANGE = "F59E0B"
    ORANGE_LIGHT = "FEF3C7"
    GRAY = "6B7280"
    GRAY_LIGHT = "F3F4F6"
    WHITE = "FFFFFF"

    # Fills
    HEADER_FILL = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")
    SUBHEADER_FILL = PatternFill(start_color="764BA2", end_color="764BA2", fill_type="solid")
    SECTION_FILL = PatternFill(start_color="E9E4F0", end_color="E9E4F0", fill_type="solid")
    ANSWERED_FILL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    UNANSWERED_FILL = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    ALT_ROW_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    STAT_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    TITLE_FILL = PatternFill(start_color="667EEA", end_color="667EEA", fill_type="solid")

    # Fonts
    TITLE_FONT = Font(name='Calibri', size=24, bold=True, color="FFFFFF")
    HEADER_FONT = Font(name='Calibri', size=12, bold=True, color="FFFFFF")
    SUBHEADER_FONT = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
    SECTION_FONT = Font(name='Calibri', size=12, bold=True, color="667EEA")
    DATA_FONT = Font(name='Calibri', size=11, color="374151")
    DATA_FONT_BOLD = Font(name='Calibri', size=11, bold=True, color="1F2937")
    STAT_LABEL_FONT = Font(name='Calibri', size=11, color="374151")
    STAT_VALUE_FONT = Font(name='Calibri', size=11, bold=True, color="667EEA")

    # Borders
    BORDER_THIN = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )

    # Key requirement mappings - questions to look for
    KEY_REQUIREMENT_PATTERNS = {
        'Timeline': ['timeline', 'project duration', 'start date', 'completion date', 'schedule'],
        'Scope': ['scope', 'linear feet', 'pipe diameter', 'total footage', 'project scope'],
        'Bid Deadline': ['bid deadline', 'bid due', 'submission deadline', 'bid opening'],
        'Payment': ['payment', 'progress payment', 'retention', 'payment terms'],
        'Warranty': ['warranty', 'guarantee period', 'warranty period'],
        'Liquidated Damages': ['liquidated damages', 'delay damages', 'penalty'],
        'Bonding': ['bond', 'bid bond', 'performance bond', 'payment bond'],
        'Certifications': ['certification', 'nassco', 'pacp', 'required certifications', 'operator certification'],
        'Insurance': ['insurance', 'liability', 'coverage requirements'],
        'Location': ['location', 'project location', 'city', 'municipality'],
    }

    def __init__(self, analysis_result, is_partial=False):
        self.result = analysis_result
        self.is_partial = is_partial
        self.wb = Workbook()
        self.footnotes = self._collect_footnotes()
        self.key_requirements = self._extract_key_requirements()

    def generate(self):
        """Generate complete 4-sheet report package"""
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        self._create_executive_summary()      # Sheet 1: Executive Summary
        self._create_detailed_results()       # Sheet 2: Detailed Results
        self._create_by_section()             # Sheet 3: By Section
        self._create_footnotes_sheet()        # Sheet 4: Footnotes

        output = io.BytesIO()
        self.wb.save(output)
        output.seek(0)
        return output

    def _collect_footnotes(self):
        """Collect all footnotes from the analysis"""
        footnotes = []
        fn_num = 1
        for section in self.result.get('sections', []):
            for q in section.get('questions', []):
                fn = q.get('footnote')
                if fn and fn.strip():
                    footnotes.append({
                        'number': fn_num,
                        'section': section.get('section_name', 'Unknown'),
                        'question': q.get('question', ''),
                        'footnote': fn.strip(),
                        'pages': q.get('page_citations', [])
                    })
                    fn_num += 1
        return footnotes

    def _extract_key_requirements(self):
        """Extract key project requirements from analysis answers"""
        requirements = {}

        for section in self.result.get('sections', []):
            for q in section.get('questions', []):
                question_text = q.get('question', '').lower()
                answer = q.get('answer', '')

                if not answer or not answer.strip():
                    continue

                # Clean answer - remove PDF citations for display
                clean_answer = re.sub(r'<PDF pg[^>]+>', '', answer).strip()
                clean_answer = re.sub(r'\s+', ' ', clean_answer)

                # Truncate if too long
                if len(clean_answer) > 200:
                    clean_answer = clean_answer[:197] + '...'

                # Check against key requirement patterns
                for req_name, patterns in self.KEY_REQUIREMENT_PATTERNS.items():
                    if req_name not in requirements:
                        for pattern in patterns:
                            if pattern in question_text:
                                requirements[req_name] = clean_answer
                                break

        return requirements

    def _calculate_statistics(self):
        """Calculate overall statistics"""
        all_questions = []
        total_confidence = 0
        confidence_count = 0

        for section in self.result.get('sections', []):
            for q in section.get('questions', []):
                all_questions.append(q)
                conf = q.get('confidence', 0)
                if conf and conf > 0:
                    total_confidence += conf
                    confidence_count += 1

        total = len(all_questions)
        answered = sum(1 for q in all_questions if q.get('answer'))
        unanswered = total - answered
        answer_rate = (answered / total * 100) if total > 0 else 0
        avg_confidence = (total_confidence / confidence_count * 100) if confidence_count > 0 else 0

        return {
            'total': total,
            'answered': answered,
            'unanswered': unanswered,
            'answer_rate': answer_rate,
            'avg_confidence': avg_confidence
        }

    def _create_executive_summary(self):
        """Sheet 1: Executive Summary - Analysis statistics and key requirements"""
        ws = self.wb.create_sheet('Executive Summary', 0)
        stats = self._calculate_statistics()

        # === TITLE BANNER ===
        ws.merge_cells('A1:C2')
        title_cell = ws['A1']
        title_cell.value = 'MUNICIPAL PIPE TOOL - ANALYSIS REPORT'
        title_cell.font = self.TITLE_FONT
        title_cell.fill = self.TITLE_FILL
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 25
        ws.row_dimensions[2].height = 25

        row = 4

        # === PARTIAL RESULTS BANNER ===
        if self.is_partial:
            ws.merge_cells(f'A{row}:C{row}')
            ws[f'A{row}'] = '⚠ PARTIAL RESULTS - Analysis was stopped before completion'
            ws[f'A{row}'].font = Font(name='Calibri', size=12, bold=True, color="92400E")
            ws[f'A{row}'].fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
            ws[f'A{row}'].alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[row].height = 30
            row += 2

        # === ANALYSIS STATISTICS SECTION ===
        ws.merge_cells(f'A{row}:C{row}')
        ws[f'A{row}'] = 'Analysis Statistics'
        ws[f'A{row}'].font = self.SECTION_FONT
        ws[f'A{row}'].fill = self.SECTION_FILL
        ws[f'A{row}'].alignment = Alignment(horizontal='left', vertical='center', indent=1)
        ws.row_dimensions[row].height = 28
        row += 1

        # Statistics rows
        stat_data = [
            ('Total Questions:', str(stats['total'])),
            ('Questions Answered:', str(stats['answered'])),
            ('Answer Rate:', f"{stats['answer_rate']:.0f}%"),
            ('Average Confidence:', f"{stats['avg_confidence']:.0f}%" if stats['avg_confidence'] > 0 else 'N/A'),
            ('Analysis Date:', self._get_timestamp()),
        ]

        for idx, (label, value) in enumerate(stat_data):
            is_alt = idx % 2 == 1

            ws.cell(row, 1, label).font = self.STAT_LABEL_FONT
            ws.cell(row, 2, value).font = self.STAT_VALUE_FONT

            for col in range(1, 4):
                cell = ws.cell(row, col)
                cell.border = self.BORDER_THIN
                if is_alt:
                    cell.fill = self.ALT_ROW_FILL

            ws.row_dimensions[row].height = 22
            row += 1

        row += 1

        # === KEY PROJECT REQUIREMENTS SECTION ===
        if self.key_requirements:
            ws.merge_cells(f'A{row}:C{row}')
            ws[f'A{row}'] = 'Key Project Requirements'
            ws[f'A{row}'].font = self.SECTION_FONT
            ws[f'A{row}'].fill = self.SECTION_FILL
            ws[f'A{row}'].alignment = Alignment(horizontal='left', vertical='center', indent=1)
            ws.row_dimensions[row].height = 28
            row += 1

            # Sort requirements by a preferred order
            preferred_order = ['Timeline', 'Scope', 'Location', 'Bid Deadline', 'Payment',
                             'Warranty', 'Liquidated Damages', 'Bonding', 'Certifications', 'Insurance']

            sorted_reqs = []
            for key in preferred_order:
                if key in self.key_requirements:
                    sorted_reqs.append((key + ':', self.key_requirements[key]))

            for key, value in self.key_requirements.items():
                if key not in preferred_order:
                    sorted_reqs.append((key + ':', value))

            for idx, (label, value) in enumerate(sorted_reqs):
                is_alt = idx % 2 == 1

                ws.cell(row, 1, label).font = self.STAT_LABEL_FONT
                ws.merge_cells(f'B{row}:C{row}')
                ws.cell(row, 2, value).font = self.DATA_FONT
                ws.cell(row, 2).alignment = Alignment(wrap_text=True, vertical='top')

                for col in range(1, 4):
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    if is_alt:
                        cell.fill = self.ALT_ROW_FILL

                # Calculate dynamic row height based on content length
                # Columns B+C combined width is ~70 chars, each line ~15px height
                chars_per_line = 60
                num_lines = max(1, (len(value) // chars_per_line) + 1)
                row_height = max(25, num_lines * 18)  # Minimum 25, 18px per line
                ws.row_dimensions[row].height = row_height
                row += 1
        else:
            row += 1
            ws[f'A{row}'] = 'Key project requirements will appear here when extracted from the analysis.'
            ws[f'A{row}'].font = Font(name='Calibri', size=11, italic=True, color="6B7280")

        # Column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 35
        ws.column_dimensions['C'].width = 35

    def _create_detailed_results(self):
        """Sheet 2: Detailed Results - All Q&A in unified professional table"""
        ws = self.wb.create_sheet('Detailed Results')

        ws.merge_cells('A1:G1')
        ws['A1'] = 'COMPLETE ANALYSIS RESULTS'
        ws['A1'].font = Font(name='Calibri', size=16, bold=True, color="667EEA")
        ws['A1'].alignment = Alignment(horizontal='left', vertical='center')
        ws.row_dimensions[1].height = 30

        row = 2
        headers = ['#', 'Section', 'Question', 'Answer', 'PDF Pages', 'Footnote', 'Status']
        widths = [5, 25, 45, 60, 12, 8, 11]

        for col, (header, width) in enumerate(zip(headers, widths), start=1):
            cell = ws.cell(row, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.row_dimensions[row].height = 25

        row = 3
        question_num = 1
        current_section = None

        for section in self.result.get('sections', []):
            section_name = section.get('section_name', '')

            for q in section.get('questions', []):
                answer_text = q.get('answer') or ''
                has_answer = bool(answer_text and answer_text.strip())
                pages = q.get('page_citations', [])
                pages_str = ', '.join(map(str, pages)) if pages else '-'
                has_footnote = bool(q.get('footnote'))

                is_section_start = section_name != current_section
                is_alt_row = question_num % 2 == 0

                ws.cell(row, 1, question_num).font = self.DATA_FONT
                ws.cell(row, 1).alignment = Alignment(horizontal='center', vertical='top')

                section_cell = ws.cell(row, 2, section_name if is_section_start else '')
                if is_section_start:
                    section_cell.font = self.DATA_FONT_BOLD
                    current_section = section_name
                else:
                    section_cell.font = self.DATA_FONT

                ws.cell(row, 3, q.get('question', '')).font = self.DATA_FONT

                answer_cell = ws.cell(row, 4, answer_text if has_answer else 'Not found in document')
                if has_answer:
                    answer_cell.font = self.DATA_FONT
                else:
                    answer_cell.font = Font(name='Calibri', size=11, italic=True, color="9CA3AF")

                pages_cell = ws.cell(row, 5, pages_str)
                pages_cell.font = self.DATA_FONT_BOLD if has_answer else self.DATA_FONT
                pages_cell.alignment = Alignment(horizontal='center', vertical='top')

                fn_cell = ws.cell(row, 6, '✓' if has_footnote else '-')
                fn_cell.font = Font(name='Calibri', size=11, bold=True, color=self.GREEN if has_footnote else self.GRAY)
                fn_cell.alignment = Alignment(horizontal='center', vertical='top')

                status_cell = ws.cell(row, 7, 'Found' if has_answer else 'Not Found')
                status_cell.font = Font(name='Calibri', size=10, bold=True)
                status_cell.fill = self.ANSWERED_FILL if has_answer else self.UNANSWERED_FILL
                status_cell.alignment = Alignment(horizontal='center', vertical='top')

                for col in range(1, 8):
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    if col not in [6, 7]:
                        if is_alt_row:
                            cell.fill = self.ALT_ROW_FILL
                    cell.alignment = Alignment(
                        horizontal='left' if col in [2, 3, 4] else 'center',
                        vertical='top',
                        wrap_text=True
                    )

                ws.row_dimensions[row].height = 55
                row += 1
                question_num += 1

    def _create_by_section(self):
        """Sheet 3: By Section - Questions grouped with section breakdown"""
        ws = self.wb.create_sheet('By Section')

        row = 1
        for section_idx, section in enumerate(self.result.get('sections', [])):
            questions = section.get('questions', [])
            answered = sum(1 for q in questions if q.get('answer') and q.get('answer').strip())
            total = len(questions)
            rate = (answered / total * 100) if total > 0 else 0

            ws.merge_cells(f'A{row}:F{row}')
            header_cell = ws[f'A{row}']
            header_text = f"{section.get('section_name', 'Unknown Section').upper()}  ({answered}/{total} answered - {rate:.0f}%)"
            header_cell.value = header_text
            header_cell.font = Font(name='Calibri', size=13, bold=True, color="FFFFFF")
            header_cell.fill = self.HEADER_FILL
            header_cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
            ws.row_dimensions[row].height = 32
            row += 1

            headers = ['#', 'Question', 'Answer', 'PDF Pages', 'Notes', 'Status']
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row, col, header)
                cell.font = self.SUBHEADER_FONT
                cell.fill = self.SUBHEADER_FILL
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = self.BORDER_THIN
            ws.row_dimensions[row].height = 22
            row += 1

            for idx, q in enumerate(questions, start=1):
                answer_text = q.get('answer') or ''
                has_answer = bool(answer_text and answer_text.strip())
                pages = q.get('page_citations', [])
                pages_str = ', '.join(map(str, pages)) if pages else '-'
                is_alt = idx % 2 == 0

                ws.cell(row, 1, idx).font = self.DATA_FONT
                ws.cell(row, 1).alignment = Alignment(horizontal='center', vertical='top')

                ws.cell(row, 2, q.get('question', '')).font = self.DATA_FONT

                answer_cell = ws.cell(row, 3, answer_text if has_answer else 'Not found in document')
                if has_answer:
                    answer_cell.font = self.DATA_FONT
                else:
                    answer_cell.font = Font(name='Calibri', size=11, italic=True, color="9CA3AF")

                ws.cell(row, 4, pages_str).font = self.DATA_FONT_BOLD if has_answer else self.DATA_FONT
                ws.cell(row, 4).alignment = Alignment(horizontal='center', vertical='top')

                has_footnote = bool(q.get('footnote'))
                notes_cell = ws.cell(row, 5, 'See footnotes' if has_footnote else '-')
                notes_cell.font = Font(name='Calibri', size=10, italic=True, color=self.PURPLE if has_footnote else self.GRAY)
                notes_cell.alignment = Alignment(horizontal='center', vertical='top')

                status_cell = ws.cell(row, 6, '✓' if has_answer else '✗')
                status_cell.font = Font(name='Calibri', size=14, bold=True, color=self.GREEN if has_answer else self.RED)
                status_cell.fill = self.ANSWERED_FILL if has_answer else self.UNANSWERED_FILL
                status_cell.alignment = Alignment(horizontal='center', vertical='top')

                for col in range(1, 7):
                    cell = ws.cell(row, col)
                    cell.border = self.BORDER_THIN
                    if col != 6 and is_alt:
                        cell.fill = self.ALT_ROW_FILL
                    cell.alignment = Alignment(
                        horizontal='left' if col in [2, 3] else 'center',
                        vertical='top',
                        wrap_text=True
                    )

                ws.row_dimensions[row].height = 50
                row += 1

            row += 1

        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 45
        ws.column_dimensions['C'].width = 60
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 14
        ws.column_dimensions['F'].width = 10

    def _create_footnotes_sheet(self):
        """Sheet 4: Footnotes - All citations and contextual notes"""
        ws = self.wb.create_sheet('Footnotes')

        ws.merge_cells('A1:E1')
        ws['A1'] = 'FOOTNOTES & CITATIONS'
        ws['A1'].font = Font(name='Calibri', size=16, bold=True, color="667EEA")
        ws['A1'].alignment = Alignment(horizontal='left', vertical='center')
        ws.row_dimensions[1].height = 30

        if not self.footnotes:
            ws['A3'] = 'No footnotes were generated during this analysis.'
            ws['A3'].font = Font(name='Calibri', size=11, italic=True, color="6B7280")
            return

        ws['A2'] = f'{len(self.footnotes)} footnotes collected from analysis'
        ws['A2'].font = Font(name='Calibri', size=11, italic=True, color="6B7280")

        row = 4
        headers = ['#', 'Section', 'Related Question', 'Footnote/Citation', 'PDF Pages']
        widths = [5, 25, 40, 55, 12]

        for col, (header, width) in enumerate(zip(headers, widths), start=1):
            cell = ws.cell(row, col, header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = self.BORDER_THIN
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.row_dimensions[row].height = 25

        for fn in self.footnotes:
            row += 1
            is_alt = fn['number'] % 2 == 0

            ws.cell(row, 1, fn['number']).font = self.DATA_FONT_BOLD
            ws.cell(row, 1).alignment = Alignment(horizontal='center', vertical='top')

            ws.cell(row, 2, fn['section']).font = self.DATA_FONT
            ws.cell(row, 3, fn['question'][:100] + '...' if len(fn['question']) > 100 else fn['question']).font = self.DATA_FONT
            ws.cell(row, 4, fn['footnote']).font = self.DATA_FONT

            pages_str = ', '.join(map(str, fn['pages'])) if fn['pages'] else '-'
            ws.cell(row, 5, pages_str).font = self.DATA_FONT_BOLD
            ws.cell(row, 5).alignment = Alignment(horizontal='center', vertical='top')

            for col in range(1, 6):
                cell = ws.cell(row, col)
                cell.border = self.BORDER_THIN
                if is_alt:
                    cell.fill = self.ALT_ROW_FILL
                cell.alignment = Alignment(
                    horizontal='left' if col in [2, 3, 4] else 'center',
                    vertical='top',
                    wrap_text=True
                )

            ws.row_dimensions[row].height = 45

    def _get_timestamp(self):
        """Get formatted timestamp"""
        return datetime.now().strftime('%B %d, %Y')
