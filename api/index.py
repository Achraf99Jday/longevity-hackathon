"""Vercel serverless function wrapper for FastAPI."""

import sys
from pathlib import Path
import os
import logging

# Set up basic logging to stderr (Vercel captures this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Vercel environment variable for database path
os.environ["VERCEL"] = "1"

# Initialize app variable
app = None

# Try to import and initialize the app
try:
    logging.info("Starting app initialization...")
    
    # Don't initialize database at import time - let it happen lazily
    logging.info("Skipping database init at import time (will initialize on first use)")
    
    # Import app (this may trigger more imports)
    from longevity_map.api.main import app
    logging.info("FastAPI app imported successfully")
    
except Exception as e:
    logging.error(f"Error importing FastAPI app: {e}", exc_info=True)
    # Create a minimal app as fallback
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Longevity R&D Map API (Error Mode)")
        
        @app.get("/")
        def root():
            return {
                "error": "Failed to initialize application",
                "details": str(e),
                "type": type(e).__name__
            }
        
        @app.get("/health")
        def health():
            return {"status": "error", "message": str(e)}
            
        logging.info("Created fallback FastAPI app")
    except Exception as fallback_error:
        logging.error(f"Could not create fallback app: {fallback_error}", exc_info=True)
        # Last resort - create a simple handler that returns error
        def handler(request):
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": {"error": "Application initialization failed", "details": str(e)}
            }
        __all__ = ['handler']
        raise

# Vercel expects a handler function
def handler(request):
    """Vercel serverless handler."""
    try:
        if app is None:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": {"error": "Application not initialized"}
            }
        
        from mangum import Mangum
        asgi_handler = Mangum(app, lifespan="off")
        return asgi_handler(request)
    except Exception as e:
        logging.error(f"Handler error: {e}", exc_info=True)
        import traceback
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": {
                "error": "Internal server error",
                "message": str(e),
                "type": type(e).__name__
            }
        }

# Also export app directly for compatibility
__all__ = ['app', 'handler']

