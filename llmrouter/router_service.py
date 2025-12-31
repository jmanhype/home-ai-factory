"""
LLMRouter Service - Intelligent Model Selection

Analyzes incoming queries and routes them to the optimal model based on:
- Query complexity
- Task type (coding, reasoning, multimodal, etc.)
- Available resources (local GPU vs cloud)
- Cost optimization (prefer local when sufficient)

Integrates with:
- Claude Max subscription (via Letta proxy)
- GPT Pro subscription (via LiteLLM)
- Local Ollama (free inference)
"""

import os
import httpx
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="LLMRouter", description="Intelligent Model Selection")

# Load config
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.yaml")
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LETTA_BASE_URL = os.getenv("LETTA_BASE_URL", "http://localhost:8283")


class RouteRequest(BaseModel):
    query: str
    prefer_local: bool = True
    max_tokens: Optional[int] = None
    task_type: Optional[str] = None  # coding, reasoning, multimodal, general


class RouteResponse(BaseModel):
    model: str
    provider: str
    endpoint: str
    reason: str
    estimated_quality: float
    estimated_cost: str


class ChatRequest(BaseModel):
    query: str
    prefer_local: bool = True
    stream: bool = False


# Simple heuristics for routing (can be replaced with LLMRouter ML model)
COMPLEXITY_KEYWORDS = {
    "high": ["analyze", "architect", "design", "complex", "optimize", "refactor",
             "explain why", "compare", "evaluate", "strategic", "comprehensive"],
    "medium": ["implement", "create", "build", "fix", "debug", "write", "modify"],
    "low": ["hello", "hi", "what is", "simple", "basic", "list", "show", "print"]
}

CODING_KEYWORDS = ["code", "function", "class", "implement", "bug", "error",
                   "python", "javascript", "typescript", "rust", "go", "sql"]

MULTIMODAL_KEYWORDS = ["image", "picture", "photo", "screenshot", "diagram",
                       "visual", "see", "look at"]


def estimate_complexity(query: str) -> str:
    """Estimate query complexity based on keywords."""
    query_lower = query.lower()

    for keyword in COMPLEXITY_KEYWORDS["high"]:
        if keyword in query_lower:
            return "high"

    for keyword in COMPLEXITY_KEYWORDS["medium"]:
        if keyword in query_lower:
            return "medium"

    return "low"


def detect_task_type(query: str) -> str:
    """Detect the type of task from the query."""
    query_lower = query.lower()

    if any(kw in query_lower for kw in MULTIMODAL_KEYWORDS):
        return "multimodal"

    if any(kw in query_lower for kw in CODING_KEYWORDS):
        return "coding"

    if any(kw in query_lower for kw in COMPLEXITY_KEYWORDS["high"]):
        return "reasoning"

    return "general"


def select_model(query: str, prefer_local: bool = True, task_type: Optional[str] = None) -> RouteResponse:
    """Select the optimal model for the given query."""

    complexity = estimate_complexity(query)
    detected_task = task_type or detect_task_type(query)

    # Routing logic
    if detected_task == "multimodal":
        # GPT-4o is best for vision tasks
        return RouteResponse(
            model="gpt-4o",
            provider="openai",
            endpoint=f"{LITELLM_BASE_URL}/v1/chat/completions",
            reason="Multimodal task detected - GPT-4o has best vision capabilities",
            estimated_quality=0.95,
            estimated_cost="free (GPT Pro subscription)"
        )

    if complexity == "high" or detected_task == "reasoning":
        # Claude Opus for complex reasoning
        return RouteResponse(
            model="claude-opus-4-5-20251101",
            provider="anthropic",
            endpoint=f"{LETTA_BASE_URL}/v1/anthropic/messages",
            reason="Complex reasoning task - Claude Opus 4.5 has best reasoning",
            estimated_quality=0.98,
            estimated_cost="free (Claude Max subscription)"
        )

    if prefer_local and complexity in ["low", "medium"]:
        if detected_task == "coding":
            # Local model for simple coding
            return RouteResponse(
                model="qwen2.5-coder:7b",
                provider="ollama",
                endpoint=f"{OLLAMA_BASE_URL}/api/generate",
                reason="Simple coding task - local model is fast and free",
                estimated_quality=0.75,
                estimated_cost="free (local GPU)"
            )
        else:
            # Local model for general simple tasks
            return RouteResponse(
                model="qwen2.5-coder:7b",
                provider="ollama",
                endpoint=f"{OLLAMA_BASE_URL}/api/generate",
                reason="Simple task - local model is sufficient",
                estimated_quality=0.70,
                estimated_cost="free (local GPU)"
            )

    # Default to Claude Sonnet for balanced performance
    return RouteResponse(
        model="claude-sonnet-4-20250514",
        provider="anthropic",
        endpoint=f"{LETTA_BASE_URL}/v1/anthropic/messages",
        reason="Balanced task - Claude Sonnet offers good performance/speed",
        estimated_quality=0.90,
        estimated_cost="free (Claude Max subscription)"
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "llmrouter"}


@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """Analyze a query and return the optimal model to use."""
    return select_model(
        query=request.query,
        prefer_local=request.prefer_local,
        task_type=request.task_type
    )


@app.post("/chat")
async def chat_with_routing(request: ChatRequest):
    """Route and execute a chat request."""
    route = select_model(request.query, request.prefer_local)

    async with httpx.AsyncClient(timeout=120.0) as client:
        if route.provider == "ollama":
            response = await client.post(
                route.endpoint,
                json={
                    "model": route.model,
                    "prompt": request.query,
                    "stream": request.stream
                }
            )
        elif route.provider == "anthropic":
            response = await client.post(
                route.endpoint,
                json={
                    "model": route.model,
                    "messages": [{"role": "user", "content": request.query}],
                    "max_tokens": 4096
                },
                headers={"x-api-key": os.getenv("ANTHROPIC_API_KEY", "")}
            )
        else:  # openai
            response = await client.post(
                route.endpoint,
                json={
                    "model": route.model,
                    "messages": [{"role": "user", "content": request.query}]
                },
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"}
            )

        return {
            "route": route.dict(),
            "response": response.json()
        }


@app.get("/models")
async def list_models():
    """List available models and their capabilities."""
    return {
        "models": config.get("models", {}),
        "routing_strategy": "complexity-based with task detection"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4001)
