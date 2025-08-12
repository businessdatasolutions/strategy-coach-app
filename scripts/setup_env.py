#!/usr/bin/env python3
"""
Environment setup script for AI Strategic Co-pilot.

This script helps users configure their environment variables interactively.
"""

import os
import shutil
from pathlib import Path


def main():
    """Interactive environment setup."""
    print("🚀 AI Strategic Co-pilot Environment Setup")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    # Check if .env already exists
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    # Copy from example
    if env_example.exists():
        shutil.copy2(env_example, env_file)
        print(f"✅ Created .env file from template")
    else:
        print("❌ .env.example not found!")
        return
    
    print("\n📝 Please configure your API keys:")
    print("You need at least one of the following:")
    
    # OpenAI API Key
    openai_key = input("Enter your OpenAI API Key (or press Enter to skip): ").strip()
    if openai_key:
        update_env_var(env_file, "OPENAI_API_KEY", openai_key)
        print("✅ OpenAI API key configured")
    
    # Anthropic API Key
    anthropic_key = input("Enter your Anthropic API Key (or press Enter to skip): ").strip()
    if anthropic_key:
        update_env_var(env_file, "ANTHROPIC_API_KEY", anthropic_key)
        print("✅ Anthropic API key configured")
    
    # Validate at least one key is provided
    if not openai_key and not anthropic_key:
        print("❌ At least one API key is required!")
        print("Please edit .env file manually to add your API keys.")
        return
    
    # Optional: LangSmith
    print("\n🔍 Optional: LangSmith for observability")
    enable_tracing = input("Enable LangSmith tracing? (y/N): ").strip().lower()
    if enable_tracing in ['y', 'yes']:
        langsmith_key = input("Enter your LangSmith API Key: ").strip()
        if langsmith_key:
            update_env_var(env_file, "LANGCHAIN_TRACING_V2", "true")
            update_env_var(env_file, "LANGSMITH_API_KEY", langsmith_key)
            print("✅ LangSmith tracing configured")
    
    print("\n🎉 Environment setup complete!")
    print(f"📁 Configuration saved to: {env_file}")
    print("\n📋 Next steps:")
    print("1. Review and customize settings in .env file")
    print("2. Run: uvicorn src.api.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")


def update_env_var(env_file: Path, key: str, value: str):
    """Update an environment variable in the .env file."""
    lines = []
    updated = False
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update existing line or add new one
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    
    if not updated:
        lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()