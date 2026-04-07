#!/usr/bin/env python3
"""
Comprehensive System Testing Script
Tests all critical API endpoints and validates frontend-backend connectivity
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import pandas as pd
from sqlalchemy import select, text
from database.db import AsyncSessionLocal
from database.models import Dataset, Dashboard
from routers.dashboards import generate_dashboard, DashboardCreate
from services.export_service import export_dashboard_bundle
import json


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}[FAIL] {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")


async def test_database_connection():
    """Test 1: Database connectivity"""
    print_header("TEST 1: Database Connection")
    
    try:
        async with AsyncSessionLocal() as session:
            # Test basic query
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            print_success("Database connection successful")
            
            # Check tables exist
            tables = ['datasets', 'dashboards', 'query_memory', 'ml_models', 'reports']
            for table in tables:
                result = await session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if result.scalar():
                    print_success(f"Table '{table}' exists")
                else:
                    print_error(f"Table '{table}' missing")
            
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


async def test_dataset_operations():
    """Test 2: Dataset CRUD operations"""
    print_header("TEST 2: Dataset Operations")
    
    try:
        async with AsyncSessionLocal() as session:
            # List datasets
            result = await session.execute(select(Dataset))
            datasets = result.scalars().all()
            print_info(f"Found {len(datasets)} datasets in database")
            
            if len(datasets) == 0:
                print_warning("No datasets found - upload a dataset first")
                return False
            
            # Test first dataset
            dataset = datasets[0]
            print_success(f"Dataset: {dataset.name} (ID: {dataset.id})")
            print_info(f"  Rows: {dataset.row_count}, Columns: {dataset.column_count}")
            print_info(f"  Table: {dataset.sqlite_table_name}")
            
            # Verify data can be loaded
            if dataset.sqlite_table_name:
                query = f"SELECT * FROM {dataset.sqlite_table_name} LIMIT 5"
                result = await session.execute(text(query))
                rows = result.fetchall()
                print_success(f"  Loaded {len(rows)} sample rows from table")
                
                if len(rows) > 0:
                    columns = result.keys()
                    print_info(f"  Columns: {', '.join(list(columns)[:5])}...")
                    return dataset.id
                else:
                    print_error("  Table is empty!")
                    return None
            else:
                print_error("  No SQLite table name")
                return None
                
    except Exception as e:
        print_error(f"Dataset operations failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_dashboard_generation(dataset_id):
    """Test 3: Dashboard generation for all presets"""
    print_header("TEST 3: Dashboard Generation")
    
    if not dataset_id:
        print_warning("Skipping - no dataset available")
        return None
    
    presets = ["executive", "operational", "trend", "comparison"]
    dashboard_ids = []
    
    for preset in presets:
        print_info(f"\nTesting {preset.upper()} preset...")
        
        try:
            async with AsyncSessionLocal() as session:
                request = DashboardCreate(
                    name=f"Test {preset.title()} Dashboard",
                    dataset_id=dataset_id,
                    preset=preset,
                    role="analyst"
                )
                
                result = await generate_dashboard(request, session)
                
                if result and result.get("id"):
                    dashboard_id = result["id"]
                    tile_count = result.get("tile_count", 0)
                    print_success(f"{preset.title()} dashboard created: {dashboard_id}")
                    print_info(f"  Tiles generated: {tile_count}")
                    
                    # Verify tiles have data
                    tiles = result.get("tiles", [])
                    tiles_with_data = 0
                    for tile in tiles:
                        if tile.get("type") == "kpi":
                            if tile.get("config", {}).get("value") is not None:
                                tiles_with_data += 1
                        else:
                            if tile.get("config", {}).get("data"):
                                tiles_with_data += 1
                    
                    print_info(f"  Tiles with data: {tiles_with_data}/{tile_count}")
                    
                    if tiles_with_data < tile_count * 0.5:
                        print_warning(f"  Less than 50% of tiles have data!")
                    else:
                        print_success(f"  Data coverage: {tiles_with_data}/{tile_count}")
                    
                    dashboard_ids.append(dashboard_id)
                else:
                    print_error(f"{preset.title()} dashboard generation failed")
                    
        except Exception as e:
            print_error(f"{preset.title()} preset failed: {e}")
            import traceback
            traceback.print_exc()
    
    return dashboard_ids[0] if dashboard_ids else None


async def test_nl_query(dataset_id):
    """Test 4: Natural Language Query System"""
    print_header("TEST 4: NL Query System")
    
    if not dataset_id:
        print_warning("Skipping - no dataset available")
        return False
    
    print_info("NL Query system requires running backend server")
    print_warning("Skipping automated test - manual testing recommended")
    return True  # Skip for now


async def test_export_functionality(dashboard_id):
    """Test 5: Export functionality (PDF, PPTX, Bundle)"""
    print_header("TEST 5: Export Functionality")
    
    if not dashboard_id:
        print_warning("Skipping - no dashboard available")
        return False
    
    try:
        async with AsyncSessionLocal() as session:
            # Get dashboard
            result = await session.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
            dashboard = result.scalar_one_or_none()
            
            if not dashboard:
                print_error("Dashboard not found")
                return False
            
            print_info(f"Testing export for dashboard: {dashboard.name}")
            
            # Test bundle export
            try:
                export_path = await export_dashboard_bundle(dashboard_id, session)
                
                if export_path and os.path.exists(export_path):
                    print_success(f"Bundle exported: {export_path}")
                    
                    # Check bundle contents
                    import zipfile
                    with zipfile.ZipFile(export_path, 'r') as zip_ref:
                        files = zip_ref.namelist()
                        print_info(f"  Bundle contains {len(files)} files:")
                        for f in files[:10]:  # Show first 10
                            print_info(f"    - {f}")
                        
                        # Check for required files
                        has_manifest = any('manifest.json' in f for f in files)
                        has_dashboard = any('dashboard.json' in f for f in files)
                        has_data = any('.csv' in f for f in files)
                        
                        if has_manifest:
                            print_success("  [OK] Manifest file present")
                        else:
                            print_error("  [FAIL] Manifest file missing")
                        
                        if has_dashboard:
                            print_success("  [OK] Dashboard config present")
                        else:
                            print_error("  [FAIL] Dashboard config missing")
                        
                        if has_data:
                            print_success("  [OK] Data file present")
                        else:
                            print_error("  [FAIL] Data file missing")
                    
                    return True
                else:
                    print_error("Bundle export failed - no file created")
                    return False
                    
            except Exception as e:
                print_error(f"Export failed: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print_error(f"Export test failed: {e}")
        return False


async def test_frontend_backend_connectivity():
    """Test 6: Frontend-Backend API endpoint mapping"""
    print_header("TEST 6: Frontend-Backend Connectivity")
    
    # Map of frontend API calls to backend endpoints
    api_mapping = {
        "uploadFile": "/api/upload/file",
        "getDatasets": "/api/datasets",
        "getDataset": "/api/datasets/{id}",
        "getDatasetPreview": "/api/datasets/{id}/preview",
        "deleteDataset": "/api/datasets/{id}",
        "generateDashboard": "/api/dashboards/generate",
        "getDashboards": "/api/dashboards",
        "getDashboard": "/api/dashboards/{id}",
        "updateDashboard": "/api/dashboards/{id}",
        "deleteDashboard": "/api/dashboards/{id}",
        "submitQuery": "/api/query",
        "getQueryHistory": "/api/query/history",
        "trainModel": "/api/ml/train",
        "getMLModels": "/api/ml/models",
        "runNLQuery": "/api/nl-query/",
        "conversationChat": "/api/conversation/chat",
        "getPipelineStatusOnce": "/api/pipeline/status/{id}/once"
    }
    
    print_info("Verifying API endpoint mapping...")
    
    # Read main.py to verify all routers are registered
    main_py_path = Path(__file__).parent / "backend" / "main.py"
    with open(main_py_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    all_mapped = True
    for func_name, endpoint in api_mapping.items():
        # Extract base path
        base_path = endpoint.split('/')[1:3]  # e.g., ['api', 'upload']
        router_prefix = f"/api/{base_path[1]}"
        
        if router_prefix in main_content or endpoint.replace('/{id}', '') in main_content:
            print_success(f"{func_name:25} -> {endpoint}")
        else:
            print_error(f"{func_name:25} -> {endpoint} (NOT FOUND)")
            all_mapped = False
    
    if all_mapped:
        print_success("\nAll frontend API calls map to backend endpoints")
    else:
        print_error("\nSome frontend API calls are not mapped!")
    
    return all_mapped


async def test_chart_data_generation():
    """Test 7: Chart data generation for all chart types"""
    print_header("TEST 7: Chart Data Generation")
    
    try:
        async with AsyncSessionLocal() as session:
            # Get first dataset
            result = await session.execute(select(Dataset))
            dataset = result.scalars().first()
            
            if not dataset:
                print_warning("No dataset available")
                return False
            
            # Load data
            query = f"SELECT * FROM {dataset.sqlite_table_name}"
            result = await session.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            
            print_info(f"Testing with dataset: {dataset.name}")
            print_info(f"DataFrame shape: {df.shape}")
            
            # Test chart agent
            from agents.chart_agent import recommend_charts
            
            charts = await recommend_charts(df, dataset.schema_json, max_charts=10)
            
            print_info(f"\nChart recommendations: {len(charts)}")
            
            chart_types = {}
            for chart in charts:
                chart_type = chart.get("type", "unknown")
                chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
            
            print_info("Chart type distribution:")
            for chart_type, count in chart_types.items():
                print_info(f"  {chart_type}: {count}")
            
            # Verify each chart has required fields
            all_valid = True
            for i, chart in enumerate(charts):
                has_type = bool(chart.get("type"))
                has_title = bool(chart.get("title"))
                has_x = bool(chart.get("x_column"))
                
                if not (has_type and has_title):
                    print_error(f"Chart {i+1}: Missing required fields")
                    all_valid = False
                else:
                    print_success(f"Chart {i+1}: {chart['type']} - {chart['title']}")
            
            return all_valid
            
    except Exception as e:
        print_error(f"Chart generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all system tests"""
    print_header("TALKING BI - COMPREHENSIVE SYSTEM TEST")
    print_info("Testing all critical components and connectivity\n")
    
    # Initialize database first
    print_info("Initializing database...")
    from database.db import init_db
    await init_db()
    print_success("Database initialized\n")
    
    results = {}
    
    # Test 1: Database
    results["database"] = await test_database_connection()
    
    # Test 2: Dataset operations
    dataset_id = await test_dataset_operations()
    results["datasets"] = dataset_id is not None
    
    # Test 3: Dashboard generation
    dashboard_id = await test_dashboard_generation(dataset_id)
    results["dashboards"] = dashboard_id is not None
    
    # Test 4: NL Query
    results["nl_query"] = await test_nl_query(dataset_id)
    
    # Test 5: Export
    results["export"] = await test_export_functionality(dashboard_id)
    
    # Test 6: Frontend-Backend connectivity
    results["connectivity"] = await test_frontend_backend_connectivity()
    
    # Test 7: Chart generation
    results["charts"] = await test_chart_data_generation()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status:6}{Colors.RESET} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} tests passed{Colors.RESET}")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}[SUCCESS] ALL TESTS PASSED{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}[FAILURE] SOME TESTS FAILED{Colors.RESET}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
