import os
import json
import logging
import time
import sys
from pathlib import Path
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP
from drivers.beckhoff import TwinCATDriver
from drivers.mock import MockDriver
from drivers.base import BasePLC
from dashboard_generator import generate_industrial_dashboard
from ai_dashboard_generator import AIDashboardGenerator

# Configuration Paths
BASE_DIR = Path(r"c:\Users\hugod\Documents\Projects\PLC_MCP\Core")
SETTINGS_DIR = BASE_DIR / "plc_settings"

# Setup logging - ALWAYS to stderr for MCP protocol compliance
# We do not use logging.basicConfig() at the top level to avoid polluting stdout
# if a misconfigured library or older python version behaves unexpectedly.
logger = logging.getLogger("plc-bridge")
logger.setLevel(logging.INFO)

# Initializer for logging (called in main)
def setup_logging():
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Optional file logger
    try:
        file_handler = logging.FileHandler(BASE_DIR / "plc_bridge_startup.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

# Initialize FastMCP server
mcp = FastMCP("PLC-Bridge")
USE_MOCK = os.getenv("PLC_MODE", "LIVE").upper() == "MOCK"

# Default machine to load if none specified in environment
DEFAULT_MACHINE = os.getenv("PLC_MACHINE", "Testing_Machine")

def load_config(machine_name: str = DEFAULT_MACHINE) -> Dict[str, Any]:
    """Helper to load machine-specific config from plc_settings/ safely."""
    config_path = SETTINGS_DIR / f"{machine_name}.json"
    try:
        if config_path.exists():
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            logger.warning(f"Config for machine '{machine_name}' not found at {config_path}")
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
    return {}

def get_driver(machine_name: str = DEFAULT_MACHINE) -> BasePLC:
    """Factory to get the correct driver based on configuration."""
    config = load_config(machine_name)
    machine_type = config.get("Type", "Unknown")
    
    if USE_MOCK:
        logger.info(f"Initializing MockDriver for {machine_name}...")
        driver = MockDriver()
    else:
        # Get IP Address from config or environment
        base_ip = config.get("IP_Address", os.getenv("PLC_IP", "199.4.42.250"))
        
        # If it's a Beckhoff PLC, automatically add .1.1 suffix for AMS Net ID logic
        if machine_type.lower() == "beckhoff" and not base_ip.endswith(".1.1"):
            ams_id = f"{base_ip}.1.1"
            logger.info(f"Beckhoff detected: Appending .1.1 suffix to {base_ip} -> {ams_id}")
        else:
            ams_id = base_ip
            
        logger.info(f"Initializing TwinCATDriver for machine '{machine_name}' at {ams_id}...")
        driver = TwinCATDriver(ams_id)
    
    if not driver.connect():
        error_msg = f"Failed to connect to PLC (Machine: {machine_name}, Mode: {'MOCK' if USE_MOCK else 'LIVE'})"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    
    return driver

@mcp.tool()
def list_machines() -> List[Dict[str, Any]]:
    """List all available machines/PLCs configured in the system."""
    machines = []
    try:
        if not SETTINGS_DIR.exists():
            return []
        for config_file in SETTINGS_DIR.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    machines.append({
                        "id": config_file.stem,
                        "name": config.get("MachineName", config_file.stem),
                        "type": config.get("Type", "Unknown"),
                        "ip": config.get("IP_Address", "Unknown")
                    })
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Error listing machines: {e}")
    return machines

@mcp.tool()
def list_plc_tags(machine_name: str = DEFAULT_MACHINE, filter_match: str = None) -> Dict[str, Any]:
    """
    List available PLC tag NAMES and types (does NOT read values).
    Use this to discover what tags exist. To read actual values, use read_plc_tag or read_all_oee_tags.
    
    :param machine_name: The name of the machine (e.g., 'Testing_Machine').
    :param filter_match: Optional substring to filter tags (e.g., 'Global', 'OEE').
    """
    config = load_config(machine_name)
    driver = get_driver(machine_name)
    try:
        logger.info(f"Listing PLC tags for {machine_name} (filter: {filter_match})...")
        all_tags = driver.list_all_tags()
        
        if filter_match:
            match_lower = filter_match.lower()
            filtered_tags = [t for t in all_tags if match_lower in t['name'].lower()]
        else:
            filtered_tags = all_tags

        return {
            "MachineName": config.get("MachineName", machine_name),
            "Type": config.get("Type", "Unknown"),
            "TotalCount": len(all_tags),
            "FilteredCount": len(filtered_tags),
            "Tags": filtered_tags
        }
    finally:
        driver.disconnect()

@mcp.tool()
def read_plc_tag(tag_path: str, machine_name: str = DEFAULT_MACHINE) -> Any:
    """
    Read the current value of a specific PLC tag.
    
    :param tag_path: The full TwinCAT path to the tag (e.g., 'Global.bMachineRunning').
    :param machine_name: The machine to read from.
    """
    driver = get_driver(machine_name)
    try:
        value = driver.read_tag(tag_path)
        logger.info(f"Read tag '{tag_path}' from {machine_name}: {value}")
        return value
    except Exception as e:
        logger.error(f"Error reading tag '{tag_path}' from {machine_name}: {e}")
        return {"error": str(e)}
    finally:
        driver.disconnect()

@mcp.tool()
def read_all_oee_tags(machine_name: str = DEFAULT_MACHINE) -> Dict[str, Any]:
    """
    Read the ACTUAL VALUES of all OEE and Machine Status tags at once.
    Use this when the user asks to 'read all tags' or 'show me all values'.
    This is the most efficient way to get all tag values in one call.
    """
    config = load_config(machine_name)
    tags_dict = config.get("Tags", {})
    if not tags_dict:
        return {"error": f"No tags defined in machine configuration for '{machine_name}'"}
    
    tag_names = list(tags_dict.keys())
    driver = get_driver(machine_name)
    try:
        logger.info(f"Batch reading {len(tag_names)} OEE tags for {config.get('MachineName')}...")
        return {
            "MachineName": config.get("MachineName"),
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Data": driver.read_tags(tag_names)
        }
    finally:
        driver.disconnect()

@mcp.tool()
def generate_dashboard(machine_name: str = DEFAULT_MACHINE, use_ai: bool = True) -> Dict[str, Any]:
    """
    Generate a Grafana dashboard JSON for a specific machine.
    
    :param machine_name: The name of the machine to generate the dashboard for.
    :param use_ai: If True (default), use AI to intelligently generate dashboard. If False, use template.
    """
    config = load_config(machine_name)
    if not config:
        return {"error": f"Machine '{machine_name}' not found."}
    
    tags_config = config.get("Tags", {})
    try:
        if use_ai:
            logger.info(f"Generating AI-powered dashboard for {machine_name}...")
            ai_generator = AIDashboardGenerator()
            dashboard_json = ai_generator.generate_dashboard(machine_name, tags_config)
            filename_prefix = "AI"
        else:
            logger.info(f"Generating template-based dashboard for {machine_name}...")
            dashboard_json = generate_industrial_dashboard(machine_name, tags_config)
            filename_prefix = ""
        
        # Save to a file for convenience
        filename = f"{filename_prefix}_{machine_name}_dashboard.json" if filename_prefix else f"{machine_name}_dashboard.json"
        output_file = BASE_DIR / "dashboards" / filename
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, "w") as f:
            f.write(dashboard_json)
            
        return {
            "message": f"{'AI-powered' if use_ai else 'Template-based'} dashboard generated successfully for {machine_name}",
            "file_path": str(output_file),
            "mode": "AI" if use_ai else "Template",
            "dashboard_json": json.loads(dashboard_json)
        }
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Configure logging
    setup_logging()
    
    config = load_config()
    logger.info(f"Starting PLC-Bridge FastMCP Server")
    logger.info(f"Active Machine: {config.get('MachineName', 'Unknown')}")
    logger.info(f"Mode: {'MOCK' if USE_MOCK else 'LIVE'}")
    
    # Run the server
    mcp.run()
