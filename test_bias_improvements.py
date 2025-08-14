#!/usr/bin/env python3
"""
Test script to verify Issue #1 improvements:
- Response length limits (150-200 words)
- Single question per response
- Unbiased question patterns
"""

import requests
import json
import time
from typing import Dict, Any


def test_conversation_quality():
    """Test the improved conversation quality with bias-aware guidelines."""
    
    base_url = "http://localhost:8000"
    
    # Start a new session
    print("Starting new session...")
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{base_url}/conversation/start", headers=headers, json={})
    if response.status_code != 200:
        print(f"Failed to start session: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"Session started: {session_id}")
    print(f"Initial message: {session_data['message']}\n")
    
    # Test messages that should trigger concise, single-question responses
    test_messages = [
        "We are a technology company focused on making software tools.",
        "Our founders wanted to make complex technology accessible to everyone.",
        "We believe that good software should be intuitive and powerful.",
        "Our goal is to empower small businesses with enterprise-level tools."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: Sending message...")
        print(f"User: {message}")
        
        # Send message
        response = requests.post(
            f"{base_url}/conversation/{session_id}/message",
            json={"message": message}
        )
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            continue
        
        data = response.json()
        ai_response = data["response"]
        
        # Analyze response quality
        print(f"\nAI Response: {ai_response}")
        
        # Check response length
        word_count = len(ai_response.split())
        print(f"\n📊 Analysis:")
        print(f"  - Word count: {word_count}")
        
        # Check for response length compliance
        if word_count <= 250:  # Allow some buffer
            print(f"  ✅ Response length appropriate (target: 150-200 words)")
        else:
            print(f"  ❌ Response too long (exceeded 250 words)")
        
        # Count questions in response
        question_count = ai_response.count("?")
        print(f"  - Questions asked: {question_count}")
        
        if question_count <= 1:
            print(f"  ✅ Single question rule followed")
        else:
            print(f"  ❌ Multiple questions detected")
        
        # Check for biased patterns
        biased_patterns = [
            "Don't you think",
            "Wouldn't you agree",
            "Isn't it true",
            "Obviously",
            "Surely",
            "Should you",
            "Why haven't you",
            "Why didn't you"
        ]
        
        biases_found = []
        for pattern in biased_patterns:
            if pattern.lower() in ai_response.lower():
                biases_found.append(pattern)
        
        if not biases_found:
            print(f"  ✅ No obvious biased language patterns detected")
        else:
            print(f"  ❌ Potential biased patterns found: {', '.join(biases_found)}")
        
        # Check for false dichotomies (simplistic)
        if " or " in ai_response and "?" in ai_response:
            print(f"  ⚠️  Possible either/or question detected (check for false dichotomy)")
        
        print(f"\n  Current phase: {data.get('current_phase', 'unknown')}")
        print(f"  Completeness: {data.get('completeness_percentage', 0):.1f}%")
        
        time.sleep(1)  # Brief pause between messages
    
    # Get final session info
    print(f"\n{'='*60}")
    print("Session Summary:")
    response = requests.get(f"{base_url}/sessions/{session_id}")
    if response.status_code == 200:
        session_info = response.json()
        print(f"  - Total messages: {session_info['message_count']}")
        print(f"  - Final phase: {session_info['current_phase']}")
        print(f"  - Final completeness: {session_info['completeness_percentage']:.1f}%")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_conversation_quality()