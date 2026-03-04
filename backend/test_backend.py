#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Service Status: {data['service_status']}")
            print(f"Documents Loaded: {data['knowledge_base']['documents_loaded']}")
            print(f"Capabilities: {', '.join(data['capabilities'])}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_verification_endpoint():
    """Test the 2-way verification endpoint"""
    test_data = {
        "po_items": [
            {"item": "Steel Rod", "qty": 100, "price": 500.0},
            {"item": "Concrete Mix", "qty": 50, "price": 200.0}
        ],
        "invoice_items": [
            {"item": "Steel Rod", "qty": 95, "price": 520.0},
            {"item": "Concrete Mix", "qty": 50, "price": 200.0},
            {"item": "Extra Item", "qty": 10, "price": 100.0}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/verify/2way",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Verification test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 VERIFICATION SUMMARY:")
            print(f"Overall Recommendation: {data['summary']['overall_recommendation']}")
            print(f"Items Checked: {data['summary']['total_items_checked']}")
            print(f" Approved: {data['summary']['items_approved']}")
            print(f"  Need Review: {data['summary']['items_need_review']}")
            print(f" Rejected: {data['summary']['items_rejected']}")
            
            print(f"\n ITEM DETAILS:")
            for item in data['item_details']:
                print(f"\n• {item['item_name']} - {item['status']}")
                print(f"  Issue: {item['issue_description']}")
                print(f"  Recommendation: {item['recommendation']}")
            
            print(f"\n📝 PROCESSING NOTES:")
            for note in data['processing_notes']:
                print(f"• {note}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Verification test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing FinVerge Backend...")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    print()
    
    # Test verification endpoint
    verify_ok = test_verification_endpoint()
    print()
    
    if health_ok and verify_ok:
        print(" All tests passed! Backend is ready for frontend integration.")
    else:
        print(" Some tests failed!")
        
    print("\n To run the backend:")
    print("cd backend && python3 run.py")
    print("\n📖 API Documentation: http://localhost:8000/docs")