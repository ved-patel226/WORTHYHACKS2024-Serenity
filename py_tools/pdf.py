from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

def generate(ppl: list, ttl: str) -> str:
            
    pdf_file = f"static/pdfs/petition_{round(datetime.now().timestamp())}.pdf"

    doc = SimpleDocTemplate(pdf_file, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["BodyText"]

    title = Paragraph(f"{ttl}", title_style)

    content = """
    We, the undersigned, are concerned citizens who urge our leaders to act now to address the issue at hand. 
    We believe that immediate action is necessary to bring about the necessary changes.
    """

    petition_text = Paragraph(content, normal_style)

    spacer = Spacer(1, 12)

    data = [["Name"]] + ppl

    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('SPAN', (0, 0), (-1, 0)),
        ('GRID', (0, 1), (-1, -1), 1, colors.black),
    ]))

    watermark = Paragraph("Made with Serenity", normal_style)
    
    elements = [title, spacer, petition_text, Spacer(1, 24), table, watermark]
    doc.build(elements)
    
    return pdf_file

def main() -> None:
    ...

if __name__ == '__main__':
    main()
