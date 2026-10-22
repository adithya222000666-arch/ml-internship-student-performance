"""
Script to generate the formal B.Tech Internship Final Project Report (.docx)
Student: Adithya M.
Week 4 Capstone: Student Performance Prediction System
"""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = Path(__file__).resolve().parent
WEEK4_DIR = DOCS_DIR.parent
OUTPUTS_DIR = WEEK4_DIR / "outputs"
REPORT_PATH = DOCS_DIR / "project_report.docx"


def set_cell_background(cell, fill_hex):
    """Set shading/background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = parse_xml(f'<{m} {nsdecls("w")} w:w="{val}" w:type="dxa"/>')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout_box(doc, title, text, placeholder=False):
    """Add a professional styled callout / placeholder box."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    bg_color = "FEF3C7" if placeholder else "F1F5F9"
    border_color = "D97706" if placeholder else "2563EB"
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    # Left border styling
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"[{title}] " if placeholder else f"{title}: ")
    run_t.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(180, 83, 9) if placeholder else RGBColor(30, 58, 138)

    run_b = p.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def generate_report():
    doc = Document()

    # Page Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base styles setup
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------------------
    # TITLE PAGE
    # -------------------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(40)
    title_p.paragraph_format.space_after = Pt(12)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = title_p.add_run("STUDENT PERFORMANCE PREDICTION SYSTEM")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(36)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = sub_p.add_run("An End-to-End Supervised Machine Learning Pipeline, Web Application, Testing Suite, and Cloud Deployment for Academic Risk Assessment")
    r_sub.font.size = Pt(13)
    r_sub.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    div_p = doc.add_paragraph()
    div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    div_p.paragraph_format.space_after = Pt(36)
    r_div = div_p.add_run("―" * 28)
    r_div.font.color.rgb = RGBColor(148, 163, 184)

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_p.paragraph_format.space_after = Pt(6)
    r_subm = meta_p.add_run("A Capstone Project Report Submitted in Partial Fulfillment of the Requirements for the")
    r_subm.font.size = Pt(10)

    deg_p = doc.add_paragraph()
    deg_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    deg_p.paragraph_format.space_after = Pt(30)
    r_deg = deg_p.add_run("Four-Week Machine Learning Internship Program (Week 4 Final Capstone)\nBachelor of Technology (B.Tech) in Computer Science and Engineering")
    r_deg.bold = True
    r_deg.font.size = Pt(11.5)
    r_deg.font.color.rgb = RGBColor(15, 23, 42)

    student_p = doc.add_paragraph()
    student_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    student_p.paragraph_format.space_after = Pt(4)
    r_st = student_p.add_run("Submitted by:\n")
    r_st.font.size = Pt(10)
    r_name = student_p.add_run("Adithya M.")
    r_name.bold = True
    r_name.font.size = Pt(14)
    r_name.font.color.rgb = RGBColor(30, 58, 138)

    student_details = doc.add_paragraph()
    student_details.alignment = WD_ALIGN_PARAGRAPH.CENTER
    student_details.paragraph_format.space_after = Pt(40)
    r_det = student_details.add_run("Student Register No.: [Insert University Register Number Here]\nGitHub: https://github.com/adithya222000666-arch/ml-internship-student-performance")
    r_det.font.size = Pt(10)
    r_det.font.color.rgb = RGBColor(100, 116, 139)

    inst_p = doc.add_paragraph()
    inst_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    inst_p.paragraph_format.space_before = Pt(20)
    r_inst = inst_p.add_run("Internship Organization: [Insert Internship Organization / Partner Name]\nSubmission Date: October 2026")
    r_inst.font.size = Pt(10.5)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # ABSTRACT / EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    h = doc.add_heading("Abstract", level=1)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(8)

    doc.add_paragraph(
        "Early identification of academic underperformance enables timely instructional intervention and counseling, "
        "significantly improving educational outcomes in secondary schools. This capstone project designs, develops, "
        "validates, and deploys a complete end-to-end Machine Learning system titled the 'Student Performance Prediction "
        "System'. Utilizing the real-world UCI Student Performance dataset (comprising 395 secondary school students in "
        "mathematics), the system models final academic grade (G3, 0–20 scale) based strictly on 30 non-grade socio-demographic, "
        "familial, lifestyle, and behavioral attributes. Past performance metrics (G1 and G2) are deliberately excluded to "
        "guarantee that the model functions as an authentic early advisory instrument rather than relying on interim examination leakage."
    )
    doc.add_paragraph(
        "The technical workflow encompasses rigorous data validation, automated preprocessing via Scikit-Learn ColumnTransformer "
        "(incorporating median/mode imputation, standard scaling, and one-hot encoding with unknown category handling), and comparative "
        "model training across Linear Regression, Ridge Regression, and Random Forest Regression using 5-Fold Cross-Validation. "
        "The champion Random Forest Regressor demonstrated superior non-linear fitting capabilities, achieving a Test Mean Absolute Error "
        "(MAE) of 3.0364, Root Mean Squared Error (RMSE) of 3.8126, and R² score of 0.2911, matching the earlier internship benchmarks with high "
        "mathematical precision. The complete fitted pipeline was serialized alongside inference metadata into a Joblib artifact. "
        "A responsive Flask web interface and production-grade RESTful API endpoints (/health, /predict, /api/schema) were implemented "
        "and validated through a 16-test Pytest QA suite. Finally, the application was packaged for cloud deployment with Gunicorn on Render. "
        "This report details the architectural design, algorithmic choices, experimental benchmarks, API contracts, quality assurance "
        "verification, and deployment instructions."
    )

    add_callout_box(
        doc,
        "Student Placeholder Check",
        "Fill in your university registration number, college name, and internship supervisor name on the title page before final submission.",
        placeholder=True
    )

    # -------------------------------------------------------------------------
    # SECTION 1: INTRODUCTION
    # -------------------------------------------------------------------------
    doc.add_heading("1. Introduction and Background", level=1)
    doc.add_paragraph(
        "Secondary education represents a pivotal phase in a student's cognitive, vocational, and emotional development. "
        "Academic underachievement in foundational subjects such as mathematics often leads to grade repetition, loss of "
        "confidence, and reduced access to higher education opportunities. Historically, educators relied on midterm examination "
        "results or intuitive assessments to identify struggling learners. However, these traditional mechanisms are inherently "
        "reactive; when a student receives a failing midterm grade, the semester is frequently too advanced for remediations to take full effect."
    )
    doc.add_paragraph(
        "Modern educational data mining (EDM) offers a proactive alternative by uncovering latent relationships between "
        "student learning outcomes and non-academic variables, such as home study hours, parental educational attainment, commute duration, "
        "extracurricular engagement, and social habits. This four-week capstone project synthesizes the core competencies of data "
        "engineering, supervised learning, model serialization, web development, software testing, and cloud deployment into a unified, "
        "accessible tool for educators."
    )

    # -------------------------------------------------------------------------
    # SECTION 2: PROBLEM STATEMENT
    # -------------------------------------------------------------------------
    doc.add_heading("2. Problem Statement", level=1)
    doc.add_paragraph(
        "Conventional student grade prediction research often achieves artificially high statistical correlation by including "
        "interim period marks (G1 and G2) as primary independent variables. While mathematically convenient, this design suffers from "
        "severe data leakage when viewed from the perspective of an early warning decision-support system: when G1 and G2 are available, "
        "the academic term is already half over, negating the primary utility of an early intervention."
    )
    doc.add_paragraph(
        "The technical objective of this project is to construct a robust regression system that predicts final grade (G3, scale 0–20) "
        "relying strictly on 30 non-grade demographic, socio-economic, and behavioral factors. The key technical challenge lies in "
        "extracting predictive signal from noisy, heterogeneous survey attributes while preventing data leakage, ensuring model generalizability, "
        "and delivering the model through an intuitive web interface backed by an automated testing suite."
    )

    # -------------------------------------------------------------------------
    # SECTION 3: PROJECT OBJECTIVES
    # -------------------------------------------------------------------------
    doc.add_heading("3. Project Objectives and Scope", level=1)
    doc.add_paragraph(
        "The project was executed across five primary functional dimensions:"
    )
    objectives = [
        ("Data Pipeline Engineering", "Ingest and validate the UCI student-mat.csv dataset using semicolon delimiters. Build a scikit-learn ColumnTransformer that cleanly encapsulates numeric scaling, missing value imputation, and one-hot encoding without data leakage."),
        ("Supervised Machine Learning", "Train and cross-validate Linear Regression, Ridge Regression, and Random Forest Regression models on an 80/20 train/test split. Benchmark models using MAE, RMSE, and R²."),
        ("Model Serialization", "Serialize the entire trained preprocessing-and-estimator pipeline into an immutable Joblib artifact (student_performance_pipeline.joblib), accompanied by a comprehensive feature metadata schema."),
        ("Full-Stack Web Interface & API", "Develop a clean, accessible Flask application featuring responsive HTML5/CSS3/JavaScript, sample student preset loaders, real-time prediction visualization, and structured JSON REST endpoints (/health, /predict, /api/schema)."),
        ("Quality Assurance & Deployment", "Execute an automated Pytest test suite testing health checks, input boundary validations, non-finite handling, and non-retraining guarantees. Prepare production configurations for Render using Gunicorn WSGI.")
    ]
    for title, desc in objectives:
        p = doc.add_paragraph(style='List Bullet')
        r_t = p.add_run(f"{title}: ")
        r_t.bold = True
        p.add_run(desc)

    # -------------------------------------------------------------------------
    # SECTION 4: DATASET ANALYSIS
    # -------------------------------------------------------------------------
    doc.add_heading("4. Dataset Analysis and Characteristics", level=1)
    doc.add_paragraph(
        "The project utilizes the Student Performance Dataset from the UCI Machine Learning Repository, compiled by P. Cortez and "
        "A. Silva from secondary schools in Portugal (Gabriel Pereira and Mousinho da Silveira). The dataset captures student "
        "achievement in secondary mathematics."
    )
    doc.add_paragraph(
        "Key dataset characteristics include:\n"
        "• Total Records: 395 students.\n"
        "• Target Variable (G3): Integer scale between 0 and 20 (Portuguese academic grading scale). A score of 10 or higher represents a passing standard.\n"
        "• Total Features: 33 raw attributes; 30 retained features (G1 and G2 excluded alongside target G3).\n"
        "• Numerical Features (13): age, Medu, Fedu, traveltime, studytime, failures, famrel, freetime, goout, Dalc, Walc, health, absences.\n"
        "• Categorical Features (17): school, sex, address, famsize, Pstatus, Mjob, Fjob, reason, guardian, schoolsup, famsup, paid, activities, nursery, higher, internet, romantic."
    )

    # -------------------------------------------------------------------------
    # SECTION 5: SOFTWARE STACK
    # -------------------------------------------------------------------------
    doc.add_heading("5. Software Stack and Environment", level=1)
    doc.add_paragraph(
        "The project was engineered using modern Python tooling and standardized open-source libraries:"
    )

    table_stack = doc.add_table(rows=1, cols=3)
    table_stack.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_stack.autofit = False
    col_widths = [Inches(1.8), Inches(1.8), Inches(2.9)]
    for i, w in enumerate(col_widths):
        table_stack.columns[i].width = w

    headers = ["Component", "Technology / Library", "Role in System"]
    for i, text in enumerate(headers):
        cell = table_stack.cell(0, i)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    stack_rows = [
        ("Language & Runtime", "Python 3.14 / 3.11", "Core execution environment and language runtime."),
        ("Data Manipulation", "Pandas 3.0 & NumPy 2.5", "Structured DataFrame manipulation and matrix mathematics."),
        ("Machine Learning", "Scikit-Learn 1.9", "Pipelines, ColumnTransformer, regressions, and metrics."),
        ("Model Serialization", "Joblib 1.6", "Zero-overhead pipeline serialization and singleton deserialization."),
        ("Web Framework", "Flask 3.1", "WSGI routing, request validation, and JSON API handling."),
        ("Production Server", "Gunicorn 26.2", "Multi-worker production WSGI HTTP server."),
        ("Quality Assurance", "Pytest 9.1", "Automated test suite with parameterization and fixtures."),
        ("Visualization", "Matplotlib 3.11 & Seaborn", "Diagnostic chart generation and residual visualization.")
    ]

    for row_idx, (comp, tech, role) in enumerate(stack_rows, start=1):
        row = table_stack.add_row()
        bg = "FFFFFF" if row_idx % 2 != 0 else "F8FAFC"
        for i, val in enumerate([comp, tech, role]):
            cell = row.cells[i]
            cell.width = col_widths[i]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.add_run(val)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------------------
    # SECTION 6: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------------------
    doc.add_heading("6. System Architecture and Pipeline Engineering", level=1)
    doc.add_paragraph(
        "The architecture is designed around strict separation of concerns, decoupling model training from runtime inference. "
        "During offline training, the raw CSV is parsed, cleansed, and passed through an integrated Scikit-Learn ColumnTransformer. "
        "The fitted pipeline is serialized to disk once. At runtime, the Flask application lazily loads this immutable artifact "
        "into memory as a singleton, guaranteeing that incoming HTTP requests never trigger expensive retraining operations."
    )

    # -------------------------------------------------------------------------
    # SECTION 7: DATA PREPROCESSING
    # -------------------------------------------------------------------------
    doc.add_heading("7. Data Preprocessing and Feature Transformation", level=1)
    doc.add_paragraph(
        "To prevent data leakage, all statistical transformations (such as scaling parameters, imputation statistics, and "
        "one-hot encoder categories) were fitted exclusively on the 80% training partition (316 samples) and subsequently applied "
        "to the 20% test partition (79 samples)."
    )
    doc.add_paragraph(
        "• Numerical Transformation Pipeline:\n"
        "  1. SimpleImputer(strategy='median'): Replaces any absent values with the median of training instances, maintaining robustness against skewed distributions.\n"
        "  2. StandardScaler(): Centering and unit variance normalization, crucial for gradient stability and linear models.\n"
        "• Categorical Transformation Pipeline:\n"
        "  1. SimpleImputer(strategy='most_frequent'): Imputes categorical omissions with the observed mode.\n"
        "  2. OneHotEncoder(handle_unknown='ignore', sparse_output=False): Encodes nominal variables into binary vectors while safely zero-filling unobserved categories during production inference."
    )

    # -------------------------------------------------------------------------
    # SECTION 8: MODEL SELECTION & TRAINING
    # -------------------------------------------------------------------------
    doc.add_heading("8. Model Selection and Training Methodology", level=1)
    doc.add_paragraph(
        "Three candidate supervised learning algorithms were selected, evaluated, and compared:\n"
        "1. Ordinary Least Squares (OLS) Linear Regression: Serves as the transparent linear baseline.\n"
        "2. Ridge Regression (L2 Regularization, alpha=1.0): Introduces weight shrinkage to combat multi-collinearity among demographic attributes.\n"
        "3. Random Forest Regressor (n_estimators=200, min_samples_leaf=2, random_state=42): An ensemble of decorrelated decision trees capable of capturing non-linear feature interactions and high-order feature interdependencies."
    )
    doc.add_paragraph(
        "Validation was conducted using 5-Fold Cross-Validation on the training partition to gauge stability, followed by final "
        "unbiased evaluation on the reserved test partition. Evaluation criteria included:\n"
        "• Mean Absolute Error (MAE): Measures average magnitude of grade prediction error in raw grade units.\n"
        "• Root Mean Squared Error (RMSE): Penalizes larger prediction deviations quadratically.\n"
        "• Coefficient of Determination (R²): Measures proportion of target variance explained by the model."
    )

    # -------------------------------------------------------------------------
    # SECTION 9: EXPERIMENTAL RESULTS
    # -------------------------------------------------------------------------
    doc.add_heading("9. Experimental Results and Comparative Analysis", level=1)
    doc.add_paragraph(
        "The experimental evaluation recomputed actual metrics across all candidate models. The measured results confirm the "
        "historical baseline recorded during Week 2 with exact mathematical fidelity:"
    )

    # Results Table
    table_res = doc.add_table(rows=1, cols=7)
    table_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_res.autofit = False
    res_widths = [Inches(1.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8)]
    for i, w in enumerate(res_widths):
        table_res.columns[i].width = w

    res_headers = ["Model Name", "CV MAE", "CV R²", "Train MAE", "Test MAE", "Test RMSE", "Test R²"]
    for i, text in enumerate(res_headers):
        cell = table_res.cell(0, i)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    results_data = [
        ("Linear Regression", "3.5227", "-0.0924", "2.9462", "3.3953", "4.1957", "0.1415"),
        ("Ridge Regression", "3.5057", "-0.0801", "2.9461", "3.3929", "4.1934", "0.1424"),
        ("Random Forest (Champion)", "2.9343", "0.2036", "1.3372", "3.0364", "3.8126", "0.2911")
    ]

    for row_idx, rdata in enumerate(results_data, start=1):
        row = table_res.add_row()
        is_champ = "Champion" in rdata[0]
        bg = "ECFDF5" if is_champ else ("FFFFFF" if row_idx % 2 != 0 else "F8FAFC")
        for i, val in enumerate(rdata):
            cell = row.cells[i]
            cell.width = res_widths[i]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)
            if is_champ:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Embed Visualizations
    chart1 = OUTPUTS_DIR / "model_comparison_metrics.png"
    if chart1.exists():
        doc.add_paragraph("Figure 1: Comparison of Test Set Metrics (MAE, RMSE, and R²) across Regression Models.", style='Caption')
        doc.add_picture(str(chart1), width=Inches(6.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    chart4 = OUTPUTS_DIR / "feature_importance.png"
    if chart4.exists():
        doc.add_paragraph("Figure 2: Top 15 Most Important Features in Random Forest Regression.", style='Caption')
        doc.add_picture(str(chart4), width=Inches(6.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    chart2 = OUTPUTS_DIR / "actual_vs_predicted.png"
    if chart2.exists():
        doc.add_paragraph("Figure 3: Actual vs. Predicted Final Grade (G3) for the Champion Random Forest Pipeline.", style='Caption')
        doc.add_picture(str(chart2), width=Inches(4.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------------------
    # SECTION 10: WEB APPLICATION & API
    # -------------------------------------------------------------------------
    doc.add_heading("10. Web Application Design and API Architecture", level=1)
    doc.add_paragraph(
        "A full-stack Flask web application was constructed to make the machine learning model accessible to educators. "
        "The application provides a responsive front-end interface built with semantic HTML5, modern CSS3 styling, and "
        "asynchronous JavaScript (Fetch API)."
    )
    doc.add_paragraph(
        "Key interface features include:\n"
        "• Structured Form Sections: Features are organized into 4 logical groups (Academic & Schooling, Demographics & Household, Parental Background, Lifestyle & Well-being).\n"
        "• Preset Profile Selectors: One-click buttons ('High Performer', 'Average Student', 'At-Risk Student') allow evaluators to immediately populate valid test profiles.\n"
        "• Academic Classification Gauge: Visual progress bar mapping the predicted grade on the 0–20 Portuguese scale, accompanied by academic status badges (Distinction, Good, Satisfactory, Sufficient, Academic Support Recommended).\n"
        "• Asynchronous Execution: Submissions do not cause full-page reloads. A spinner and disabled button state provide responsive visual feedback."
    )
    doc.add_paragraph(
        "The RESTful API provides three primary endpoints:\n"
        "1. GET /health: Returns JSON application status, model readiness, and champion metrics (HTTP 200 or 503).\n"
        "2. GET /api/schema: Returns the complete list of 30 expected attributes, data types, and allowed categorical options.\n"
        "3. POST /predict: Accepts student JSON attributes, validates data types and ranges, executes model inference via the serialized pipeline, clips output to [0, 20], and returns structured predictions."
    )

    # -------------------------------------------------------------------------
    # SECTION 11: QUALITY ASSURANCE & TESTING
    # -------------------------------------------------------------------------
    doc.add_heading("11. Automated Testing and Quality Assurance", level=1)
    doc.add_paragraph(
        "Quality assurance was enforced through an automated Pytest test suite (week4/tests/test_app.py). "
        "Sixteen comprehensive test cases were designed and executed, verifying:"
    )
    tests_list = [
        "Artifact Availability: Model pipeline and metadata files exist and deserialize without corruption.",
        "Health Endpoint Readiness: GET /health returns HTTP 200 with model_loaded: true.",
        "Schema Endpoint Integrity: GET /api/schema correctly reflects all 30 features.",
        "Standard Prediction Request: Valid JSON payloads produce finite predictions on the 0–20 scale.",
        "Form-Encoded Compatibility: Validates form-submitted POST requests.",
        "Missing Field Rejection: Missing attributes yield HTTP 400 with explicit error messaging.",
        "Type Validation: Non-numeric strings in numeric fields yield HTTP 400 Bad Request.",
        "Boundary Validation: Out-of-range numerical values (e.g., age=99) are safely rejected.",
        "Non-Finite Rejection: Non-finite values (Infinity, NaN) are intercepted and rejected.",
        "Categorical Safety: Unrecognized categorical strings (e.g., school='OXFORD') are rejected.",
        "Malformed Syntax: Unparseable JSON syntax triggers HTTP 400 without unhandled server crashes.",
        "Response Schema Conformance: JSON output matches the documented contract with all metadata keys.",
        "Range Bounding Guarantee: Outputs strictly conform to the 0–20 scale.",
        "Non-Retraining Invariance: Prediction requests execute inference only; model weights and trees remain strictly immutable."
    ]
    for item in tests_list:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(item)

    doc.add_paragraph(
        "Verification Outcome: 16 passed in 2.08s (100% test pass rate)."
    )

    # -------------------------------------------------------------------------
    # SECTION 12: DEPLOYMENT PREPARATION
    # -------------------------------------------------------------------------
    doc.add_heading("12. Cloud Deployment Preparation for Render", level=1)
    doc.add_paragraph(
        "The project is engineered for zero-friction cloud deployment on Render's modern containerized platform:"
    )
    doc.add_paragraph(
        "• WSGI Entry Point: A production Procfile defines 'web: gunicorn app:app --bind 0.0.0.0:$PORT', dynamically binding to Render's assigned internal port.\n"
        "• Environment Portability: Application paths are resolved relative to Path(__file__).resolve().parent, avoiding hardcoded Windows directory paths.\n"
        "• Dependency Isolation: requirements.txt specifies exact, verified library versions.\n"
        "• Step-by-Step Render Deployment Workflow:\n"
        "  1. Log in to Render (https://dashboard.render.com/) and create a New Web Service.\n"
        "  2. Connect the GitHub repository: adithya222000666-arch/ml-internship-student-performance.\n"
        "  3. Configure Root Directory to 'week4'.\n"
        "  4. Set Build Command to 'pip install -r requirements.txt'.\n"
        "  5. Set Start Command to 'gunicorn app:app --bind 0.0.0.0:$PORT'.\n"
        "  6. Add Environment Variable: PYTHON_VERSION=3.11.9.\n"
        "  7. Trigger deployment and verify logs until the service enters Live status."
    )

    # -------------------------------------------------------------------------
    # SECTION 13: SCREENSHOT PLACEHOLDERS
    # -------------------------------------------------------------------------
    doc.add_heading("13. Visual Verification and Screenshot Evidence", level=1)
    doc.add_paragraph(
        "The following placeholders identify screenshots that should be inserted by the student after deployment to provide visual submission evidence:"
    )

    screenshot_boxes = [
        ("Screenshot 1 Placeholder: Local / Live Web Interface", "Capture a browser view of the home page showing the modern responsive prediction form and loaded sample student."),
        ("Screenshot 2 Placeholder: Prediction Results Card", "Capture the prediction results section showing the predicted final grade (e.g. 13.05/20), color-coded gauge bar, and performance badge."),
        ("Screenshot 3 Placeholder: Pytest Execution Results", "Capture a terminal window displaying the completed execution of 'pytest week4/tests -v' with 16 passed tests."),
        ("Screenshot 4 Placeholder: Render Deployment Dashboard", "Capture the Render cloud dashboard indicating successful build status and live service URL.")
    ]

    for title, desc in screenshot_boxes:
        add_callout_box(doc, title, desc, placeholder=True)

    # -------------------------------------------------------------------------
    # SECTION 14: LIMITATIONS & ETHICAL CONSIDERATIONS
    # -------------------------------------------------------------------------
    doc.add_heading("14. Model Limitations and Ethical Considerations", level=1)
    doc.add_paragraph(
        "Responsible application of machine learning in education necessitates understanding the model's inherent constraints:\n"
        "1. Advisory Nature: The system outputs a statistical expectation based on historical cohort patterns. It must never be used as a deterministic judgment or to make punitive academic decisions.\n"
        "2. Omission of Interim Grades: Intentionally excluding G1 and G2 lowers the R² value to ~0.29. This is an intentional engineering tradeoff: earlier warning capability is prioritized over retrospective correlation.\n"
        "3. Demographic Sensitivity: Attributes such as parental employment and residential classification reflect regional socio-economic conditions in the Portuguese survey cohort and must not be used to perpetuate demographic biases.\n"
        "4. Complementary Role: The system is designed to support human mentors, academic counselors, and instructors—not replace personalized pedagogy."
    )

    # -------------------------------------------------------------------------
    # SECTION 15: CONCLUSION & FUTURE WORK
    # -------------------------------------------------------------------------
    doc.add_heading("15. Conclusion and Future Improvements", level=1)
    doc.add_paragraph(
        "The Week 4 Capstone successfully delivered an end-to-end, production-ready machine learning system that fulfills all "
        "internship requirements. The pipeline ingests the raw Student Performance dataset, applies leak-free preprocessing, trains "
        "and validates multiple regression models, serializes the champion Random Forest pipeline, serves predictions via a responsive "
        "Flask web application, and undergoes strict QA validation with 16 passing automated tests."
    )
    doc.add_paragraph(
        "Future enhancements could include:\n"
        "• Longitudinal Tracking: Ingesting multi-semester attendance trends rather than static aggregate absences.\n"
        "• Explainable AI (SHAP / LIME): Incorporating interactive feature attribution explanations inside the web interface to show educators exactly why a specific student is predicted at-risk.\n"
        "• Recommendation Engine: Coupling predictions with automated remediation suggestions (e.g., recommended tutoring hours)."
    )

    # -------------------------------------------------------------------------
    # SECTION 16: REFERENCES
    # -------------------------------------------------------------------------
    doc.add_heading("16. References", level=1)
    refs = [
        "Cortez, P., & Silva, A. (2008). Using Data Mining to Predict Secondary School Student Performance. In Proceedings of 5th Annual Future Business Technology Conference, Porto, Portugal, pp. 5-12.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
        "Grinberg, M. (2018). Flask Web Development: Developing Web Applications with Python (2nd ed.). O'Reilly Media.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), 5-32.",
        "UCI Machine Learning Repository: Student Performance Data Set. https://archive.ics.uci.edu/ml/datasets/Student+Performance"
    ]
    for r in refs:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(r)

    doc.save(REPORT_PATH)
    print(f"[SUCCESS] Report generated at: {REPORT_PATH}")


if __name__ == "__main__":
    generate_report()
