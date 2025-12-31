# Custom Letta image with subscription-friendly memory agent
# Uses free models for memory operations while proxying subscription for inference

FROM letta/letta:latest

# Patch the proxy_helpers.py to use free models for agent creation
RUN sed -i 's|model="anthropic/claude-sonnet-4-5-20250929"|model="letta/letta-free"|g' \
    /app/letta/server/rest_api/proxy_helpers.py && \
    sed -i 's|embedding="openai/text-embedding-ada-002"|embedding="letta/letta-free"|g' \
    /app/letta/server/rest_api/proxy_helpers.py

# Verify the patch was applied
RUN grep -A2 'model="letta/letta-free"' /app/letta/server/rest_api/proxy_helpers.py || \
    echo "WARNING: Patch may not have been applied correctly"

# The proxy still forwards YOUR subscription credentials for main inference!
# Only the background memory operations use free models.
