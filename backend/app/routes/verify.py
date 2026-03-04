from fastapi import APIRouter
from ..services.matcher import match
from ..services.rag_service import rag_validate
from ..services.llm import explain_with_rag, parse_llm_response
from ..models.document import VerificationRequest
from ..models.discrepancy import VerificationResponse, DiscrepancyResult, VerificationSummary

router = APIRouter()

# We'll get these from the main app context
faiss_index = None
docs = None

def set_rag_components(index, documents):
    global faiss_index, docs
    faiss_index = index
    docs = documents

def format_issue_description(discrepancy):
    """Convert technical discrepancy info into user-friendly descriptions"""
    issue_type = discrepancy["type"]
    item = discrepancy["item"]
    
    if issue_type == "quantity_mismatch":
        po_qty = discrepancy["po_value"]
        invoice_qty = discrepancy["invoice_value"]
        return f"Quantity difference: PO shows {po_qty} units, but invoice shows {invoice_qty} units"
    
    elif issue_type == "price_mismatch":
        po_price = discrepancy["po_value"]
        invoice_price = discrepancy["invoice_value"]
        return f"Price difference: PO shows ${po_price:.2f}, but invoice shows ${invoice_price:.2f}"
    
    elif issue_type == "missing_from_invoice":
        return f"Item ordered in PO but not found in invoice"
    
    elif issue_type == "extra_in_invoice":
        return f"Item appears in invoice but was not ordered in PO"
    
    return f"Discrepancy detected: {issue_type}"

def get_recommendation(decision, issue_type):
    """Provide actionable recommendations based on the decision"""
    if decision == "ACCEPTABLE":
        return "No action required - this discrepancy is within acceptable limits"
    
    elif decision == "REJECTED":
        if issue_type == "extra_in_invoice":
            return "Contact vendor immediately - do not pay for unauthorized items"
        elif issue_type == "price_mismatch":
            return "Reject invoice - price exceeds acceptable variance limits"
        else:
            return "Reject invoice - discrepancy violates procurement policy"
    
    else:  # NEEDS_REVIEW
        if issue_type == "quantity_mismatch":
            return "Review with procurement team - verify if partial delivery was authorized"
        elif issue_type == "price_mismatch":
            return "Review with vendor - confirm if price change was pre-approved"
        elif issue_type == "missing_from_invoice":
            return "Contact vendor - request delivery confirmation for missing items"
        else:
            return "Manual review required - escalate to procurement manager"

@router.post("/2way", response_model=VerificationResponse)
def verify_2way(request: VerificationRequest):
    # Convert Pydantic models to dictionaries for the matcher
    po_items = [item.dict() for item in request.po_items]
    invoice_items = [item.dict() for item in request.invoice_items]
    
    discrepancies = match(po_items, invoice_items)
    
    item_details = []
    processing_notes = []
    all_contexts = []  # Track all contexts for processing notes

    # Check if there are any discrepancies
    if not discrepancies:
        # Perfect match - no discrepancies
        processing_notes.append("Perfect match - all items match between PO and invoice")
        processing_notes.append("No discrepancies found")
        
        summary = VerificationSummary(
            total_items_checked=0,  # Don't show total for perfect match
            items_approved=1,  # Show as approved
            items_need_review=0,
            items_rejected=0,
            overall_recommendation="APPROVED - Documents match perfectly"
        )
        
        return VerificationResponse(
            summary=summary,
            item_details=[],  # No items to show
            processing_notes=processing_notes
        )
    
    # There are discrepancies - process them
    approved_count = 0
    needs_review_count = 0
    rejected_count = 0

    for d in discrepancies:
        context = rag_validate(d, faiss_index, docs)
        all_contexts.extend(context)  # Collect all contexts
        llm_response = explain_with_rag(d, context)
        decision, explanation = parse_llm_response(llm_response)
        
        # Count decisions
        if decision == "ACCEPTABLE":
            approved_count += 1
            status = "APPROVED"
        elif decision == "REJECTED":
            rejected_count += 1
            status = "REJECTED"
        else:
            needs_review_count += 1
            status = "NEEDS_REVIEW"
        
        # Create user-friendly result
        result = DiscrepancyResult(
            item_name=d["item"],
            issue_type=d["type"].replace("_", " ").title(),
            issue_description=format_issue_description(d),
            status=status,
            explanation=explanation if not explanation.startswith("Error calling") else "AI analysis unavailable - manual review recommended",
            recommendation=get_recommendation(decision, d["type"]),
            supporting_documents=[doc["source"] for doc in context]
        )
        item_details.append(result)
    
    # Determine overall recommendation
    total_items = len(discrepancies)
    if rejected_count > 0 or needs_review_count > 0:
        overall_recommendation = f"REJECTED - {total_items} discrepancies found"
        final_approved = 0
        final_rejected = 1
    else:
        overall_recommendation = "APPROVED - All discrepancies are within acceptable limits"
        final_approved = 1
        final_rejected = 0
    
    # Add processing notes
    processing_notes.append(f"Found {total_items} discrepancies requiring attention")
    
    if all_contexts:
        unique_sources = len(set([doc['source'] for doc in all_contexts]))
        processing_notes.append(f"Analysis based on {unique_sources} policy documents")
    
    summary = VerificationSummary(
        total_items_checked=total_items,  # Show total only when there are discrepancies
        items_approved=final_approved,
        items_need_review=0,  # Simplified: either approved or rejected
        items_rejected=final_rejected,
        overall_recommendation=overall_recommendation
    )

    return VerificationResponse(
        summary=summary,
        item_details=item_details,
        processing_notes=processing_notes
    )


