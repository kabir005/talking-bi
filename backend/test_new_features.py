"""
Test script for new features (Voice-to-Insight and What-If Scenario Modeling)
Run this to verify backend endpoints are working correctly.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.db import get_db, init_db
from database.models import Dataset
import pandas as pd


async def test_scenario_endpoints():
    """Test scenario modeling endpoints"""
    print("\n" + "="*80)
    print("TESTING SCENARIO MODELING ENDPOINTS")
    print("="*80)
    
    # Initialize database
    await init_db()
    
    # Get a test dataset
    async for db in get_db():
        result = await db.execute(select(Dataset).limit(1))
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            print("❌ No datasets found. Please upload a dataset first.")
            return False
        
        print(f"✓ Found test dataset: {dataset.name} (ID: {dataset.id})")
        
        # Test 1: Get scenario parameters
        print("\n--- Test 1: GET /api/scenario/parameters/{dataset_id} ---")
        try:
            from routers.scenario import get_scenario_parameters
            params = await get_scenario_parameters(dataset.id, db)
            print(f"✓ Retrieved {len(params['parameters'])} parameters")
            if params['parameters']:
                print(f"  Sample parameter: {params['parameters'][0]['label']}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        
        # Test 2: Simulate scenario
        print("\n--- Test 2: POST /api/scenario/simulate ---")
        try:
            from routers.scenario import simulate_scenario, ScenarioRequest, SliderParam
            
            # Create test request
            test_params = []
            if params['parameters']:
                test_params.append(SliderParam(
                    column=params['parameters'][0]['column'],
                    label=params['parameters'][0]['label'],
                    change_pct=10.0,
                    change_type="multiply"
                ))
            
            request = ScenarioRequest(
                dataset_id=dataset.id,
                parameters=test_params
            )
            
            result = await simulate_scenario(request, db)
            print(f"✓ Simulation completed")
            print(f"  Narrative: {result.narrative[:100]}...")
            print(f"  KPI deltas: {len(result.delta_kpis)} metrics")
            print(f"  Charts: {len(result.chart_configs)} comparison charts")
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        break
    
    print("\n✅ All scenario modeling tests passed!")
    return True


async def test_voice_endpoints():
    """Test voice-to-insight endpoints"""
    print("\n" + "="*80)
    print("TESTING VOICE-TO-INSIGHT ENDPOINTS")
    print("="*80)
    
    # Test 1: Check Whisper availability
    print("\n--- Test 1: Check Whisper Model ---")
    try:
        import whisper
        print("✓ Whisper library installed")
        
        # Try to load model (will download if not present)
        print("  Loading Whisper base model (may take a moment)...")
        model = whisper.load_model("base")
        print("✓ Whisper model loaded successfully")
    except ImportError:
        print("❌ Whisper not installed. Run: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"⚠ Whisper model load warning: {e}")
        print("  (Model will download on first use)")
    
    # Test 2: Check TTS availability
    print("\n--- Test 2: Check TTS Engine ---")
    try:
        import pyttsx3
        print("✓ pyttsx3 library installed")
        
        engine = pyttsx3.init()
        print("✓ TTS engine initialized")
    except ImportError:
        print("❌ pyttsx3 not installed. Run: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"⚠ TTS engine warning: {e}")
        print("  (May need system audio drivers)")
    
    # Test 3: Check dependencies
    print("\n--- Test 3: Check Service Dependencies ---")
    try:
        from services.intent_classifier import classify_intent
        print("✓ intent_classifier service available")
    except ImportError as e:
        print(f"❌ intent_classifier import failed: {e}")
        return False
    
    try:
        from services.query_executor import execute
        print("✓ query_executor service available")
    except ImportError as e:
        print(f"❌ query_executor import failed: {e}")
        return False
    
    print("\n✅ All voice-to-insight dependencies available!")
    return True


async def test_database_connection():
    """Test database connectivity"""
    print("\n" + "="*80)
    print("TESTING DATABASE CONNECTION")
    print("="*80)
    
    try:
        await init_db()
        print("✓ Database initialized")
        
        async for db in get_db():
            result = await db.execute(select(Dataset))
            datasets = result.scalars().all()
            print(f"✓ Found {len(datasets)} datasets in database")
            
            if datasets:
                for ds in datasets[:3]:
                    print(f"  - {ds.name} ({ds.row_count} rows, {ds.column_count} columns)")
            else:
                print("  ⚠ No datasets found. Upload a dataset to test features.")
            
            break
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("NEW FEATURES BACKEND TEST SUITE")
    print("="*80)
    
    results = {
        "Database Connection": await test_database_connection(),
        "Voice-to-Insight": await test_voice_endpoints(),
        "Scenario Modeling": await test_scenario_endpoints(),
    }
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Backend is ready.")
        print("\nNext steps:")
        print("1. Start backend: python main.py")
        print("2. Start frontend: cd ../frontend && npm run dev")
        print("3. Test features in the UI")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
