#!/usr/bin/env python3
"""
Register Ollama provider with Letta at startup.
This script runs before the main server and ensures Ollama is available.
"""

import os
import sys
import time
import requests

LETTA_SERVER = "http://localhost:8283"
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

def wait_for_server(timeout=60):
    """Wait for Letta server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{LETTA_SERVER}/v1/providers/", timeout=5)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def register_ollama():
    """Register Ollama provider if not already present."""
    try:
        # Check if Ollama already registered
        resp = requests.get(f"{LETTA_SERVER}/v1/providers/")
        providers = resp.json()
        for p in providers:
            if p.get("name") == "ollama":
                print("Ollama provider already registered")
                return True

        # Register Ollama
        # Note: The API doesn't expose default_prompt_formatter,
        # so we need to use the internal configuration
        print(f"Registering Ollama provider at {OLLAMA_BASE_URL}")
        resp = requests.post(
            f"{LETTA_SERVER}/v1/providers/",
            json={
                "name": "ollama",
                "provider_type": "ollama",
                "api_key": "not-needed",
                "base_url": OLLAMA_BASE_URL
            }
        )

        if resp.status_code in (200, 201):
            print("Ollama provider registered successfully")
            return True
        else:
            print(f"Failed to register: {resp.status_code} {resp.text}")
            return False

    except Exception as e:
        print(f"Error registering Ollama: {e}")
        return False

if __name__ == "__main__":
    # This script is meant to be run after the server starts
    # For now, just print instructions
    print("Ollama registration script loaded")
    print(f"OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