@router.post("/3way", response_model=VerificationResponse)
def verify_3way(request: VerificationRequest):
    """
    3-Way Matching: PO vs Invoice vs Goods Receipt
    Checks all three documents for consistency
    
    Logic:
    1. PO vs Invoice: Compare with tax included (normal comparison)
    2. Invoice vs GR: Direct comparison (both should have same values in test data)
    
    Note: In real-world scenarios, GR typically doesn't include tax, but our test
    data includes tax in all documents for consistency.
    """
    # Convert Pydantic models to dictionaries
    po_items = [item.dict() for item in request.po_items]
    invoice_items = [item.dict() for item in request.invoice_items]
    gr_items = [item.dict() for item in request.gr_items] if request.gr_items else []
    
    # Debug logging
    print(f"\n=== 3-WAY MATCHING DEBUG ===")
    print(f"PO Items: {po_items}")
    print(f"Invoice Items: {invoice_items}")
    print(f"GR Items: {gr_items}")
    print(f"========================\n")
    
    # If no GR items provided, fallback to 2-way matching
    if not gr_items:
        return verify_2way(request)
    
    item_details = []
    processing_notes = []
    all_contexts = []
    
    # Step 1: Compare PO vs Invoice (with tax)
    po_inv_discrepancies = match(po_items, invoice_items)
    print(f"PO vs Invoice discrepancies: {len(po_inv_discrepancies)}")
    if po_inv_discrepancies:
        print(f"Details: {po_inv_discrepancies}")
    
    # Step 2: Compare Invoice vs GR (direct comparison)
    # Since our test data includes tax in GR, we compare directly
    inv_gr_discrepancies = match(invoice_items, gr_items)
    print(f"Invoice vs GR discrepancies: {len(inv_gr_discrepancies)}")
    if inv_gr_discrepancies:
        print(f"Details: {inv_gr_discrepancies}")
    
    # Combine all discrepancies
    all_discrepancies = []
    
    # Add PO vs Invoice discrepancies
    for d in po_inv_discrepancies:
        d['comparison'] = 'PO vs Invoice'
        all_discrepancies.append(d)
    
    # Add Invoice vs GR discrepancies
    for d in inv_gr_discrepancies:
        d['comparison'] = 'Invoice vs GR'
        all_discrepancies.append(d)
    
    print(f"Total discrepancies: {len(all_discrepancies)}")
    
    # Check if there are any discrepancies
    if not all_discrepancies:
        processing_notes.append("Perfect match - all documents (PO, Invoice, GR) match perfectly")
        processing_notes.append("No discrepancies found across all three documents")
        
        summary = VerificationSummary(
            total_items_checked=0,
            items_approved=1,
            items_need_review=0,
            items_rejected=0,
            overall_recommendation="APPROVED - All documents match perfectly"
        )
        
        return VerificationResponse(
            summary=summary,
            item_details=[],
            processing_notes=processing_notes
        )
    
    # Process discrepancies
    approved_count = 0
    needs_review_count = 0
    rejected_count = 0
    
    for d in all_discrepancies:
        context = rag_validate(d, faiss_index, docs)
        all_contexts.extend(context)
        llm_response = explain_with_rag(d, context)
        decision, explanation = parse_llm_response(llm_response)
        
        # Count decisions
        if decision == "ACCEPTABLE":
            approved_count += 1
            status = "APPROVED"
        elif decision == "REJECTED":
            rejected_count += 1
            status = "REJECTED"
        else:
            needs_review_count += 1
            status = "NEEDS_REVIEW"
        
        # Create user-friendly result with comparison info
        issue_desc = format_issue_description(d)
        issue_desc = f"[{d['comparison']}] {issue_desc}"
        
        result = DiscrepancyResult(
            item_name=d["item"],
            issue_type=d["type"].replace("_", " ").title(),
            issue_description=issue_desc,
            status=status,
            explanation=explanation if not explanation.startswith("Error calling") else "AI analysis unavailable - manual review recommended",
            recommendation=get_recommendation(decision, d["type"]),
            supporting_documents=[doc["source"] for doc in context]
        )
        item_details.append(result)
    
    # Determine overall recommendation
    total_items = len(all_discrepancies)
    if rejected_count > 0 or needs_review_count > 0:
        overall_recommendation = f"REJECTED - {total_items} discrepancies found across documents"
        final_approved = 0
        final_rejected = 1
    else:
        overall_recommendation = "APPROVED - All discrepancies are within acceptable limits"
        final_approved = 1
        final_rejected = 0
    
    processing_notes.append(f"Found {total_items} discrepancies across PO, Invoice, and GR")
    processing_notes.append(f"   • PO vs Invoice: {len(po_inv_discrepancies)} discrepancies")
    processing_notes.append(f"   • Invoice vs GR: {len(inv_gr_discrepancies)} discrepancies")
    
    if all_contexts:
        unique_sources = len(set([doc['source'] for doc in all_contexts]))
        processing_notes.append(f"Analysis based on {unique_sources} policy documents")
    
    summary = VerificationSummary(
        total_items_checked=total_items,
        items_approved=final_approved,
        items_need_review=0,
        items_rejected=final_rejected,
        overall_recommendation=overall_recommendation
    )

    return VerificationResponse(
        summary=summary,
        item_details=item_details,
        processing_notes=processing_notes
    )
