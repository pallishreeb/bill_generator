import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, QHeaderView, QMessageBox
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

class BillApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Commercial Invoice Generator")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # --- Invoice Details Form ---
        form_layout = QFormLayout()
        # Company Information
        self.company_name_edit = QLineEdit()
        form_layout.addRow("Company Name:", self.company_name_edit)
        
        self.company_gstin_edit = QLineEdit()
        form_layout.addRow("Company GSTIN:", self.company_gstin_edit)
        
        self.invoice_number_edit = QLineEdit()
        form_layout.addRow("Invoice Number:", self.invoice_number_edit)
        
        self.invoice_date_edit = QLineEdit()
        form_layout.addRow("Invoice Date:", self.invoice_date_edit)
        
        self.gst_rate_edit = QLineEdit()
        form_layout.addRow("GST Rate (%):", self.gst_rate_edit)
        
        # Addresses
        self.ship_to_edit = QLineEdit()
        self.bill_to_edit = QLineEdit()
        self.ship_from_edit = QLineEdit()
        form_layout.addRow("Ship To:", self.ship_to_edit)
        form_layout.addRow("Bill To:", self.bill_to_edit)
        form_layout.addRow("Ship From:", self.ship_from_edit)
        
        # Footer Details
        self.bank_details_edit = QLineEdit()
        form_layout.addRow("Bank Details:", self.bank_details_edit)
        
        self.signature_date_edit = QLineEdit()
        form_layout.addRow("Signature/Date:", self.signature_date_edit)

        layout.addLayout(form_layout)

        # --- Products Table Section ---
        self.products_table = QTableWidget(0, 4)
        self.products_table.setHorizontalHeaderLabels(
            ["Description", "Quantity", "HSN/SAC", "Rate"]
        )
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Products:"))
        layout.addWidget(self.products_table)

        # Buttons to add or remove product rows
        product_buttons_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Add Product")
        self.add_product_button.clicked.connect(self.add_product_row)
        self.remove_product_button = QPushButton("Remove Selected Product")
        self.remove_product_button.clicked.connect(self.remove_product_row)
        product_buttons_layout.addWidget(self.add_product_button)
        product_buttons_layout.addWidget(self.remove_product_button)
        layout.addLayout(product_buttons_layout)

        # --- Generate PDF Button ---
        self.generate_pdf_button = QPushButton("Generate PDF Invoice")
        self.generate_pdf_button.clicked.connect(self.generate_pdf)
        layout.addWidget(self.generate_pdf_button)

        # Status message
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def add_product_row(self):
        """Adds a new empty row in the products table."""
        row_count = self.products_table.rowCount()
        self.products_table.insertRow(row_count)

    def remove_product_row(self):
        """Removes selected row(s) from the products table."""
        selected = self.products_table.selectedItems()
        if selected:
            rows = set(item.row() for item in selected)
            for row in sorted(rows, reverse=True):
                self.products_table.removeRow(row)
        else:
            QMessageBox.warning(self, "Warning", "No product selected to remove.")

    def generate_pdf(self):
        """Collects data from the form, calculates amounts, and generates the PDF invoice."""
        try:
            gst_rate = float(self.gst_rate_edit.text())
        except ValueError:
            gst_rate = 0.0

        data = {
            "company_name": self.company_name_edit.text() or "Your Company Name",
            "company_gstin": self.company_gstin_edit.text() or "Not Provided",
            "invoice_number": self.invoice_number_edit.text() or "N/A",
            "invoice_date": self.invoice_date_edit.text() or "N/A",
            "gst_rate": gst_rate,
            "addresses": {
                "ship_to": self.ship_to_edit.text() or "Not provided",
                "bill_to": self.bill_to_edit.text() or "Not provided",
                "ship_from": self.ship_from_edit.text() or "Not provided"
            },
            "products": [],
            "bank_details": self.bank_details_edit.text() or "Not provided",
            "signature_date": self.signature_date_edit.text() or "Not provided"
        }

        # Process each product row
        for row in range(self.products_table.rowCount()):
            desc = self.products_table.item(row, 0).text() if self.products_table.item(row, 0) else ""
            qty_text = self.products_table.item(row, 1).text() if self.products_table.item(row, 1) else "0"
            hsn = self.products_table.item(row, 2).text() if self.products_table.item(row, 2) else ""
            rate_text = self.products_table.item(row, 3).text() if self.products_table.item(row, 3) else "0"
            try:
                qty = int(qty_text)
            except ValueError:
                qty = 0
            try:
                rate = float(rate_text)
            except ValueError:
                rate = 0.0
            data["products"].append({
                "description": desc,
                "quantity": qty,
                "hsn": hsn,
                "rate": rate,
                "amount": qty * rate
            })

        try:
            filename = self.create_pdf_invoice(data)
            self.status_label.setText(f"PDF generated successfully: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_pdf_invoice(self, data):
        """Generates a styled PDF invoice using ReportLab."""
        filename = "invoice.pdf"
        doc = SimpleDocTemplate(
            filename, pagesize=letter,
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18
        )
        styles = getSampleStyleSheet()
        # Custom styles for a better look
        styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=16, spaceAfter=10))
        styles.add(ParagraphStyle(name='RightAlign', alignment=2))
        elements = []

        # Header: Company Name and Invoice MetaData
        header_data = [
            [
                Paragraph(f"<b>{data.get('company_name')}</b>", styles['Title']),
                Paragraph(f"Invoice No: <b>{data.get('invoice_number')}</b><br/>Date: <b>{data.get('invoice_date')}</b>", styles['RightAlign'])
            ]
        ]
        header_table = Table(header_data, colWidths=[300, 200])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 12))
        
        # Company GSTIN
        elements.append(Paragraph(f"GSTIN: <b>{data.get('company_gstin')}</b>", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Title
        elements.append(Paragraph("TAX INVOICE", styles['CenterTitle']))
        elements.append(Spacer(1, 12))
        
        # Addresses Section
        addr = data.get("addresses", {})
        addr_data = [
            [
                Paragraph(f"<b>Ship To:</b><br/>{addr.get('ship_to')}", styles['Normal']),
                Paragraph(f"<b>Bill To:</b><br/>{addr.get('bill_to')}", styles['Normal']),
                Paragraph(f"<b>Ship From:</b><br/>{addr.get('ship_from')}", styles['Normal'])
            ]
        ]
        addr_table = Table(addr_data, colWidths=[170, 170, 170])
        addr_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        elements.append(addr_table)
        elements.append(Spacer(1, 12))

        # Products Table Header and Data
        table_header = ['Description', 'HSN/SAC', 'Quantity', 'Rate', 'Amount']
        table_data = [table_header]
        subtotal = 0.0
        for prod in data.get("products", []):
            row = [
                prod.get("description", ""),
                prod.get("hsn", ""),
                str(prod.get("quantity", "")),
                f"${prod.get('rate', 0):.2f}",
                f"${prod.get('amount', 0):.2f}"
            ]
            subtotal += prod.get("amount", 0)
            table_data.append(row)
        
        prod_table = Table(table_data, colWidths=[200, 80, 60, 60, 60])
        prod_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(prod_table)
        elements.append(Spacer(1, 12))

        # Calculations: Subtotal, GST, Total
        gst_amount = subtotal * (data.get("gst_rate", 0) / 100)
        total_amount = subtotal + gst_amount
        summary_data = [
            ["", "", "Subtotal:", f"${subtotal:.2f}"],
            ["", "", f"GST ({data.get('gst_rate', 0)}%):", f"${gst_amount:.2f}"],
            ["", "", "Total:", f"${total_amount:.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[200, 80, 100, 80])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (2,0), (-1,-1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 12))

        # Footer: Bank Details and Signature/Date
        footer_text = (
            f"<b>Bank Details:</b> {data.get('bank_details')}<br/><br/>"
            f"<b>Authorized Signature:</b> {data.get('signature_date')}"
        )
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Build the PDF
        doc.build(elements)
        return filename

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillApp()
    window.show()
    sys.exit(app.exec())
