# Letta Memory Server with Claude Max Subscription

Uses your $200/month Claude Max subscription for everything - no extra API costs!

## Architecture

```
Claude Code (Mac) ──> Letta ──> Anthropic (your auth header)
                        │
                        └──> Sleeptime Agents ──> claude-code-proxy ──> Anthropic
                                                       │
                                                  (your credentials.json)
```

## Prerequisites (Windows 3090)

1. **Claude Code installed and logged in**
   ```powershell
   # Verify credentials exist (Windows native path)
   type %USERPROFILE%\.claude\.credentials.json
   ```

2. **Ollama running with embedding model**
   ```bash
   ollama pull mxbai-embed-large
   ollama serve  # if not already running
   ```

3. **Docker Desktop for Windows**

4. **Node.js installed**

---

## Setup: claude-code-proxy (Windows Native)

### Step 1: Clone and patch claude-code-proxy

```powershell
cd C:\Users\Dominic
git clone https://github.com/horselock/claude-code-proxy.git
cd claude-code-proxy
```

### Step 2: Patch for native Windows path (no WSL dependency)

The proxy defaults to using WSL. Patch it to use native Windows paths:

```powershell
# In ClaudeRequest.js, replace WSL credential loading with native path
# Line ~85: Change this:
#   return execSync('wsl cat ~/.claude/.credentials.json', { encoding: 'utf8', timeout: 10000 });
# To:
#   const credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json'); return fs.readFileSync(credentialsPath, 'utf8');
```

Or use the patch script:
```powershell
node C:\Users\Dominic\letta-patches\patch_proxy.js C:\Users\Dominic\claude-code-proxy\server\ClaudeRequest.js
```

### Step 3: Patch for /v1/models endpoint

Letta needs a models endpoint. Add this patch:
```powershell
node C:\Users\Dominic\letta-patches\patch_proxy_models.js C:\Users\Dominic\claude-code-proxy\server\server.js
```

### Step 4: Install as Windows Service

```powershell
cd C:\Users\Dominic\claude-code-proxy
npm install node-windows

# Create install-service.js:
@"
const Service = require('node-windows').Service;
const path = require('path');

const svc = new Service({
  name: 'claude-code-proxy',
  description: 'Claude Code Proxy for Letta memory server',
  script: path.join(__dirname, 'server', 'server.js'),
  nodeOptions: []
});

svc.on('install', function() {
  console.log('Service installed');
  svc.start();
});

svc.install();
"@ | Out-File -FilePath install-service.js -Encoding UTF8

# Install the service
node install-service.js

# Start the service
sc start claudecodeproxy.exe
```

The service will auto-start on Windows boot.

### Step 5: Allow through firewall

```powershell
netsh advfirewall firewall add rule name="claude-code-proxy" dir=in action=allow protocol=TCP localport=42069
```

---

## Setup: Letta Docker Container

### Step 1: Build the patched Letta image

```powershell
cd C:\Users\Dominic\letta-patches
docker build -f Dockerfile.claude-proxy -t letta-claude-proxy:v4 .
```

### Step 2: Start with docker-compose

```powershell
docker-compose up -d
```

### Step 3: Register the proxy provider (IMPORTANT!)

After Letta starts, register the proxy as a provider with a **unique name** (not "anthropic"):

```bash
curl -X POST http://localhost:8283/v1/providers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "claude-proxy",
    "provider_type": "anthropic",
    "api_key": "not-needed-proxy-handles-auth",
    "base_url": "http://host.docker.internal:42069"
  }'
```

This creates models with the handle `claude-proxy/claude-sonnet-4-20250514`.

---

## Using the Proxy Models

### Create an agent with the proxy

```bash
curl -X POST http://localhost:8283/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "model": "claude-proxy/claude-sonnet-4-20250514",
    "embedding": "ollama/mxbai-embed-large:latest"
  }'
```

### Send a message

```bash
curl -X POST http://localhost:8283/v1/agents/{agent-id}/messages \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

---

## Verify Everything Works

1. **Check proxy is running:**
   ```bash
   curl http://192.168.1.143:42069/v1/models
   # Should return list of Claude models in Anthropic format
   ```

2. **Check Letta is running:**
   ```bash
   curl http://192.168.1.143:8283/v1/health
   ```

3. **Check proxy models are registered:**
   ```bash
   curl http://192.168.1.143:8283/v1/models/ | jq '.[] | select(.provider_name == "claude-proxy")'
   ```

4. **Check proxy logs for POST requests:**
   When you send messages, you should see:
   ```
   INFO: POST /v1/messages from 127.0.0.1
   ```

---

## Key Points

### Why "claude-proxy" instead of "anthropic"?

Letta has a bug where if you register a provider with the same name as a base provider (like "anthropic"), it crashes due to a logging error when trying to handle multiple providers. Using a unique name like "claude-proxy" avoids this.

### Model handles

- Base Anthropic: `anthropic/claude-sonnet-4-20250514` (uses direct API, needs API key)
- Via Proxy: `claude-proxy/claude-sonnet-4-20250514` (uses your subscription)

### Required patches for claude-code-proxy

1. **Native Windows paths**: The proxy defaults to WSL credential loading
2. **Models endpoint**: Letta needs `/v1/models` to register the provider

---

## Troubleshooting

### "Token expired" from claude-code-proxy
The proxy auto-refreshes tokens. If it fails:
```bash
# Close and reopen Claude Code to refresh token
```

### "Connection refused" to host.docker.internal
On Windows Docker Desktop, ensure Docker Desktop is running.

### Letta crashes with "Multiple providers" error
Use a unique provider name like "claude-proxy" instead of "anthropic".

### Models endpoint returns wrong format
The patch adds Anthropic-format models response. Verify the patch was applied:
```bash
curl http://192.168.1.143:42069/v1/models | jq .
# Should have created_at, display_name, type fields
```

---

## What You're Getting

| Component | Purpose | Auth |
|-----------|---------|------|
| claude-code-proxy | Wraps subscription as API | Your credentials.json |
| Letta | Memory server + agents | Via claude-proxy provider |
| Ollama | Embeddings | Free, local |

**Total extra cost: $0** - Everything uses your existing Claude Max subscription!
