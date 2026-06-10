import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw 'Page X of Y' footers
    and a consistent running header.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b")) # slate text
        
        # Draw header (except on cover page/first page)
        if self._pageNumber > 1:
            self.drawString(54, 750, "LERNIX - CurrHub Pro: Industry-Aligned Curriculum Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
        # Draw footer (all pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, footer_text)
        self.drawString(54, 36, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered by AI")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, letter[0] - 54, 48)
        
        self.restoreState()


def generate_curriculum_pdf(curriculum_data):
    """
    Generates a beautifully typeset PDF of the curriculum data using ReportLab
    and returns it as a bytes buffer.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom, premium typography
    primary_color = colors.HexColor("#4f46e5")    # Indigo
    secondary_color = colors.HexColor("#0f172a")  # Dark Slate
    accent_color = colors.HexColor("#0891b2")     # Cyan
    border_color = colors.HexColor("#e2e8f0")
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary_color,
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#475569"),
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=secondary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b")
    )
    
    story = []
    
    # --- Title / Cover Section ---
    story.append(Spacer(1, 40))
    story.append(Paragraph(curriculum_data['title'], title_style))
    story.append(Paragraph(f"Field of Study: {curriculum_data['field_of_study']}", subtitle_style))
    
    # Metadata block table
    meta_data = [
        [Paragraph("Duration:", meta_label_style), Paragraph(f"{curriculum_data['duration_semesters']} Semesters", body_style),
         Paragraph("Total Courses:", meta_label_style), Paragraph(str(sum(len(sem['courses']) for sem in curriculum_data['semesters'])), body_style)],
        [Paragraph("Generated By:", meta_label_style), Paragraph("CurrHub Pro (LERNIX AI)", body_style),
         Paragraph("Design Paradigm:", meta_label_style), Paragraph("Outcome-Based Education (OBE)", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[1.2*inch, 2.2*inch, 1.2*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))
    
    # Scope and standard sources
    story.append(Paragraph("<b>Primary Resource References:</b>", h2_style))
    for src in curriculum_data.get("resource_sources", ["LERNIX AI Engine"]):
        story.append(Paragraph(f"• {src}", bullet_style))
        
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # --- Semesters & Courses Detail ---
    for sem in curriculum_data['semesters']:
        sem_num = sem['semester_number']
        story.append(Paragraph(f"Semester {sem_num}", h1_style))
        story.append(Spacer(1, 5))
        
        for course in sem['courses']:
            course_story = []
            
            # Header card style for course
            c_header = f"<b>{course['code']}: {course['name']}</b> ({course['credits']} Credits)"
            course_story.append(Paragraph(c_header, h2_style))
            
            # Summary stats
            stats_text = (
                f"<b>Difficulty:</b> {course['difficulty']} | "
                f"<b>weekly time:</b> {course.get('weekly_hours', 6)} hours | "
                f"<b>Relevance:</b> {course.get('industry_relevance_score', 90)}%"
            )
            course_story.append(Paragraph(stats_text, body_style))
            course_story.append(Paragraph(course['description'], body_style))
            
            # Prereqs
            prereqs = ", ".join(course['prerequisites']) if course['prerequisites'] else "None"
            course_story.append(Paragraph(f"<b>Prerequisites:</b> {prereqs}", body_style))
            
            # Outcomes list
            course_story.append(Paragraph("<b>Learning Outcomes:</b>", meta_label_style))
            for outcome in course['learning_outcomes']:
                course_story.append(Paragraph(f"• {outcome}", bullet_style))
            
            # Career Opportunities
            careers = ", ".join(course.get('career_opportunities', []))
            if careers:
                course_story.append(Paragraph(f"<b>Career Pathways:</b> {careers}", body_style))
                
            # Projects
            projects = ", ".join(course.get('recommended_projects', []))
            if projects:
                course_story.append(Paragraph(f"<b>Recommended Capstones:</b> {projects}", body_style))
                
            # Assessment
            assessments = ", ".join(course.get('assessment_methods', []))
            if assessments:
                course_story.append(Paragraph(f"<b>Assessments:</b> {assessments}", body_style))
                
            # Reference Resources Table (Tabular Form, No Empty Spaces)
            resources = course.get('resources')
            if not resources:
                skills = course.get("key_skills", ["IT"])
                skill_name = skills[0] if skills else "Technology"
                resources = [
                    {"title": f"ACM/IEEE Guidelines on {course.get('name', 'this course')}", "url": "https://www.acm.org"},
                    {"title": f"IBM Cognitive Class: {skill_name}", "url": "https://cognitiveclass.ai"}
                ]
                course['resources'] = resources
                
            resource_data = [
                [Paragraph("<b>Resource Reference Title</b>", meta_label_style), 
                 Paragraph("<b>Access Link</b>", meta_label_style)]
            ]
            for res in resources:
                link_url = res.get('url', 'https://www.acm.org')
                link_html = f'<a href="{link_url}" color="#0891b2"><u>{link_url}</u></a>'
                resource_data.append([
                    Paragraph(res.get('title', 'Academic Guidelines'), body_style),
                    Paragraph(link_html, body_style)
                ])
                
            res_table = Table(resource_data, colWidths=[2.8*inch, 4.0*inch])
            res_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            
            course_story.append(Spacer(1, 6))
            course_story.append(Paragraph("<b>Reference Learning Resources:</b>", meta_label_style))
            course_story.append(Spacer(1, 4))
            course_story.append(res_table)
            
            course_story.append(Spacer(1, 12))
            
            # Add line separator
            sep_table = Table([['']], colWidths=[6.8*inch])
            sep_table.setStyle(TableStyle([
                ('LINEBELOW', (0,0), (-1,-1), 1.0, border_color),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            course_story.append(sep_table)
            course_story.append(Spacer(1, 8))
            
            # Wrap each course details to keep them together if possible
            story.append(KeepTogether(course_story))
            
        story.append(Spacer(1, 15))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
