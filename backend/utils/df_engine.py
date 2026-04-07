"""
DataFrame Engine - FireDucks integration for 10-100x performance
"""

import logging

logger = logging.getLogger(__name__)

# Try to import FireDucks (10-100x faster pandas drop-in)
try:
    import fireducks.pandas as pd
    USING_FIREDUCKS = True
    logger.info("✓ Using FireDucks for 10-100x faster data processing")
except ImportError:
    import pandas as pd
    USING_FIREDUCKS = False
    logger.info("Using standard pandas (install fireducks-pandas for 10-100x speedup)")

# Export for use across the application
__all__ = ['pd', 'USING_FIREDUCKS']
