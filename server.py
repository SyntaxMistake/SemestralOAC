#!/usr/bin/env python3
import socket
import threading
import json
import sys
import os
import time
import urllib.request
import urllib.error


def _start_keep_alive():
    """
    Start a daemon thread that periodically pings a URL to prevent process shutdown.
    
    Configuration via environment variables:
    - KEEP_ALIVE_URL: Full URL to ping (if not set, constructs from PORT)
    - PORT: Fallback port if KEEP_ALIVE_URL not provided (default: 5555)
    - KEEP_ALIVE_INTERVAL: Seconds between pings (default: 1500 = 25 minutes)
    """
    keep_alive_url = os.environ.get('KEEP_ALIVE_URL')
    
    if not keep_alive_url:
        # Construct URL from PORT environment variable
        port = os.environ.get('PORT', '5555')
        keep_alive_url = f'http://127.0.0.1:{port}'
    
    # Get interval in seconds (default 1500 = 25 minutes)
    try:
        interval = int(os.environ.get('KEEP_ALIVE_INTERVAL', '1500'))
    except ValueError:
        interval = 1500
    
    def _keep_alive_worker():
        """Worker function that performs periodic HTTP GET requests."""
        while True:
            try:
                req = urllib.request.Request(keep_alive_url, method='GET')
                with urllib.request.urlopen(req, timeout=10) as response:
                    # Read response to complete the request
                    _ = response.read()
                print(f"Keep-alive ping successful to {keep_alive_url}", flush=True)
            except urllib.error.URLError as e:
                # Log connection errors - server might not be ready yet
                print(f"Keep-alive ping failed: {e}", flush=True)
            except Exception as e:
                # Log unexpected errors but continue running
                print(f"Keep-alive unexpected error: {e}", flush=True)
            
            # Sleep after ping attempt to avoid initial delay
            time.sleep(interval)
    
    # Start daemon thread
    thread = threading.Thread(target=_keep_alive_worker, daemon=True, name='KeepAlive')
    thread.start()
    print(f"Keep-alive helper started: pinging {keep_alive_url} every {interval} seconds", flush=True)


# Start keep-alive helper on module import
_start_keep_alive()


class TicTacToe3DServer:
    def __init__(self, host='0.0.0.0', port=None):
        # Render provides PORT environment variable
        if port is None:
            port = int(os.environ.get('PORT', 5555))
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server.bind((host, port))
        except OSError as e:
            print(f"Failed to bind to port {port}: {e}", flush=True)
            print(f"Available ports from Render: {os.environ.get('PORT', 'Not set')}", flush=True)
            raise
        
        self.server.listen(4)
        print(f"Server listening on {host}:{port}", flush=True)
        
        # [Rest of your existing server code remains the same...]

if __name__ == "__main__":
    # Render-specific: Get host/port from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port_env = os.environ.get('PORT')
    
    if port_env:
        port = int(port_env)
    else:
        # For local development
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555
    
    server = TicTacToe3DServer(host, port)
    server.run()