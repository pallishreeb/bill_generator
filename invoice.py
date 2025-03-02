from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Optional: register a custom font for a more professional look
# pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))

def generate_bill_pdf(data, filename="invoice.pdf"):
    """
    Generates a PDF invoice/bill matching a design similar to the provided screenshot.
    `data` is a dictionary containing all the fields needed.
    Example structure of `data` (customize as needed):

    data = {
        "company_gstin": "21EQQS1807D1ZX",
        "company_name": "KROZTEK INTEGRATED SOLUTION",
        "office_address": "1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
        "contact_info": "Office: 1983/0465, Badashabilata, Dhenkanal\nEmail: kroztekintegratedsolution@gmail.com",
        "bill_to": "BEHERA TRADERS\nSujupadar, Jamankira, Sambalpur, Odisha\nGST No: 21ASBP1719K1ZX",
        "ship_from": "CG Power and Industrial Solutions Limited\nRaisen, Madhya Pradesh 462046\nGST No: 3AAACC3840K4Z2",
        "ship_to": "GANAPATI ENGINEERING WORKS\nSohela, Bargarh, Odisha, 768033\nGST No: 21ABWPB70B7D1ZX",
        "bill_no": "061",
        "bill_date": "15/01/2025",

        "items": [
            {
                "sr_no": 1,
                "description": "VFD WITH COMPLETE WIRED PANEL",
                "hsn_sac": "8537",
                "qty": 1,
                "price": 112000,
                "amount": 112000
            },
            # Add more items as needed
        ],
        "taxable_value": 112000,
        "sgst_rate": 9,
        "sgst_amount": 10080,
        "cgst_rate": 9,
        "cgst_amount": 10080,
        "total": 132160,
        "amount_in_words": "THIRTEEN LAKH TWENTY ONE THOUSAND SIX HUNDRED RUPEES ONLY",

        # Footer/Static Info
        "footer_bank_details": "Bank: XYZ Bank, A/c 123456789, IFSC: XYZB0001234",
        "footer_note": "Office: 1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
        "footer_signature_label": "Authorized Signatory",
    }
    """

    # Create the PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    # Optional: define some custom paragraph styles
    styles.add(ParagraphStyle(name="TableHeader", alignment=1, fontSize=10, textColor=colors.white))
    styles.add(ParagraphStyle(name="NormalBold", fontName='Helvetica-Bold'))

    # Container for all flowables
    elements = []

    # ----------------------------
    # 1) HEADER SECTION
    # ----------------------------
    # We'll build a top table that has:
    #  - Left: "GSTIN: ..."
    #  - Center: "TAX INVOICE"
    #  - Right: "Bill No. & Date"
    #
    # Then a second row with the company name in bold.
    # Then a third row with office address and contact info.

    header_data = [
        [
            Paragraph(f"GSTIN: <b>{data.get('company_gstin', '')}</b>", styles["Normal"]),
            Paragraph("<b>TAX INVOICE</b>", styles["NormalBold"]),
            Paragraph(f"<b>Bill No:</b> {data.get('bill_no','')}<br/><b>Date:</b> {data.get('bill_date','')}", styles["Normal"]),
        ],
        [
            Paragraph(f"<b>{data.get('company_name','')}</b>", styles["NormalBold"]),
            "",
            ""
        ],
        [
            Paragraph(data.get("office_address", ""), styles["Normal"]),
            Paragraph(data.get("contact_info", ""), styles["Normal"]),
            ""
        ]
    ]

    # We'll use a 3-column table for alignment
    header_table = Table(header_data, colWidths=[200, 120, 200])
    header_table.setStyle(TableStyle([
        ("SPAN", (1,1), (2,1)),  # Company name across columns 1 and 2
        ("SPAN", (0,2), (0,2)),  # Office address only in first cell
        ("SPAN", (1,2), (2,2)),  # contact_info spanning second row
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (1,1), (1,1), "CENTER"),
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (2,0), colors.black),
        ("TEXTCOLOR", (0,0), (2,0), colors.white),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # 2) BILL TO / SHIP FROM / SHIP TO
    # ----------------------------
    # We'll create a single table with three columns, each containing:
    #  - Title (BILL TO / SHIP FROM / SHIP TO)
    #  - Address lines

    addresses_data = [
        [
            Paragraph("<b>BILL TO</b><br/>" + data.get("bill_to", ""), styles["Normal"]),
            Paragraph("<b>SHIP FROM</b><br/>" + data.get("ship_from", ""), styles["Normal"]),
            Paragraph("<b>SHIP TO</b><br/>" + data.get("ship_to", ""), styles["Normal"]),
        ]
    ]
    addresses_table = Table(addresses_data, colWidths=[180, 180, 180])
    addresses_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(addresses_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # 3) ITEMS TABLE
    # ----------------------------
    # Columns: S. No, PARTICULARS, HSN/SAC, QTY, PRICE, AMOUNT
    items_data = [[
        Paragraph("<b>S. No.</b>", styles["Normal"]),
        Paragraph("<b>Particulars</b>", styles["Normal"]),
        Paragraph("<b>HSN/SAC</b>", styles["Normal"]),
        Paragraph("<b>Qty</b>", styles["Normal"]),
        Paragraph("<b>Price</b>", styles["Normal"]),
        Paragraph("<b>Amount</b>", styles["Normal"]),
    ]]

    # Populate rows from data["items"]
    for item in data.get("items", []):
        sr_no = item.get("sr_no", "")
        desc = item.get("description", "")
        hsn_sac = item.get("hsn_sac", "")
        qty = item.get("qty", "")
        price = item.get("price", 0)
        amount = item.get("amount", 0)
        items_data.append([
            str(sr_no),
            desc,
            str(hsn_sac),
            str(qty),
            f"{price:,.2f}",
            f"{amount:,.2f}",
        ])

    items_table = Table(items_data, colWidths=[40, 180, 60, 40, 60, 60])
    items_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (3,1), (5,-1), "RIGHT"),  # Align numeric columns to right
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # 4) TAX DETAILS & TOTALS
    # ----------------------------
    # We'll create a table summarizing: Taxable Value, SGST, CGST, and Grand Total.
    # Then a separate line for the amount in words.

    taxable_value = data.get("taxable_value", 0)
    sgst_rate = data.get("sgst_rate", 0)
    sgst_amount = data.get("sgst_amount", 0)
    cgst_rate = data.get("cgst_rate", 0)
    cgst_amount = data.get("cgst_amount", 0)
    total = data.get("total", 0)

    totals_data = [
        ["Taxable Value", f"{taxable_value:,.2f}"],
        [f"SGST {sgst_rate}% on {taxable_value:,.2f}", f"{sgst_amount:,.2f}"],
        [f"CGST {cgst_rate}% on {taxable_value:,.2f}", f"{cgst_amount:,.2f}"],
        ["Total", f"{total:,.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[300, 120])
    totals_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 10))

    # Amount in words
    amount_in_words = data.get("amount_in_words", "")
    if amount_in_words:
        elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", styles["Normal"]))
        elements.append(Spacer(1, 10))

    # ----------------------------
    # 5) FOOTER (STATIC OR SEMI-STATIC)
    # ----------------------------
    # According to your request, bank details, company name, date, or signature can be placed here.
    # We'll create a table with 2 columns: left for bank details & note, right for signature.

    footer_data = [
        [
            Paragraph(f"<b>Bank Details:</b><br/>{data.get('footer_bank_details','')}<br/><br/>{data.get('footer_note','')}", styles["Normal"]),
            Paragraph(f"<br/><br/><b>{data.get('footer_signature_label','Authorized Signatory')}</b>", styles["Normal"]),
        ]
    ]
    footer_table = Table(footer_data, colWidths=[300, 140])
    footer_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(footer_table)

    # Build the PDF
    doc.build(elements)

    return filename

# ----------------------------
# EXAMPLE USAGE
# ----------------------------
if __name__ == "__main__":
    sample_data = {
        "company_gstin": "21EQQS1807D1ZX",
        "company_name": "KROZTEK INTEGRATED SOLUTION",
        "office_address": "1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
        "contact_info": "Email: kroztekintegratedsolution@gmail.com\nPh: +91-9999999999",
        "bill_to": "BEHERA TRADERS\nSujupadar, Jamankira, Sambalpur, Odisha\nGST No: 21ASBP1719K1ZX",
        "ship_from": "CG Power and Industrial Solutions Limited\nRaisen, Madhya Pradesh 462046\nGST No: 3AAACC3840K4Z2",
        "ship_to": "GANAPATI ENGINEERING WORKS\nSohela, Bargarh, Odisha, 768033\nGST No: 21ABWPB70B7D1ZX",
        "bill_no": "061",
        "bill_date": "15/01/2025",
        "items": [
            {
                "sr_no": 1,
                "description": "VFD WITH COMPLETE WIRED PANEL",
                "hsn_sac": "8537",
                "qty": 1,
                "price": 112000,
                "amount": 112000
            }
        ],
        "taxable_value": 112000,
        "sgst_rate": 9,
        "sgst_amount": 10080,
        "cgst_rate": 9,
        "cgst_amount": 10080,
        "total": 132160,
        "amount_in_words": "THIRTEEN LAKH TWENTY ONE THOUSAND SIX HUNDRED RUPEES ONLY",
        "footer_bank_details": "Bank: XYZ Bank, A/c 123456789, IFSC: XYZB0001234",
        "footer_note": "Office: 1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
        "footer_signature_label": "Authorized Signatory",
    }

    generate_bill_pdf(sample_data, filename="sample_invoice.pdf")
    print("PDF generated: sample_invoice.pdf")
