#!/usr/bin/env python3
"""
Generate extended test samples:
- 10 perfect match + 10 mismatch for 2-way
- 10 perfect match + 10 mismatch for 3-way
Total: 40 samples
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
    """Generate 40 test samples"""
    print("Generating Extended Test Samples (40 total)")
    print("=" * 70)
    
    # Create directories
    test_dir = Path("datasets/test_samples")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Item templates for variety
    item_templates = [
        {"description": "Steel Rods", "base_qty": 100, "base_price": 50.00},
        {"description": "Concrete Mix", "base_qty": 50, "base_price": 25.00},
        {"description": "Paint Cans", "base_qty": 20, "base_price": 15.00},
        {"description": "Wooden Planks", "base_qty": 200, "base_price": 30.00},
        {"description": "Nails Box", "base_qty": 10, "base_price": 12.00},
        {"description": "Screws Box", "base_qty": 15, "base_price": 10.00},
        {"description": "PVC Pipes", "base_qty": 75, "base_price": 40.00},
        {"description": "Copper Tubes", "base_qty": 30, "base_price": 60.00},
        {"description": "Glass Panels", "base_qty": 50, "base_price": 80.00},
        {"description": "Aluminum Sheets", "base_qty": 40, "base_price": 55.00},
        {"description": "Cement Bags", "base_qty": 100, "base_price": 20.00},
        {"description": "Brick Pallets", "base_qty": 25, "base_price": 150.00},
        {"description": "Roofing Tiles", "base_qty": 200, "base_price": 8.00},
        {"description": "Insulation Rolls", "base_qty": 30, "base_price": 45.00},
        {"description": "Electrical Wire", "base_qty": 500, "base_price": 2.50},
    ]
    
    sample_num = 1
    
    # ========== 2-WAY MATCHING SAMPLES ==========
    print("\n=== 2-Way Matching Samples ===")
    
    # 10 Perfect Matches for 2-Way
    print("\nGenerating 10 Perfect Match samples for 2-Way...")
    for i in range(10):
        # Select 3 random items
        selected_items = random.sample(item_templates, 3)
        items = []
        for item_template in selected_items:
            items.append({
                "description": item_template["description"],
                "quantity": item_template["base_qty"] + random.randint(-10, 10),
                "unit_price": item_template["base_price"] + random.uniform(-5, 5),
                "total": 0
            })
            items[-1]["total"] = items[-1]["quantity"] * items[-1]["unit_price"]
        
        po_num = f"PO-2024-{1000 + sample_num}"
        inv_num = f"INV-{50000 + sample_num}"
        
        create_purchase_order_pdf(
            str(test_dir / f"Sample{sample_num}_PO_MATCH.pdf"),
            po_num, VENDOR, generate_date(30 + i), items
        )
        create_invoice_pdf(
            str(test_dir / f"Sample{sample_num}_INV_MATCH.pdf"),
            inv_num, po_num, VENDOR, generate_date(15 + i), items
        )
        print(f"  Sample{sample_num}: Created PO + Invoice (MATCH)")
        sample_num += 1
    
    # 10 Mismatches for 2-Way
    print("\nGenerating 10 Mismatch samples for 2-Way...")
    for i in range(10):
        # Select 3 random items for PO
        selected_items = random.sample(item_templates, 3)
        items_po = []
        for item_template in selected_items:
            items_po.append({
                "description": item_template["description"],
                "quantity": item_template["base_qty"] + random.randint(-10, 10),
                "unit_price": item_template["base_price"] + random.uniform(-5, 5),
                "total": 0
            })
            items_po[-1]["total"] = items_po[-1]["quantity"] * items_po[-1]["unit_price"]
        
        # Create invoice with discrepancies
        items_inv = []
        for idx, item in enumerate(items_po):
            inv_item = item.copy()
            
            # Introduce different types of discrepancies
            discrepancy_type = i % 4
            if discrepancy_type == 0 and idx == 0:
                # Quantity mismatch
                inv_item["quantity"] = int(item["quantity"] * 0.9)
                inv_item["total"] = inv_item["quantity"] * inv_item["unit_price"]
            elif discrepancy_type == 1 and idx == 0:
                # Price mismatch
                inv_item["unit_price"] = item["unit_price"] * 1.15
                inv_item["total"] = inv_item["quantity"] * inv_item["unit_price"]
            elif discrepancy_type == 2 and idx == 1:
                # Missing item (skip this item)
                continue
            
            items_inv.append(inv_item)
        
        # Add extra item for some samples
        if discrepancy_type == 3:
            extra_item = random.choice([t for t in item_templates if t not in selected_items])
            items_inv.append({
                "description": extra_item["description"],
                "quantity": extra_item["base_qty"],
                "unit_price": extra_item["base_price"],
                "total": extra_item["base_qty"] * extra_item["base_price"]
            })
        
        po_num = f"PO-2024-{1000 + sample_num}"
        inv_num = f"INV-{50000 + sample_num}"
        
        create_purchase_order_pdf(
            str(test_dir / f"Sample{sample_num}_PO_MISMATCH.pdf"),
            po_num, VENDOR, generate_date(30 + i), items_po
        )
        create_invoice_pdf(
            str(test_dir / f"Sample{sample_num}_INV_MISMATCH.pdf"),
            inv_num, po_num, VENDOR, generate_date(15 + i), items_inv
        )
        print(f"  Sample{sample_num}: Created PO + Invoice (MISMATCH)")
        sample_num += 1
    
    # ========== 3-WAY MATCHING SAMPLES ==========
    print("\n=== 3-Way Matching Samples ===")
    
    # 10 Perfect Matches for 3-Way
    print("\nGenerating 10 Perfect Match samples for 3-Way...")
    for i in range(10):
        # Select 2 random items
        selected_items = random.sample(item_templates, 2)
        items = []
        for item_template in selected_items:
            items.append({
                "description": item_template["description"],
                "quantity": item_template["base_qty"] + random.randint(-10, 10),
                "unit_price": item_template["base_price"] + random.uniform(-5, 5),
                "total": 0
            })
            items[-1]["total"] = items[-1]["quantity"] * items[-1]["unit_price"]
        
        po_num = f"PO-2024-{1000 + sample_num}"
        inv_num = f"INV-{50000 + sample_num}"
        gr_num = f"GR-{300000 + sample_num}"
        
        create_purchase_order_pdf(
            str(test_dir / f"Sample{sample_num}_PO_MATCH.pdf"),
            po_num, VENDOR, generate_date(35 + i), items
        )
        create_invoice_pdf(
            str(test_dir / f"Sample{sample_num}_INV_MATCH.pdf"),
            inv_num, po_num, VENDOR, generate_date(20 + i), items
        )
        create_goods_receipt_pdf(
            str(test_dir / f"Sample{sample_num}_GR_MATCH.pdf"),
            gr_num, po_num, inv_num, VENDOR, generate_date(5 + i), items
        )
        print(f"  Sample{sample_num}: Created PO + Invoice + GR (MATCH)")
        sample_num += 1
    
    # 10 Mismatches for 3-Way
    print("\nGenerating 10 Mismatch samples for 3-Way...")
    for i in range(10):
        # Select 2 random items
        selected_items = random.sample(item_templates, 2)
        items_po = []
        for item_template in selected_items:
            items_po.append({
                "description": item_template["description"],
                "quantity": item_template["base_qty"] + random.randint(-10, 10),
                "unit_price": item_template["base_price"] + random.uniform(-5, 5),
                "total": 0
            })
            items_po[-1]["total"] = items_po[-1]["quantity"] * items_po[-1]["unit_price"]
        
        # Create invoice with potential discrepancies
        items_inv = []
        for idx, item in enumerate(items_po):
            inv_item = item.copy()
            
            # Introduce price mismatch for some samples
            if i % 3 == 0 and idx == 0:
                inv_item["unit_price"] = item["unit_price"] * 1.1
                inv_item["total"] = inv_item["quantity"] * inv_item["unit_price"]
            
            items_inv.append(inv_item)
        
        # Create GR with discrepancies
        items_gr = []
        for idx, item in enumerate(items_inv):
            gr_item = item.copy()
            
            # Introduce quantity discrepancies (partial receipt, damaged goods)
            discrepancy_type = i % 3
            if discrepancy_type == 0 and idx == 0:
                # Partial receipt
                gr_item["quantity"] = int(item["quantity"] * 0.9)
                gr_item["total"] = gr_item["quantity"] * gr_item["unit_price"]
            elif discrepancy_type == 1 and idx == 1:
                # Damaged goods
                gr_item["quantity"] = int(item["quantity"] * 0.95)
                gr_item["total"] = gr_item["quantity"] * gr_item["unit_price"]
            
            items_gr.append(gr_item)
        
        po_num = f"PO-2024-{1000 + sample_num}"
        inv_num = f"INV-{50000 + sample_num}"
        gr_num = f"GR-{300000 + sample_num}"
        
        create_purchase_order_pdf(
            str(test_dir / f"Sample{sample_num}_PO_MISMATCH.pdf"),
            po_num, VENDOR, generate_date(40 + i), items_po
        )
        create_invoice_pdf(
            str(test_dir / f"Sample{sample_num}_INV_MISMATCH.pdf"),
            inv_num, po_num, VENDOR, generate_date(25 + i), items_inv
        )
        create_goods_receipt_pdf(
            str(test_dir / f"Sample{sample_num}_GR_MISMATCH.pdf"),
            gr_num, po_num, inv_num, VENDOR, generate_date(10 + i), items_gr
        )
        print(f"  Sample{sample_num}: Created PO + Invoice + GR (MISMATCH)")
        sample_num += 1
    
    # Create README
    readme_content = """# Test Samples

