# Using LIVE Mode with Real PLC

## Quick Start

### 1. Test PLC Connection
Before using LIVE mode, verify your PLC is reachable:

```powershell
.venv\Scripts\python.exe tests\test_plc_connection.py
```

This will check:
- Network connectivity to `199.4.42.250`
- TwinCAT ADS server status
- Ability to list and read tags

### 2. Run LIVE Mode Host

If the connection test passes, run:

```powershell
.venv\Scripts\python.exe ollama_host_live.py
```

This connects to your **real PLC** instead of using mock data.

## Troubleshooting

### Connection Failed

If you see `❌ Failed to connect to PLC`, check:

1. **TwinCAT Runtime**: Ensure the PLC is in RUN mode
2. **ADS Server**: Verify ADS is enabled in TwinCAT System Manager
3. **Firewall**: Port 48898 (ADS/AMS) must be open
4. **Network**: Can you ping `199.4.42.250`?

### Tool Selection Issues

If the LLM calls the wrong tool:
- Use **explicit commands**: "Read all tag values" instead of "read tags"
- The tool descriptions have been improved to help with this
- Consider using a larger model like `qwen3:8b` for better accuracy

## Switching Between MOCK and LIVE

- **MOCK mode** (default): `ollama_host.py`
- **LIVE mode**: `ollama_host_live.py`

Both use the same tools, just different data sources.
