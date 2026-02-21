"""
Quick test to verify PLC connectivity before running the full host.
"""
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(r"c:\Users\hugod\Documents\Projects\PLC_MCP\Core")
sys.path.insert(0, str(BASE_DIR))

from drivers.beckhoff import TwinCATDriver
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plc-test")

def test_plc_connection():
    """Test connection to the real PLC."""
    plc_ip = "199.4.42.250"
    ams_id = f"{plc_ip}.1.1"
    
    logger.info(f"Testing connection to PLC at {ams_id}...")
    
    driver = TwinCATDriver(ams_id)
    
    if not driver.connect():
        logger.error("❌ Failed to connect to PLC!")
        logger.error("Possible issues:")
        logger.error("  1. TwinCAT ADS server not running on the PLC")
        logger.error("  2. Network connectivity issue (firewall, routing)")
        logger.error("  3. Incorrect AMS Net ID or IP address")
        return False
    
    logger.info("✅ Successfully connected to PLC!")
    
    # Try to list tags
    try:
        logger.info("Attempting to list tags...")
        tags = driver.list_all_tags()
        logger.info(f"✅ Found {len(tags)} tags on the PLC")
        
        # Show first 5 tags
        logger.info("First 5 tags:")
        for tag in tags[:5]:
            logger.info(f"  - {tag['name']} ({tag['type']})")
            
    except Exception as e:
        logger.error(f"❌ Failed to list tags: {e}")
        driver.disconnect()
        return False
    
    # Try to read a tag
    try:
        if tags:
            test_tag = tags[0]['name']
            logger.info(f"Attempting to read tag: {test_tag}")
            value = driver.read_tag(test_tag)
            logger.info(f"✅ Read value: {value}")
    except Exception as e:
        logger.error(f"❌ Failed to read tag: {e}")
    
    driver.disconnect()
    logger.info("✅ All tests passed! You can now use LIVE mode.")
    return True

if __name__ == "__main__":
    success = test_plc_connection()
    sys.exit(0 if success else 1)
