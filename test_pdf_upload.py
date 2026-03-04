#!/usr/bin/env python3
"""
Test PDF upload functionality
"""

import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_pdf_upload(pdf_path):
    """Test uploading a PDF file"""
    print(f"\n📄 Testing upload: {Path(pdf_path).name}")
    print("=" * 70)
    
    if not Path(pdf_path).exists():
        print(f" File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(
                f"{API_BASE}/upload/",
                files=files,
                timeout=30
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f" Success: {result['message']}")
            print(f" Document Info:")
            print(f"   - Filename: {result['document_info']['filename']}")
            print(f"   - Size: {result['document_info']['file_size_mb']} MB")
            print(f"   - Pages: {result['document_info']['page_count']}")
            print(f"   - Text Extracted: {result['document_info']['text_extracted']}")
            print(f"\n📦 Extracted Items: {len(result['extracted_items'])}")
            for item in result['extracted_items'][:5]:  # Show first 5
                print(f"   - {item['name']}: Qty {item['quantity']} @ ${item['unit_price']:.2f} = ${item['total_price']:.2f}")
            if len(result['extracted_items']) > 5:
                print(f"   ... and {len(result['extracted_items']) - 5} more items")
            print(f"\n📝 Processing Notes:")
            for note in result['processing_notes']:
                print(f"   • {note}")
            return True
        else:
            print(f" Error: {response.status_code}")
            try:
                error = response.json()
                print(f"   Detail: {error.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(" Cannot connect to backend")
        print("   Make sure the server is running: cd backend && python3 run.py")
        return False
    except Exception as e:
        print(f" Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🧪 PDF Upload Test")
    print("=" * 70)
    
    # Find actual generated PDFs
    po_dir = Path("datasets/2way_matching/purchase_orders")
    inv_dir = Path("datasets/2way_matching/invoices")
    gr_dir = Path("datasets/3way_matching/goods_receipts")
    
    test_files = []
    
    if po_dir.exists():
        po_files = list(po_dir.glob("*.pdf"))
        if po_files:
            test_files.append(str(po_files[0]))
    
    if inv_dir.exists():
        inv_files = list(inv_dir.glob("*.pdf"))
        if inv_files:
            test_files.append(str(inv_files[0]))
    
    if gr_dir.exists():
        gr_files = list(gr_dir.glob("*.pdf"))
        if gr_files:
            test_files.append(str(gr_files[0]))
    
    if not test_files:
        print(" No PDF files found in datasets/")
        print("   Run: python3 generate_pdf_datasets.py")
        return
    
    results = []
    for pdf_path in test_files:
        results.append(test_pdf_upload(pdf_path))
    
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(results)}")
    print(f" Passed: {sum(results)}")
    print(f" Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n All tests passed! PDF upload is working correctly.")
    else:
        print("\n  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()
