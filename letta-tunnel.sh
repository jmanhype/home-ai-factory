#!/bin/bash
# Letta SSH Tunnel Script
# Creates tunnel to Letta server on 3090 PC through Docker VM

DOCKER_VM_IP="172.30.219.49"
LOCAL_PORT=8283
REMOTE_PORT=8283

# Kill existing tunnel
pkill -f "ssh.*${LOCAL_PORT}.*dominic@10.0.0.3" 2>/dev/null

# Check WireGuard
if ! ping -c 1 -W 2 10.0.0.3 &>/dev/null; then
    # Try Ollama endpoint instead (ping blocked)
    if ! curl -s --connect-timeout 3 http://10.0.0.3:11434/api/tags &>/dev/null; then
        echo "Error: Cannot reach 3090 PC. Start WireGuard first:"
        echo "  sudo wg-quick up ~/.config/wireguard/wg0.conf"
        exit 1
    fi
fi

echo "Creating SSH tunnel to Letta (via Docker VM)..."
ssh -i ~/.ssh/id_rsa -f -N -L ${LOCAL_PORT}:${DOCKER_VM_IP}:${REMOTE_PORT} dominic@10.0.0.3

sleep 2

if curl -s --connect-timeout 3 http://localhost:${LOCAL_PORT}/ &>/dev/null; then
    echo "✓ Letta tunnel established!"
    echo "  UI:     http://localhost:${LOCAL_PORT}"
    echo "  API:    http://localhost:${LOCAL_PORT}/v1"
    echo ""
    echo "To use Claude Code with persistent memory:"
    echo "  ANTHROPIC_BASE_URL=http://localhost:${LOCAL_PORT}/v1/anthropic claude"
else
    echo "✗ Tunnel created but Letta not responding"
    echo "  Check if Letta is running: ssh dominic@10.0.0.3 docker ps"
fi
