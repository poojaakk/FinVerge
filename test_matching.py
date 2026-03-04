#!/usr/bin/env python3
"""
Test the matching logic with sample files
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_verification(po_file, inv_file, expected_result):
    """Test verification with specific files"""
    print(f"\n{'='*70}")
    print(f"Testing: {Path(po_file).name} vs {Path(inv_file).name}")
    print(f"Expected: {expected_result}")
    print('='*70)
    
    # Upload PO
    with open(po_file, 'rb') as f:
        po_response = requests.post(
            f"{API_BASE}/upload/",
            files={'file': (Path(po_file).name, f, 'application/pdf')}
        )
    
    if po_response.status_code != 200:
        print(f" PO Upload failed: {po_response.status_code}")
        print(po_response.text)
        return
    
    po_data = po_response.json()
    print(f" PO uploaded: {len(po_data['extracted_items'])} items extracted")
    for item in po_data['extracted_items']:
        print(f"   - {item['name']}: Qty {item['quantity']} @ ${item['unit_price']}")
    
    # Upload Invoice
    with open(inv_file, 'rb') as f:
        inv_response = requests.post(
            f"{API_BASE}/upload/",
            files={'file': (Path(inv_file).name, f, 'application/pdf')}
        )
    
    if inv_response.status_code != 200:
        print(f" Invoice Upload failed: {inv_response.status_code}")
        print(inv_response.text)
        return
    
    inv_data = inv_response.json()
    print(f" Invoice uploaded: {len(inv_data['extracted_items'])} items extracted")
    for item in inv_data['extracted_items']:
        print(f"   - {item['name']}: Qty {item['quantity']} @ ${item['unit_price']}")
    
    # Verify
    verify_request = {
        "po_items": [
            {"item": item['name'], "qty": item['quantity'], "price": item['unit_price']}
            for item in po_data['extracted_items']
        ],
        "invoice_items": [
            {"item": item['name'], "qty": item['quantity'], "price": item['unit_price']}
            for item in inv_data['extracted_items']
        ]
    }
    
    print(f"\n Sending verification request...")
    print(f"PO Items: {len(verify_request['po_items'])}")
    print(f"Invoice Items: {len(verify_request['invoice_items'])}")
    
    verify_response = requests.post(
        f"{API_BASE}/verify/2way",
        json=verify_request
    )
    
    if verify_response.status_code != 200:
        print(f" Verification failed: {verify_response.status_code}")
        print(verify_response.text)
        return
    
    result = verify_response.json()
    
    print(f"\n VERIFICATION RESULT:")
    print(f"Overall: {result['summary']['overall_recommendation']}")
    print(f"Total Discrepancies: {result['summary']['total_items_checked']}")
    print(f" Approved: {result['summary']['items_approved']}")
    print(f" Rejected: {result['summary']['items_rejected']}")
    
    if result['item_details']:
        print(f"\n Discrepancy Details:")
        for item in result['item_details']:
            print(f"   • {item['item_name']}: {item['issue_description']}")
    
    print(f"\n Processing Notes:")
    for note in result['processing_notes']:
        print(f"   • {note}")
    
    # Check if result matches expectation
    if expected_result == "MATCH":
        if result['summary']['items_approved'] == 1 and result['summary']['total_items_checked'] == 0:
            print(f"\n TEST PASSED: Correctly identified as perfect match")
        else:
            print(f"\n TEST FAILED: Should be perfect match but got discrepancies")
    else:
        if result['summary']['total_items_checked'] > 0:
            print(f"\n TEST PASSED: Correctly identified discrepancies")
        else:
            print(f"\n TEST FAILED: Should have discrepancies but showed perfect match")


def main():
    """Run tests"""
    print("🧪 Testing Matching Logic")
    print("="*70)
    
    # Test 1: Perfect Match
    test_verification(
        "datasets/test_samples/Sample1_PO_MATCH.pdf",
        "datasets/test_samples/Sample1_INV_MATCH.pdf",
        "MATCH"
    )
    
    # Test 2: With Discrepancies
    test_verification(
        "datasets/test_samples/Sample2_PO_MISMATCH.pdf",
        "datasets/test_samples/Sample2_INV_MISMATCH.pdf",
        "MISMATCH"
    )


if __name__ == "__main__":
    main()
