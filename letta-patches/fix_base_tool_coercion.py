#!/usr/bin/env python3
"""
Patch Letta agent.py to add type coercion for base tools.

Base tools (LETTA_CORE) skip type coercion, causing errors when LLMs like
llama3.1 pass string numbers like "-1" instead of int -1.

This script patches the execute_tool_and_persist_state method to coerce
numeric strings before calling base tool functions.
"""

import sys

AGENT_PY = "/app/letta/agent.py"

# The unique line before which we need to insert coercion
# This is the function call line in the LETTA_CORE block
TARGET_LINE = 'function_response = callable_func(**function_args)'

# The coercion code to insert (must match surrounding indentation)
COERCION_CODE = '''                # PATCH: Coerce string numbers to int/float for base tools
                # LLMs like llama3.1 may pass "-1" instead of -1
                for _k, _v in list(function_args.items()):
                    if isinstance(_v, str) and _k != "self":
                        try:
                            if _v.lstrip('-').isdigit():
                                function_args[_k] = int(_v)
                            elif '.' in _v and _v.replace('.', '', 1).lstrip('-').isdigit():
                                function_args[_k] = float(_v)
                        except (ValueError, AttributeError):
                            pass
'''

def main():
    with open(AGENT_PY, 'r') as f:
        lines = f.readlines()

    # Check if already patched
    content = ''.join(lines)
    if "Coerce string numbers to int/float for base tools" in content:
        print("Already patched!")
        return 0

    # Find the LETTA_CORE block and insert coercion before function call
    patched = False
    new_lines = []
    in_letta_core_block = False

    for i, line in enumerate(lines):
        # Detect entering LETTA_CORE block
        if 'ToolType.LETTA_CORE' in line:
            in_letta_core_block = True

        # Insert coercion before the function call in LETTA_CORE block
        if in_letta_core_block and TARGET_LINE in line and not patched:
            new_lines.append(COERCION_CODE)
            patched = True
            in_letta_core_block = False  # Only patch first occurrence

        new_lines.append(line)

    if not patched:
        print("ERROR: Could not find target line in agent.py")
        print(f"Looking for: {TARGET_LINE}")
        return 1

    with open(AGENT_PY, 'w') as f:
        f.writelines(new_lines)

    print("Successfully patched agent.py with base tool type coercion")
    return 0

if __name__ == "__main__":
    sys.exit(main())
