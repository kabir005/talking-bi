"""
Initialize database and create default SQLite connection for testing
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.db import init_db, AsyncSessionLocal
from database.models import DBConnection
from sqlalchemy import select


async def main():
    # Initialize database (creates tables)
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized")
    
    # Create default SQLite connection if it doesn't exist
    async with AsyncSessionLocal() as db:
        # Check if connection already exists
        result = await db.execute(select(DBConnection).where(DBConnection.name == "LocalDB"))
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"✓ Connection 'LocalDB' already exists (ID: {existing.id})")
        else:
            # Create new connection
            connection = DBConnection(
                name="LocalDB",
                db_type="sqlite",
                database="./data/talking.db",
                host=None,
                port=None,
                username=None,
                password=None,
                ssl=False
            )
            
            db.add(connection)
            await db.commit()
            
            print(f"✓ Created default connection 'LocalDB' (ID: {connection.id})")
            print(f"  Database: ./data/talking.db")
            print(f"  Type: SQLite")
    
    print("\n✅ Setup complete! You can now use the Database Agent.")


if __name__ == "__main__":
    asyncio.run(main())
