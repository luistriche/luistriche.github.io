#!/usr/bin/env python3
"""
Multi-role CV Generator — Genera CVs adaptados a cada puesto
Uso: python3 generate_cv.py [role]

Roles: data-scientist | learning-analytics | ml-engineer | edtech-consultant | default
"""
import sys, os, json
from fpdf import FPDF

ROLES = {
    "default": {
        "title": "Data Scientist & Learning Analytics Specialist",
        "summary": "Data Scientist with a unique hybrid profile: B.A. in Educational Sciences combined with 3 Google Professional Certifications and 100+ hands-on data science projects. 11 years bridging pedagogy and technology.",
        "highlights": [
            "100+ data science projects across 15+ domains",
            "3x Google Certified (Data Analytics, Advanced Data Analytics, BI)",
            "B.A. Educational Sciences + B.S. Data Science (in progress)",
            "11 years combining education and technology"
        ]
    },

    "data-scientist": {
        "title": "Data Scientist",
        "summary": "Data Scientist with 100+ end-to-end projects across finance, health, NLP, and computer vision. 3 Google certifications. Proven ability to deliver production-ready ML models and data pipelines.",
        "highlights": [
            "Built 100+ data science projects in 15+ domains",
            "3x Google Certified (Data Analytics, Advanced Data Analytics, BI)",
            "Developed AI agents, RAG systems, and NLP pipelines",
            "Proficient in Python, scikit-learn, TensorFlow, Streamlit"
        ]
    },
    "learning-analytics": {
        "title": "Learning Analytics Specialist",
        "summary": "Educational Sciences graduate with 11 years bridging pedagogy and data science. Designs data-driven learning systems, assessment frameworks, and personalized learning pathways.",
        "highlights": [
            "11 years combining education and technology",
            "B.A. Educational Sciences + Data Science degree",
            "Built EdTech platforms, NLP essay graders, and skill gap analyzers",
            "Google-certified in Data Analytics and BI"
        ]
    },
    "ml-engineer": {
        "title": "Machine Learning Engineer",
        "summary": "Hands-on ML engineer with 100+ projects. Expertise in NLP (Transformers, BERT), computer vision (CNN, DenseNet), time series (LSTM, Prophet), and MLOps with multiple LLM APIs.",
        "highlights": [
            "100+ ML/DL projects from regression to transformers",
            "Experience with Gemini, OpenRouter, DeepSeek, Mistral APIs",
            "Built RAG systems, chatbots, and real-time ML pipelines",
            "Proficient in TensorFlow, PyTorch, scikit-learn, Docker"
        ]
    },
    "edtech-consultant": {
        "title": "EdTech & Data Consultant",
        "summary": "Independent consultant helping educational institutions and EdTech companies leverage data for learning outcomes. Combines rigorous Google certifications with 11 years of pedagogical experience.",
        "highlights": [
            "11 years at the intersection of education and data",
            "3 Google Certifications + B.A. Educational Sciences",
            "Built learning analytics platforms and assessment tools",
            "Bilingual: Spanish native, English professional (technical)"
        ]
    }
}

def generate_cv(role="default"):
    profile = ROLES.get(role, ROLES["default"])
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    DARK, PRIMARY, GRAY = (26, 26, 46), (255, 107, 53), (100, 100, 100)

    # Header
    pdf.set_fill_color(*DARK)
    pdf.rect(0, 0, 210, 50, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_xy(20, 10)
    pdf.cell(0, 10, 'LUIS TRICHE')
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(*PRIMARY)
    pdf.set_xy(20, 22)
    pdf.cell(0, 8, profile["title"])
    pdf.set_text_color(200, 200, 200)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_xy(20, 33)
    pdf.cell(0, 5, 'Tijuana, Mexico  |  luistriche501@gmail.com  |  linkedin.com/in/luistriche')

    y = 62
    for section_data in [
        ("PROFESSIONAL SUMMARY", [profile["summary"]], False),
        ("KEY QUALIFICATIONS", profile["highlights"], True),
        ("CERTIFICATIONS", [
            "Google Data Analytics (2024)",
            "Google Advanced Data Analytics (2024)",
            "Google Business Intelligence (2024)"
        ], True),
    ]:
        pdf.set_text_color(*DARK)
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_xy(20, y)
        pdf.cell(0, 8, section_data[0])
        pdf.set_draw_color(*PRIMARY)
        pdf.set_line_width(0.5)
        pdf.line(20, y+9, 190, y+9)
        y += 14

        if section_data[2]:
            for item in section_data[1]:
                pdf.set_text_color(50, 50, 50)
                pdf.set_font('Helvetica', '', 9)
                pdf.set_xy(22, y)
                pdf.cell(4, 5, '-')
                pdf.set_x(28)
                pdf.multi_cell(160, 5, item)
                y = pdf.get_y()
            y += 2
        else:
            pdf.set_text_color(50, 50, 50)
            pdf.set_font('Helvetica', '', 9.5)
            pdf.set_xy(20, y)
            pdf.multi_cell(170, 5, section_data[1][0])
            y = pdf.get_y() + 4

    # Save
    filename = f"/tmp/opencode/Luis_Triche_CV_{role}.pdf"
    pdf.output(filename)
    print(f"✅ CV generated: {filename} ({pdf.pages_count} pages)")
    return filename

if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "default"
    if role not in ROLES and role != "default":
        print(f"Roles disponibles: {', '.join(ROLES.keys())}")
        sys.exit(1)
    generate_cv(role)
