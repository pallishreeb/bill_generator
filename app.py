import sys
import os
import sqlite3
import datetime
from datetime import date
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QFileDialog, QDateEdit, QSpinBox, QDoubleSpinBox, QGroupBox,
                             QScrollArea, QFrame, QGridLayout, QComboBox, QDialog, QTextEdit,
                             QProgressBar,QDialogButtonBox)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image
from fpdf import FPDF
from num2words import num2words
import pandas as pd


def amount_to_words(amount):
    """Convert numeric amount to words dynamically."""
    return num2words(amount, to='currency', lang='en_IN').replace("euro", "rupees").replace("cents", "paise")

def get_dynamic_invoice_data(bill_to, ship_to, ship_from, bill_no, bill_date, items, taxable_value, sgst_rate, sgst_amount, cgst_rate, cgst_amount, total, amount_in_words, signature_path):
    return {
        # Static company info
        "company_gstin": "07ABCDE1234F1Z5",
        "company_name": "KROZTEK INTEGRATED SOLUTION",
        "office_address": "1983/0465, Badashabilata, Dhenkanal, Odisha - 759001",
        "contact_info": "Email: kroztekintegratedsolution@gmail.com\nPh: +91-9999999999",
        "footer_bank_details": "Bank: ABC Bank\nA/C No: 1234567890\nIFSC: ABCD0001234",
        "footer_bank_address": "Badashabilata, Dhenkanal, Odisha - 759001",
        "footer_note": "Thank you for your business!",
        "footer_signature_label": "Authorized Signatory",
        # Dynamic fields
        "bill_to": bill_to,
        "ship_from": ship_from,
        "ship_to": ship_to,
        "bill_no": bill_no,
        "bill_date": bill_date,
        "items": items,
        "taxable_value": taxable_value,
        "sgst_rate": sgst_rate,
        "sgst_amount": sgst_amount,
        "cgst_rate": cgst_rate,
        "cgst_amount": cgst_amount,
        "total": total,
        "amount_in_words": amount_in_words,
        "signature_path": signature_path
    }


