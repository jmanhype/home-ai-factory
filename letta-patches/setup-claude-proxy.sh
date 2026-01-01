#!/bin/bash
# Setup script for claude-code-proxy on Windows/WSL
# This exposes your Claude Max subscription as an API for Letta's sleeptime agents

set -e

PROXY_DIR="$HOME/claude-code-proxy"

echo "=== Setting up claude-code-proxy ==="
echo "This will expose your Claude Max subscription as an API at localhost:42069"
echo ""

# Check if Claude Code credentials exist
if [ ! -f "$HOME/.claude/.credentials.json" ]; then
    echo "ERROR: Claude Code credentials not found at ~/.claude/.credentials.json"
    echo "Make sure you're logged into Claude Code first (run 'claude' and authenticate)"
    exit 1
fi

echo "Found Claude Code credentials"

# Clone or update the proxy
if [ -d "$PROXY_DIR" ]; then
    echo "Updating existing claude-code-proxy..."
    cd "$PROXY_DIR"
    git pull
else
    echo "Cloning claude-code-proxy..."
    git clone https://github.com/horselock/claude-code-proxy.git "$PROXY_DIR"
    cd "$PROXY_DIR"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Install it with:"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  source ~/.bashrc"
    echo "  nvm install --lts"
    exit 1
fi

echo "Node.js version: $(node --version)"

# Install dependencies
echo "Installing dependencies..."
npm install

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the proxy, run:"
echo "  cd $PROXY_DIR && npm start"
echo ""
echo "The proxy will be available at: http://localhost:42069/v1"
echo ""
echo "From Docker, use: http://host.docker.internal:42069/v1"
echo ""
