from ..config import settings

def match(po_items, invoice_items):
    """
    Compare PO items with invoice items and find discrepancies.
    
    Args:
        po_items: List of PO items [{"item": str, "qty": int, "price": float}]
        invoice_items: List of invoice items [{"item": str, "qty": int, "price": float}]
    
    Returns:
        List of discrepancies [{"item": str, "type": str, "po_value": any, "invoice_value": any}]
    """
    discrepancies = []
    
    # Convert to dictionaries for easier lookup
    po_dict = {item["item"]: item for item in po_items}
    invoice_dict = {item["item"]: item for item in invoice_items}
    
    # Check for items in PO but not in invoice
    for item_name, po_item in po_dict.items():
        if item_name not in invoice_dict:
            discrepancies.append({
                "item": item_name,
                "type": "missing_from_invoice",
                "po_value": po_item,
                "invoice_value": None
            })
        else:
            invoice_item = invoice_dict[item_name]
            
            # Check quantity discrepancies
            if po_item["qty"] != invoice_item["qty"]:
                discrepancies.append({
                    "item": item_name,
                    "type": "quantity_mismatch",
                    "po_value": po_item["qty"],
                    "invoice_value": invoice_item["qty"]
                })
            
            # Check price discrepancies using configured tolerance
            price_diff = abs(po_item["price"] - invoice_item["price"])
            price_tolerance = po_item["price"] * (settings.PRICE_TOLERANCE_PERCENT / 100)
            
            if price_diff > price_tolerance:
                discrepancies.append({
                    "item": item_name,
                    "type": "price_mismatch",
                    "po_value": po_item["price"],
                    "invoice_value": invoice_item["price"]
                })
    
    # Check for items in invoice but not in PO
    for item_name, invoice_item in invoice_dict.items():
        if item_name not in po_dict:
            discrepancies.append({
                "item": item_name,
                "type": "extra_in_invoice",
                "po_value": None,
                "invoice_value": invoice_item
            })
    
    return discrepancies