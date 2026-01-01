#!/usr/bin/env python3
"""
Patch OllamaProvider to have a default value for default_prompt_formatter.
The REST API doesn't expose this required field, so we add a sensible default.
"""

import sys

OLLAMA_PY = "/app/letta/schemas/providers/ollama.py"

# The old pattern (required field with no default)
OLD_PATTERN = '''    default_prompt_formatter: str = Field(
        ..., description="Default prompt formatter (aka model wrapper) to use on a /completions style API."
    )'''

# The new pattern (with default value)
NEW_PATTERN = '''    default_prompt_formatter: str = Field(
        default="chatml", description="Default prompt formatter (aka model wrapper) to use on a /completions style API."
    )'''

def main():
    with open(OLLAMA_PY, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'default="chatml"' in content:
        print("OllamaProvider already patched!")
        return 0

    # Apply patch
    if OLD_PATTERN in content:
        content = content.replace(OLD_PATTERN, NEW_PATTERN)
        with open(OLLAMA_PY, 'w') as f:
            f.write(content)
        print("Successfully patched OllamaProvider with default prompt formatter")
        return 0
    else:
        print("ERROR: Could not find target pattern in ollama.py")
        print("Looking for:", repr(OLD_PATTERN[:100]))
        return 1

if __name__ == "__main__":
    sys.exit(main())
