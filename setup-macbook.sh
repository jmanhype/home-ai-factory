#!/bin/bash
# AI Factory - MacBook Setup Script
# Configures Claude Code to use Letta memory proxy on 3090 PC

set -e

echo "========================================"
echo "   AI Factory - MacBook Setup"
echo "========================================"
echo

# Check WireGuard connection
echo "Checking WireGuard connection to 3090 PC..."
if ping -c 1 10.0.0.3 &> /dev/null; then
    echo "✓ 3090 PC reachable via WireGuard"
else
    echo "✗ Cannot reach 3090 PC. Make sure WireGuard is connected."
    echo "  Run: sudo wg-quick up ~/.config/wireguard/wg0.conf"
    exit 1
fi

# Check Letta server
echo "Checking Letta server..."
if curl -s --connect-timeout 5 http://10.0.0.3:8283/health &> /dev/null; then
    echo "✓ Letta server is running"
else
    echo "✗ Letta server not responding. Deploy AI Factory on 3090 PC first."
    exit 1
fi

# Add environment variables to shell config
SHELL_CONFIG="$HOME/.zshrc"
if [[ -f "$HOME/.bash_profile" ]] && [[ ! -f "$HOME/.zshrc" ]]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

echo
echo "Adding AI Factory environment variables to $SHELL_CONFIG..."

# Check if already configured
if grep -q "AI_FACTORY_CONFIG" "$SHELL_CONFIG" 2>/dev/null; then
    echo "Already configured in $SHELL_CONFIG"
else
    cat >> "$SHELL_CONFIG" << 'EOF'

# === AI_FACTORY_CONFIG ===
# Letta Memory Proxy for Claude Code
export LETTA_SERVER_URL="http://10.0.0.3:8283"

# Uncomment to route Claude Code through Letta proxy:
# export ANTHROPIC_BASE_URL="http://10.0.0.3:8283/v1/anthropic"

# VectorGraph connection
export VECTORGRAPH_URL="postgresql://vectorgraph:vectorgraph_secret@10.0.0.3:5432/ai_factory"

# Local Ollama on 3090
export OLLAMA_HOST="http://10.0.0.3:11434"
# === END AI_FACTORY_CONFIG ===
EOF
    echo "✓ Environment variables added"
fi

# Create convenience aliases
echo
echo "Adding convenience commands..."
if ! grep -q "ai-factory-aliases" "$SHELL_CONFIG" 2>/dev/null; then
    cat >> "$SHELL_CONFIG" << 'EOF'

# === ai-factory-aliases ===
alias ai-status='curl -s http://10.0.0.3:8283/health && echo " Letta OK" || echo " Letta DOWN"'
alias ai-logs='ssh dominic@10.0.0.3 "cd C:\\ai-factory && docker compose logs -f"'
# === end ai-factory-aliases ===
EOF
    echo "✓ Aliases added"
fi

echo
echo "========================================"
echo "   Setup Complete!"
echo "========================================"
echo
echo "To use Claude Code with Letta memory proxy:"
echo "  1. Restart your terminal (or run: source $SHELL_CONFIG)"
echo "  2. Uncomment ANTHROPIC_BASE_URL in $SHELL_CONFIG"
echo "  3. Run: claude"
echo
echo "Or use one-time proxy mode:"
echo "  ANTHROPIC_BASE_URL=http://10.0.0.3:8283/v1/anthropic claude"
echo
echo "Useful commands:"
echo "  ai-status  - Check if AI Factory is running"
echo "  ai-logs    - View logs from 3090 PC"
echo
