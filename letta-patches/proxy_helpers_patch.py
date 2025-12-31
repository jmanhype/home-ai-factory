"""
Patch for Letta proxy_helpers.py

This patch modifies the Claude Code agent creation to use FREE models
for memory operations, while the main inference uses YOUR subscription.

Changes:
- model: anthropic/claude-sonnet → ollama/qwen2.5-coder:7b (local, free)
- embedding: openai/text-embedding-ada-002 → letta/letta-free (free tier)

This allows self-hosted Letta to work with Claude Max/GPT Pro subscriptions
without needing separate API keys for memory operations.
"""

# Original code in get_or_create_claude_code_agent():
ORIGINAL_AGENT_CONFIG = '''
agent_config = CreateAgent(
    name=agent_name,
    description="Agent for capturing Claude Code conversations",
    memory_blocks=[...],
    tags=["claude-code"],
    enable_sleeptime=True,
    agent_type="letta_v1_agent",
    model="anthropic/claude-sonnet-4-5-20250929",  # PAID - needs API key
    embedding="openai/text-embedding-ada-002",      # PAID - needs API key
    project_id=project_id,
)
'''

# Patched version - uses FREE models for memory operations
PATCHED_AGENT_CONFIG = '''
agent_config = CreateAgent(
    name=agent_name,
    description="Agent for capturing Claude Code conversations",
    memory_blocks=[...],
    tags=["claude-code"],
    enable_sleeptime=True,
    agent_type="letta_v1_agent",
    model="letta/letta-free",                       # FREE - Letta's free tier
    embedding="letta/letta-free",                   # FREE - Letta's free tier
    project_id=project_id,
)
'''

# Alternative using local Ollama (completely self-hosted):
PATCHED_AGENT_CONFIG_OLLAMA = '''
agent_config = CreateAgent(
    name=agent_name,
    description="Agent for capturing Claude Code conversations",
    memory_blocks=[...],
    tags=["claude-code"],
    enable_sleeptime=True,
    agent_type="letta_v1_agent",
    model="ollama/qwen2.5-coder:7b",               # FREE - local GPU
    embedding="letta/letta-free",                   # FREE - Letta's free tier
    project_id=project_id,
)
'''

# How the flow works:
#
# 1. Claude Code sends request to your self-hosted Letta
#    └─ Headers include your Max subscription OAuth token
#
# 2. Letta's anthropic.py proxy:
#    a) Creates/gets a memory agent (uses FREE models above)
#    b) Injects memory context into the request
#    c) Forwards to api.anthropic.com WITH YOUR AUTH HEADERS
#    d) Anthropic validates your subscription → request succeeds
#    e) Response comes back, Letta stores in memory (using FREE models)
#
# 3. Result:
#    - Main inference: YOUR Claude Max subscription (unlimited!)
#    - Memory operations: FREE (letta-free or local Ollama)
