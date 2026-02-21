# Project Summary - PLC MCP Bridge

## 🎯 What This Project Does

The **PLC MCP Bridge** is an industrial automation platform that connects Beckhoff TwinCAT PLCs to AI assistants and provides multiple interfaces for monitoring and querying machine data.

## 🚀 Main Features

### 1. **Interactive Web Dashboard** ⭐ NEW!
- **Modern web interface** with conversational AI
- **Real-time metrics** updated every 5 seconds
- **Canvas-style dashboard** that generates dynamically based on your questions
- **Dark theme** with glassmorphism effects
- **No external dependencies** (runs standalone)

**Quick Start:**
```powershell
.venv\Scripts\python.exe web_dashboard_server.py
# Open http://localhost:5000
```

### 2. **AI-Powered Dashboard Generator**
- Uses **DeepSeek LLM** to analyze PLC tags
- **Intelligently selects** panel types (Gauge, Stat, TimeSeries, StateTimeline)
- **Optimizes layout** based on priority and category
- **No templates** - adapts to any machine configuration

### 3. **Local AI Chat Interface**
- Terminal-based chat with **DeepSeek** integration
- **Natural language queries** for PLC data
- **Tool calling** for advanced automation
- **Offline operation** via Ollama

### 4. **MCP Server**
- **Model Context Protocol** server for AI integration
- **5 tools** available: list_machines, list_plc_tags, read_plc_tag, read_all_oee_tags, generate_dashboard
- **LIVE and MOCK modes** for testing

## 📁 Project Structure

```
Core/
├── 🌐 Web Dashboard
│   ├── web_dashboard_server.py    # Flask server with WebSocket
│   └── static/
│       ├── index.html             # Main page
│       ├── styles.css             # Modern dark theme
│       └── app.js                 # Interactive logic
│
├── 🤖 AI Components
│   ├── ollama_host.py             # AI chat interface
│   └── ai_dashboard_generator.py  # AI dashboard generator
│
├── 📊 Dashboard Generation
│   ├── dashboard_generator.py     # Template-based generator
│   └── preview_dashboard.py       # HTML preview generator
│
├── 🔌 PLC Integration
│   ├── server.py                  # MCP server
│   ├── drivers/
│   │   ├── beckhoff.py           # TwinCAT ADS driver
│   │   ├── mock.py               # Simulated driver
│   │   └── base.py               # Base driver interface
│   └── plc_settings/
│       └── Testing_Machine.json   # Machine configuration
│
├── 📚 Documentation
│   ├── README.md                  # Main documentation
│   ├── WEB_DASHBOARD.md          # How web dashboard works
│   ├── LIVE_MODE.md              # PLC connection guide
│   ├── TESTING_DASHBOARDS.md     # Dashboard testing
│   └── changelog.md              # Version history
│
└── 🧪 Testing
    └── tests/
        └── test_plc_connection.py # Connection tests
```

## 🎨 Key Technologies

- **Backend**: Flask + Flask-SocketIO (WebSocket)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **PLC**: pyads (TwinCAT ADS protocol)
- **AI**: DeepSeek via Ollama
- **Dashboards**: Grafanalib
- **Protocol**: Model Context Protocol (MCP)

## 📖 Documentation Files

1. **README.md** - Main project documentation and quick start
2. **WEB_DASHBOARD.md** - Detailed explanation of how the web dashboard works
3. **LIVE_MODE.md** - Guide for connecting to real PLCs
4. **TESTING_DASHBOARDS.md** - How to test and visualize dashboards
5. **changelog.md** - Complete version history

## 🔧 Configuration

All machine configurations are in `plc_settings/Testing_Machine.json`:
```json
{
  "MachineName": "Testing Machine",
  "Type": "Beckhoff",
  "IP_Address": "199.4.42.250",
  "Tags": {
    "Global.fOEE_Overall": {
      "type": "REAL",
      "description": "Overall Equipment Effectiveness"
    }
    // ... more tags
  }
}
```

## 🚦 Usage Examples

### Web Dashboard
```powershell
# Start server
.venv\Scripts\python.exe web_dashboard_server.py

# Open browser to http://localhost:5000

# Ask questions:
# - "Show me all metrics"
# - "What is the OEE?"
# - "Show production data"
```

### AI Chat
```powershell
# Start chat interface
.venv\Scripts\python.exe ollama_host.py

# Ask questions:
# - "List all available tags"
# - "Read all OEE values"
# - "Generate a dashboard for Testing_Machine"
```

### AI Dashboard Generator
```powershell
# Generate AI-powered dashboard
.venv\Scripts\python.exe ai_dashboard_generator.py

# Output: dashboards/AI_Testing_Machine_dashboard.json
```

## 🎯 Use Cases

1. **Real-time Monitoring** - Use web dashboard for live metrics
2. **Data Analysis** - Ask AI questions about machine performance
3. **Dashboard Creation** - Generate Grafana dashboards automatically
4. **Automation** - Use MCP tools for programmatic access
5. **Testing** - Use MOCK mode for development without hardware

## 🔒 Modes

- **LIVE Mode**: Connects to real PLC at 199.4.42.250
- **MOCK Mode**: Uses simulated data for testing

Change mode by setting `PLC_MODE` environment variable or editing the scripts.

## 📊 Generated Dashboards

The project generates three types of dashboards:

1. **AI-Generated** (`AI_Testing_Machine_dashboard.json`)
   - Intelligent panel selection
   - Optimized layout
   - Adapts to any configuration

2. **Template-Based** (`Testing_Machine_dashboard.json`)
   - Fast generation
   - Predictable structure
   - Good for prototyping

3. **HTML Preview** (`Testing_Machine_preview.html`)
   - Quick visualization
   - No Grafana needed
   - Browser-based

## 🎉 Recent Additions (2026-02-14)

✅ **Interactive Web Dashboard** - Modern web interface with real-time updates  
✅ **DeepSeek Integration** - Improved AI reasoning for industrial controls  
✅ **AI Dashboard Generator** - Template-free dashboard creation  
✅ **WebSocket Support** - Live data streaming to browsers  
✅ **Conversational Interface** - Ask questions in natural language  

## 🛠️ Dependencies

All dependencies are in `requirements.txt`. Key packages:
- Flask, Flask-SocketIO, Flask-CORS
- pyads (TwinCAT communication)
- ollama (AI integration)
- grafanalib (dashboard generation)
- mcp (Model Context Protocol)

## 📝 Notes

- **DeepSeek-R1** doesn't support tool calling - use llama3.2 for AI chat
- **Web dashboard** works with both LIVE and MOCK modes
- **Background updates** run every 5 seconds in web dashboard
- **Multiple interfaces** can run simultaneously
