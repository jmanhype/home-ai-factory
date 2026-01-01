# Home AI Factory

**Self-hosted AI infrastructure combining Claude Code + Letta persistent memory + intelligent model routing + local GPU inference.**

A personal "AI command center" that gives you:
- **Persistent memory** across Claude Code sessions via Letta
- **Intelligent model routing** via LLMRouter - automatically picks the right model for each task
- **Local inference** on RTX 3090 via Ollama (free compute for simple tasks)
- **Vector search + graph database** via PostgreSQL + pgvector + Apache AGE
- **Document ingestion pipeline** via CocoIndex
- **Secure mesh networking** via WireGuard

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           YOUR WORKSTATION (MacBook)                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                      Claude Code + Letta Memory Proxy                    │    │
│  │  - Opus 4.5 reasoning (via Claude Max subscription - FREE inference)     │    │
│  │  - GPT-4o/o1 (via GPT Pro subscription - FREE inference)                 │    │
│  │  - Persistent memory across ALL sessions                                 │    │
│  │  - Full filesystem + SSH access                                          │    │
│  └─────────────────────────────────┬───────────────────────────────────────┘    │
└────────────────────────────────────┼────────────────────────────────────────────┘
                                     │ WireGuard VPN (10.0.0.0/24)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GPU SERVER (RTX 3090 PC)                               │
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  Letta Server   │  │   LLMRouter     │  │     Ollama      │                  │
│  │  (Memory API)   │  │ (Smart Routing) │  │  (Local LLM)    │                  │
│  │  :8283          │  │  :4001          │  │  :11434         │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Postgres+pgvec  │  │   CocoIndex     │  │   LiteLLM       │                  │
│  │ +Apache AGE     │  │ (Data Pipeline) │  │ (Model Proxy)   │                  │
│  │  :5432          │  │  CLI tool       │  │  :4000          │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                  │
│  GPU: RTX 3090 (24GB VRAM) - runs qwen2.5-coder, embeddings, local inference    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Model Routing Strategy

This setup uses **intelligent model routing** to optimize cost and performance:

