// Patch claude-code-proxy to use native Windows paths instead of WSL
const fs = require('fs');
const path = require('path');

const filePath = process.argv[2] || path.join(__dirname, 'claude-code-proxy', 'server', 'ClaudeRequest.js');
let content = fs.readFileSync(filePath, 'utf8');

// Patch loadCredentialsFromFile to always use native path
const oldLoadFunc = `loadCredentialsFromFile() {
    if (process.platform === 'win32') {
      return execSync('wsl cat ~/.claude/.credentials.json', { encoding: 'utf8', timeout: 10000 });
    } else {
      const credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
      return fs.readFileSync(credentialsPath, 'utf8');
    }
  }`;

const newLoadFunc = `loadCredentialsFromFile() {
    // Patched: Always use native path (no WSL dependency)
    const credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
    return fs.readFileSync(credentialsPath, 'utf8');
  }`;

// Patch writeCredentialsToFile to always use native path
const oldWriteFunc = `writeCredentialsToFile(credentialsJson) {
    if (process.platform === 'win32') {
      execSync(\`wsl tee ~/.claude/.credentials.json\`, { input: credentialsJson, encoding: 'utf8', timeout: 10000 });
    } else {
      const credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
      fs.writeFileSync(credentialsPath, credentialsJson, 'utf8');
    }
  }`;

const newWriteFunc = `writeCredentialsToFile(credentialsJson) {
    // Patched: Always use native path (no WSL dependency)
    const credentialsPath = path.join(os.homedir(), '.claude', '.credentials.json');
    fs.writeFileSync(credentialsPath, credentialsJson, 'utf8');
  }`;

if (content.includes(oldLoadFunc)) {
  content = content.replace(oldLoadFunc, newLoadFunc);
  console.log('Patched loadCredentialsFromFile');
} else {
  console.log('loadCredentialsFromFile already patched or pattern not found');
}

if (content.includes(oldWriteFunc)) {
  content = content.replace(oldWriteFunc, newWriteFunc);
  console.log('Patched writeCredentialsToFile');
} else {
  console.log('writeCredentialsToFile already patched or pattern not found');
}

fs.writeFileSync(filePath, content);
console.log('Patch complete!');
