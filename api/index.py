"""Vercel serverless function wrapper for FastAPI."""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize database on first import
from longevity_map.database.session import init_db
try:
    init_db()
except Exception as e:
    print(f"Database init warning: {e}")

from longevity_map.api.main import app

# Vercel expects a handler function
def handler(request):
    """Vercel serverless handler."""
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(request)

# Also export app directly for compatibility
__all__ = ['app', 'handler']

