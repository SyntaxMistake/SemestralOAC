# Simple Dockerfile for the TicTacToe3D server (listens on $PORT)
FROM python:3.11-slim

WORKDIR /app

# Copy server code
COPY server.py /app/server.py

# Install any required packages (none for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Default port (can be overridden by Render env vars)
ENV PORT=5555
EXPOSE 5555

# Run server; server.py reads HOST/PORT from environment variables
CMD ["python", "server.py"]