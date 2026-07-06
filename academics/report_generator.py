from django.db.models import Avg
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from .models import Submission, StudentProfile, SchoolTerm


class ReportGenerator:
    """Generate ZIMSEC-style termly reports"""

    @staticmethod
    def generate_termly_report(student_id, term_id):
        """Generate PDF report for a student"""

        student = StudentProfile.objects.get(id=student_id)
        term = SchoolTerm.objects.get(id=term_id)

        # Get all submissions for this term
        submissions = Submission.objects.filter(
            student=student,
            assignment__term=term,
            is_marked=True
        ).select_related('assignment__subject')

        # Group by subject
        subject_data = {}
        for sub in submissions:
            subject_name = sub.assignment.subject.name
            if subject_name not in subject_data:
                subject_data[subject_name] = {
                    'marks': [],
                    'max_marks': sub.assignment.max_marks,
                    'count': 0
                }
            subject_data[subject_name]['marks'].append(sub.marks_obtained)
            subject_data[subject_name]['count'] += 1

        # Calculate averages and ZIMSEC grades
        for subject, data in subject_data.items():
            avg = sum(data['marks']) / len(data['marks']) if data['marks'] else 0
            data['average'] = round(avg, 1)
            data['grade'] = ReportGenerator.get_zimsec_grade(avg, student.current_form)

        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # Content
        elements = []

        # Header
        elements.append(Paragraph(f"EduGrid - Academic Report", title_style))
        elements.append(Paragraph(f"Student: {student.user.full_name}", styles['Heading2']))
        elements.append(Paragraph(f"Student ID: {student.student_id}", styles['Normal']))
        elements.append(Paragraph(f"Form: {student.current_form}", styles['Normal']))
        elements.append(Paragraph(f"Term: {term}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Subject table
        table_data = [['Subject', 'Marks Obtained', 'Average', 'Grade', 'Status']]

        for subject, data in subject_data.items():
            marks_str = ', '.join([str(m) for m in data['marks']])
            status = 'Excellent' if data['average'] >= 70 else 'Good' if data['average'] >= 50 else 'Needs Improvement'
            table_data.append([
                subject,
                marks_str,
                f"{data['average']}%",
                data['grade'],
                status
            ])

        # Add overall average row
        all_marks = [m for data in subject_data.values() for m in data['marks']]
        overall_avg = sum(all_marks) / len(all_marks) if all_marks else 0

        table_data.append([
            '<b>TOTAL</b>',
            '',
            f'<b>{round(overall_avg, 1)}%</b>',
            ReportGenerator.get_zimsec_grade(overall_avg, student.current_form),
            ''
        ])

        table = Table(table_data, colWidths=[100, 100, 80, 60, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 30))

        # Signature section
        elements.append(Paragraph("School Stamp & Signature", styles['Normal']))
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("_________________________", styles['Normal']))
        elements.append(Paragraph("Head of Department", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        return buffer

    @staticmethod
    def get_zimsec_grade(percentage, form):
        """Convert percentage to ZIMSEC grade (O-Level and A-Level)"""

        if 'A' in form:  # A-Level
            if percentage >= 80: return 'A'
            if percentage >= 70: return 'B'
            if percentage >= 60: return 'C'
            if percentage >= 50: return 'D'
            if percentage >= 40: return 'E'
            return 'F'
        else:  # O-Level (0-9 scale)
            if percentage >= 80: return '1 (Distinction)'
            if percentage >= 70: return '2'
            if percentage >= 60: return '3'
            if percentage >= 50: return '4'
            if percentage >= 40: return '5'
            if percentage >= 30: return '6'
            if percentage >= 20: return '7'
            if percentage >= 10: return '8'
            return '9'