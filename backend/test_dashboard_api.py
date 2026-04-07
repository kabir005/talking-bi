"""
Test script to check if dashboard API returns data
"""
import asyncio
import sys
from sqlalchemy import select
from database.db import get_async_session
from database.models import Dashboard
import json

async def test_dashboard():
    print("=" * 60)
    print("TESTING DASHBOARD API DATA")
    print("=" * 60)
    
    async for session in get_async_session():
        # Get the most recent dashboard
        result = await session.execute(
            select(Dashboard).order_by(Dashboard.created_at.desc()).limit(1)
        )
        dashboard = result.scalar_one_or_none()
        
        if not dashboard:
            print("❌ No dashboards found!")
            print("Generate a dashboard first!")
            return
        
        print(f"\n✅ Found dashboard: {dashboard.name}")
        print(f"ID: {dashboard.id}")
        print(f"Preset: {dashboard.preset}")
        print(f"Created: {dashboard.created_at}")
        
        # Check tiles
        tiles = dashboard.tiles_json
        if not tiles:
            print("\n❌ No tiles in dashboard!")
            return
        
        print(f"\n✅ Total tiles: {len(tiles)}")
        
        # Check each tile
        kpi_count = 0
        chart_count = 0
        tiles_with_data = 0
        tiles_without_data = 0
        
        for i, tile in enumerate(tiles[:10]):  # Check first 10
            tile_type = tile.get('type', 'unknown')
            title = tile.get('title', 'Untitled')
            config = tile.get('config', {})
            data = config.get('data', [])
            
            print(f"\nTile {i+1}: {title}")
            print(f"  Type: {tile_type}")
            print(f"  Has config: {bool(config)}")
            print(f"  Has data: {bool(data)}")
            print(f"  Data length: {len(data) if data else 0}")
            
            if tile_type == 'kpi':
                kpi_count += 1
                value = config.get('value', 0)
                print(f"  KPI value: {value}")
            else:
                chart_count += 1
                if data and len(data) > 0:
                    tiles_with_data += 1
                    print(f"  Sample data: {data[0]}")
                else:
                    tiles_without_data += 1
                    print(f"  ❌ NO DATA!")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"KPI cards: {kpi_count}")
        print(f"Chart tiles: {chart_count}")
        print(f"Charts with data: {tiles_with_data}")
        print(f"Charts WITHOUT data: {tiles_without_data}")
        
        if tiles_without_data > 0:
            print(f"\n❌ PROBLEM: {tiles_without_data} charts have no data!")
            print("This is why charts are empty on the dashboard.")
            print("\nCheck backend logs when generating dashboard:")
            print("  - Look for 'Data points: 0' warnings")
            print("  - Check column names match")
            print("  - Verify data types are correct")
        else:
            print(f"\n✅ All charts have data!")
            print("If charts still don't show, it's a frontend rendering issue.")
        
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_dashboard())
