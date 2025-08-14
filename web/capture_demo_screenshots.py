#!/usr/bin/env python3
"""
Automated script to capture demo screenshots for the AI Strategic Co-pilot application.
This script runs through a complete user journey and captures key moments.
"""

import asyncio
from playwright.async_api import async_playwright
import os
import time

async def capture_demo_screenshots():
    """Run through the application and capture demo screenshots."""
    
    # Create screenshots directory
    screenshots_dir = "/Users/witoldtenhove/Documents/Projects/strategy-coach-app-v1/web/demo-screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()
        
        # Navigate to the application
        await page.goto("http://localhost:8080/")
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        # 1. Capture initial landing page
        print("📸 Capturing initial landing page...")
        await page.screenshot(path=f"{screenshots_dir}/01-landing-page.png", full_page=False)
        
        # 2. Start a conversation
        await page.fill('textarea[placeholder="Type your strategic thoughts..."]', 
                       "We are a technology company creating AI-powered tools for small businesses")
        await page.press('textarea[placeholder="Type your strategic thoughts..."]', 'Enter')
        await asyncio.sleep(3)
        
        print("📸 Capturing first interaction...")
        await page.screenshot(path=f"{screenshots_dir}/02-first-interaction.png", full_page=False)
        
        # 3. Continue conversation - purpose discovery
        await page.fill('textarea[placeholder="Type your strategic thoughts..."]', 
                       "Our purpose is to democratize access to enterprise-level AI technology")
        await page.press('textarea[placeholder="Type your strategic thoughts..."]', 'Enter')
        await asyncio.sleep(3)
        
        # 4. Continue to trigger belief exploration
        await page.fill('textarea[placeholder="Type your strategic thoughts..."]', 
                       "We want to empower small businesses to compete with Fortune 500 companies")
        await page.press('textarea[placeholder="Type your strategic thoughts..."]', 'Enter')
        await asyncio.sleep(3)
        
        # 5. Add one more message to trigger interactive selection
        await page.fill('textarea[placeholder="Type your strategic thoughts..."]', 
                       "Our mission is making powerful AI tools accessible and affordable for everyone")
        await page.press('textarea[placeholder="Type your strategic thoughts..."]', 'Enter')
        await asyncio.sleep(5)
        
        # Check if interactive panel appeared
        try:
            # Wait for the interactive panel
            await page.wait_for_selector('text="Which of these core beliefs resonate with your organization?"', timeout=10000)
            
            print("📸 Capturing interactive belief selection...")
            await page.screenshot(path=f"{screenshots_dir}/03-interactive-selection.png", full_page=False)
            
            # Make selections
            await page.click('text="Customer success is our success"')
            await asyncio.sleep(0.5)
            await page.click('text="Technology should empower, not complicate"')
            await asyncio.sleep(0.5)
            await page.click('text="Innovation drives sustainable growth"')
            await asyncio.sleep(0.5)
            
            print("📸 Capturing selections made...")
            await page.screenshot(path=f"{screenshots_dir}/04-selections-made.png", full_page=False)
            
            # Submit selections
            await page.click('button:has-text("Submit Selection")')
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Interactive panel not found: {e}")
        
        # 6. Continue conversation to show progression
        await page.fill('textarea[placeholder="Type your strategic thoughts..."]', 
                       "We believe that AI should augment human capabilities, not replace them")
        await page.press('textarea[placeholder="Type your strategic thoughts..."]', 'Enter')
        await asyncio.sleep(3)
        
        print("📸 Capturing conversation progression...")
        await page.screenshot(path=f"{screenshots_dir}/05-conversation-progress.png", full_page=False)
        
        # 7. Scroll to show strategy map area
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        
        print("📸 Capturing strategy map area...")
        await page.screenshot(path=f"{screenshots_dir}/06-strategy-map.png", full_page=False)
        
        # 8. Click Export Strategy button
        await page.click('button:has-text("Export Strategy")')
        await asyncio.sleep(2)
        
        # Navigate back to capture the full view
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        
        print("📸 Capturing complete interface...")
        await page.screenshot(path=f"{screenshots_dir}/07-complete-interface.png", full_page=False)
        
        print("✅ All screenshots captured successfully!")
        
        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_demo_screenshots())