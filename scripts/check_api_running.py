"""Check if API server is running and warn user."""

import socket
import sys

def check_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except OSError:
            return True

if __name__ == "__main__":
    api_port = 8000
    
    if check_port_in_use(api_port):
        print("=" * 60)
        print("WARNING: API SERVER IS RUNNING!")
        print("=" * 60)
        print(f"Port {api_port} is in use, which means the API server is running.")
        print("\nThe database will be locked. You must:")
        print("  1. Stop the API server (Ctrl+C in the terminal running 'npm start')")
        print("  2. Wait 2-3 seconds")
        print("  3. Run the fetch script again")
        print("=" * 60)
        sys.exit(1)
    else:
        print("[OK] API server is not running. Database should be available.")
        sys.exit(0)


