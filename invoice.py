import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMessageBox,
    QFileDialog, QDateEdit, QLineEdit,QFileDialog, QPushButton
)
from PyQt6.QtCore import QDate
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)

def init_db():
    conn = sqlite3.connect('bills.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (
            gst_number TEXT PRIMARY KEY,
            company_name TEXT,
            company_address TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product (
            sku TEXT PRIMARY KEY,
            product_name TEXT,
            hsn_code TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill (
            bill_no TEXT,
            product_sku TEXT,
            client_gst TEXT,
            date TEXT,
            FOREIGN KEY (product_sku) REFERENCES product(sku),
            FOREIGN KEY (client_gst) REFERENCES client(gst_number)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()


# ---------------------------------------------------------------------
# 1) PDF GENERATOR (Unchanged from your snippet)
# ---------------------------------------------------------------------
def generate_bill_pdf(data, filename="invoice.pdf"):
    """
    Generates a PDF invoice/bill matching the design from your screenshot.
    Expects a data dict with keys like:
      company_gstin, company_name, office_address, contact_info,
      bill_to, ship_from, ship_to, bill_no, bill_date,
      items (list of {sr_no, description, hsn_sac, qty, price, amount}),
      taxable_value, sgst_rate, sgst_amount, cgst_rate, cgst_amount,
      total, amount_in_words,
      footer_bank_details, footer_note, footer_signature_label
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TableHeader", alignment=1, fontSize=10, textColor=colors.white))
    styles.add(ParagraphStyle(name="NormalBold", fontName='Helvetica-Bold'))

    elements = []

    # ----------------------------
    # (A) HEADER SECTION
    # ----------------------------
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
    header_table = Table(header_data, colWidths=[200, 140, 200])
    header_table.setStyle(TableStyle([
        ("SPAN", (1,1), (2,1)),
        ("SPAN", (0,2), (0,2)),
        ("SPAN", (1,2), (2,2)),
        ("ALIGN", (1,0), (1,0), "CENTER"),
        ("ALIGN", (1,1), (1,1), "CENTER"),
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (2,0), colors.white),
        ("TEXTCOLOR", (0,0), (2,0), colors.black),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (B) BILL TO / SHIP FROM / SHIP TO
    # ----------------------------
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
    # (C) ITEMS TABLE
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

    items_table = Table(items_data, colWidths=[40, 220, 80, 50, 70, 80])
    items_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.black),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (3,1), (5,-1), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (D) TAX DETAILS & TOTALS
    # ----------------------------
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
    totals_table = Table(totals_data, colWidths=[400, 140])
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
    # (E) FOOTER (STATIC OR SEMI-STATIC)
    # ----------------------------
    footer_data = [
        [
            Paragraph(f"<b>Bank Details:</b><br/>{data.get('footer_bank_details','')}<br/><br/>{data.get('footer_note','')}", styles["Normal"]),
            Paragraph(f"<br/><br/><b>{data.get('footer_signature_label','Authorized Signatory')}</b>", styles["Normal"]),
        ]
    ]
    footer_table = Table(footer_data, colWidths=[400, 140])
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

    doc.build(elements)
    return filename

# ---------------------------------------------------------------------
# 2) PYQT6 APP: Takes minimal user input, everything else is static
# ---------------------------------------------------------------------
class BillApp(QWidget):
   
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Invoice App")
        self.setup_ui()
        self.setup_db_connections()

    def setup_db_connections(self):
        # Connect GST fields to auto-fill
        self.bill_to_gst.textChanged.connect(
            lambda: self.auto_fill_client(self.bill_to_gst, 
                                        self.bill_to_company,
                                        self.bill_to_address))
        
        self.ship_to_gst.textChanged.connect(
            lambda: self.auto_fill_client(self.ship_to_gst,
                                        self.ship_to_company,
                                        self.ship_to_address))
        
        self.ship_from_gst.textChanged.connect(
            lambda: self.auto_fill_client(self.ship_from_gst,
                                         self.ship_from_company,
                                         self.ship_from_address))
        
        # Connect SKU field in table
        self.items_table.cellChanged.connect(self.auto_fill_product)

    def auto_fill_client(self, gst_input, name_input, address_input):
        gst = gst_input.text().strip()
        if len(gst) == 15:  # GSTIN validation
            conn = sqlite3.connect('bills.db')
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, company_address FROM client WHERE gst_number=?", (gst,))
            result = cursor.fetchone()
            if result:
                name_input.setText(result[0])
                address_input.setText(result[1])
            conn.close()

    def auto_fill_product(self, row, column):
        if column == 1:  # SKU column
            sku_item = self.items_table.item(row, 1)
            sku = sku_item.text().strip() if sku_item else ""
            if sku:
                conn = sqlite3.connect('bills.db')
                cursor = conn.cursor()
                cursor.execute("SELECT product_name, hsn_code FROM product WHERE sku=?", (sku,))
                result = cursor.fetchone()
                if result:
                    self.items_table.setItem(row, 3, QTableWidgetItem(result[0]))  # Product Name
                    self.items_table.setItem(row, 4, QTableWidgetItem(result[1]))  # HSN
                conn.close()

    def save_to_database(self, data):
        conn = sqlite3.connect('bills.db')
        cursor = conn.cursor()
        
        try:
            # Save clients
            clients = [
                (self.bill_to_gst.text(), self.bill_to_company.text(), self.bill_to_address.text()),
                (self.ship_to_gst.text(), self.ship_to_company.text(), self.ship_to_address.text()),
                (self.ship_from_gst.text(), self.ship_from_company.text(), self.ship_from_address.text())
            ]
            
            for gst, name, addr in clients:
                if gst:
                    cursor.execute('''
                        INSERT INTO client (gst_number, company_name, company_address)
                        VALUES (?, ?, ?)
                        ON CONFLICT(gst_number) DO UPDATE SET
                            company_name=excluded.company_name,
                            company_address=excluded.company_address
                    ''', (gst, name, addr))
            
            # Save products
            for row in range(self.items_table.rowCount()):
                sku = self.items_table.item(row, 1).text()
                name = self.items_table.item(row, 3).text()
                hsn = self.items_table.item(row, 4).text()
                
                if sku:
                    cursor.execute('''
                        INSERT INTO product (sku, product_name, hsn_code)
                        VALUES (?, ?, ?)
                        ON CONFLICT(sku) DO UPDATE SET
                            product_name=excluded.product_name,
                            hsn_code=excluded.hsn_code
                    ''', (sku, name, hsn))
            
            # Generate bill number
            bill_date = QDate.currentDate().toString("yyyyMMdd")
            cursor.execute("SELECT MAX(bill_no) FROM bill WHERE bill_no LIKE ?", (f"INV-{bill_date}-%",))
            max_bill = cursor.fetchone()[0]
            bill_no = f"INV-{bill_date}-{int(max_bill.split('-')[-1]) + 1 if max_bill else 1:04d}"

            # Save bill items
            client_gst = self.bill_to_gst.text()
            for row in range(self.items_table.rowCount()):
                sku = self.items_table.item(row, 1).text()
                if sku and client_gst:
                    cursor.execute('''
                        INSERT INTO bill (bill_no, product_sku, client_gst, date)
                        VALUES (?, ?, ?, ?)
                    ''', (bill_no, sku, client_gst, data['bill_date']))
            
            conn.commit()
            return bill_no
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def generate_pdf(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Save Invoice", "invoice.pdf", "PDF Files (*.pdf)")
            if not path:
                return

            # Collect data as before
            data = {
                # ... your existing data collection code ...
                "bill_date": self.date_edit.date().toString("dd/MM/yyyy"),
                # ... rest of your data collection ...
            }

            # Save to database and get generated bill number
            bill_no = self.save_to_database(data)
            data['bill_no'] = bill_no  # Update data with generated bill number

            # Generate PDF
            generate_bill_pdf(data, filename=path)
            self.status_label.setText(f"PDF generated: {path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def setup_ui(self):
        main_layout = QVBoxLayout()

        # --- (A) Date Field (QDateEdit with calendar) ---
        date_layout = QHBoxLayout()
        date_label = QLabel("Bill Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        signature_label = QLabel("Signature:")
        self.signature_upload = QLineEdit()
        self.signature_upload.setPlaceholderText("Upload Signature")
        self.signature_upload.setReadOnly(True)  # Make it read-only to prevent manual input

        upload_button = QPushButton("Choose File")
        upload_button.clicked.connect(self.browse_signature)

        date_layout.addWidget(signature_label)
        date_layout.addWidget(self.signature_upload)
        date_layout.addWidget(upload_button)

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        # date_layout.addWidget(signature_label)
        # date_layout.addWidget(self.signature_upload)
        main_layout.addLayout(date_layout)


        # --- (B) Addresses: Bill To, Ship From, Ship To ---
        bill_to_layout = QHBoxLayout()
        bill_to_label = QLabel("Bill To:")
        self.bill_to_company = QLineEdit()
        self.bill_to_company.setPlaceholderText("Bill To Company")
        self.bill_to_address = QLineEdit()
        self.bill_to_address.setPlaceholderText("Bill To Address")
        self.bill_to_gst = QLineEdit()
        self.bill_to_gst.setPlaceholderText("Bill To GST")
        bill_to_layout.addWidget(bill_to_label)
        bill_to_layout.addWidget(self.bill_to_company)
        bill_to_layout.addWidget(self.bill_to_address)
        bill_to_layout.addWidget(self.bill_to_gst)
        main_layout.addLayout(bill_to_layout)

        #--- Ship To Layout
        ship_to_layout = QHBoxLayout()
        ship_to_label = QLabel("Ship To:")
        self.ship_to_company = QLineEdit()
        self.ship_to_company.setPlaceholderText("Ship To Company")
        self.ship_to_address = QLineEdit()
        self.ship_to_address.setPlaceholderText("Ship To Address")
        self.ship_to_gst = QLineEdit()
        self.ship_to_gst.setPlaceholderText("Ship To GST")
        ship_to_layout.addWidget(ship_to_label)
        ship_to_layout.addWidget(self.ship_to_company)
        ship_to_layout.addWidget(self.ship_to_address)
        ship_to_layout.addWidget(self.ship_to_gst)
        main_layout.addLayout(ship_to_layout)

        #---Ship from layout
        ship_from_layout = QHBoxLayout()
        ship_from_label = QLabel("Ship From:")
        self.ship_from_company = QLineEdit()
        self.ship_from_company.setPlaceholderText("Ship From Company")
        self.ship_from_address = QLineEdit()
        self.ship_from_address.setPlaceholderText("Ship From Address")
        self.ship_from_gst = QLineEdit()
        self.ship_from_gst.setPlaceholderText("Ship From GST")
        ship_from_layout.addWidget(ship_from_label)
        ship_from_layout.addWidget(self.ship_from_company)
        ship_from_layout.addWidget(self.ship_from_address)
        ship_from_layout.addWidget(self.ship_from_gst)
        main_layout.addLayout(ship_from_layout)


        # --- (C) Items Table: S. No, Particulars, HSN/SAC, Qty, Price, Amount
        self.items_table = QTableWidget(0, 8)
        self.items_table.setHorizontalHeaderLabels([
           "SL No." , "SKU Code", "Serial No", "Product Name", "HSN", "QTY", "Price per Unit", "Amount"
        ])
        main_layout.addWidget(QLabel("Items:"))
        main_layout.addWidget(self.items_table)

        # Add/Remove buttons
        btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_item_row)
        rem_btn = QPushButton("Remove Row")
        rem_btn.clicked.connect(self.remove_item_row)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rem_btn)
        main_layout.addLayout(btn_row)

        # --- (D) Generate PDF Button ---
        generate_btn = QPushButton("Generate PDF")
        generate_btn.clicked.connect(self.generate_pdf)
        main_layout.addWidget(generate_btn)

        # Status label
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def add_item_row(self):
        """Add a new row with placeholders."""
        row_count = self.items_table.rowCount()
        self.items_table.insertRow(row_count)

        # S. No. is row+1
        s_no_item = QTableWidgetItem(str(row_count + 1))
        self.items_table.setItem(row_count, 0, s_no_item)

        # Placeholders for the rest
        self.items_table.setItem(row_count, 1, QTableWidgetItem(""))  # Particulars
        self.items_table.setItem(row_count, 2, QTableWidgetItem(""))  # HSN/SAC
        self.items_table.setItem(row_count, 3, QTableWidgetItem("0")) # Qty
        self.items_table.setItem(row_count, 4, QTableWidgetItem("0")) # Price
        self.items_table.setItem(row_count, 5, QTableWidgetItem("0")) # Amount

    def remove_item_row(self):
        """Remove the selected row(s)."""
        selected = self.items_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "No row selected!")
            return
        rows = set(item.row() for item in selected)
        for row in sorted(rows, reverse=True):
            self.items_table.removeRow(row)

    def generate_pdf(self):
        """Gather minimal user input, fill in static data, create PDF."""
        try:
            # Let user pick a save path
            path, _ = QFileDialog.getSaveFileName(self, "Save Invoice", "invoice.pdf", "PDF Files (*.pdf)")
            if not path:
                return

            # 1) Collect addresses & date from user
            bill_date_str = self.date_edit.date().toString("dd/MM/yyyy")

            # Updated: Correctly fetch text from input fields
            bill_to_str = f"{self.bill_to_company.text().strip()}, {self.bill_to_address.text().strip()}, GST: {self.bill_to_gst.text().strip()}"
            ship_from_str = f"{self.ship_from_company.text().strip()}, {self.ship_from_address.text().strip()}, GST: {self.ship_from_gst.text().strip()}"
            ship_to_str = f"{self.ship_to_company.text().strip()}, {self.ship_to_address.text().strip()}, GST: {self.ship_to_gst.text().strip()}"

            # 2) Collect items
            items = []
            subtotal = 0.0
            for row in range(self.items_table.rowCount()):
                s_no = row + 1
                self.items_table.setItem(row, 0, QTableWidgetItem(str(s_no)))

                desc_item = self.items_table.item(row, 1)
                hsn_item = self.items_table.item(row, 2)
                qty_item = self.items_table.item(row, 3)
                price_item = self.items_table.item(row, 4)
                amt_item = self.items_table.item(row, 5)

                desc = desc_item.text() if desc_item else ""
                hsn = hsn_item.text() if hsn_item else ""
                try:
                    qty = float(qty_item.text()) if qty_item else 0.0
                except ValueError:
                    qty = 0.0
                try:
                    price = float(price_item.text()) if price_item else 0.0
                except ValueError:
                    price = 0.0

                amount = qty * price
                amt_item.setText(f"{amount:.2f}")
                subtotal += amount

                items.append({
                    "sr_no": s_no,
                    "description": desc,
                    "hsn_sac": hsn,
                    "qty": qty,
                    "price": price,
                    "amount": amount
                })

            # 3) Tax calculations
            sgst_rate = 9
            cgst_rate = 9
            sgst_amount = subtotal * (sgst_rate / 100)
            cgst_amount = subtotal * (cgst_rate / 100)
            total = subtotal + sgst_amount + cgst_amount

            # 4) Build the data dictionary
            data = {
                "company_gstin": "21EQQS1807D1ZX",
                "company_name": "KROZTEK INTEGRATED SOLUTION",
                "office_address": "1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
                "contact_info": "Email: kroztekintegratedsolution@gmail.com\nPh: +91-9999999999",
                "bill_to": bill_to_str,
                "ship_from": ship_from_str,
                "ship_to": ship_to_str,
                "bill_no": "061",  # Example bill number
                "bill_date": bill_date_str,

                "items": items,
                "taxable_value": subtotal,
                "sgst_rate": sgst_rate,
                "sgst_amount": sgst_amount,
                "cgst_rate": cgst_rate,
                "cgst_amount": cgst_amount,
                "total": total,
                "amount_in_words": "",  # Optional

                "footer_bank_details": "Bank: XYZ Bank, A/c 123456789, IFSC: XYZB0001234",
                "footer_note": "Office: 1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
                "footer_signature_label": "Authorized Signatory",
            }

            # 5) Generate the PDF
            generate_bill_pdf(data, filename=path)
            self.status_label.setText(f"PDF generated: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def browse_signature(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Signature", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if file_path:
            self.signature_upload.setText(file_path)

# ---------------------------------------------------------------------
# 3) RUN THE APP
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillApp()
    window.show()
    sys.exit(app.exec())