This directory contains 40 curated test samples for demonstration:

## 2-Way Matching Samples (20 samples)

### Perfect Match Samples (10 samples)
- Sample1 through Sample10: PO and Invoice match perfectly
- Files: SampleX_PO_MATCH.pdf + SampleX_INV_MATCH.pdf

### Mismatch Samples (10 samples)
- Sample11 through Sample20: Various discrepancies between PO and Invoice
- Files: SampleX_PO_MISMATCH.pdf + SampleX_INV_MISMATCH.pdf
- Discrepancy types: Quantity mismatch, Price mismatch, Missing items, Extra items

## 3-Way Matching Samples (20 samples)

### Perfect Match Samples (10 samples)
- Sample21 through Sample30: PO, Invoice, and GR all match perfectly
- Files: SampleX_PO_MATCH.pdf + SampleX_INV_MATCH.pdf + SampleX_GR_MATCH.pdf

### Mismatch Samples (10 samples)
- Sample31 through Sample40: Various discrepancies across documents
- Files: SampleX_PO_MISMATCH.pdf + SampleX_INV_MISMATCH.pdf + SampleX_GR_MISMATCH.pdf
- Discrepancy types: Price mismatch, Partial receipt, Damaged goods

## Usage

Upload these files in the FinVerge frontend to test the verification system.
"""
    
    with open(test_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print("\n" + "=" * 70)
    print("Test Samples Generated Successfully!")
    print(f"\nLocation: {test_dir}/")
    print("\nSummary:")
    print("  2-Way Match:     10 samples (Sample1-10)")
    print("  2-Way Mismatch:  10 samples (Sample11-20)")
    print("  3-Way Match:     10 samples (Sample21-30)")
    print("  3-Way Mismatch:  10 samples (Sample31-40)")
    print(f"\nTotal: {sample_num - 1} test samples")


if __name__ == "__main__":
    main()
