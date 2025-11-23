"""Vercel serverless function wrapper for FastAPI."""

import sys
from pathlib import Path
import os
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Vercel environment variable for database path
os.environ["VERCEL"] = "1"

# Don't initialize database at import time - let it happen lazily
# Database will be created on first request if needed
logging.info("Skipping database init at import time (will initialize on first use)")

# Import app (this may trigger more imports)
try:
    from longevity_map.api.main import app
    logging.info("FastAPI app imported successfully")
except Exception as e:
    logging.error(f"Error importing FastAPI app: {e}", exc_info=True)
    # Create a minimal app as fallback
    from fastapi import FastAPI
    app = FastAPI(title="Longevity R&D Map API (Error Mode)")
    
    @app.get("/")
    def root():
        return {"error": "Failed to initialize application", "details": str(e)}

# Vercel expects a handler function
def handler(request):
    """Vercel serverless handler."""
    try:
        from mangum import Mangum
        asgi_handler = Mangum(app, lifespan="off")
        return asgi_handler(request)
    except Exception as e:
        logging.error(f"Handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {"error": "Internal server error", "message": str(e)}
        }

# Also export app directly for compatibility
__all__ = ['app', 'handler']

