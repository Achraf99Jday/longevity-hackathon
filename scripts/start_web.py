"""Start web server, trying multiple ports if needed."""

import socket
import subprocess
import sys
import os
from pathlib import Path

def is_port_available(port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=3000, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None

if __name__ == "__main__":
    # Try to find an available port
    port = find_available_port(3000)
    
    if port is None:
        print("❌ Could not find an available port (tried 3000-3009)")
        sys.exit(1)
    
    print("=" * 50)
    print(f"🌐 Web Server Starting")
    print(f"   URL: http://localhost:{port}")
    print(f"   Open this URL in your browser!")
    print("=" * 50)
    print()
    
    # Change to public directory
    public_dir = Path(__file__).parent.parent / "public"
    os.chdir(str(public_dir))
    
    # Start the server
    try:
        subprocess.run([sys.executable, "-m", "http.server", str(port)])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
