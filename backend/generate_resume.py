"""
Sahil Nawaz — Professional Resume Generator (ATS-Friendly, Single-Page, ReportLab)
Generates Sahil_Nawaz_Resume.pdf conforming to principal software engineering standards.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

def build_resume(output_path="frontend/Sahil_Nawaz_Resume.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Page setup: letter (8.5 x 11 in) with 0.45 in (32.4 pt) margins
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=32.4,
        rightMargin=32.4,
        topMargin=28.0,
        bottomMargin=28.0
    )

    styles = getSampleStyleSheet()

    # Color Palette: Clean white background, charcoal/black text, coral-pink accents
    COLOR_PRIMARY = colors.HexColor("#1a1514")       # Dark Charcoal / Black
    COLOR_SECONDARY = colors.HexColor("#4a3f3b")     # Subtle slate
    COLOR_ACCENT = colors.HexColor("#df7568")        # Brand Coral-Pink
    COLOR_BORDER = colors.HexColor("#f3b5aa")        # Soft coral border
    COLOR_LINK = colors.HexColor("#cf6255")          # Coral-pink link

    # Custom Typography Styles
    style_name = ParagraphStyle(
        "ResumeName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=22,
        textColor=COLOR_PRIMARY,
        alignment=0
    )

    style_title = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=COLOR_ACCENT,
        alignment=0
    )

    style_contact = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=11.5,
        textColor=COLOR_SECONDARY,
        alignment=0
    )

    style_contact_links = ParagraphStyle(
        "ResumeContactLinks",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=11.5,
        textColor=COLOR_LINK,
        alignment=0
    )

    style_section_heading = ParagraphStyle(
        "ResumeSectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=COLOR_PRIMARY,
        textTransform="uppercase",
        spaceAfter=2
    )

    style_body = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=11,
        textColor=COLOR_PRIMARY
    )

    style_bold_item = ParagraphStyle(
        "ResumeBoldItem",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_PRIMARY
    )

    style_meta_item = ParagraphStyle(
        "ResumeMetaItem",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.0,
        leading=10.5,
        textColor=COLOR_SECONDARY,
        alignment=2 # Right aligned
    )

    style_bullet = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.0,
        leading=10.8,
        textColor=COLOR_SECONDARY,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=1.5
    )

    style_skill_label = ParagraphStyle(
        "ResumeSkillLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.2,
        leading=11,
        textColor=COLOR_PRIMARY
    )

    story = []

    # 1. HEADER (Name, Title, Contact Info, Direct Links)
    header_left = [
        Paragraph("SAHIL NAWAZ", style_name),
        Spacer(1, 1),
        Paragraph("FORWARD DEPLOYED DEVELOPER", style_title),
    ]
    header_right = [
        Paragraph("<b>Location:</b> Bihar, India &nbsp;|&nbsp; <b>Mobile:</b> +91 7323018308", style_contact),
        Paragraph("<b>Email:</b> <font color='#cf6255'>sahilnawaaz257@gmail.com</font>", style_contact),
        Paragraph("<b>GitHub:</b> github.com/sahilnawaz257 &nbsp;|&nbsp; <b>LinkedIn:</b> in/ali-sahil-nawaz-622b58213", style_contact_links),
        Paragraph("<b>LeetCode:</b> leetcode.com/u/Alisahilnawaz", style_contact_links),
    ]

    header_table = Table(
        [[header_left, header_right]],
        colWidths=[240, 307]
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.2, color=COLOR_ACCENT, spaceBefore=1, spaceAfter=5))

    # Helper function for section headings with subtle accent line
    def add_section_header(title):
        story.append(Paragraph(title, style_section_heading))
        story.append(HRFlowable(width="100%", thickness=0.6, color=COLOR_BORDER, spaceBefore=1, spaceAfter=4))

    # 2. PROFESSIONAL SUMMARY
    add_section_header("Professional Summary")
    summary_text = (
        "Forward Deployed Developer with a solid computer science foundation and full-stack software engineering proficiency. "
        "Experienced in bridging technical implementation with strategic product goals, building resilient web applications, "
        "integrating machine learning pipelines, and delivering customer-centric digital solutions. Founder of Gymsewa "
        "(powered by Bytewave Innovation), with a hands-on track record in system architecture, algorithmic problem-solving, "
        "and production operations."
    )
    story.append(Paragraph(summary_text, style_body))
    story.append(Spacer(1, 6))

    # 3. TECHNICAL & BUSINESS SKILLS
    add_section_header("Technical & Business Competencies")
    skills_data = [
        [
            Paragraph("<b>Programming Languages:</b>", style_skill_label),
            Paragraph("Python, C, C++, SQL", style_body)
        ],
        [
            Paragraph("<b>Frontend Engineering:</b>", style_skill_label),
            Paragraph("HTML5, CSS3, JavaScript (ES6+), React JS, Responsive UI/UX", style_body)
        ],
        [
            Paragraph("<b>Data & Machine Learning:</b>", style_skill_label),
            Paragraph("NumPy, Pandas, Data Analysis, Artificial Intelligence, YOLOv8, LangChain (RAG)", style_body)
        ],
        [
            Paragraph("<b>Databases & Developer Tools:</b>", style_skill_label),
            Paragraph("PostgreSQL (Supabase), SQLite, Git, GitHub, RESTful APIs, Flask", style_body)
        ],
        [
            Paragraph("<b>Core Professional Areas:</b>", style_skill_label),
            Paragraph("Forward Deployed Development, Product Development, Business Strategy, Solution Delivery", style_body)
        ],
    ]
    skills_table = Table(skills_data, colWidths=[130, 417])
    skills_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 6))

    # 4. EXPERIENCE
    add_section_header("Professional Experience")
    exp_header = Table([
        [
            Paragraph("<b>Founder & Product Strategist — Gymsewa</b> &nbsp;|&nbsp; <i>Powered by Bytewave Innovation</i>", style_bold_item),
            Paragraph("2024 – Present", style_meta_item)
        ]
    ], colWidths=[430, 117])
    exp_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(exp_header)
    story.append(Paragraph("• Spearheaded end-to-end digital product planning, technical architecture, and platform roadmap for fitness enterprise management.", style_bullet))
    story.append(Paragraph("• Directed operational workflows, customer-facing technical design, and service automation under Bytewave Innovation.", style_bullet))
    story.append(Paragraph("• Formulated business development and user onboarding strategies to ensure long-term platform scalability and operational resilience.", style_bullet))
    story.append(Spacer(1, 6))

    # 5. PROJECTS
    add_section_header("Selected Engineering Projects")
    
    # Project 1: Crowd Density Counting System
    p1_header = Table([
        [
            Paragraph("<b>Crowd Density Counting System</b> &nbsp;|&nbsp; <i>Python, Computer Vision, YOLOv8</i>", style_bold_item),
            Paragraph("AI & Vision", style_meta_item)
        ]
    ], colWidths=[430, 117])
    p1_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(p1_header)
    story.append(Paragraph("• Built an automated computer vision pipeline leveraging YOLOv8 object detection to calculate real-time crowd density and occupancy metrics.", style_bullet))
    story.append(Paragraph("• Designed spatial heatmapping visualizers and automated threshold triggers for venue capacity monitoring and crowd safety management.", style_bullet))
    story.append(Spacer(1, 3))

    # Project 2: Library Management Software
    p2_header = Table([
        [
            Paragraph("<b>Library Management Software</b> &nbsp;|&nbsp; <i>Python, SQL, Relational Architecture</i>", style_bold_item),
            Paragraph("Database Systems", style_meta_item)
        ]
    ], colWidths=[430, 117])
    p2_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(p2_header)
    story.append(Paragraph("• Engineered a relational inventory management system with robust ACID transaction support for book circulation and catalog management.", style_bullet))
    story.append(Paragraph("• Developed membership tracking, due-date calculation routines, fine-accrual algorithms, and SQL query optimizations.", style_bullet))
    story.append(Spacer(1, 3))

    # Project 3: Brand Guideline Audit Tool
    p3_header = Table([
        [
            Paragraph("<b>Brand Guideline Audit Tool</b> &nbsp;|&nbsp; <i>Frontend Engineering, Asset Verification</i>", style_bold_item),
            Paragraph("Design Systems", style_meta_item)
        ]
    ], colWidths=[430, 117])
    p3_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(p3_header)
    story.append(Paragraph("• Created an automated compliance tool verifying digital design assets against official typography, hex palettes, and layout hierarchies.", style_bullet))
    story.append(Paragraph("• Streamlined developer-designer collaboration by highlighting styling discrepancies and generating actionable compliance audit summaries.", style_bullet))
    story.append(Spacer(1, 6))

    # 6. EDUCATION
    add_section_header("Education & Academic Background")
    
    # Record 1: JB Group
    edu1_header = Table([
        [
            Paragraph("<b>JB Group of Institutions of Technology</b> &nbsp;|&nbsp; B.Tech in Computer Science and Engineering", style_bold_item),
            Paragraph("2025 – 2029", style_meta_item)
        ]
    ], colWidths=[430, 117])
    edu1_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(edu1_header)
    story.append(Paragraph("• Location: Dehradun, Uttarakhand, India &nbsp;|&nbsp; Focus: Data Structures, Algorithmic Analysis, and System Architecture", style_bullet))
    story.append(Spacer(1, 3))

    # Record 2: The Open University
    edu2_header = Table([
        [
            Paragraph("<b>The Open University</b> &nbsp;|&nbsp; Data Analyst Online, Computer Science", style_bold_item),
            Paragraph("June 2026 – July 2029", style_meta_item)
        ]
    ], colWidths=[430, 117])
    edu2_header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(edu2_header)
    story.append(Paragraph("• Focus: Artificial Intelligence, Retrieval-Augmented Generation (RAG), and LangChain Frameworks", style_bullet))

    doc.build(story)
    print(f"[SUCCESS] Resume generated successfully at: {output_path}")

if __name__ == "__main__":
    build_resume()
