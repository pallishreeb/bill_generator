from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def create_invoice(data):
    pdf = SimpleDocTemplate(f"invoices/Invoice_{data['bill_no']}.pdf", pagesize=A4)
    elements = []

    table_data = [
        ["Product", "Quantity", "Price per Unit", "Total"],
        *data['items']
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    pdf.build(elements)
