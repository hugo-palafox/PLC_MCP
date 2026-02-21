# PLC-Bridge MCP Server

Industrial automation bridge connecting Beckhoff TwinCAT PLCs to AI assistants via the Model Context Protocol (MCP).

## Features

- **Live PLC Integration**: Read real-time data from Beckhoff TwinCAT PLCs via ADS/AMS
- **Interactive Web Dashboard**: Modern web interface with conversational AI for querying PLC data
- **AI-Powered Dashboard Generator**: Uses DeepSeek LLM to intelligently create Grafana dashboards
- **Local AI Chat**: Interact with PLC data using natural language via DeepSeek (offline)
- **Autonomous Dashboards**: Generate Grafana dashboards programmatically using `grafanalib`
- **Optimized Performance**: Batch reads and symbol caching for large projects
- **Mock Mode**: Test without hardware using simulated data

## Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Web Dashboard (Recommended)
```powershell
.venv\Scripts\python.exe web_dashboard_server.py
```
Then open http://localhost:5000 in your browser.

**Features:**
- Ask questions: "Show me all metrics", "What is the OEE?"
- Live dashboard updates every 5 seconds
- Modern dark theme with glassmorphism effects

### 3. Alternative: Run the AI Chat Host
```powershell
.venv\Scripts\python.exe ollama_host.py
```

**Default**: LIVE mode (connects to real PLC at `199.4.42.250`)

To use MOCK mode instead, edit `ollama_host.py` and change:
```python
server_env["PLC_MODE"] = "LIVE"  # Change to "MOCK"
```

## Project Structure

```
Core/
├── web_dashboard_server.py  # Web dashboard server (NEW!)
├── static/                   # Web dashboard frontend
│   ├── index.html           # Main page
│   ├── styles.css           # Styling
│   └── app.js               # JavaScript logic
├── server.py                # MCP server with PLC tools
├── ollama_host.py           # Local AI chat interface
├── ai_dashboard_generator.py # AI-powered dashboard generator
├── dashboard_generator.py   # Template-based dashboard generator
├── drivers/
│   ├── beckhoff.py         # TwinCAT ADS driver
│   └── mock.py             # Simulated PLC driver
├── plc_settings/
│   └── Testing_Machine.json # Machine configuration
├── tests/
│   └── test_plc_connection.py  # Connection verification
└── dashboards/              # Generated dashboard JSONs

```

## Available Interfaces

### 1. Web Dashboard (Recommended)
Modern web interface with conversational AI:
- **URL**: http://localhost:5000
- **Features**: Live metrics, chat interface, auto-refresh
- **Best for**: Monitoring and visualization

### 2. AI Chat Host
Terminal-based chat interface:
- **Command**: `.venv\Scripts\python.exe ollama_host.py`
- **Features**: Natural language queries, tool calling
- **Best for**: Advanced queries and automation

### 3. MCP Tools
When using the AI host, you can:
- **List machines**: "Show me the machines"
- **List tags**: "What tags are available?"
- **Read values**: "Read all tag values" or "What is the OEE?"
- **Generate dashboards**: "Create a dashboard for Testing_Machine"

## Configuration

Edit `plc_settings/Testing_Machine.json` to configure:
- Machine name and type
- IP address
- Tag definitions with types and descriptions

## Documentation

- [LIVE_MODE.md](LIVE_MODE.md) - Guide for connecting to real PLCs
- [TESTING_DASHBOARDS.md](TESTING_DASHBOARDS.md) - Dashboard testing guide
- [changelog.md](changelog.md) - Version history
- [.agent/rules/plc-safety.md](.agent/rules/plc-safety.md) - Safety guidelines

## Requirements

- Python 3.12+
- Ollama with DeepSeek model (for local AI)
- TwinCAT ADS (for live PLC connection)
- Grafanalib (for dashboard generation)
- Flask, Flask-SocketIO (for web dashboard)

## Web Dashboard Usage

1. **Start the server**:
   ```powershell
   .venv\Scripts\python.exe web_dashboard_server.py
   ```

2. **Open browser**: Navigate to http://localhost:5000

3. **Ask questions**:
   - "Show me all metrics" - Displays all PLC tags
   - "What is the OEE?" - Shows OEE metric
   - "Show production data" - Displays production metrics

4. **Watch live updates**: Dashboard auto-refreshes every 5 seconds

## Technology Stack

- **Backend**: Flask + Flask-SocketIO for real-time communication
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript (no frameworks)
- **PLC Communication**: pyads for TwinCAT ADS protocol
- **AI**: DeepSeek via Ollama for intelligent analysis
- **Dashboard Generation**: Grafanalib for programmatic dashboard creation
