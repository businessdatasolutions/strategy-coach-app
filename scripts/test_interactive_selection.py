#!/usr/bin/env python3
"""
Test script for Issue #2 - Interactive Selection UI functionality
"""

import requests
import json
import time
from typing import Dict, Any


def test_interactive_selection():
    """Test the interactive selection functionality."""
    
    base_url = "http://localhost:8000"
    headers = {"Content-Type": "application/json"}
    
    # Start a new session
    print("Starting new session...")
    response = requests.post(f"{base_url}/conversation/start", headers=headers, json={})
    if response.status_code != 200:
        print(f"Failed to start session: {response.text}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"Session started: {session_id}\n")
    
    # Progress through conversation to reach belief exploration stage
    # Need 3+ turns and purpose indicators to trigger belief exploration
    test_messages = [
        "We are a technology company making software tools for small businesses",
        "Our purpose is to democratize access to enterprise-level technology",
        "We exist to empower small businesses to compete with larger companies",
        "Our mission is making powerful tools accessible to everyone"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"{'='*60}")
        print(f"Message {i}: {message}")
        
        response = requests.post(
            f"{base_url}/conversation/{session_id}/message",
            json={"message": message}
        )
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            continue
        
        data = response.json()
        print(f"Response: {data['response'][:200]}...")
        print(f"Phase: {data.get('current_phase', 'unknown')}")
        
        # Check for interactive elements
        if data.get("interactive_elements"):
            print("\n🎯 INTERACTIVE ELEMENT DETECTED!")
            interactive = data["interactive_elements"]
            print(f"Type: {interactive.get('type')}")
            print(f"Prompt: {interactive.get('prompt')}")
            print(f"Number of options: {len(interactive.get('options', []))}")
            print(f"Min selections: {interactive.get('min_selections')}")
            print(f"Max selections: {interactive.get('max_selections')}")
            
            # Display options
            print("\nOptions:")
            for opt in interactive.get('options', []):
                print(f"  - [{opt['id']}] {opt['text']} ({opt.get('category', 'general')})")
            
            # Simulate selection
            print("\n📝 Simulating user selection...")
            selected_ids = ["1", "3", "5"]  # Select a few options
            selected_texts = [
                opt['text'] for opt in interactive['options'] 
                if opt['id'] in selected_ids
            ]
            
            selection_message = f"I select: {', '.join(selected_texts)}"
            print(f"Sending selection: {selection_message}")
            
            # Send the selection
            response = requests.post(
                f"{base_url}/conversation/{session_id}/message",
                json={"message": selection_message}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Selection response: {data['response'][:200]}...")
                print("✅ Interactive selection processed successfully!")
            else:
                print(f"❌ Failed to process selection: {response.text}")
            
            break
        
        time.sleep(1)
    
    # If no interactive elements were found, try to trigger them
    if not any("interactive_elements" in r for r in [data]):
        print("\n⚠️ No interactive elements detected in normal flow.")
        print("Sending a message that might trigger belief exploration...")
        
        response = requests.post(
            f"{base_url}/conversation/{session_id}/message",
            json={"message": "We believe in empowering small businesses with powerful tools"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("interactive_elements"):
                print("✅ Interactive elements now available!")
                interactive = data["interactive_elements"]
                print(f"Type: {interactive.get('type')}")
                print(f"Prompt: {interactive.get('prompt')}")
                print(f"Options: {len(interactive.get('options', []))} available")
            else:
                print("Still no interactive elements in response")
    
    print(f"\n{'='*60}")
    print("Test completed!")


if __name__ == "__main__":
    test_interactive_selection()