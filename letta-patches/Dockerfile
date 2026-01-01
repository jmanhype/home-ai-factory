# Custom Letta image for AI Factory
# Applies patches from https://github.com/jmanhype/letta/tree/ai-factory-patches
#
# Patches included:
# 1. proxy_helpers.py: Use free models for memory, forward auth header
# 2. anthropic.py: Hardcode MODEL_LIST for proxy providers
# 3. anthropic_client.py: Route requests through custom base_url
# 4. agent.py: Type coercion for base tool arguments
# 5. ollama.py: Default prompt formatter for OllamaProvider

FROM letta/letta:latest

# Clone patched files from fork and overlay them
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    git clone --depth 1 --branch ai-factory-patches https://github.com/jmanhype/letta.git /tmp/patched-letta && \
    cp /tmp/patched-letta/letta/server/rest_api/proxy_helpers.py /app/letta/server/rest_api/proxy_helpers.py && \
    cp /tmp/patched-letta/letta/schemas/providers/anthropic.py /app/letta/schemas/providers/anthropic.py && \
    cp /tmp/patched-letta/letta/schemas/providers/ollama.py /app/letta/schemas/providers/ollama.py && \
    cp /tmp/patched-letta/letta/llm_api/anthropic_client.py /app/letta/llm_api/anthropic_client.py && \
    cp /tmp/patched-letta/letta/agent.py /app/letta/agent.py && \
    rm -rf /tmp/patched-letta && \
    apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Verify patches are present
RUN grep 'model="ollama/qwen2.5-coder:7b"' /app/letta/server/rest_api/proxy_helpers.py && \
    grep 'Using hardcoded MODEL_LIST for proxy provider' /app/letta/schemas/providers/anthropic.py && \
    grep 'Using custom base_url for Anthropic client' /app/letta/llm_api/anthropic_client.py && \
    grep 'Coerce string numbers to int/float for base tools' /app/letta/agent.py && \
    grep 'default="chatml"' /app/letta/schemas/providers/ollama.py && \
    echo "All AI Factory patches verified!"
