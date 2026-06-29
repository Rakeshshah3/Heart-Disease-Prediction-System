from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import os


def generate_pdf(data, prediction, suggestions):

    file_path = "heart_report.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    # ==========================
    # 🎨 STYLES
    # ==========================
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=16,
        alignment=1,
        textColor=colors.darkblue
    )

    header_style = ParagraphStyle(
        name="HeaderStyle",
        fontSize=14,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        name="NormalStyle",
        fontSize=10,
        leading=14,
        textColor=colors.black
    )

    day_style = ParagraphStyle(
        name="DayStyle",
        fontSize=12,
        textColor=colors.darkblue
    )

    label_style = ParagraphStyle(
        name="LabelStyle",
        fontSize=10,
        leading=14
    )

    content = []

    # ==========================
    # 🏥 LOGO
    # ==========================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "logo.png")

    try:
        logo = Image(logo_path, width=45, height=45)
    except:
        logo = Paragraph("<b>AI CARE</b>", styles["Normal"])

    # ==========================
    # 🏥 HEADER
    # ==========================
    hospital_info = Paragraph(
        "<b>AI CARE HOSPITAL</b><br/>"
        "<font size=9>Advanced Cardiac Diagnostics</font><br/>"
        "<font size=8>Delhi | +91 XXXXXXXX</font>",
        ParagraphStyle(name="Hospital", alignment=0)
    )

    header = Table([[logo, hospital_info]], colWidths=[60, 400])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))

    content.append(header)
    content.append(Spacer(1, 8))

    content.append(Paragraph("<b>Heart Health Medical Report</b>", title_style))

    content.append(HRFlowable(
        width="100%",
        thickness=1.5,
        color=colors.grey,
        spaceBefore=5,
        spaceAfter=12
    ))

    # ==========================
    # 📄 METADATA (LEFT ALIGNED TEXT ✅)
    # ==========================
    content.append(Paragraph("<b>Report ID:</b> AI-2026-001", normal_style))
    content.append(Paragraph("<b>Date:</b> " + datetime.now().strftime("%d-%m-%Y %H:%M"), normal_style))
    content.append(Paragraph("<b>Doctor:</b> Dr. AI Cardiologist", normal_style))

    content.append(Spacer(1, 15))

    # ==========================
    # 👤 PATIENT INFO (LEFT ALIGNED)
    # ==========================
    content.append(Paragraph("<b>Patient Information</b>", header_style))

    gender = "Male" if str(data.get("sex")) in ["1", "Male"] else "Female"

    patient_info = Table([
        [Paragraph("<b>Name:</b>", normal_style), data.get("name", "N/A")],
        [Paragraph("<b>Age:</b>", normal_style), str(data.get("age"))],
        [Paragraph("<b>Gender:</b>", normal_style), gender],
        [Paragraph("<b>Blood Pressure:</b>", normal_style), str(data.get("trestbps"))],
        [Paragraph("<b>Cholesterol:</b>", normal_style), str(data.get("chol"))],
    ], colWidths=[140, 320])

    patient_info.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
    ]))

    content.append(patient_info)
    content.append(Spacer(1, 20))

    # ==========================
    # 📊 RESULT
    # ==========================
    content.append(Paragraph("<b>Diagnosis Result</b>", header_style))

    risk_text = "HIGH RISK" if prediction == 1 else "LOW RISK"
    risk_color = colors.red if prediction == 1 else colors.green

    risk_box = Table([[Paragraph(risk_text, ParagraphStyle(
        name="Risk",
        alignment=1,
        textColor=colors.white,
        fontSize=12
    ))]])

    risk_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), risk_color),
        ("INNERPADDING", (0,0), (-1,-1), 8),
    ]))

    content.append(risk_box)
    content.append(Spacer(1, 15))

    # ==========================
    # 🧠 INTERPRETATION
    # ==========================
    interpretation = """
    Based on the clinical parameters, the patient shows signs of elevated cardiovascular risk.
    It is advised to maintain a healthy lifestyle and consult a cardiologist.
    """

    content.append(Paragraph("<b>Clinical Interpretation</b>", header_style))
    content.append(Paragraph(interpretation, normal_style))
    content.append(Spacer(1, 15))

    # ==========================
    # 📅 WEEKLY PLAN
    # ==========================
    content.append(Paragraph("<b>Weekly Health Plan</b>", header_style))
    content.append(Spacer(1, 10))

    suggestions = suggestions[:35]

    for i in range(0, len(suggestions), 5):
        try:
            day = suggestions[i].replace(":", "")
            diet = suggestions[i+1].replace("Diet: ", "")
            exercise = suggestions[i+2].replace("Exercise: ", "")
            precautions = suggestions[i+3].replace("Precautions: ", "")

            box = Table([
                [Paragraph(f"<b>{day}</b>", day_style)],
                [Paragraph(f"<b>Diet:</b> {diet}", label_style)],
                [Paragraph(f"<b>Exercise:</b> {exercise}", label_style)],
                [Paragraph(f"<b>Precautions:</b> {precautions}", label_style)],
            ])

            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERPADDING", (0, 0), (-1, -1), 10),
            ]))

            content.append(KeepTogether([box, Spacer(1, 18)]))

        except:
            break

    # ==========================
    # ✍️ SIGNATURE
    # ==========================
    content.append(Spacer(1, 30))
    content.append(Paragraph("Authorized Signature", normal_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph("Dr. AI Cardiologist", normal_style))

    # ==========================
    # ⚠️ FOOTER
    # ==========================
    content.append(Spacer(1, 15))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    content.append(Spacer(1, 8))

    content.append(Paragraph(
        "This is an AI-generated report. Please consult a medical professional.",
        ParagraphStyle(name="Footer", fontSize=9, alignment=1, textColor=colors.grey)
    ))

    # ==========================
    # 🎨 BACKGROUND
    # ==========================
    def add_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColorRGB(0.90, 0.95, 1)
        canvas.rect(0, 0, A4[0], A4[1], fill=1)

        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(580, 20, f"Page {doc.page}")

        canvas.restoreState()

    doc.build(content, onFirstPage=add_background, onLaterPages=add_background)

    return file_path

