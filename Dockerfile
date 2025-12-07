# Simple Dockerfile for the TicTacToe3D server
FROM python:3.11-slim

WORKDIR /app

# Copy server code
COPY server.py /app/server.py

# Expose the TCP port the server listens on
EXPOSE 5555

# Run server; keep binding to 0.0.0.0 and port 5555 (you can override via CLI args)
CMD ["python", "server.py", "0.0.0.0", "5555"]