def generate_bill_pdf(data, filename="invoice_static.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    # Define custom styles
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontSize=8,
        textColor=colors.white,
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name="NormalBold",
        fontName='Helvetica-Bold',
        fontSize=10
    ))
    styles.add(ParagraphStyle(
        name="TaxInvoiceStyle",
        fontSize=14,
        fontName="Helvetica-Bold",
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name="TableContent",
        fontSize=9,
        alignment=1  # Center alignment
    ))
    elements = []

    # ----------------------------
    # (A) HEADER SECTION with Borders
    # ----------------------------
    header_data = [
        [
            Paragraph(f"GSTIN: <b>{data['company_gstin']}</b>", styles["Normal"]),
            Paragraph("<b>TAX INVOICE</b>", styles["TaxInvoiceStyle"]),
            Paragraph(f"<b>Bill No:</b> {data['bill_no']}<br/><b>Date:</b> {data['bill_date']}", styles["Normal"]),
        ]
    ]
    header_table = Table(header_data, colWidths=[200, 140, 200])
    header_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (1, 0), (1, 0), colors.grey),  # Grey background for TAX INVOICE
        ("TEXTCOLOR", (1, 0), (1, 0), colors.white),  # White text for TAX INVOICE
        ("TOPPADDING", (0, 0), (-1, -1), 8),  # Add top padding
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),  # Add bottom padding
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (B) COMPANY INFO SECTION at the Top with Borders
    # ----------------------------
    company_info_data = [
        [
            Paragraph(f"<b>{data['company_name']}</b>", ParagraphStyle(
                'CompanyName',
                fontSize=16,
                alignment=1,
                spaceAfter=6
            ))
        ],
        [
            Paragraph(data['office_address'], ParagraphStyle(
                'OfficeAddress',
                fontSize=11,
                alignment=1,
                spaceAfter=4
            ))
        ],
        [
            Paragraph(data['contact_info'], ParagraphStyle(
                'ContactInfo',
                fontSize=11,
                alignment=1,
            ))
        ]
    ]

    company_info_table = Table(company_info_data, colWidths=[540])
    company_info_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),  # Light grey background
    ]))

    elements.append(company_info_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (C) BILL TO / SHIP FROM / SHIP TO with Borders
    # ----------------------------
    addresses_data = [
        [
            Paragraph("<b>BILL TO</b><br/>" + data["bill_to"], styles["Normal"]),
            Paragraph("<b>SHIP FROM</b><br/>" + data["ship_from"], styles["Normal"]),
            Paragraph("<b>SHIP TO</b><br/>" + data["ship_to"], styles["Normal"]),
        ]
    ]
    addresses_table = Table(addresses_data, colWidths=[180, 180, 180])
    addresses_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # Light grey background for headers
    ]))
    elements.append(addresses_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (D) ITEMS TABLE with Updated Dynamic Fields
    # ----------------------------
    items_data = [[
        Paragraph("<b>Sl No.</b>", styles["TableHeader"]),
        Paragraph("<b>SKU</b>", styles["TableHeader"]),
        Paragraph("<b>Product</b>", styles["TableHeader"]),
        Paragraph("<b>HSN</b>", styles["TableHeader"]),
        Paragraph("<b>Qty</b>", styles["TableHeader"]),
        Paragraph("<b>Price per Unit</b>", styles["TableHeader"]),
        Paragraph("<b>Amount</b>", styles["TableHeader"]),
    ]]

    if data["items"]:
        for idx, item in enumerate(data["items"], 1):
            items_data.append([
                Paragraph(str(idx), styles["TableContent"]),
                Paragraph(item.get("sku_code", "N/A"), styles["TableContent"]),
                Paragraph(item.get("product_name", "N/A"), styles["TableContent"]),
                Paragraph(item.get("hsn_code", "N/A"), styles["TableContent"]),
                Paragraph(str(item.get("quantity", 0)), styles["TableContent"]),
                Paragraph(f"{item.get('price_per_unit', 0):.2f}", styles["TableContent"]),
                Paragraph(f"{item.get('amount', 0):.2f}", styles["TableContent"]),
            ])
    else:
        items_data.append([
            Paragraph("", styles["TableContent"]),
            Paragraph("No products available", styles["TableContent"]),
            Paragraph("", styles["TableContent"]),
            Paragraph("", styles["TableContent"]),
            Paragraph("", styles["TableContent"]),
            Paragraph("", styles["TableContent"]),
            Paragraph("", styles["TableContent"]),
        ])

    items_table = Table(items_data, colWidths=[40, 80, 150, 80, 50, 70, 80])
    items_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (E) TAX DETAILS & TOTALS with Borders
    # ----------------------------
    totals_data = [
        ["Taxable Value", f"{data['taxable_value']:.2f}"],
        [f"SGST {data['sgst_rate']}% on {data['taxable_value']:.2f}", f"{data['sgst_amount']:.2f}"],
        [f"CGST {data['cgst_rate']}% on {data['taxable_value']:.2f}", f"{data['cgst_amount']:.2f}"],
        ["Total", f"{data['total']:.2f}"]
    ]
    totals_table = Table(totals_data, colWidths=[400, 140])
    totals_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (-1, -1), (-1, -1), colors.lightgrey),  # Light grey background for total
        ("FONTNAME", (-1, -1), (-1, -1), "Helvetica-Bold"),  # Bold for total
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),  # Right align all cells
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(Spacer(1, 10))
    elements.append(totals_table)
    elements.append(Spacer(1, 10))

    # Amount in words
    elements.append(Paragraph(f"<b>Amount in Words:</b> {data['amount_in_words']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # ----------------------------
    # (F) FOOTER with Borders
    # ----------------------------
    signature_path = data.get("signature_path")
    signature_img = Image(signature_path, width=120, height=40)

    footer_data = [
        [
            Paragraph(f"<b>Bank Details:</b><br/>{data['footer_bank_details']}<br/><br/>{data['footer_bank_address']}", styles["Normal"]),
            signature_img
        ],
        [
            Paragraph(f"{data['footer_note']}", styles["Normal"]),
            Paragraph(f"<br/><b>{data['footer_signature_label']}</b>", styles["Normal"]),
        ]
    ]

    footer_table = Table(footer_data, colWidths=[380, 160])
    footer_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),  # Light grey background
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(footer_table)

    # Save PDF
    doc.build(elements)
    return filename

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # If PyInstaller used
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DatabaseManager:
    def __init__(self, db_file="invoice_app.db"):
        self.db_file = db_file
        self.create_tables()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Companies table (for bill_to, ship_to, and ship_from)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            address TEXT NOT NULL,
            gst_number TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku_code TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            hsn_code TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Invoices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT UNIQUE NOT NULL,
            bill_date DATE NOT NULL,
            bill_to_company_id INTEGER NOT NULL,
            ship_to_company_id INTEGER NOT NULL,
            ship_from_company_id INTEGER NOT NULL,
            signature_path TEXT,
            advance_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bill_to_company_id) REFERENCES companies (id),
            FOREIGN KEY (ship_to_company_id) REFERENCES companies (id),
            FOREIGN KEY (ship_from_company_id) REFERENCES companies (id)
        )
        ''')
        
        # Invoice items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_company(self, company_name, address, gst_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO companies (company_name, address, gst_number)
            VALUES (?, ?, ?)
            ''', (company_name, address, gst_number))
            conn.commit()
            company_id = cursor.lastrowid
            conn.close()
            return company_id, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "GST Number already exists"
    
    def get_company_by_gst(self, gst_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM companies WHERE gst_number = ?
        ''', (gst_number,))
        
        company = cursor.fetchone()
        conn.close()
        
        if company:
            return dict(company)
        return None
    
    def get_all_companies(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM companies ORDER BY company_name')
        
        companies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return companies
    
    def get_company_by_id(self, company_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
        
        company = cursor.fetchone()
        conn.close()
        
        if company:
            return dict(company)
        return None
    
    def update_company(self, company_id, company_name, address, gst_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First check if the new GST number conflicts with any other company
            cursor.execute('''
            SELECT id FROM companies 
            WHERE gst_number = ? AND id != ?
            ''', (gst_number, company_id))
            
            if cursor.fetchone():
                conn.close()
                return False, "GST Number already exists for another company"
            
            cursor.execute('''
            UPDATE companies 
            SET company_name = ?, address = ?, gst_number = ?
            WHERE id = ?
            ''', (company_name, address, gst_number, company_id))
            
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def delete_company(self, company_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if company is used in any invoice
            cursor.execute('''
            SELECT COUNT(*) FROM invoices 
            WHERE bill_to_company_id = ? OR ship_to_company_id = ? OR ship_from_company_id = ?
            ''', (company_id, company_id, company_id))
            
            count = cursor.fetchone()[0]
            if count > 0:
                conn.close()
                return False, "Cannot delete company as it is used in invoices"
            
            cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def add_product(self, sku_code, product_name, hsn_code, price_per_unit):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO products (sku_code, product_name, hsn_code, price_per_unit)
            VALUES (?, ?, ?, ?)
            ''', (sku_code, product_name, hsn_code, price_per_unit))
            conn.commit()
            product_id = cursor.lastrowid
            conn.close()
            return product_id, None
        except sqlite3.IntegrityError:
            conn.close()
            return None, "SKU Code already exists"
    
    def get_product_by_id(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return dict(product)
        return None
    
    def get_all_products(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY product_name')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return products
    
    def update_product(self, product_id, sku_code, product_name, hsn_code, price_per_unit):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE products 
            SET sku_code = ?, product_name = ?, hsn_code = ?, price_per_unit = ?
            WHERE id = ?
            ''', (sku_code, product_name, hsn_code, price_per_unit, product_id))
            conn.commit()
            conn.close()
            return True, None
        except sqlite3.IntegrityError:
            conn.close()
            return False, "SKU Code already exists"
    
    def delete_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if product is used in any invoice
            cursor.execute('SELECT COUNT(*) FROM invoice_items WHERE product_id = ?', (product_id,))
            
            count = cursor.fetchone()[0]
            if count > 0:
                conn.close()
                return False, "Cannot delete product as it is used in invoices"
            
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)
    
    def get_next_bill_number(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM invoices')
        count = cursor.fetchone()[0]
        
        # Format: INV-YYYYMMDD-XXXX
        today = datetime.datetime.now().strftime('%Y%m%d')
        bill_number = f"INV-{today}-{count+1:04d}"
        
        conn.close()
        return bill_number
    
    def create_invoice(self, bill_date, bill_to_company_id, ship_to_company_id, 
                      ship_from_company_id, signature_path, advance_amount, total_amount, items):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            bill_number = self.get_next_bill_number()
            
            cursor.execute('''
            INSERT INTO invoices (bill_number, bill_date, bill_to_company_id, 
                                ship_to_company_id, ship_from_company_id, 
                                signature_path, advance_amount, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (bill_number, bill_date, bill_to_company_id, ship_to_company_id, 
                 ship_from_company_id, signature_path, advance_amount, total_amount))
            
            invoice_id = cursor.lastrowid
            
            # Add invoice items
            for item in items:
                cursor.execute('''
                INSERT INTO invoice_items (invoice_id, product_id, quantity, 
                                         price_per_unit, amount)
                VALUES (?, ?, ?, ?, ?)
                ''', (invoice_id, item['product_id'], item['quantity'], 
                     item['price_per_unit'], item['amount']))
            
            conn.commit()
            conn.close()
            return bill_number, None
        except Exception as e:
            conn.rollback()
            conn.close()
            return None, str(e)
    
    def get_all_invoices(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT i.*, 
               b.company_name as bill_to_name, 
               s.company_name as ship_to_name,
               f.company_name as ship_from_name
        FROM invoices i
        JOIN companies b ON i.bill_to_company_id = b.id
        JOIN companies s ON i.ship_to_company_id = s.id
        JOIN companies f ON i.ship_from_company_id = f.id
        ORDER BY i.bill_date DESC
        ''')
        
        invoices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return invoices
    
    def get_invoice_details(self, invoice_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get invoice header
        cursor.execute('''
        SELECT i.*, 
               b.company_name as bill_to_name, b.address as bill_to_address, b.gst_number as bill_to_gst,
               s.company_name as ship_to_name, s.address as ship_to_address, s.gst_number as ship_to_gst,
               f.company_name as ship_from_name, f.address as ship_from_address, f.gst_number as ship_from_gst
        FROM invoices i
        JOIN companies b ON i.bill_to_company_id = b.id
        JOIN companies s ON i.ship_to_company_id = s.id
        JOIN companies f ON i.ship_from_company_id = f.id
        WHERE i.id = ?
        ''', (invoice_id,))
        
        invoice = cursor.fetchone()
        
        if not invoice:
            conn.close()
            return None
        
        invoice_dict = dict(invoice)
        
        # Get invoice items
        cursor.execute('''
        SELECT ii.*, p.sku_code, p.product_name, p.hsn_code
        FROM invoice_items ii
        JOIN products p ON ii.product_id = p.id
        WHERE ii.invoice_id = ?
        ''', (invoice_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        invoice_dict['items'] = items
        
        conn.close()
        return invoice_dict
    
    def get_invoice_by_bill_number(self, bill_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM invoices WHERE bill_number = ?', (bill_number,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        invoice_id = result['id']
        conn.close()
        
        return self.get_invoice_details(invoice_id)

    def get_product_details(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sku_code, product_name, hsn_code FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        if product:
            return {
                "sku_code": product[0],
                "product_name": product[1],
                "hsn_code": product[2]
            }
        return None

    def update_invoice(self, bill_number, new_date, new_advance):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE invoices 
            SET bill_date = ?, advance_amount = ?
            WHERE bill_number = ?
            ''', (new_date, new_advance, bill_number))
            
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            conn.close()
            return False, str(e)

class LoadingScreen(QDialog):
    def __init__(self, message="Processing...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout()
        
        self.loading_label = QLabel(message)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont("Arial", 12))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

class InvoiceItem(QFrame):
    def __init__(self, index, db_manager, products, parent=None):
        super().__init__(parent)
        self.index = index
        self.db_manager = db_manager
        self.all_products = products
        self.product_id = None
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Serial Number (read-only)
        layout.addWidget(QLabel(f"{self.index + 1}"), 0, 0)
        
        # SKU Code (Combobox for selection)
        self.sku_combo = QComboBox()
        self.sku_combo.addItem("-- Select Product --", None)
        for product in self.all_products:
            self.sku_combo.addItem(f"{product['sku_code']} - {product['product_name']}", product['id'])
        
        self.sku_combo.currentIndexChanged.connect(self.product_selected)
        layout.addWidget(self.sku_combo, 0, 1)
        
        # Product Name (read-only)
        self.product_name = QLineEdit()
        self.product_name.setReadOnly(True)
        layout.addWidget(self.product_name, 0, 2)
        
        # HSN Code (read-only)
        self.hsn_code = QLineEdit()
        self.hsn_code.setReadOnly(True)
        layout.addWidget(self.hsn_code, 0, 3)
        
        # Quantity
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(9999)
        self.quantity.valueChanged.connect(self.calculate_amount)
        layout.addWidget(self.quantity, 0, 4)
        
        # Price per Unit (read-only)
        self.price_per_unit = QDoubleSpinBox()
        self.price_per_unit.setReadOnly(True)
        self.price_per_unit.setMaximum(999999.99)
        self.price_per_unit.setDecimals(2)
        layout.addWidget(self.price_per_unit, 0, 5)
        
        # Amount (editable)
        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(9999999.99)
        self.amount.setDecimals(2)
        self.amount.valueChanged.connect(self.update_price_per_unit)
        layout.addWidget(self.amount, 0, 6)
        
        # Remove button
        self.remove_btn = QPushButton("X")
        self.remove_btn.setFixedWidth(30)
        self.remove_btn.clicked.connect(self.remove_item)
        layout.addWidget(self.remove_btn, 0, 7)
        
        self.setLayout(layout)
    
    def product_selected(self):
        product_id = self.sku_combo.currentData()
        if product_id:
            self.product_id = product_id
            
            # Find the product
            for product in self.all_products:
                if product['id'] == product_id:
                    self.product_name.setText(product['product_name'])
                    self.hsn_code.setText(product['hsn_code'])
                    self.price_per_unit.setValue(product['price_per_unit'])
                    # Set initial amount based on quantity and price
                    self.amount.setValue(self.quantity.value() * product['price_per_unit'])
                    break
        else:
            self.product_id = None
            self.product_name.clear()
            self.hsn_code.clear()
            self.price_per_unit.setValue(0)
            self.amount.setValue(0)
            # Find the parent GenerateBillTab and update total
            parent = self.parent()
            while parent and not isinstance(parent, GenerateBillTab):
                parent = parent.parent()
            if parent:
                parent.calculate_total()
    
    def calculate_amount(self):
        qty = self.quantity.value()
        price = self.price_per_unit.value()
        self.amount.setValue(qty * price)
        # Find the parent GenerateBillTab and update total
        parent = self.parent()
        while parent and not isinstance(parent, GenerateBillTab):
            parent = parent.parent()
        if parent:
            parent.calculate_total()
    
    def update_price_per_unit(self):
        qty = self.quantity.value()
        if qty > 0:
            new_price = self.amount.value() / qty
            self.price_per_unit.setValue(new_price)
            # Find the parent GenerateBillTab and update total
            parent = self.parent()
            while parent and not isinstance(parent, GenerateBillTab):
                parent = parent.parent()
            if parent:
                parent.calculate_total()
    
    def remove_item(self):
        # Find the parent GenerateBillTab
        parent = self.parent()
        while parent and not isinstance(parent, GenerateBillTab):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'remove_product_item'):
            parent.remove_product_item(self)
        else:
            QMessageBox.warning(self, "Error", "Could not remove product item")
    
    def get_data(self):
        if not self.product_id:
            return None
        
        return {
            'product_id': self.product_id,
            'quantity': self.quantity.value(),
            'price_per_unit': self.price_per_unit.value(),
            'amount': self.amount.value()
        }

class GenerateBillTab(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product_items = []
        self.signature_path = None
        
        self.init_ui()
        self.load_company_data()
        self.load_products()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # === Client Section ===
        client_group = QGroupBox("Client Section")
        client_layout = QGridLayout()
        
        # Bill To Company (Left Column)
        bill_to_group = QGroupBox("Bill To")
        bill_to_layout = QFormLayout()
        self.bill_to_gst = QLineEdit()
        self.bill_to_gst.setPlaceholderText("Enter GST Number")
        self.bill_to_gst.textChanged.connect(self.bill_to_gst_changed)
        self.bill_to_name = QLineEdit()
        self.bill_to_name.setPlaceholderText("Company Name")
        self.bill_to_address = QTextEdit()
        self.bill_to_address.setPlaceholderText("Company Address")
        self.bill_to_address.setMaximumHeight(80)
        bill_to_layout.addRow("GST Number:", self.bill_to_gst)
        bill_to_layout.addRow("Company Name:", self.bill_to_name)
        bill_to_layout.addRow("Address:", self.bill_to_address)
        bill_to_group.setLayout(bill_to_layout)
        client_layout.addWidget(bill_to_group, 0, 0)
        
        # Ship To Company (Middle Column)
        ship_to_group = QGroupBox("Ship To")
        ship_to_layout = QFormLayout()
        self.ship_to_gst = QLineEdit()
        self.ship_to_gst.setPlaceholderText("Enter GST Number")
        self.ship_to_gst.textChanged.connect(self.ship_to_gst_changed)
        self.ship_to_name = QLineEdit()
        self.ship_to_name.setPlaceholderText("Company Name")
        self.ship_to_address = QTextEdit()
        self.ship_to_address.setPlaceholderText("Company Address")
        self.ship_to_address.setMaximumHeight(80)
        ship_to_layout.addRow("GST Number:", self.ship_to_gst)
        ship_to_layout.addRow("Company Name:", self.ship_to_name)
        ship_to_layout.addRow("Address:", self.ship_to_address)
        ship_to_group.setLayout(ship_to_layout)
        client_layout.addWidget(ship_to_group, 0, 1)
        
        # Ship From Company (Right Column)
        ship_from_group = QGroupBox("Ship From")
        ship_from_layout = QFormLayout()
        self.ship_from_gst = QLineEdit()
        self.ship_from_gst.setPlaceholderText("Enter GST Number")
        self.ship_from_gst.textChanged.connect(self.ship_from_gst_changed)
        self.ship_from_name = QLineEdit()
        self.ship_from_name.setPlaceholderText("Company Name")
        self.ship_from_address = QTextEdit()
        self.ship_from_address.setPlaceholderText("Company Address")
        self.ship_from_address.setMaximumHeight(80)
        ship_from_layout.addRow("GST Number:", self.ship_from_gst)
        ship_from_layout.addRow("Company Name:", self.ship_from_name)
        ship_from_layout.addRow("Address:", self.ship_from_address)
        ship_from_group.setLayout(ship_from_layout)
        client_layout.addWidget(ship_from_group, 0, 2)
        
        client_group.setLayout(client_layout)
        main_layout.addWidget(client_group)
        
        # === Product Section ===
        product_group = QGroupBox("Product Section")
        product_layout = QVBoxLayout()
        
        # Headers
        header_layout = QGridLayout()
        header_layout.addWidget(QLabel("S.No"), 0, 0)
        header_layout.addWidget(QLabel("SKU Code"), 0, 1)
        header_layout.addWidget(QLabel("Product Name"), 0, 2)
        header_layout.addWidget(QLabel("HSN Code"), 0, 3)
        header_layout.addWidget(QLabel("Qty"), 0, 4)
        header_layout.addWidget(QLabel("Price per Unit"), 0, 5)
        header_layout.addWidget(QLabel("Amount"), 0, 6)
        header_layout.addWidget(QLabel(""), 0, 7)
        product_layout.addLayout(header_layout)
        
        # Scrollable area for product items
        self.product_scroll = QScrollArea()
        self.product_scroll.setWidgetResizable(True)
        self.product_container = QWidget()
        self.product_container_layout = QVBoxLayout()
        self.product_container.setLayout(self.product_container_layout)
        self.product_scroll.setWidget(self.product_container)
        product_layout.addWidget(self.product_scroll)
        
        # Add Product Button
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product_item)
        product_layout.addWidget(self.add_product_btn)
        
        # Total Amount
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Total Amount:"))
        self.total_amount = QDoubleSpinBox()
        self.total_amount.setReadOnly(True)
        self.total_amount.setMaximum(9999999.99)
        self.total_amount.setDecimals(2)
        total_layout.addWidget(self.total_amount)
        product_layout.addLayout(total_layout)
        
        product_group.setLayout(product_layout)
        main_layout.addWidget(product_group)
        
        # === Bill Info Section ===
        bill_group = QGroupBox("Bill Information")
        bill_layout = QHBoxLayout()
        
        # Bill Number
        bill_number_layout = QFormLayout()
        self.bill_number = QLineEdit()
        self.bill_number.setReadOnly(True)
        self.bill_number.setText(self.db_manager.get_next_bill_number())
        bill_number_layout.addRow("Bill No:", self.bill_number)
        bill_layout.addLayout(bill_number_layout)
        
        # Bill Date
        bill_date_layout = QFormLayout()
        self.bill_date = QDateEdit()
        self.bill_date.setDate(QDate.currentDate())
        self.bill_date.setCalendarPopup(True)
        bill_date_layout.addRow("Bill Date:", self.bill_date)
        bill_layout.addLayout(bill_date_layout)
        
        # Upload Signature
        signature_layout = QFormLayout()
        self.signature_btn = QPushButton("Upload Signature")
        self.signature_btn.clicked.connect(self.upload_signature)
        self.signature_label = QLabel("No file selected")
        signature_layout.addRow(self.signature_btn, self.signature_label)
        bill_layout.addLayout(signature_layout)
        
        # Advance Amount
        advance_layout = QFormLayout()
        self.advance_amount = QDoubleSpinBox()
        self.advance_amount.setMaximum(9999999.99)
        self.advance_amount.setDecimals(2)
        advance_layout.addRow("Advance Amount:", self.advance_amount)
        bill_layout.addLayout(advance_layout)
        
        bill_group.setLayout(bill_layout)
        main_layout.addWidget(bill_group)
        
        # Button Layout
        button_layout = QHBoxLayout()
        
        # Generate Bill Button
        self.generate_btn = QPushButton("Generate Bill")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setFont(QFont("Arial", 12))
        self.generate_btn.clicked.connect(self.generate_bill)
        button_layout.addWidget(self.generate_btn)
        
        # Print Bill Button
        self.print_btn = QPushButton("Print Bill")
        self.print_btn.setFixedHeight(40)
        self.print_btn.setFont(QFont("Arial", 12))
        self.print_btn.clicked.connect(self.print_bill)
        button_layout.addWidget(self.print_btn)
        
        # Refresh Button
        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.setFont(QFont("Arial", 12))
        self.refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(button_layout)

        # Create QLabel to show the PDF save path
        self.pdf_path_label = QLabel("", self)
        self.pdf_path_label.setStyleSheet("color: white; font-size: 14pt;")
        self.pdf_path_label.setGeometry(10, self.height() - 30, self.width() - 20, 20)
        self.pdf_path_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.pdf_path_label)
        
        self.setLayout(main_layout)
    
    def add_product_item(self):
        item = InvoiceItem(len(self.product_items), self.db_manager, self.all_products, self)
        self.product_items.append(item)
        self.product_container_layout.addWidget(item)
        
        # Make sure we can see the newly added item
        self.product_scroll.ensureWidgetVisible(item)
        
        # Update total after adding new item
        self.calculate_total()
    
    def remove_product_item(self, item):
        if item in self.product_items:
            self.product_items.remove(item)
            item.deleteLater()
            
            # Renumber remaining items
            for i, item in enumerate(self.product_items):
                item.index = i
                item.layout().itemAt(0).widget().setText(f"{i + 1}")
            
            self.calculate_total()
    
    def bill_to_gst_changed(self):
        gst = self.bill_to_gst.text()
        company = self.db_manager.get_company_by_gst(gst)
        if company:
            self.bill_to_name.setText(company['company_name'])
            self.bill_to_address.setText(company['address'])
    
    def ship_to_gst_changed(self):
        gst = self.ship_to_gst.text()
        company = self.db_manager.get_company_by_gst(gst)
        if company:
            self.ship_to_name.setText(company['company_name'])
            self.ship_to_address.setText(company['address'])
    
    def ship_from_gst_changed(self):
        gst = self.ship_from_gst.text()
        company = self.db_manager.get_company_by_gst(gst)
        if company:
            self.ship_from_name.setText(company['company_name'])
            self.ship_from_address.setText(company['address'])
    
    def load_company_data(self):
        # This is just to set up the companies comboboxes and autocomplete
        pass
    
    def load_products(self):
        try:
            self.all_products = self.db_manager.get_all_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
            self.all_products = []
    
    def upload_signature(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signature Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Copy the file to a local directory
            signature_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signatures")
            os.makedirs(signature_dir, exist_ok=True)
            
            # Generate a unique filename
            file_ext = os.path.splitext(file_path)[1]
            signature_filename = f"signature_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            save_path = os.path.join(signature_dir, signature_filename)
            
            try:
                # Copy the file
                with open(file_path, 'rb') as src, open(save_path, 'wb') as dst:
                    dst.write(src.read())
                
                self.signature_path = save_path
                self.signature_label.setText(os.path.basename(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save signature: {str(e)}")
    
    def calculate_total(self):
        total = 0.0
        for item in self.product_items:
            data = item.get_data()
            if data:
                total += data['amount']
        self.total_amount.setValue(total)

    def print_bill(self):
        # Show loading screen
        loading = LoadingScreen("Preparing Bill for Printing...", self)
        loading.show()
        QApplication.processEvents()

        try:
            # First save the bill to database and generate PDF
            bill_number = self.save_bill_to_database()
            if not bill_number:
                return

            # Ask user to choose where to save the PDF temporarily
            temp_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_bill.pdf")
            
            # Generate PDF
            pdf_path = generate_bill_pdf(self.prepare_invoice_data(), temp_pdf_path)
            
            # Show print dialog
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                # Print the PDF
                os.system(f'lpr -P {printer.printerName()} "{pdf_path}"')
                QMessageBox.information(self, "Success", "Bill printed successfully!")
            
            # Clean up temporary file
            try:
                os.remove(temp_pdf_path)
            except:
                pass
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print bill: {str(e)}")
        finally:
            loading.close()

    def save_bill_to_database(self):
        try:
            # Validate company information
            if not all([self.bill_to_gst.text(), self.ship_to_gst.text(), 
                       self.ship_from_gst.text()]):
                raise ValueError("All GST numbers are required")

            # Get or create companies
            companies = []
            for gst, name, address in [
                (self.bill_to_gst.text(), self.bill_to_name.text(), self.bill_to_address.toPlainText()),
                (self.ship_to_gst.text(), self.ship_to_name.text(), self.ship_to_address.toPlainText()),
                (self.ship_from_gst.text(), self.ship_from_name.text(), self.ship_from_address.toPlainText())
            ]:
                company = self.db_manager.get_company_by_gst(gst)
                if not company:
                    company_id, error = self.db_manager.add_company(name, address, gst)
                    if error:
                        raise ValueError(f"Company creation error: {error}")
                    companies.append(company_id)
                else:
                    companies.append(company['id'])

            # Validate products
            items = []
            for item in self.product_items:
                data = item.get_data()
                if data:
                    # Fetch product details based on product_id
                    product_details = self.db_manager.get_product_details(data['product_id'])
                    if product_details:
                        # Merge product details into the item
                        data.update(product_details)
                        items.append(data)

            if not items:
                raise ValueError("At least one product item required")

            # Prepare invoice data
            invoice_data = {
                'bill_date': self.bill_date.date().toString("yyyy-MM-dd"),
                'bill_to_company_id': companies[0],
                'ship_to_company_id': companies[1],
                'ship_from_company_id': companies[2],
                'signature_path': self.signature_path,
                'advance_amount': self.advance_amount.value(),
                'total_amount': self.total_amount.value(),
                'items': items
            }

            # Create invoice in database
            bill_number, error = self.db_manager.create_invoice(
                invoice_data['bill_date'],
                invoice_data['bill_to_company_id'],
                invoice_data['ship_to_company_id'],
                invoice_data['ship_from_company_id'],
                invoice_data['signature_path'],
                invoice_data['advance_amount'],
                invoice_data['total_amount'],
                invoice_data['items']
            )

            if error:
                raise ValueError(f"Failed to create invoice: {error}")

            return bill_number

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return None

    def prepare_invoice_data(self):
        # Calculate tax details dynamically
        items = []
        for item in self.product_items:
            data = item.get_data()
            if data:
                product_details = self.db_manager.get_product_details(data['product_id'])
                if product_details:
                    data.update(product_details)
                    items.append(data)

        taxable_value = sum(item['amount'] for item in items)
        sgst_rate = 9  # Static for now; can be dynamic if needed
        cgst_rate = 9  # Static for now; can be dynamic if needed
        sgst_amount = taxable_value * sgst_rate / 100
        cgst_amount = taxable_value * cgst_rate / 100
        total = taxable_value + sgst_amount + cgst_amount

        # Handle signature path
        signature_path = self.signature_path
        if not signature_path:
            # Use default signature if none is selected
            default_signature = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Signature.png")
            if os.path.exists(default_signature):
                signature_path = default_signature
            else:
                QMessageBox.warning(self, "Warning", "Default signature file not found. Please add a signature.")
                return None

        return get_dynamic_invoice_data(
            bill_to=f"{self.bill_to_name.text()}\n{self.bill_to_address.toPlainText()}\nGSTIN: {self.bill_to_gst.text()}",
            ship_to=f"{self.ship_to_name.text()}\n{self.ship_to_address.toPlainText()}\nGSTIN: {self.ship_to_gst.text()}",
            ship_from=f"{self.ship_from_name.text()}\n{self.ship_from_address.toPlainText()}\nGSTIN: {self.ship_from_gst.text()}",
            bill_no=self.bill_number.text(),
            bill_date=self.bill_date.date().toString("yyyy-MM-dd"),
            items=items,
            taxable_value=taxable_value,
            sgst_rate=sgst_rate,
            sgst_amount=sgst_amount,
            cgst_rate=cgst_rate,
            cgst_amount=cgst_amount,
            total=total,
            amount_in_words=amount_to_words(total),
            signature_path=signature_path
        )

    def generate_bill(self):
        # Show loading screen
        loading = LoadingScreen("Generating Invoice...", self)
        loading.show()
        QApplication.processEvents()

        try:
            # Save to database first
            bill_number = self.save_bill_to_database()
            if not bill_number:
                return

            # Ask user to choose where to save the PDF
            save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if save_path:
                if not save_path.endswith(".pdf"):
                    save_path += ".pdf"

                # Generate PDF
                pdf_path = generate_bill_pdf(self.prepare_invoice_data(), save_path)
                QMessageBox.information(self, "Success", f"Invoice saved and PDF generated at {pdf_path}!")

                # Display the save path at the bottom of the app
                self.pdf_path_label.setText(f"PDF saved at: {pdf_path}")

                self.reset_form()
            else:
                QMessageBox.warning(self, "Cancelled", "PDF save cancelled.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            loading.close()

    def reset_form(self):
        # Reset all fields
        self.bill_to_gst.clear()
        self.bill_to_name.clear()
        self.bill_to_address.clear()
        self.ship_to_gst.clear()
        self.ship_to_name.clear()
        self.ship_to_address.clear()
        self.ship_from_gst.clear()
        self.ship_from_name.clear()
        self.ship_from_address.clear()
        
        # Clear product items
        for item in self.product_items:
            item.deleteLater()
        self.product_items.clear()
        self.add_product_item()
        
        # Reset bill info
        self.bill_number.setText(self.db_manager.get_next_bill_number())
        self.bill_date.setDate(QDate.currentDate())
        self.signature_path = None
        self.signature_label.setText("No file selected")
        self.advance_amount.setValue(0.0)
        self.total_amount.setValue(0.0)

    def refresh_data(self):
        # Show loading screen
        loading = LoadingScreen("Refreshing Data...", self)
        loading.show()
        QApplication.processEvents()

        try:
            # Reload products
            self.load_products()
            
            # Clear existing product items
            for item in self.product_items:
                item.deleteLater()
            self.product_items.clear()
            
            # Add a new empty product item
            self.add_product_item()
            
            QMessageBox.information(self, "Success", "Data refreshed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh data: {str(e)}")
        finally:
            loading.close()

# Add remaining tabs
class DisplayBillsTab(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_invoices()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Button layout at the top
        btn_layout = QHBoxLayout()
        
        # Edit button
        edit_btn = QPushButton("Edit Invoice")
        edit_btn.clicked.connect(self.edit_invoice)
        btn_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete Invoice")
        delete_btn.clicked.connect(self.delete_invoice)
        btn_layout.addWidget(delete_btn)
        
        # Export to Excel button
        export_btn = QPushButton("Export to Excel")
        export_btn.clicked.connect(self.export_to_excel)
        btn_layout.addWidget(export_btn)
        
        # Add some spacing
        btn_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_invoices)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        # Invoice table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Bill Number", "Date", "Bill To", "Total", "Advance"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.show_invoice_details)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def export_to_excel(self):
        # Show loading screen
        loading = LoadingScreen("Preparing Excel Export...", self)
        loading.show()
        QApplication.processEvents()

        try:
            # Get all invoices with details
            invoices = self.db_manager.get_all_invoices()
            
            # Create a list to store all invoice data
            excel_data = []
            
            for invoice in invoices:
                # Get detailed invoice information
                invoice_details = self.db_manager.get_invoice_by_bill_number(invoice['bill_number'])
                if invoice_details:
                    # Add invoice header information
                    for item in invoice_details['items']:
                        excel_data.append({
                            'Bill Number': invoice['bill_number'],
                            'Date': invoice['bill_date'],
                            'Bill To': invoice['bill_to_name'],
                            'Bill To GST': invoice_details['bill_to_gst'],
                            'Ship To': invoice['ship_to_name'],
                            'Ship To GST': invoice_details['ship_to_gst'],
                            'Ship From': invoice['ship_from_name'],
                            'Ship From GST': invoice_details['ship_from_gst'],
                            'SKU': item['sku_code'],
                            'Product': item['product_name'],
                            'HSN': item['hsn_code'],
                            'Quantity': item['quantity'],
                            'Price per Unit': item['price_per_unit'],
                            'Amount': item['amount'],
                            'Total Amount': invoice['total_amount'],
                            'Advance Amount': invoice['advance_amount']
                        })
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Ask user where to save the Excel file
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel File", "", "Excel Files (*.xlsx)"
            )
            
            if save_path:
                if not save_path.endswith('.xlsx'):
                    save_path += '.xlsx'
                
                # Save to Excel
                df.to_excel(save_path, index=False, engine='openpyxl')
                QMessageBox.information(self, "Success", f"Data exported successfully to {save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
        finally:
            loading.close()

    def load_invoices(self):
        # Show loading screen
        loading = LoadingScreen("Loading Invoices...", self)
        loading.show()
        QApplication.processEvents()

        try:
            self.table.setRowCount(0)
            invoices = self.db_manager.get_all_invoices()
            for invoice in invoices:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(invoice['bill_number']))
                self.table.setItem(row, 1, QTableWidgetItem(invoice['bill_date']))
                self.table.setItem(row, 2, QTableWidgetItem(invoice['bill_to_name']))
                self.table.setItem(row, 3, QTableWidgetItem(f"{invoice['total_amount']:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{invoice['advance_amount']:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoices: {str(e)}")
        finally:
            loading.close()

    def edit_invoice(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select an invoice to edit")
            return
        
        bill_number = self.table.item(selected, 0).text()
        
        # Show loading screen
        loading = LoadingScreen("Loading Invoice Details...", self)
        loading.show()
        QApplication.processEvents()

        try:
            invoice = self.db_manager.get_invoice_by_bill_number(bill_number)
            if not invoice:
                QMessageBox.critical(self, "Error", "Invoice not found")
                return
            
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Invoice - {bill_number}")
            dialog.setMinimumWidth(600)
            layout = QVBoxLayout()
            
            # Form layout for basic details
            form_layout = QFormLayout()
            
            # Date edit
            date_edit = QDateEdit()
            date_edit.setDate(QDate.fromString(invoice['bill_date'], "yyyy-MM-dd"))
            date_edit.setCalendarPopup(True)
            form_layout.addRow("Bill Date:", date_edit)
            
            # Advance amount
            advance = QDoubleSpinBox()
            advance.setMaximum(999999.99)
            advance.setValue(invoice['advance_amount'])
            form_layout.addRow("Advance Amount:", advance)
            
            layout.addLayout(form_layout)
            
            # Add buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(lambda: self.save_invoice_changes(
                dialog, bill_number, date_edit.date().toString("yyyy-MM-dd"), advance.value()
            ))
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoice details: {str(e)}")
        finally:
            loading.close()

    def save_invoice_changes(self, dialog, bill_number, new_date, new_advance):
        # Show loading screen
        loading = LoadingScreen("Saving Changes...", self)
        loading.show()
        QApplication.processEvents()

        try:
            success, error = self.db_manager.update_invoice(bill_number, new_date, new_advance)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self.load_invoices()
                QMessageBox.information(self, "Success", "Invoice updated successfully!")
                dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update invoice: {str(e)}")
        finally:
            loading.close()

    def show_invoice_details(self, row):
        bill_number = self.table.item(row, 0).text()
        
        # Show loading screen
        loading = LoadingScreen("Loading Invoice Details...", self)
        loading.show()
        QApplication.processEvents()

        try:
            invoice = self.db_manager.get_invoice_by_bill_number(bill_number)
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Invoice Details - {bill_number}")
            dialog.setMinimumWidth(600)
            layout = QVBoxLayout()
            
            text = QTextEdit()
            text.setReadOnly(True)
            text.append(f"<h3>Invoice {invoice['bill_number']}</h3>")
            text.append(f"<b>Date:</b> {invoice['bill_date']}\n")
            text.append("<h4>Bill To:</h4>")
            text.append(f"{invoice['bill_to_name']}\n{invoice['bill_to_address']}\nGST: {invoice['bill_to_gst']}\n")
            text.append("<h4>Items:</h4>")
            text.append("<table border='1' cellspacing='0' cellpadding='5' width='100%'>")
            text.append("<tr><th>SNo</th><th>SKU</th><th>Product</th><th>Qty</th><th>Price</th><th>Amount</th></tr>")
            
            for idx, item in enumerate(invoice['items'], 1):
                text.append(f"<tr><td>{idx}</td><td>{item['sku_code']}</td><td>{item['product_name']}</td>" \
                          f"<td>{item['quantity']}</td><td>{item['price_per_unit']:.2f}</td>" \
                          f"<td>{item['amount']:.2f}</td></tr>")
            
            text.append("</table>\n")
            text.append(f"<b>Total Amount:</b> {invoice['total_amount']:.2f}")
            text.append(f"<b>Advance Amount:</b> {invoice['advance_amount']:.2f}")
            
            layout.addWidget(text)
            
            # Add close button
            buttons = QDialogButtonBox(QDialogButtonBox.Close)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load invoice details: {str(e)}")
        finally:
            loading.close()

    def delete_invoice(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select an invoice to delete")
            return
        
        bill_number = self.table.item(selected, 0).text()
        bill_to = self.table.item(selected, 2).text()
        
        # Show confirmation dialog
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete invoice '{bill_number}' for '{bill_to}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Show loading screen
            loading = LoadingScreen("Deleting Invoice...", self)
            loading.show()
            QApplication.processEvents()

            try:
                # Get invoice ID
                invoice = self.db_manager.get_invoice_by_bill_number(bill_number)
                if not invoice:
                    raise ValueError("Invoice not found")
                
                # Delete invoice items first
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice['id'],))
                
                # Delete invoice
                cursor.execute('DELETE FROM invoices WHERE id = ?', (invoice['id'],))
                conn.commit()
                conn.close()
                
                self.load_invoices()
                QMessageBox.information(self, "Success", "Invoice deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")
            finally:
                loading.close()

class ManageClientsTab(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_clients()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Client table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Company Name", "Address", "GST"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Client")
        add_btn.clicked.connect(self.add_client)
        edit_btn = QPushButton("Edit Client")
        edit_btn.clicked.connect(self.edit_client)
        delete_btn = QPushButton("Delete Client")
        delete_btn.clicked.connect(self.delete_client)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def load_clients(self):
        # Show loading screen
        loading = LoadingScreen("Loading Clients...", self)
        loading.show()
        QApplication.processEvents()

        try:
            self.table.setRowCount(0)
            clients = self.db_manager.get_all_companies()
            for client in clients:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(client['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(client['company_name']))
                self.table.setItem(row, 2, QTableWidgetItem(client['address']))
                self.table.setItem(row, 3, QTableWidgetItem(client['gst_number']))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load clients: {str(e)}")
        finally:
            loading.close()

    def add_client(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Client")
        layout = QFormLayout()
        
        name = QLineEdit()
        gst = QLineEdit()
        address = QTextEdit()
        
        layout.addRow("Company Name:", name)
        layout.addRow("GST Number:", gst)
        layout.addRow("Address:", address)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_client(dialog, name.text(), gst.text(), address.toPlainText()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def save_client(self, dialog, name, gst, address):
        if not all([name, gst, address]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Show loading screen
        loading = LoadingScreen("Adding Client...", self)
        loading.show()
        QApplication.processEvents()

        try:
            company_id, error = self.db_manager.add_company(name, address, gst)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self.load_clients()
                QMessageBox.information(self, "Success", "Client added successfully!")
                dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add client: {str(e)}")
        finally:
            loading.close()

    def edit_client(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select a client to edit")
            return
        
        client_id = int(self.table.item(selected, 0).text())
        
        # Show loading screen
        loading = LoadingScreen("Loading Client Details...", self)
        loading.show()
        QApplication.processEvents()

        try:
            client = self.db_manager.get_company_by_id(client_id)
            if not client:
                QMessageBox.critical(self, "Error", "Client not found")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load client details: {str(e)}")
            return
        finally:
            loading.close()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Client")
        layout = QFormLayout()
        
        name = QLineEdit(client['company_name'])
        gst = QLineEdit(client['gst_number'])
        address = QTextEdit()
        address.setText(client['address'])
        address.setMaximumHeight(100)
        
        layout.addRow("Company Name:", name)
        layout.addRow("GST Number:", gst)
        layout.addRow("Address:", address)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.update_client(
            dialog, client_id, name.text(), gst.text(), address.toPlainText()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def update_client(self, dialog, client_id, name, gst, address):
        if not all([name, gst, address]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Show loading screen
        loading = LoadingScreen("Updating Client...", self)
        loading.show()
        QApplication.processEvents()

        try:
            success, error = self.db_manager.update_company(client_id, name, address, gst)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self.load_clients()
                QMessageBox.information(self, "Success", "Client updated successfully!")
                dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update client: {str(e)}")
        finally:
            loading.close()

    def delete_client(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select a client to delete")
            return
        
        client_id = int(self.table.item(selected, 0).text())
        client_name = self.table.item(selected, 1).text()
        
        # Show confirmation dialog with client name
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete client '{client_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Show loading screen
            loading = LoadingScreen("Deleting Client...", self)
            loading.show()
            QApplication.processEvents()

            try:
                success, error = self.db_manager.delete_company(client_id)
                if error:
                    QMessageBox.critical(self, "Error", error)
                else:
                    self.load_clients()
                    QMessageBox.information(self, "Success", "Client deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete client: {str(e)}")
            finally:
                loading.close()

class ManageProductsTab(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Product table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "SKU", "Product Name", "HSN", "Price"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        edit_btn = QPushButton("Edit Product")
        edit_btn.clicked.connect(self.edit_product)
        delete_btn = QPushButton("Delete Product")
        delete_btn.clicked.connect(self.delete_product)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def load_products(self):
        # Show loading screen
        loading = LoadingScreen("Loading Products...", self)
        loading.show()
        QApplication.processEvents()

        try:
            self.table.setRowCount(0)
            products = self.db_manager.get_all_products()
            for product in products:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(product['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(product['sku_code']))
                self.table.setItem(row, 2, QTableWidgetItem(product['product_name']))
                self.table.setItem(row, 3, QTableWidgetItem(product['hsn_code']))
                self.table.setItem(row, 4, QTableWidgetItem(f"{product['price_per_unit']:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
        finally:
            loading.close()

    def add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        layout = QFormLayout()
        
        sku = QLineEdit()
        name = QLineEdit()
        hsn = QLineEdit()
        price = QDoubleSpinBox()
        price.setMaximum(999999.99)
        
        layout.addRow("SKU Code:", sku)
        layout.addRow("Product Name:", name)
        layout.addRow("HSN Code:", hsn)
        layout.addRow("Price:", price)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_product(dialog, sku.text(), name.text(), hsn.text(), price.value()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def save_product(self, dialog, sku, name, hsn, price):
        if not all([sku, name, hsn]) or price <= 0:
            QMessageBox.warning(self, "Error", "All fields are required and price must be positive")
            return
        
        # Show loading screen
        loading = LoadingScreen("Saving Product...", self)
        loading.show()
        QApplication.processEvents()

        try:
            product_id, error = self.db_manager.add_product(sku, name, hsn, price)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self.load_products()
                QMessageBox.information(self, "Success", "Product added successfully!")
                dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
        finally:
            loading.close()

    def edit_product(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select a product to edit")
            return
        
        product_id = int(self.table.item(selected, 0).text())
        
        # Show loading screen
        loading = LoadingScreen("Loading Product Details...", self)
        loading.show()
        QApplication.processEvents()

        try:
            product = self.db_manager.get_product_by_id(product_id)
            if not product:
                QMessageBox.critical(self, "Error", "Product not found")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load product details: {str(e)}")
            return
        finally:
            loading.close()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product")
        layout = QFormLayout()
        
        sku = QLineEdit(product['sku_code'])
        name = QLineEdit(product['product_name'])
        hsn = QLineEdit(product['hsn_code'])
        price = QDoubleSpinBox()
        price.setValue(product['price_per_unit'])
        price.setMaximum(999999.99)
        
        layout.addRow("SKU Code:", sku)
        layout.addRow("Product Name:", name)
        layout.addRow("HSN Code:", hsn)
        layout.addRow("Price:", price)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.update_product(
            dialog, product_id, sku.text(), name.text(), hsn.text(), price.value()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def update_product(self, dialog, product_id, sku, name, hsn, price):
        if not all([sku, name, hsn]) or price <= 0:
            QMessageBox.warning(self, "Error", "All fields are required and price must be positive")
            return
        
        # Show loading screen
        loading = LoadingScreen("Updating Product...", self)
        loading.show()
        QApplication.processEvents()

        try:
            success, error = self.db_manager.update_product(product_id, sku, name, hsn, price)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self.load_products()
                QMessageBox.information(self, "Success", "Product updated successfully!")
                dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update product: {str(e)}")
        finally:
            loading.close()

    def delete_product(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "Please select a product to delete")
            return
        
        product_id = int(self.table.item(selected, 0).text())
        product_name = self.table.item(selected, 2).text()
        
        # Show confirmation dialog
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete product '{product_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Show loading screen
            loading = LoadingScreen("Deleting Product...", self)
            loading.show()
            QApplication.processEvents()

            try:
                success, error = self.db_manager.delete_product(product_id)
                if error:
                    QMessageBox.critical(self, "Error", error)
                else:
                    self.load_products()
                    QMessageBox.information(self, "Success", "Product deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
            finally:
                loading.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        
        self.setWindowTitle("Invoice Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(GenerateBillTab(self.db_manager), "Generate Bill")
        tabs.addTab(DisplayBillsTab(self.db_manager), "Display Bills")
        tabs.addTab(ManageClientsTab(self.db_manager), "Manage Clients")
        tabs.addTab(ManageProductsTab(self.db_manager), "Manage Products")
        
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())