#!/usr/bin/env python3
"""Initialize database tables"""

import asyncio
from database.db import init_db

async def main():
    print("Initializing database...")
    await init_db()
    print("✓ Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
