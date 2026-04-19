import pandas as pd
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def export_to_csv(data: list, title: str = "Data Export") -> StringIO:
    """
    Export any data to CSV format
    
    Args:
        data: List of dictionaries with query results
        title: Title for the export (optional)
    """
    if not data:
        df = pd.DataFrame([{"Message": "No data found"}])
    else:
        df = pd.DataFrame(data)
    
    # Create CSV in memory
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output


def export_to_excel(data: list, title: str = "Data Export") -> BytesIO:
    """
    Export any data to Excel format
    
    Args:
        data: List of dictionaries with query results
        title: Title for the export (optional)
    """
    if not data:
        # Create empty dataframe with message
        df = pd.DataFrame([{"Message": "No data found"}])
    else:
        df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Data']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
    
    output.seek(0)
    return output


def export_to_pdf(data: list, title: str = "Data Export", question: str = None) -> BytesIO:
    """
    Export any data to PDF format
    
    Args:
        data: List of dictionaries with query results
        title: Title for the PDF document
        question: Optional question that generated this data
    """
    # Create PDF in memory
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Title
    title_text = Paragraph(f"{title} - {datetime.now().strftime('%Y-%m-%d %H:%M')}", title_style)
    elements.append(title_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Question if provided
    if question:
        question_text = Paragraph(f"<b>Question:</b> {question}", styles['Normal'])
        elements.append(question_text)
        elements.append(Spacer(1, 0.2*inch))
    
    # Summary
    summary = Paragraph(f"Total Records: {len(data)}", styles['Normal'])
    elements.append(summary)
    elements.append(Spacer(1, 0.2*inch))
    
    # Table data
    if data:
        # Get column names from first record
        columns = list(data[0].keys())
        table_data = [columns]
        
        # Add data rows
        for record in data:
            row = [str(record.get(col, "")) for col in columns]
            table_data.append(row)
        
        # Create table with dynamic column widths
        col_widths = [min(100, max(50, len(str(col)) * 8)) for col in columns]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No data found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    output.seek(0)
    return output
