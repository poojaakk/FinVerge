#!/usr/bin/env python3
"""
Generate 4 curated test samples:
- 2-Way: 1 perfect match + 1 with discrepancies
- 3-Way: 1 perfect match + 1 with discrepancies
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import json

# Sample data
VENDOR = {
    "name": "BuildMart Supplies",
    "address": "123 Industrial Ave, Chicago, IL 60601",
    "phone": "(312) 555-0100",
    "email": "orders@buildmart.com"
}

COMPANY_INFO = {
    "name": "FinVerge Construction Inc",
    "address": "1000 Corporate Plaza, New York, NY 10001",
    "phone": "(212) 555-1000",
    "email": "procurement@finverge.com"
}


def generate_date(days_ago=0):
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%B %d, %Y")


def create_purchase_order_pdf(filename, po_number, vendor, po_date, items):
    """Generate a Purchase Order PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                 textColor=colors.HexColor('#2c3e50'), spaceAfter=30, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#34495e'))
    
    story.append(Paragraph("PURCHASE ORDER", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Company and Vendor Info
    info_data = [
        [Paragraph("<b>From:</b>", header_style), Paragraph("<b>To:</b>", header_style)],
        [Paragraph(f"<b>{COMPANY_INFO['name']}</b>", header_style), Paragraph(f"<b>{vendor['name']}</b>", header_style)],
        [Paragraph(COMPANY_INFO['address'], header_style), Paragraph(vendor['address'], header_style)],
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # PO Details
    po_details = [[Paragraph("<b>PO Number:</b>", header_style), Paragraph(po_number, header_style),
                   Paragraph("<b>Date:</b>", header_style), Paragraph(po_date, header_style)]]
    
    details_table = Table(po_details, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [['Item Description', 'Quantity', 'Unit Price', 'Total']]
    for item in items:
        items_data.append([item['description'], str(item['quantity']), f"${item['unit_price']:.2f}", f"${item['total']:.2f}"])
    
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax
    
    items_data.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
    items_data.append(['', '', 'Tax (8%):', f"${tax:.2f}"])
    items_data.append(['', '', 'Total:', f"${total:.2f}"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
        ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(items_table)
    
    doc.build(story)


def create_invoice_pdf(filename, invoice_number, po_number, vendor, invoice_date, items):
    """Generate an Invoice PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                 textColor=colors.HexColor('#e74c3c'), spaceAfter=30, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#34495e'))
    
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Vendor and Company Info
    info_data = [
        [Paragraph("<b>From:</b>", header_style), Paragraph("<b>Bill To:</b>", header_style)],
        [Paragraph(f"<b>{vendor['name']}</b>", header_style), Paragraph(f"<b>{COMPANY_INFO['name']}</b>", header_style)],
        [Paragraph(vendor['address'], header_style), Paragraph(COMPANY_INFO['address'], header_style)],
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Details
    invoice_details = [
        [Paragraph("<b>Invoice #:</b>", header_style), Paragraph(invoice_number, header_style),
         Paragraph("<b>Date:</b>", header_style), Paragraph(invoice_date, header_style)],
        [Paragraph("<b>PO Reference:</b>", header_style), Paragraph(po_number, header_style), Paragraph("", header_style), Paragraph("", header_style)],
    ]
    
    details_table = Table(invoice_details, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef5e7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f39c12')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [['Item Description', 'Quantity', 'Unit Price', 'Total']]
    for item in items:
        items_data.append([item['description'], str(item['quantity']), f"${item['unit_price']:.2f}", f"${item['total']:.2f}"])
    
    subtotal = sum(item['total'] for item in items)
    tax = subtotal * 0.08
    total = subtotal + tax
    
    items_data.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
    items_data.append(['', '', 'Tax (8%):', f"${tax:.2f}"])
    items_data.append(['', '', '<b>Amount Due:</b>', f"<b>${total:.2f}</b>"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
    ]))
    story.append(items_table)
    
    doc.build(story)


def create_goods_receipt_pdf(filename, gr_number, po_number, invoice_number, vendor, gr_date, items):
    """Generate a Goods Receipt PDF"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                 textColor=colors.HexColor('#27ae60'), spaceAfter=30, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#34495e'))
    
    story.append(Paragraph("GOODS RECEIPT", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Company and Vendor Info
    info_data = [
        [Paragraph("<b>Received By:</b>", header_style), Paragraph("<b>Received From:</b>", header_style)],
        [Paragraph(f"<b>{COMPANY_INFO['name']}</b>", header_style), Paragraph(f"<b>{vendor['name']}</b>", header_style)],
        [Paragraph(COMPANY_INFO['address'], header_style), Paragraph(vendor['address'], header_style)],
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # GR Details
    gr_details = [
        [Paragraph("<b>GR Number:</b>", header_style), Paragraph(gr_number, header_style),
         Paragraph("<b>Date:</b>", header_style), Paragraph(gr_date, header_style)],
        [Paragraph("<b>PO Reference:</b>", header_style), Paragraph(po_number, header_style),
         Paragraph("<b>Invoice #:</b>", header_style), Paragraph(invoice_number, header_style)],
    ]
    
    details_table = Table(gr_details, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#d5f4e6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#27ae60')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [['Item Description', 'Quantity Received', 'Unit Price', 'Total']]
    for item in items:
        items_data.append([item['description'], str(item['quantity']), f"${item['unit_price']:.2f}", f"${item['total']:.2f}"])
    
    subtotal = sum(item['total'] for item in items)
    items_data.append(['', '', 'Total Received:', f"${subtotal:.2f}"])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(items_table)
    
    doc.build(story)


def main():
    """Generate 4 test samples"""
    print(" Generating 4 Test Samples")
    print("=" * 70)
    
    # Create directories
    test_dir = Path("datasets/test_samples")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample 1: 2-Way Perfect Match
    print("\n Sample 1: 2-Way Perfect Match")
    items_1 = [
        {"description": "Steel Rods", "quantity": 100, "unit_price": 50.00, "total": 5000.00},
        {"description": "Concrete Mix", "quantity": 50, "unit_price": 25.00, "total": 1250.00},
        {"description": "Paint Cans", "quantity": 20, "unit_price": 15.00, "total": 300.00}
    ]
    
    create_purchase_order_pdf(
        str(test_dir / "Sample1_PO_MATCH.pdf"),
        "PO-2024-1001", VENDOR, generate_date(30), items_1
    )
    create_invoice_pdf(
        str(test_dir / "Sample1_INV_MATCH.pdf"),
        "INV-50001", "PO-2024-1001", VENDOR, generate_date(15), items_1
    )
    print(" Created: Sample1_PO_MATCH.pdf + Sample1_INV_MATCH.pdf")
    
    # Sample 2: 2-Way With Discrepancies
    print("\n Sample 2: 2-Way With Discrepancies")
    items_2_po = [
        {"description": "Wooden Planks", "quantity": 200, "unit_price": 30.00, "total": 6000.00},
        {"description": "Nails Box", "quantity": 10, "unit_price": 12.00, "total": 120.00},
        {"description": "Screws Box", "quantity": 15, "unit_price": 10.00, "total": 150.00}
    ]
    
    items_2_inv = [
        {"description": "Wooden Planks", "quantity": 180, "unit_price": 30.00, "total": 5400.00},  # Quantity mismatch
        {"description": "Nails Box", "quantity": 10, "unit_price": 15.00, "total": 150.00},  # Price mismatch
        {"description": "Screws Box", "quantity": 15, "unit_price": 10.00, "total": 150.00},
        {"description": "Extra Bolts", "quantity": 5, "unit_price": 8.00, "total": 40.00}  # Extra item
    ]
    
    create_purchase_order_pdf(
        str(test_dir / "Sample2_PO_MISMATCH.pdf"),
        "PO-2024-1002", VENDOR, generate_date(25), items_2_po
    )
    create_invoice_pdf(
        str(test_dir / "Sample2_INV_MISMATCH.pdf"),
        "INV-50002", "PO-2024-1002", VENDOR, generate_date(10), items_2_inv
    )
    print(" Created: Sample2_PO_MISMATCH.pdf + Sample2_INV_MISMATCH.pdf")
    print("   Discrepancies: Quantity mismatch, Price mismatch, Extra item")
    
    # Sample 3: 3-Way Perfect Match
    print("\n Sample 3: 3-Way Perfect Match")
    items_3 = [
        {"description": "PVC Pipes", "quantity": 75, "unit_price": 40.00, "total": 3000.00},
        {"description": "Copper Tubes", "quantity": 30, "unit_price": 60.00, "total": 1800.00}
    ]
    
    create_purchase_order_pdf(
        str(test_dir / "Sample3_PO_MATCH.pdf"),
        "PO-2024-1003", VENDOR, generate_date(35), items_3
    )
    create_invoice_pdf(
        str(test_dir / "Sample3_INV_MATCH.pdf"),
        "INV-50003", "PO-2024-1003", VENDOR, generate_date(20), items_3
    )
    create_goods_receipt_pdf(
        str(test_dir / "Sample3_GR_MATCH.pdf"),
        "GR-300001", "PO-2024-1003", "INV-50003", VENDOR, generate_date(5), items_3
    )
    print(" Created: Sample3_PO_MATCH.pdf + Sample3_INV_MATCH.pdf + Sample3_GR_MATCH.pdf")
    
    # Sample 4: 3-Way With Discrepancies
    print("\n Sample 4: 3-Way With Discrepancies")
    items_4_po = [
        {"description": "Glass Panels", "quantity": 50, "unit_price": 80.00, "total": 4000.00},
        {"description": "Aluminum Sheets", "quantity": 40, "unit_price": 55.00, "total": 2200.00}
    ]
    
    items_4_inv = [
        {"description": "Glass Panels", "quantity": 50, "unit_price": 85.00, "total": 4250.00},  # Price mismatch
        {"description": "Aluminum Sheets", "quantity": 40, "unit_price": 55.00, "total": 2200.00}
    ]
    
    items_4_gr = [
        {"description": "Glass Panels", "quantity": 45, "unit_price": 85.00, "total": 3825.00},  # Partial receipt
        {"description": "Aluminum Sheets", "quantity": 38, "unit_price": 55.00, "total": 2090.00}  # Damaged goods
    ]
    
    create_purchase_order_pdf(
        str(test_dir / "Sample4_PO_MISMATCH.pdf"),
        "PO-2024-1004", VENDOR, generate_date(40), items_4_po
    )
    create_invoice_pdf(
        str(test_dir / "Sample4_INV_MISMATCH.pdf"),
        "INV-50004", "PO-2024-1004", VENDOR, generate_date(25), items_4_inv
    )
    create_goods_receipt_pdf(
        str(test_dir / "Sample4_GR_MISMATCH.pdf"),
        "GR-300002", "PO-2024-1004", "INV-50004", VENDOR, generate_date(10), items_4_gr
    )
    print(" Created: Sample4_PO_MISMATCH.pdf + Sample4_INV_MISMATCH.pdf + Sample4_GR_MISMATCH.pdf")
    print("   Discrepancies: Price mismatch, Partial receipt, Damaged goods")
    
    # Create README
    readme_content = """# Test Samples

This directory contains 4 curated test samples for demonstration:

## 2-Way Matching Samples

### Sample 1: Perfect Match 
- **Files**: Sample1_PO_MATCH.pdf + Sample1_INV_MATCH.pdf
- **Expected Result**: All items match perfectly
- **Items**: Steel Rods, Concrete Mix, Paint Cans

### Sample 2: With Discrepancies ⚠️
- **Files**: Sample2_PO_MISMATCH.pdf + Sample2_INV_MISMATCH.pdf
- **Expected Result**: Multiple discrepancies detected
- **Discrepancies**:
  - Wooden Planks: Quantity mismatch (200 vs 180)
  - Nails Box: Price mismatch ($12 vs $15)
  - Extra Bolts: Extra item not in PO

## 3-Way Matching Samples

### Sample 3: Perfect Match 
- **Files**: Sample3_PO_MATCH.pdf + Sample3_INV_MATCH.pdf + Sample3_GR_MATCH.pdf
- **Expected Result**: All documents match perfectly
- **Items**: PVC Pipes, Copper Tubes

### Sample 4: With Discrepancies ⚠️
- **Files**: Sample4_PO_MISMATCH.pdf + Sample4_INV_MISMATCH.pdf + Sample4_GR_MISMATCH.pdf
- **Expected Result**: Multiple discrepancies across documents
- **Discrepancies**:
  - Glass Panels: Price mismatch ($80 vs $85), Partial receipt (50 vs 45)
  - Aluminum Sheets: Damaged goods (40 vs 38 received)

## Usage

Upload these files in the FinVerge frontend to test the verification system.
"""
    
    with open(test_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print("\n" + "=" * 70)
    print(" Test Samples Generated Successfully!")
    print(f"\n Location: {test_dir}/")
    print("\n Files Created:")
    print("  2-Way Match:     Sample1_PO_MATCH.pdf + Sample1_INV_MATCH.pdf")
    print("  2-Way Mismatch:  Sample2_PO_MISMATCH.pdf + Sample2_INV_MISMATCH.pdf")
    print("  3-Way Match:     Sample3_PO_MATCH.pdf + Sample3_INV_MATCH.pdf + Sample3_GR_MATCH.pdf")
    print("  3-Way Mismatch:  Sample4_PO_MISMATCH.pdf + Sample4_INV_MISMATCH.pdf + Sample4_GR_MISMATCH.pdf")
    print("\n Use these samples to test the verification system!")


if __name__ == "__main__":
    main()
