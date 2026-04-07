"""
Test the chatbot/query feature
"""

import requests
import json

DASHBOARD_ID = "76716eb4-d215-4883-870f-81d1d07a6f76"  # test_data9.csv Dashboard
API_URL = "http://localhost:8000"

def test_chatbot():
    """Test the conversational query endpoint"""
    
    print("="*80)
    print("TESTING CHATBOT/QUERY FEATURE")
    print("="*80)
    
    # Get dashboard to get dataset_id
    print("\n1. Getting dashboard info...")
    dashboard_response = requests.get(f"{API_URL}/api/dashboards/{DASHBOARD_ID}")
    if dashboard_response.status_code != 200:
        print(f"   ❌ Failed to get dashboard: {dashboard_response.status_code}")
        return
    
    dataset_id = dashboard_response.json().get('dataset_id')
    print(f"   ✅ Dataset ID: {dataset_id}")
    
    # Test query
    test_queries = [
        "What are the top selling products?",
        "Show me sales trends over time",
        "Which region has the highest profit?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i+1}. Testing query: '{query}'")
        try:
            response = requests.post(
                f"{API_URL}/api/query",
                json={
                    "dataset_id": dataset_id,
                    "query": query,
                    "user_role": "analyst"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS")
                
                # Get the actual result data
                query_result = result.get('result', {})
                plan = query_result.get('plan', {})
                summary = query_result.get('summary', {})
                agent_outputs = query_result.get('agent_outputs', {})
                
                print(f"   Intent: {plan.get('intent', 'N/A')}")
                print(f"   KPIs analyzed: {summary.get('kpis_analyzed', 0)}")
                print(f"   Charts generated: {summary.get('charts_generated', 0)}")
                print(f"   Insights found: {summary.get('insights_found', 0)}")
                print(f"   Recommendations: {summary.get('recommendations_count', 0)}")
                print(f"   Confidence: {summary.get('overall_confidence', 0)}%")
                
                # Show some insights if available
                insights = agent_outputs.get('insights', {})
                if insights.get('key_insights'):
                    print(f"\n   Key Insights:")
                    for idx, insight in enumerate(insights['key_insights'][:2], 1):
                        print(f"   {idx}. {insight}")
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
        
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_chatbot()
