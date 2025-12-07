#!/usr/bin/env python3
import socket
import threading
import json
import sys
import os

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