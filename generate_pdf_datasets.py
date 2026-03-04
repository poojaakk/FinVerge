#!/usr/bin/env python3
"""
PDF Dataset Generator for FinVerge
Generates separate 2-way and 3-way matching PDF datasets
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
ITEMS = [
    "Steel Rod", "Concrete Mix", "Cement Bags", "Wooden Planks", "Paint Cans",
    "Electrical Wire", "PVC Pipes", "Copper Tubes", "Aluminum Sheets", "Glass Panels",
    "Screws Box", "Nails Box", "Bolts Set", "Washers Pack", "Hinges Set",
    "Door Handles", "Window Frames", "Roofing Tiles", "Insulation Rolls", "Drywall Sheets",
    "Plywood Boards", "Lumber 2x4", "Rebar Bundles", "Gravel Bags", "Sand Bags",
    "Bricks Pallet", "Tiles Box", "Adhesive Tubes", "Sealant Cans", "Primer Bottles"
]

VENDORS = [
    {"name": "BuildMart Supplies", "address": "123 Industrial Ave, Chicago, IL 60601", "phone": "(312) 555-0100", "email": "orders@buildmart.com"},
    {"name": "Industrial Materials Co", "address": "456 Commerce St, Houston, TX 77002", "phone": "(713) 555-0200", "email": "sales@indmat.com"},
    {"name": "ProConstruct Ltd", "address": "789 Builder Blvd, Phoenix, AZ 85001", "phone": "(602) 555-0300", "email": "info@proconstruct.com"},
    {"name": "Quality Hardware Inc", "address": "321 Supply Lane, Denver, CO 80202", "phone": "(303) 555-0400", "email": "orders@qualityhw.com"},
    {"name": "MegaSupply Corp", "address": "654 Warehouse Dr, Atlanta, GA 30303", "phone": "(404) 555-0500", "email": "sales@megasupply.com"},
    {"name": "Premier Building Materials", "address": "987 Trade Center, Seattle, WA 98101", "phone": "(206) 555-0600", "email": "contact@premierbm.com"}
]

COMPANY_INFO = {
    "name": "FinVerge Construction Inc",
    "address": "1000 Corporate Plaza, New York, NY 10001",
    "phone": "(212) 555-1000",
    "email": "procurement@finverge.com"
}


def generate_po_number():
    return f"PO-{random.randint(2024, 2025)}-{random.randint(1000, 9999)}"


def generate_invoice_number():
    return f"INV-{random.randint(10000, 99999)}"


def generate_gr_number():
    return f"GR-{random.randint(100000, 999999)}"


def generate_date(days_ago=0):
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%B %d, %Y")


def generate_items(num_items=5):
    selected_items = random.sample(ITEMS, min(num_items, len(ITEMS)))
    items = []
    
    for item_name in selected_items:
        base_price = random.randint(50, 1000)
        quantity = random.choice([10, 25, 50, 100, 200, 500])
        
        items.append({
            "description": item_name,
            "quantity": quantity,
            "unit_price": float(base_price),
            "total": quantity * base_price
        })
    
    return items


def apply_discrepancy(po_items, discrepancy_type):
    """Apply discrepancy to create invoice items"""
    invoice_items = []
    
    if discrepancy_type == "perfect_match":
        invoice_items = [item.copy() for item in po_items]
    
    elif discrepancy_type == "quantity_mismatch":
        for item in po_items:
            new_item = item.copy()
            if random.random() > 0.5:
                variance = random.choice([-10, -5, 5, 10, 15])
                new_item["quantity"] = max(1, item["quantity"] + variance)
                new_item["total"] = new_item["quantity"] * new_item["unit_price"]
            invoice_items.append(new_item)
    
    elif discrepancy_type == "price_mismatch":
        for item in po_items:
            new_item = item.copy()
            if random.random() > 0.5:
                variance_percent = random.choice([0.03, 0.07, 0.10, 0.15])
                direction = random.choice([-1, 1])
                new_item["unit_price"] = round(item["unit_price"] * (1 + direction * variance_percent), 2)
                new_item["total"] = new_item["quantity"] * new_item["unit_price"]
            invoice_items.append(new_item)
    
    elif discrepancy_type == "missing_item":
        num_to_keep = max(1, len(po_items) - random.randint(1, 2))
        invoice_items = random.sample([item.copy() for item in po_items], num_to_keep)
    
    elif discrepancy_type == "extra_item":
        invoice_items = [item.copy() for item in po_items]
        num_extra = random.randint(1, 2)
        extra_items = generate_items(num_extra)
        invoice_items.extend(extra_items)
    
    elif discrepancy_type == "partial_delivery":
        for item in po_items:
            new_item = item.copy()
            new_item["quantity"] = int(item["quantity"] * random.uniform(0.7, 0.95))
            new_item["total"] = new_item["quantity"] * new_item["unit_price"]
            invoice_items.append(new_item)
    
    return invoice_items


def generate_gr_items(po_items, invoice_items, gr_scenario):
    """Generate Goods Receipt items for 3-way matching"""
    gr_items = []
    
    if gr_scenario == "match_invoice":
        gr_items = [item.copy() for item in invoice_items]
    
    elif gr_scenario == "match_po":
        gr_items = [item.copy() for item in po_items]
    
    elif gr_scenario == "partial_receipt":
        for item in invoice_items:
            new_item = item.copy()
            new_item["quantity"] = int(item["quantity"] * random.uniform(0.8, 0.95))
            new_item["total"] = new_item["quantity"] * new_item["unit_price"]
            gr_items.append(new_item)
    
    elif gr_scenario == "damaged_goods":
        for item in invoice_items:
            new_item = item.copy()
            if random.random() > 0.7:
                new_item["quantity"] = int(item["quantity"] * random.uniform(0.85, 0.98))
                new_item["total"] = new_item["quantity"] * new_item["unit_price"]
            gr_items.append(new_item)
    
    return gr_items


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
        [Paragraph(f"Phone: {COMPANY_INFO['phone']}", header_style), Paragraph(f"Phone: {vendor['phone']}", header_style)],
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 5)]))
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
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Received By:</b> _____________________ Date: _____________________", header_style))
    
    doc.build(story)


def generate_2way_dataset(num_pairs=500):
    """Generate 2-way matching dataset (PO + Invoice)"""
    base_dir = Path("datasets/2way_matching")
    po_dir = base_dir / "purchase_orders"
    invoice_dir = base_dir / "invoices"
    po_dir.mkdir(parents=True, exist_ok=True)
    invoice_dir.mkdir(parents=True, exist_ok=True)
    
    discrepancy_types = ["perfect_match", "quantity_mismatch", "price_mismatch", "missing_item", "extra_item", "partial_delivery"]
    metadata = []
    
    print(f"\n Generating 2-Way Matching Dataset ({num_pairs} pairs)...")
    print("=" * 70)
    
    for i in range(num_pairs):
        po_number = generate_po_number()
        invoice_number = generate_invoice_number()
        vendor = random.choice(VENDORS)
        po_date = generate_date(random.randint(30, 90))
        invoice_date = generate_date(random.randint(1, 30))
        discrepancy_type = random.choice(discrepancy_types)
        num_items = random.randint(3, 8)
        
        po_items = generate_items(num_items)
        invoice_items = apply_discrepancy(po_items, discrepancy_type)
        
        po_filename = po_dir / f"PO_{po_number.replace('-', '_')}.pdf"
        invoice_filename = invoice_dir / f"INV_{invoice_number.replace('-', '_')}.pdf"
        
        create_purchase_order_pdf(str(po_filename), po_number, vendor, po_date, po_items)
        create_invoice_pdf(str(invoice_filename), invoice_number, po_number, vendor, invoice_date, invoice_items)
        
        metadata.append({
            "pair_id": i + 1,
            "po_number": po_number,
            "invoice_number": invoice_number,
            "po_file": str(po_filename),
            "invoice_file": str(invoice_filename),
            "vendor": vendor['name'],
            "discrepancy_type": discrepancy_type,
        })
        
        if (i + 1) % 100 == 0:
            print(f" Generated {i + 1}/{num_pairs} pairs...")
    
    metadata_file = base_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f" 2-Way Dataset Complete: {num_pairs} pairs generated")
    return metadata


def generate_3way_dataset(num_sets=500):
    """Generate 3-way matching dataset (PO + Invoice + GR)"""
    base_dir = Path("datasets/3way_matching")
    po_dir = base_dir / "purchase_orders"
    invoice_dir = base_dir / "invoices"
    gr_dir = base_dir / "goods_receipts"
    po_dir.mkdir(parents=True, exist_ok=True)
    invoice_dir.mkdir(parents=True, exist_ok=True)
    gr_dir.mkdir(parents=True, exist_ok=True)
    
    discrepancy_types = ["perfect_match", "quantity_mismatch", "price_mismatch", "missing_item", "extra_item", "partial_delivery"]
    gr_scenarios = ["match_invoice", "match_po", "partial_receipt", "damaged_goods"]
    metadata = []
    
    print(f"\n Generating 3-Way Matching Dataset ({num_sets} sets)...")
    print("=" * 70)
    
    for i in range(num_sets):
        po_number = generate_po_number()
        invoice_number = generate_invoice_number()
        gr_number = generate_gr_number()
        vendor = random.choice(VENDORS)
        po_date = generate_date(random.randint(30, 90))
        invoice_date = generate_date(random.randint(15, 30))
        gr_date = generate_date(random.randint(1, 15))
        discrepancy_type = random.choice(discrepancy_types)
        gr_scenario = random.choice(gr_scenarios)
        num_items = random.randint(3, 8)
        
        po_items = generate_items(num_items)
        invoice_items = apply_discrepancy(po_items, discrepancy_type)
        gr_items = generate_gr_items(po_items, invoice_items, gr_scenario)
        
        po_filename = po_dir / f"PO_{po_number.replace('-', '_')}.pdf"
        invoice_filename = invoice_dir / f"INV_{invoice_number.replace('-', '_')}.pdf"
        gr_filename = gr_dir / f"GR_{gr_number.replace('-', '_')}.pdf"
        
        create_purchase_order_pdf(str(po_filename), po_number, vendor, po_date, po_items)
        create_invoice_pdf(str(invoice_filename), invoice_number, po_number, vendor, invoice_date, invoice_items)
        create_goods_receipt_pdf(str(gr_filename), gr_number, po_number, invoice_number, vendor, gr_date, gr_items)
        
        metadata.append({
            "set_id": i + 1,
            "po_number": po_number,
            "invoice_number": invoice_number,
            "gr_number": gr_number,
            "po_file": str(po_filename),
            "invoice_file": str(invoice_filename),
            "gr_file": str(gr_filename),
            "vendor": vendor['name'],
            "discrepancy_type": discrepancy_type,
            "gr_scenario": gr_scenario,
        })
        
        if (i + 1) % 100 == 0:
            print(f" Generated {i + 1}/{num_sets} sets...")
    
    metadata_file = base_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f" 3-Way Dataset Complete: {num_sets} sets generated")
    return metadata


def print_statistics(metadata_2way, metadata_3way):
    """Print dataset statistics"""
    print("\n" + "=" * 70)
    print("📊 DATASET STATISTICS")
    print("=" * 70)
    
    print(f"\n2-Way Matching: {len(metadata_2way)} pairs")
    print(f"3-Way Matching: {len(metadata_3way)} sets")
    print(f"Total PDFs Generated: {len(metadata_2way) * 2 + len(metadata_3way) * 3}")


def main():
    """Main function"""
    print("📄 FinVerge PDF Dataset Generator")
    print("=" * 70)
    print("Generating separate 2-way and 3-way matching datasets...")
    
    # Generate datasets
    metadata_2way = generate_2way_dataset(num_pairs=500)
    metadata_3way = generate_3way_dataset(num_sets=500)
    
    # Print statistics
    print_statistics(metadata_2way, metadata_3way)
    
    print("\n" + "=" * 70)
    print(" PDF Dataset Generation Complete!")
    print("\n📁 Generated Datasets:")
    print("  • datasets/2way_matching/ (500 PO + 500 Invoice PDFs)")
    print("  • datasets/3way_matching/ (500 PO + 500 Invoice + 500 GR PDFs)")
    print("\n💡 Each dataset includes:")
    print("  • Realistic PDF documents")
    print("  • metadata.json with document mappings")
    print("  • Various discrepancy scenarios")


if __name__ == "__main__":
    main()
