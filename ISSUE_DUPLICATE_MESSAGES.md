# Issue: Duplicate Messages in Web UI

## Problem Description
The web UI displays duplicate welcome messages when a new conversation session is started. This creates a confusing user experience with redundant information being shown twice in the chat interface.

## Current Behavior
- When starting a new session, the welcome message appears twice
- Both messages are identical in content
- The duplication appears to be a rendering issue in the frontend

## Expected Behavior
- Welcome message should appear only once when starting a new session
- Clean, single message flow without duplicates

## Steps to Reproduce
1. Open the web UI at http://localhost:8081
2. Start a new conversation session
3. Observe that the welcome message appears twice in the chat

## Technical Details
- **Affected Component**: web/index.html (Alpine.js message rendering)
- **API Version**: Working correctly with single responses
- **Frontend Framework**: Alpine.js with Tailwind CSS

## Impact
- **Severity**: Low (cosmetic issue)
- **User Impact**: Confusing user experience but doesn't affect functionality
- **Priority**: Medium

## Potential Root Causes
1. Double initialization of Alpine.js components
2. Duplicate event listeners for message rendering
3. State management issue causing messages to be appended twice
4. WebSocket/HTTP response handling triggering multiple renders

## Suggested Fix
1. Review Alpine.js initialization code for duplicate init() calls
2. Check message append logic in the frontend
3. Ensure event listeners are properly cleaned up
4. Add deduplication logic based on message timestamps or IDs

## Related Issues
- Chart.js stack overflow errors (may be related to similar initialization issues)

## Testing Notes
- Test with Playwright confirmed the issue is consistent
- Issue occurs with all LLM providers (Claude, GPT, Gemini)
- Backend API returns single messages correctly

## Screenshots
- Screenshot available from Playwright test: ui-test-conversation-flow.png

---
**Date Reported**: 2025-08-14
**Reported By**: Strategy Coach Development Team
**Status**: Open