// Patch claude-code-proxy to return a models list
// This prevents 401 errors when Letta tries to list models

const fs = require('fs');
const path = require('path');

const serverPath = process.argv[2] || path.join(__dirname, 'claude-code-proxy', 'server', 'server.js');
let content = fs.readFileSync(serverPath, 'utf8');

// Add models endpoint handler before the catch-all
const modelsHandler = `
// Models endpoint for Letta compatibility (Anthropic format)
if (req.method === 'GET' && pathname === '/v1/models') {
  Logger.info('GET /v1/models from ' + req.socket.remoteAddress);
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    data: [
      { id: "claude-sonnet-4-20250514", created_at: "2025-05-14T00:00:00Z", display_name: "Claude Sonnet 4", type: "model" },
      { id: "claude-3-5-sonnet-20241022", created_at: "2024-10-22T00:00:00Z", display_name: "Claude 3.5 Sonnet", type: "model" },
      { id: "claude-3-opus-20240229", created_at: "2024-02-29T00:00:00Z", display_name: "Claude 3 Opus", type: "model" },
      { id: "claude-3-5-haiku-20241022", created_at: "2024-10-22T00:00:00Z", display_name: "Claude 3.5 Haiku", type: "model" }
    ],
    first_id: "claude-sonnet-4-20250514",
    last_id: "claude-3-5-haiku-20241022",
    has_more: false
  }));
  return;
}
`;

// Find the message handler and insert before it
const messagePattern = "if (req.method === 'POST' && (pathname === '/v1/messages'";
if (content.includes(messagePattern)) {
  content = content.replace(messagePattern, modelsHandler + '\n  ' + messagePattern);
  fs.writeFileSync(serverPath, content);
  console.log('Successfully patched server.js with /v1/models endpoint');
} else {
  console.log('Could not find message handler pattern');
  console.log('Looking for:', messagePattern);
}
