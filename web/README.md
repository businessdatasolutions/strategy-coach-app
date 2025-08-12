# AI Strategic Co-pilot Web UI

A modern, responsive web interface for the AI Strategic Co-pilot system.

## Features

✨ **Modern Chat Interface**
- Real-time message exchange with AI agents
- Typing indicators and loading states
- Markdown rendering for formatted responses
- Message timestamps and role distinction

📊 **Strategy Visualization**
- Interactive radar chart showing Six Value Components
- Real-time progress tracking
- Phase progression indicators (WHY → HOW → WHAT)

🎯 **Session Management**
- Start new strategic sessions
- Export strategy as JSON
- Persistent conversation history
- Connection status monitoring

🎨 **Beautiful Design**
- Tailwind CSS for modern styling
- Responsive layout for all devices
- Smooth animations and transitions
- Professional color scheme

## Technology Stack

- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first styling (via CDN)
- **Alpine.js** - Lightweight reactive framework (via CDN)
- **Chart.js** - Data visualization (via CDN)
- **Marked.js** - Markdown rendering (via CDN)

## Quick Start

### Option 1: Direct File Access
Simply open `index.html` in your web browser:
```bash
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

### Option 2: Python HTTP Server
Run the included server script:
```bash
python3 serve.py
```
Then open http://localhost:8080 in your browser.

### Option 3: Any HTTP Server
Serve the directory with any HTTP server:
```bash
# Using Python's built-in server
python3 -m http.server 8080

# Using Node.js http-server
npx http-server -p 8080

# Using PHP's built-in server
php -S localhost:8080
```

## Prerequisites

1. **API Server Running**: Ensure the FastAPI backend is running at `http://localhost:8000`
   ```bash
   cd ..
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Modern Web Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

3. **Internet Connection**: Required for CDN resources (Tailwind, Alpine.js, etc.)

## Configuration

To change the API endpoint, modify the `apiUrl` variable in `index.html`:
```javascript
apiUrl: 'http://localhost:8000',  // Change this to your API URL
```

## UI Components

### 1. Header Section
- Application title and description
- Export Strategy button
- New Session button

### 2. Progress Tracker
- Visual phase indicators (WHY, HOW, WHAT)
- Completeness percentage
- Phase completion checkmarks

### 3. Chat Interface
- Message history with user/AI distinction
- Input field with Enter key support
- Send button with disabled states
- Typing indicators

### 4. Information Panels
- **Current Focus**: Shows active agent and phase
- **Next Steps**: Recommendations from the AI
- **Strategy Map**: Radar chart visualization

## Features in Detail

### Conversation Flow
1. Automatically starts a new session on page load
2. Sends user messages to the API
3. Displays AI responses with markdown formatting
4. Updates progress and recommendations in real-time

### Session Management
- Each session gets a unique ID
- Progress is tracked throughout the conversation
- Strategy can be exported at any time
- New sessions can be started without page reload

### Error Handling
- Connection status monitoring
- Graceful error messages
- Automatic retry logic for failed requests
- User-friendly error notifications

### Responsive Design
- Mobile-first approach
- Adaptive layouts for different screen sizes
- Touch-friendly interface elements
- Optimized for both desktop and mobile

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### File Structure
```
web/
├── index.html      # Main UI file
├── serve.py        # Development server
└── README.md       # This file
```

### Customization

#### Colors
Modify Tailwind classes in the HTML:
- Primary: `blue-600`, `blue-700`
- Success: `green-500`, `green-600`
- Warning: `yellow-500`, `yellow-600`
- Error: `red-500`, `red-600`

#### Layout
Adjust grid classes:
- Chat width: `lg:col-span-2`
- Sidebar width: `lg:col-span-1`

#### Chart Configuration
Modify the Chart.js options in `initStrategyMapChart()`:
```javascript
scales: {
    r: {
        max: 100,  // Maximum value
        ticks: {
            stepSize: 20  // Grid intervals
        }
    }
}
```

## Troubleshooting

### Connection Issues
- Verify the API server is running at `http://localhost:8000`
- Check browser console for CORS errors
- Ensure no firewall is blocking local connections

### Display Issues
- Clear browser cache
- Ensure CDN resources are loading
- Check browser console for JavaScript errors

### Performance
- Limit conversation history if needed
- Reduce animation complexity for older devices
- Consider local CDN alternatives for offline use

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Dark mode toggle
- [ ] Voice input/output
- [ ] Collaborative sessions
- [ ] Advanced visualizations with D3.js
- [ ] Progressive Web App (PWA) features
- [ ] Offline support with service workers

## License

Part of the AI Strategic Co-pilot project.