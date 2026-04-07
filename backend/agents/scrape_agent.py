"""
Scrape Agent - Web scraping for external data enrichment
"""
import pandas as pd
import asyncio
import requests
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from io import StringIO
import re
import json
from datetime import datetime
import random


async def scrape_url(
    url: str,
    extract_tables: bool = True,
    max_pages: int = 10,
    wait_time: int = 3
) -> Dict[str, Any]:
    """
    Web scraping using requests + BeautifulSoup.
    
    Features:
    - Table extraction
    - Works on all platforms
    - No browser dependencies
    
    Args:
        url: Target URL
        extract_tables: Whether to extract HTML tables
        max_pages: Maximum pages to scrape (pagination)
        wait_time: Seconds to wait for page load
    
    Returns:
        {
            "dataframes": [list of DataFrames],
            "metadata": {...},
            "errors": [...]
        }
    """
    print(f"\n{'='*80}")
    print(f"SCRAPE AGENT - WEB SCRAPING")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"Max pages: {max_pages}")
    
    dataframes = []
    metadata = {
        "url": url,
        "scraped_at": datetime.now().isoformat(),
        "pages_scraped": 0,
        "tables_found": 0,
        "rows_extracted": 0
    }
    errors = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching URL...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✓ Page loaded successfully")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if extract_tables:
            tables = soup.find_all('table')
            metadata["tables_found"] = len(tables)
            print(f"Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                try:
                    # Use StringIO to avoid FutureWarning
                    table_html = str(table)
                    dfs = pd.read_html(StringIO(table_html))
                    if dfs and len(dfs) > 0:
                        df = dfs[0]
                        # Clean column names
                        df.columns = [str(col).strip() for col in df.columns]
                        dataframes.append(df)
                        print(f"✓ Table {i+1}: {len(df)} rows, {len(df.columns)} columns")
                except Exception as e:
                    print(f"✗ Table {i+1} failed: {e}")
        
        metadata["pages_scraped"] = 1
        metadata["rows_extracted"] = sum(len(df) for df in dataframes)
        
    except requests.exceptions.RequestException as e:
        errors.append(f"HTTP error: {str(e)}")
        print(f"✗ HTTP Error: {e}")
    except Exception as e:
        errors.append(f"Scraping error: {str(e)}")
        print(f"✗ Error: {e}")
    
    print(f"\n{'='*80}")
    print(f"SCRAPING COMPLETE")
    print(f"Pages scraped: {metadata['pages_scraped']}")
    print(f"Tables found: {metadata['tables_found']}")
    print(f"Rows extracted: {metadata['rows_extracted']}")
    print(f"{'='*80}\n")
    
    return {
        "dataframes": dataframes,
        "metadata": metadata,
        "errors": errors
    }


async def merge_datasets(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    join_key: Optional[str] = None,
    join_type: str = "left"
) -> Dict[str, Any]:
    """
    Merge two datasets with auto-detection of join keys.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        join_key: Column to join on (auto-detected if None)
        join_type: "left", "right", "inner", "outer"
    
    Returns:
        {
            "merged_df": DataFrame,
            "join_key": str,
            "rows_before": int,
            "rows_after": int,
            "rows_lost": int
        }
    """
    print(f"\n{'='*80}")
    print(f"DATASET MERGE")
    print(f"{'='*80}")
    print(f"Dataset 1: {df1.shape}")
    print(f"Dataset 2: {df2.shape}")
    
    rows_before = len(df1)
    
    # Auto-detect join key if not provided
    if join_key is None:
        join_key = auto_detect_join_key(df1, df2)
        print(f"Auto-detected join key: {join_key}")
    
    if join_key is None:
        raise ValueError("Could not auto-detect join key. Please specify manually.")
    
    # Perform merge
    merged_df = pd.merge(df1, df2, on=join_key, how=join_type, suffixes=('', '_right'))
    
    rows_after = len(merged_df)
    rows_lost = rows_before - rows_after if join_type == "left" else 0
    
    print(f"Join type: {join_type}")
    print(f"Rows before: {rows_before}")
    print(f"Rows after: {rows_after}")
    print(f"Rows lost: {rows_lost}")
    print(f"\n{'='*80}")
    print(f"MERGE COMPLETE")
    print(f"{'='*80}\n")
    
    return {
        "merged_df": merged_df,
        "join_key": join_key,
        "join_type": join_type,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_lost": rows_lost
    }


def auto_detect_join_key(df1: pd.DataFrame, df2: pd.DataFrame) -> Optional[str]:
    """Auto-detect join key by column name similarity"""
    from difflib import SequenceMatcher
    
    # Find common columns
    common_cols = set(df1.columns) & set(df2.columns)
    if common_cols:
        # Prefer columns with "id", "key", "date" in name
        priority_keywords = ['id', 'key', 'date', 'code', 'name']
        for keyword in priority_keywords:
            for col in common_cols:
                if keyword in col.lower():
                    return col
        # Return first common column
        return list(common_cols)[0]
    
    # Try fuzzy matching
    best_match = None
    best_score = 0
    
    for col1 in df1.columns:
        for col2 in df2.columns:
            # Normalize column names
            norm1 = col1.lower().strip()
            norm2 = col2.lower().strip()
            
            # Calculate similarity
            score = SequenceMatcher(None, norm1, norm2).ratio()
            
            if score > best_score and score > 0.8:  # 80% similarity threshold
                best_score = score
                best_match = (col1, col2)
    
    if best_match:
        # Rename column in df2 to match df1
        print(f"Fuzzy match: '{best_match[0]}' ≈ '{best_match[1]}' (score: {best_score:.2f})")
        return best_match[0]
    
    return None