### LLMRouter (Query-Aware Routing)
From [ulab-uiuc/LLMRouter](https://github.com/ulab-uiuc/LLMRouter) - analyzes each query and routes to the optimal model:

| Query Type | Routed To | Why |
|------------|-----------|-----|
| Simple code completion | Ollama (local) | Free, fast, good enough |
| Complex reasoning | Claude Opus 4.5 | Best reasoning (via Max subscription) |
| Multimodal/vision | GPT-4o | Best vision (via Pro subscription) |
| Long context | Claude | 200K context window |
| Math/logic puzzles | o1 | Specialized reasoning |

### Your Subscriptions
- **Claude Max ($100/mo)**: Unlimited Opus 4.5, Sonnet - used via Letta proxy
- **GPT Pro ($200/mo)**: Unlimited GPT-4o, o1 - used via LiteLLM proxy

**Result**: You get the best of ALL models with zero per-token costs!

## Why This Setup?

| Approach | Hardware Cost | Monthly Cost | Memory | Best Model Access |
|----------|---------------|--------------|--------|-------------------|
| **Pure Cloud** | $0 | $200+ API costs | None | Limited by budget |
| **Pure Local (8x 3090)** | $18,000 | ~$50 electricity | None | Open source only |
| **This Hybrid** | ~$1,500 | ~$300 subscriptions | Persistent | ALL best models, unlimited |

Inspired by [@0xSero's 8x RTX 3090 rig](https://twitter.com/0xSero), but optimized for **smart orchestration** over raw compute:
- His: 192GB VRAM, $18k hardware, pure local inference
- Ours: 24GB VRAM, $1.5k hardware, Claude Max + GPT Pro + local offload + persistent memory

## Components

### Letta Server (Port 8283)
Persistent memory layer for Claude Code. The key innovation:
- **Stores context across sessions** - remembers your projects, preferences, past conversations
- **Works with Claude Max** - routes through your subscription (no extra API costs)
- **Learns your patterns** - improves suggestions over time

Usage:
```bash
# Start the tunnel first
./letta-tunnel.sh

# Then run Claude Code with Letta memory proxy
ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic claude
```

### LLMRouter (Port 4001)
Intelligent model selection from [ulab-uiuc/LLMRouter](https://github.com/ulab-uiuc/LLMRouter):
- Analyzes query complexity in real-time
- Routes to optimal model (local vs cloud, Claude vs GPT)
- Saves money by using local models when sufficient
- Uses cloud models only when necessary

### PostgreSQL + pgvector + Apache AGE (Port 5432)
Combined vector + graph database:
- **pgvector**: Semantic search over embeddings
- **Apache AGE**: Graph queries for relationships
- **VectorGraph pattern**: Query both vectors AND graphs in single SQL

From [QuixiAI/vectorgraph](https://github.com/QuixiAI/vectorgraph) concepts.

### CocoIndex (CLI Tool)
Data ingestion pipeline from [cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex):
- Transforms documents into embeddings
- Maintains incremental updates
- Supports multiple data sources

### Ollama (Port 11434)
Local LLM inference on your GPU:
- **qwen2.5-coder:7b** - Fast code completion
- **qwen2.5-coder:32b** - High quality local coding
- Custom models as needed

### LiteLLM Proxy (Port 4000)
Unified API for all model providers:
- Single endpoint for Claude, GPT, Ollama
- Automatic failover and retries
- Usage tracking and rate limiting

## Quick Start

### Prerequisites
- MacBook (or Linux workstation) with Claude Code installed
- Windows/Linux PC with RTX 3090 (or similar GPU)
- WireGuard VPN connecting both machines
- Docker Desktop on the GPU server
- **Claude Max subscription** (for unlimited Opus 4.5)
- **GPT Pro subscription** (optional, for unlimited GPT-4o/o1)

### 1. Deploy on GPU Server

```bash
# Copy files to GPU server
scp -r . user@gpu-server:/home/user/ai-factory/

# SSH to GPU server
ssh user@gpu-server

# Deploy
cd ai-factory
cp .env.template .env

# Edit .env with your API keys (for fallback/Letta)
nano .env

# Start the stack
docker compose up -d

# For full stack (includes LiteLLM, Qdrant):
docker compose --profile full up -d
```

### 2. Configure MacBook

```bash
# Run setup script
./setup-macbook.sh

# Or manually start SSH tunnel
./letta-tunnel.sh

# Use Claude Code with persistent memory
ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic claude
```

### 3. Verify Everything Works

```bash
# Check Letta
curl http://localhost:8283/v1/health

# Check Ollama
curl http://10.0.0.3:11434/api/tags

# Check PostgreSQL
psql postgresql://vectorgraph:vectorgraph_secret@10.0.0.3:5432/ai_factory -c "SELECT 1"
```

## Files

```
.
├── docker-compose.yml      # Main stack definition
├── litellm-config.yaml     # Model routing configuration
├── letta-tunnel.sh         # SSH tunnel script for MacBook
├── setup-macbook.sh        # MacBook environment setup
├── deploy-windows.bat      # Windows deployment script
├── cocoindex-config/       # Document indexing pipeline
│   └── pipeline.yaml
├── .env.template           # Environment variables template
└── README.md               # This file
```

## Using Your Subscriptions

### How It Works (The Magic)

We patched Letta to work with your **existing subscriptions** instead of requiring separate API keys:

```
Claude Code (authenticated with your Max subscription)
    │
    │  OAuth token in x-api-key header
    ▼
Your Self-Hosted Letta (port 8283)
    │
    ├─► Memory Operations: Uses FREE models (letta-free)
    │   - Agent creation, embeddings, background processing
    │   - Costs you nothing!
    │
    └─► Main Inference: Passes YOUR auth headers through
        │
        ▼
    https://api.anthropic.com
        │
        └─► Validates your Max subscription token
            └─► Request processed under YOUR subscription (unlimited!)
```

The key insight: Letta's proxy just forwards your authentication headers. We patched the memory agent to use free models so you don't need API keys.

### Claude Max (Unlimited Opus 4.5)

```bash
# 1. Start the tunnel to your self-hosted Letta
./letta-tunnel.sh

# 2. Run Claude Code with Letta memory proxy
ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic claude

# Or export for the session
export ANTHROPIC_BASE_URL=http://localhost:8283/v1/anthropic
claude
```

Your Max subscription handles ALL inference. Letta just adds persistent memory for free.

### GPT Pro (Unlimited GPT-4o, o1)

For OpenAI, you'd need to create a similar proxy (coming soon) or use LiteLLM:

```bash
# Query GPT-4o through LiteLLM proxy
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-ai-factory-master-key" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}]}'
```

Note: GPT Pro subscription passthrough requires additional work (OpenAI uses different auth flow).

### Intelligent Routing (Best of Both)

LLMRouter analyzes queries and picks the best model:

```bash
# Let the router decide
curl http://localhost:4001/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Write a simple hello world in Python"}'
# Returns: ollama/qwen2.5-coder:7b (free, fast)

curl http://localhost:4001/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze this complex system architecture and suggest improvements"}'
# Returns: claude-opus-4-5 (best reasoning)
```

## Advanced Usage

### Add Documents to Knowledge Base

Using CocoIndex:
```bash
pip install cocoindex
cocoindex run --config cocoindex-config/pipeline.yaml
```

### Query VectorGraph

Combined vector + graph query:
```sql
-- Find related concepts with semantic similarity
SELECT v.content, v.embedding <-> query_embedding AS distance,
       ag.*
FROM vectors v
JOIN ag_catalog.cypher('knowledge_graph', $$
  MATCH (n)-[r]->(m) WHERE n.id = $1 RETURN n, r, m
$$, ARRAY[v.id]) AS ag
WHERE v.embedding <-> query_embedding < 0.5
ORDER BY distance;
```

### Monitor GPU Usage

```bash
ssh user@gpu-server nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1
```

## Troubleshooting

### Letta not accessible
```bash
# Check if tunnel is running
lsof -i :8283

# Restart tunnel
pkill -f "ssh.*8283"
./letta-tunnel.sh
```

### Ollama model not loading
```bash
# Check GPU memory
ssh user@gpu-server nvidia-smi

# Restart Ollama (Windows)
ssh user@gpu-server 'taskkill /F /IM ollama.exe && Start-Process ollama -ArgumentList "serve"'

# Pull model again
curl http://10.0.0.3:11434/api/pull -d '{"name": "qwen2.5-coder:7b"}'
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

## Roadmap

- [ ] LLMRouter integration for automatic model selection
- [ ] Apache AGE graph database for knowledge graphs
- [ ] Voice interface via Whisper + local TTS
- [ ] Multi-agent orchestration
- [ ] Web UI for monitoring and configuration

## References

- [Letta AI](https://github.com/letta-ai/letta) - Persistent memory for LLMs
- [LLMRouter](https://github.com/ulab-uiuc/LLMRouter) - Intelligent model routing
- [VectorGraph](https://github.com/QuixiAI/vectorgraph) - Vector + Graph database
- [CocoIndex](https://github.com/cocoindex-io/cocoindex) - Data transformation pipeline
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM proxy
- [@0xSero's Setup](https://twitter.com/0xSero) - Inspiration for home AI rigs

## License

MIT
