import re
from typing import List, Dict

def extract_items(text: str) -> List[Dict]:
    """
    Extract items from text using regex patterns.
    Handles various PDF formats including ReportLab generated PDFs.
    
    Returns:
    [
      { "item": "Steel Rod", "qty": 100, "price": 500.0 },
      ...
    ]
    """
    items = []
    
    if not text or not text.strip():
        return items
    
    # Common header words to skip
    skip_words = [
        'item description', 'description', 'item', 'subtotal', 'tax', 'total', 
        'amount due', 'quantity', 'unit price', 'price', 'received', 'quantity received',
        'from', 'to', 'bill', 'date', 'number', 'reference'
    ]
    
    # Pattern 1: Line-by-line parsing for ReportLab PDFs
    # These PDFs have items on separate lines
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and headers
        if not line or any(skip in line.lower() for skip in skip_words):
            i += 1
            continue
        
        # Check if this line looks like an item name (starts with letter, has letters)
        if re.match(r'^[A-Za-z]', line) and len(line) >= 3:
            # Look ahead for quantity and price on next lines
            qty_line = lines[i+1].strip() if i+1 < len(lines) else ""
            price_line = lines[i+2].strip() if i+2 < len(lines) else ""
            
            # Try to extract quantity and price
            qty_match = re.match(r'^(\d+)$', qty_line)
            price_match = re.match(r'^\$?([\d,]+\.?\d*)$', price_line)
            
            if qty_match and price_match:
                try:
                    quantity = int(qty_match.group(1))
                    price = float(price_match.group(1).replace(',', ''))
                    
                    # Sanity checks
                    if quantity > 0 and price > 0 and quantity < 100000 and price < 1000000:
                        items.append({
                            "item": line,
                            "qty": quantity,
                            "price": price
                        })
                        i += 4  # Skip item, qty, price, total lines
                        continue
                except (ValueError, IndexError):
                    pass
        
        i += 1
    
    # Pattern 2: Table format on same line (fallback)
    if not items:
        # Match items where everything is on one line
        table_pattern = r'([A-Za-z][A-Za-z0-9\s\-]+?)\s+(\d+)\s+\$?([\d,]+\.?\d*)\s+\$?([\d,]+\.?\d*)'
        matches = re.findall(table_pattern, text)
        
        for match in matches:
            item_name = match[0].strip()
            # Skip header rows and footer rows
            if any(skip in item_name.lower() for skip in skip_words):
                continue
            
            # Skip if item name is too short
            if len(item_name) < 3:
                continue
            
            try:
                quantity = int(match[1])
                unit_price = float(match[2].replace(',', ''))
                
                # Sanity checks
                if quantity <= 0 or unit_price <= 0:
                    continue
                
                items.append({
                    "item": item_name,
                    "qty": quantity,
                    "price": unit_price
                })
            except (ValueError, IndexError):
                continue
    
    return items
