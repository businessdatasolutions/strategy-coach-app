#!/usr/bin/env python3
"""
Quick test to validate message extraction fix.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def test_message_extraction():
    """Test the fixed message extraction logic."""
    
    print("🧪 Testing message extraction fix...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to application
            await page.goto("http://localhost:8081")
            await page.wait_for_selector('input[type="text"]', timeout=10000)
            await asyncio.sleep(3)
            
            print("✅ Application loaded")
            
            # Get initial AI message using fixed extraction
            await asyncio.sleep(2)
            
            # Find AI messages using correct selectors
            ai_message_containers = await page.query_selector_all('.message-fade-in.flex.justify-start')
            print(f"📋 Found {len(ai_message_containers)} AI message containers")
            
            if ai_message_containers:
                last_ai_container = ai_message_containers[-1]
                
                # Try to get content using prose selector
                content_div = await last_ai_container.query_selector('.prose.prose-sm.max-w-none')
                
                if content_div:
                    message_text = await content_div.inner_text()
                    print(f"✅ AI message extracted ({len(message_text)} chars):")
                    print(f"   {message_text[:150]}...")
                else:
                    # Fallback method
                    fallback_text = await last_ai_container.inner_text()
                    print(f"⚠️ Fallback extraction ({len(fallback_text)} chars):")
                    print(f"   {fallback_text[:150]}...")
            else:
                print("❌ No AI message containers found")
            
            # Test sending a message and extracting response
            print("\n🔄 Testing message send and extraction...")
            
            await page.fill('input[type="text"]', "Hello, I'm interested in strategic coaching")
            await page.press('input[type="text"]', 'Enter')
            
            # Wait for typing indicator
            try:
                await page.wait_for_selector('.typing-indicator', timeout=5000)
                print("  🤔 Typing indicator detected")
                await page.wait_for_selector('.typing-indicator', state='detached', timeout=20000)
                print("  ✅ Typing complete")
            except Exception as e:
                print(f"  ⚠️ Typing indicator issue: {e}")
            
            # Wait for rendering
            await asyncio.sleep(4)
            
            # Extract new AI message
            ai_message_containers = await page.query_selector_all('.message-fade-in.flex.justify-start')
            print(f"📋 Now found {len(ai_message_containers)} AI message containers")
            
            if len(ai_message_containers) > 1:  # Should be 2 now (initial + response)
                last_ai_container = ai_message_containers[-1]
                content_div = await last_ai_container.query_selector('.prose.prose-sm.max-w-none')
                
                if content_div:
                    message_text = await content_div.inner_text()
                    print(f"✅ New AI response extracted ({len(message_text)} chars):")
                    print(f"   {message_text[:150]}...")
                    
                    if len(message_text) > 50:
                        print("🎉 Message extraction fix SUCCESSFUL!")
                    else:
                        print("❌ Message extraction still failing")
                else:
                    print("❌ Could not find content div in new message")
            else:
                print("❌ No new AI message detected")
                
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_message_extraction())