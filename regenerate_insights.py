"""
Script to regenerate insights for existing dashboard
"""

import requests
import json

# Dashboard ID from the user's screenshots
DASHBOARD_ID = "ad23bd64-1415-49e8-9654-936425cb60c6"
API_URL = "http://localhost:8000"

def regenerate_insights():
    """Regenerate insights for the dashboard"""
    
    url = f"{API_URL}/api/dashboards/{DASHBOARD_ID}/regenerate-insights"
    
    print(f"Regenerating insights for dashboard: {DASHBOARD_ID}")
    print(f"Calling: {url}")
    
    try:
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print(f"Insights generated: {result.get('insights_generated')}")
            print(f"Recommendations generated: {result.get('recommendations_generated')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")

if __name__ == "__main__":
    regenerate_insights()
