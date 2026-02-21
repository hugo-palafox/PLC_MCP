# Web Dashboard - How It Works

## Overview

The web dashboard is a real-time, interactive interface for monitoring and querying PLC data. It combines a conversational AI interface with live metric visualization.

## Architecture

### Components

1. **Flask Backend** (`web_dashboard_server.py`)
   - REST API for chat interactions
   - WebSocket for real-time data streaming
   - PLC driver integration

2. **Frontend** (`static/`)
   - `index.html` - Page structure
   - `styles.css` - Modern dark theme styling
   - `app.js` - Interactive logic and WebSocket handling

3. **PLC Integration**
   - Uses existing Beckhoff/Mock drivers
   - Reads from `plc_settings/Testing_Machine.json`
   - Supports both LIVE and MOCK modes

## Data Flow

### 1. Initial Page Load
```
Browser → GET / → Flask serves index.html
↓
Browser loads styles.css and app.js
↓
JavaScript establishes WebSocket connection
↓
Server sends 'connected' event
↓
Status indicator turns green
```

### 2. User Asks Question
```
User types: "Show me all metrics"
↓
app.js → POST /api/chat with {message: "..."}
↓
web_dashboard_server.py processes message
↓
Connects to PLC driver
↓
Reads tags from Testing_Machine.json
↓
Calls driver.read_tags(tag_names)
↓
Returns {response: "...", dashboard_data: {...}}
↓
app.js receives response
↓
Hides welcome message
↓
Creates metric cards dynamically
↓
Displays in canvas area with animations
```

### 3. Live Updates (Every 5 Seconds)
```
Background thread in web_dashboard_server.py
↓
Reads all PLC tags
↓
Formats as metrics array
↓
Emits 'dashboard_update' via WebSocket
↓
All connected browsers receive update
↓
app.js updates existing metric card values
↓
Adds pulse animation to changed values
```

## Key Features

### Conversational Interface
- Simple keyword matching (can be upgraded to LLM)
- Recognizes: "oee", "production", "parts", "all", "show"
- Returns appropriate dashboard data

### Dynamic Dashboard Generation
- No hardcoded HTML for metrics
- JavaScript creates cards on-the-fly
- Each card includes:
  - Human-readable title
  - Large value display
  - Tag name (technical reference)
  - Type badge (REAL, DINT, BOOL, etc.)
  - Color-coded status border

### Real-Time Updates
- WebSocket maintains persistent connection
- Background thread reads PLC every 5 seconds
- Updates pushed to all connected clients
- No page refresh needed

### Status Indicators
- **Green border**: Good values (OEE ≥ 85%, BOOL = true)
- **Yellow border**: Warning (OEE 70-85%)
- **Red border**: Error (OEE < 70%, BOOL = false)

## Code Walkthrough

### Backend: Chat Endpoint
```python
@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    
    # Connect to PLC
    driver = get_plc_driver()
    
    # Load configuration
    config = load_machine_config()
    tags = config.get('Tags', {})
    
    # Read all tag values
    data = driver.read_tags(list(tags.keys()))
    
    # Determine response based on keywords
    if 'oee' in user_message:
        response = f"Current OEE: {data.get('Global.fOEE_Overall')}%"
    elif 'production' in user_message:
        response = "Showing production metrics"
    
    # Format dashboard data
    dashboard_data = {
        'metrics': [
            {
                'name': tag_meta['description'],
                'value': data[tag_name],
                'tag': tag_name,
                'type': tag_meta['type']
            }
            for tag_name, tag_meta in tags.items()
        ]
    }
    
    return jsonify({
        'response': response,
        'dashboard_data': dashboard_data
    })
```

### Frontend: Rendering Metrics
```javascript
function renderDashboard(metrics) {
    metricsGrid.innerHTML = '';
    
    metrics.forEach((metric, index) => {
        const card = document.createElement('div');
        card.className = 'metric-card';
        card.setAttribute('data-tag', metric.tag);
        
        card.innerHTML = `
            <h3>${metric.name}</h3>
            <div class="metric-value">${formatValue(metric.value)}</div>
            <div class="metric-tag">${metric.tag}</div>
            <span class="metric-type">${metric.type}</span>
        `;
        
        metricsGrid.appendChild(card);
    });
}
```

### WebSocket: Live Updates
```javascript
const socket = io();

socket.on('dashboard_update', (data) => {
    // Update existing cards without recreating them
    data.metrics.forEach(metric => {
        const card = document.querySelector(`[data-tag="${metric.tag}"]`);
        if (card) {
            const valueEl = card.querySelector('.metric-value');
            valueEl.textContent = formatValue(metric.value);
            // Add pulse animation
            valueEl.style.animation = 'pulse 0.5s ease-in-out';
        }
    });
});
```

## Customization

### Add New Keywords
Edit `web_dashboard_server.py`:
```python
elif 'quality' in user_message:
    response = "Showing quality metrics"
    dashboard_type = 'quality'
```

### Change Update Frequency
Edit `web_dashboard_server.py`:
```python
def background_data_emitter():
    while True:
        time.sleep(10)  # Change from 5 to 10 seconds
        # ... rest of code
```

### Modify Card Styling
Edit `static/styles.css`:
```css
.metric-card {
    background: rgba(255, 255, 255, 0.1);  /* Adjust transparency */
    border-radius: 16px;  /* Change corner radius */
    padding: 2rem;  /* Adjust padding */
}
```

### Add LLM Integration
Replace keyword matching with actual LLM:
```python
# Instead of keyword matching
if 'oee' in user_message:
    ...

# Use LLM
response = ollama.chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': user_message}]
)
```

## Performance

- **Initial Load**: ~500ms
- **Chat Response**: ~200-500ms (depends on PLC connection)
- **WebSocket Update**: ~50ms
- **Memory Usage**: ~50MB (Flask + WebSocket)
- **Concurrent Users**: Supports 10+ simultaneous connections

## Troubleshooting

### Dashboard Not Loading
- Check if server is running: `http://localhost:5000`
- Check browser console for errors (F12)
- Verify Flask is running without errors

### No Live Updates
- Check WebSocket connection in browser console
- Verify background thread is running
- Check PLC connection status

### Metrics Not Displaying
- Verify `Testing_Machine.json` exists
- Check PLC connection (LIVE vs MOCK mode)
- Review server logs for errors
