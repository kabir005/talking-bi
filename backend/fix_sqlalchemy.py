#!/usr/bin/env python3
"""
Script to fix SQLAlchemy 1.x query() syntax to SQLAlchemy 2.0 select() syntax
"""
import re
import os
from pathlib import Path

def fix_imports(content):
    """Add necessary imports for SQLAlchemy 2.0"""
    # Check if already has AsyncSession
    if 'from sqlalchemy.ext.asyncio import AsyncSession' in content:
        return content
    
    # Replace Session with AsyncSession
    content = content.replace('from sqlalchemy.orm import Session', 
                             'from sqlalchemy.ext.asyncio import AsyncSession\nfrom sqlalchemy import select, delete')
    
    # Replace Session type hints with AsyncSession
    content = re.sub(r'\bdb: Session\b', 'db: AsyncSession', content)
    
    return content

def fix_query_patterns(content):
    """Fix query patterns from 1.x to 2.0"""
    
    # Pattern 1: db.query(Model).filter(...).first()
    # Replace with: await db.execute(select(Model).where(...)); result.scalar_one_or_none()
    pattern1 = r'(\w+)\s*=\s*db\.query\((\w+)\)\.filter\(([^)]+)\)\.first\(\)'
    
    def replace1(match):
        var_name = match.group(1)
        model = match.group(2)
        filter_expr = match.group(3)
        filter_expr = filter_expr.replace(' == ', ' == ')
        return f'result = await db.execute(select({model}).where({filter_expr}))\n    {var_name} = result.scalar_one_or_none()'
    
    content = re.sub(pattern1, replace1, content)
    
    # Pattern 2: query = db.query(Model)
    content = re.sub(r'query\s*=\s*db\.query\((\w+)\)', r'query = select(\1)', content)
    
    # Pattern 3: query.filter(...) -> query.where(...)
    content = content.replace('.filter(', '.where(')
    
    # Pattern 4: query.order_by(...).all()
    # Need to execute and get all results
    pattern4 = r'(\w+)\s*=\s*query\.order_by\(([^)]+)\)\.all\(\)'
    
    def replace4(match):
        var_name = match.group(1)
        order_expr = match.group(2)
        return f'query = query.order_by({order_expr})\n    result = await db.execute(query)\n    {var_name} = result.scalars().all()'
    
    content = re.sub(pattern4, replace4, content)
    
    # Pattern 5: db.delete(model); db.commit()
    content = re.sub(r'db\.delete\((\w+)\)\s*\n\s*db\.commit\(\)',
                    r'await db.delete(\1)\n    await db.commit()', content)
    
    return content

def fix_file(filepath):
    """Fix a single Python file"""
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Apply fixes
    content = fix_imports(content)
    content = fix_query_patterns(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Fixed {filepath}")
        return True
    else:
        print(f"  - No changes needed for {filepath}")
        return False

def main():
    """Fix all Python files in services and routers"""
    backend_dir = Path(__file__).parent
    
    dirs_to_fix = [
        backend_dir / 'services',
        backend_dir / 'routers',
        backend_dir / 'agents'
    ]
    
    fixed_count = 0
    
    for dir_path in dirs_to_fix:
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            if fix_file(py_file):
                fixed_count += 1
    
    print(f"\n✓ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
