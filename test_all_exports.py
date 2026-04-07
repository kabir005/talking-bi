"""
Test all export features
"""

import requests
import json

DASHBOARD_ID = "ad23bd64-1415-49e8-9654-936425cb60c6"
API_URL = "http://localhost:8000"

def test_exports():
    """Test all export endpoints"""
    
    print("="*80)
    print("TESTING ALL EXPORT FEATURES")
    print("="*80)
    
    # Test 1: Dashboard JSON Export
    print("\n1. Testing Dashboard JSON Export...")
    try:
        response = requests.post(
            f"{API_URL}/api/export-v2/dashboard/json",
            json={"dashboard_id": DASHBOARD_ID, "include_data": False}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Tiles: {len(data.get('tiles', []))}")
            # Check for insights
            insights_tile = next((t for t in data.get('tiles', []) if t.get('type') == 'insights'), None)
            if insights_tile:
                print(f"   ✅ Insights tile found with {len(insights_tile.get('data', {}).get('key_insights', []))} insights")
            else:
                print(f"   ⚠️  No insights tile found")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Data CSV Export
    print("\n2. Testing Data CSV Export...")
    try:
        # Get dataset_id from dashboard
        dashboard_response = requests.get(f"{API_URL}/api/dashboards/{DASHBOARD_ID}")
        dataset_id = dashboard_response.json().get('dataset_id')
        
        response = requests.post(
            f"{API_URL}/api/export-v2/data/csv",
            json={"dataset_id": dataset_id}
        )
        if response.status_code == 200:
            csv_size = len(response.content)
            print(f"   ✅ SUCCESS - CSV size: {csv_size} bytes")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: PDF Report
    print("\n3. Testing PDF Report Export...")
    try:
        response = requests.post(
            f"{API_URL}/api/reports/generate",
            json={"dashboard_id": DASHBOARD_ID, "format": "pdf"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Report ID: {data.get('pdf', {}).get('report_id')}")
            print(f"   📄 File: {data.get('pdf', {}).get('file_path')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 4: PowerPoint Report
    print("\n4. Testing PowerPoint Report Export...")
    try:
        response = requests.post(
            f"{API_URL}/api/reports/generate",
            json={"dashboard_id": DASHBOARD_ID, "format": "pptx"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Report ID: {data.get('pptx', {}).get('report_id')}")
            print(f"   📊 File: {data.get('pptx', {}).get('file_path')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 5: Complete Bundle
    print("\n5. Testing Complete Bundle Export...")
    try:
        response = requests.post(
            f"{API_URL}/api/export-v2/dashboard/bundle",
            json={"dashboard_id": DASHBOARD_ID}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS - Export ID: {data.get('export_id')}")
            print(f"   📦 Directory: {data.get('export_dir')}")
            print(f"   📊 Charts: {data.get('chart_count')}")
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_exports()
