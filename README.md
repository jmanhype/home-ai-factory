# Home AI Factory

**Self-hosted AI infrastructure combining Claude Code + Letta persistent memory + local GPU inference.**

A personal "AI command center" that gives you:
- **Persistent memory** across Claude Code sessions via Letta
- **Local inference** on RTX 3090 via Ollama
- **Vector search + graph database** via PostgreSQL + pgvector
- **Secure mesh networking** via WireGuard

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         YOUR WORKSTATION (MacBook)                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Claude Code + Letta Proxy                     │    │
│  │  - Opus 4.5 reasoning (via Claude Max subscription)              │    │
│  │  - Persistent memory across sessions                             │    │
│  │  - Full filesystem + SSH access                                  │    │
│  └─────────────────────────────────┬───────────────────────────────┘    │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │ WireGuard VPN (10.0.0.0/24)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         GPU SERVER (RTX 3090 PC)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Letta Server   │  │ Postgres+pgvec  │  │     Ollama      │          │
│  │  (Memory API)   │  │ (Vector + SQL)  │  │  (Local LLM)    │          │
│  │  :8283          │  │  :5432          │  │  :11434         │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│  GPU: RTX 3090 (24GB VRAM) - runs qwen2.5-coder, embeddings, etc.       │
└─────────────────────────────────────────────────────────────────────────┘
```

## Why This Setup?

| Approach | Hardware Cost | Monthly Cost | Memory | Best Model Access |
|----------|---------------|--------------|--------|-------------------|
| **Pure Cloud** | $0 | $200+ | None | Opus 4.5 |
| **Pure Local (8x 3090)** | $18,000 | ~$50 electricity | None | Open source only |
| **This Hybrid** | ~$1,500 | ~$100-200 | Persistent | Opus 4.5 + local offload |

This setup gives you **Claude Opus 4.5 reasoning** (the best) with **persistent memory** (Letta) and **local inference** for simple tasks (Ollama on 3090).

## Quick Start

### Prerequisites

- MacBook (or Linux workstation) with Claude Code installed
- Windows/Linux PC with RTX 3090 (or similar GPU)
- WireGuard VPN connecting both machines
- Docker Desktop on the GPU server

### 1. Deploy on GPU Server

```bash
# Copy files to GPU server
scp -r . user@gpu-server:/home/user/ai-factory/

# SSH to GPU server
ssh user@gpu-server

# Deploy
cd ai-factory
cp .env.template .env
# Edit .env with your API keys
docker compose up -d
```

### 2. Configure MacBook

```bash
# Start SSH tunnel to Letta
./letta-tunnel.sh

# Use Claude Code with persistent memory
ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic claude
```

## Components

### Letta Server (Port 8283)
Persistent memory layer for Claude Code. Stores context across sessions, learns your preferences, maintains conversation history.

### PostgreSQL + pgvector (Port 5432)
Vector database for RAG and semantic search. Also stores Letta's memory and any documents you want to index.

### Ollama (Port 11434)
Local LLM inference on your GPU. Use for:
- Simple code completion
- Embeddings generation
- Tasks that don't need Opus-level reasoning

## Files

```
.
├── docker-compose.yml      # Main stack definition
├── letta-tunnel.sh         # SSH tunnel script for MacBook
├── setup-macbook.sh        # MacBook environment setup
├── deploy-windows.bat      # Windows deployment script
├── litellm-config.yaml     # Model routing configuration
├── cocoindex-config/       # Document indexing pipeline
│   └── pipeline.yaml
├── .env.template           # Environment variables template
└── README.md               # This file
```

## Usage

### Start the Tunnel (MacBook)

```bash
./letta-tunnel.sh
```

### Use Claude Code with Memory

```bash
# One-time
ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic claude

# Or add to ~/.zshrc for permanent use
export ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic
```

### Query Ollama Directly

```bash
curl http://10.0.0.3:11434/api/generate -d '{
  "model": "qwen2.5-coder:7b",
  "prompt": "Write a Python hello world",
  "stream": false
}'
```

### Access Letta UI

Open http://localhost:8283 in your browser (after starting tunnel).

## Troubleshooting

### Letta not accessible
```bash
# Check if tunnel is running
lsof -i :8283

# Restart tunnel
pkill -f "ssh.*8283"
./letta-tunnel.sh
```

### Docker containers not starting
```bash
# Check logs
docker compose logs -f

# Restart specific service
docker compose restart letta-server
```

### WireGuard not connected
```bash
# MacBook
sudo wg-quick up ~/.config/wireguard/wg0.conf

# Check connection
curl http://10.0.0.3:11434/api/tags
```

## Inspiration

Inspired by setups like [@0xSero's 8x RTX 3090 rig](https://twitter.com/0xSero), but optimized for **smart orchestration** over raw compute:

- His: 192GB VRAM, $18k hardware, pure local inference
- This: 24GB VRAM, $1.5k hardware, Claude + memory + local offload

Same productivity, fraction of the cost, with persistent memory.

## License

MIT
