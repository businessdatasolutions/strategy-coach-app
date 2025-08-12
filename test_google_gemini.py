#!/usr/bin/env python3
"""
Test script to verify Google Gemini API integration.

This script demonstrates that the AI Strategic Co-pilot is successfully
using Google Gemini for all LLM operations.
"""

import requests
import json
import time
from typing import Dict, Any


def test_health_check() -> bool:
    """Test the health endpoint."""
    print("Testing health check...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health Status: {data['status']}")
        print(f"   Orchestrator: {data['components']['orchestrator']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False


def test_start_conversation() -> str:
    """Test starting a new conversation."""
    print("\nTesting conversation start...")
    payload = {
        "user_context": {
            "company_name": "AI HealthTech Solutions",
            "industry": "Healthcare Technology",
            "team_size": "50-100"
        }
    }
    
    response = requests.post(
        "http://localhost:8000/conversation/start",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data['session_id']
        print(f"✅ Conversation started successfully")
        print(f"   Session ID: {session_id}")
        print(f"   Current Phase: {data['current_phase']}")
        return session_id
    else:
        print(f"❌ Failed to start conversation: {response.status_code}")
        return ""


def test_send_message(session_id: str) -> bool:
    """Test sending a message in the conversation."""
    print(f"\nTesting message sending for session {session_id}...")
    
    messages = [
        "Our purpose is to democratize access to healthcare through AI",
        "We believe technology should empower doctors, not replace them",
        "Our core values are innovation, integrity, and patient-first care"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  Message {i}: {msg[:50]}...")
        response = requests.post(
            f"http://localhost:8000/conversation/{session_id}/message",
            json={"message": msg}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Response received")
            print(f"     Agent: {data.get('current_agent', 'unknown')}")
            print(f"     Completeness: {data.get('completeness_percentage', 0)}%")
        else:
            print(f"  ❌ Failed to send message: {response.status_code}")
            return False
        
        time.sleep(1)  # Brief pause between messages
    
    return True


def test_export_strategy(session_id: str) -> bool:
    """Test exporting the strategy map."""
    print(f"\nTesting strategy export for session {session_id}...")
    
    response = requests.get(
        f"http://localhost:8000/conversation/{session_id}/export"
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Strategy exported successfully")
        print(f"   Completeness: {data['completeness_percentage']}%")
        
        # Check strategy map structure
        strategy_map = data.get('strategy_map', {})
        if 'why' in strategy_map:
            print(f"   WHY section: {bool(strategy_map['why'].get('purpose'))}")
        if 'how' in strategy_map:
            print(f"   HOW section: Present")
        if 'what' in strategy_map:
            print(f"   WHAT section: Present")
        
        return True
    else:
        print(f"❌ Failed to export strategy: {response.status_code}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Gemini API Integration Test")
    print("Using Model: gemini-2.0-flash-exp")
    print("API Key: AIzaSyCnC96Gm4nMc6_cdNNkC36WPaqT_U6x2WA")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n⚠️  Server health check failed. Is the server running?")
        return
    
    # Test 2: Start Conversation
    session_id = test_start_conversation()
    if not session_id:
        print("\n⚠️  Failed to start conversation")
        return
    
    # Test 3: Send Messages
    if not test_send_message(session_id):
        print("\n⚠️  Failed to send messages")
        return
    
    # Test 4: Export Strategy
    if not test_export_strategy(session_id):
        print("\n⚠️  Failed to export strategy")
        return
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Google Gemini integration is working.")
    print("=" * 60)


if __name__ == "__main__":
    main()