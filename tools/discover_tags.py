import json
from drivers.beckhoff import TwinCATDriver

def discover_tags():
    with open('tags.json', 'r') as f:
        config = json.load(f)
    
    ams_id = config.get("AMS_NET_ID", "199.4.42.250.1.1")
    
    print(f"--- PLC DISCOVERY ---")
    print(f"Target AMS NetID: {ams_id}")
    
    driver = TwinCATDriver(ams_id)
    
    if not driver.connect():
        print("CRITICAL: Connection failed.")
        return

    try:
        print("Fetching all available symbols...")
        symbols = driver.list_all_tags()
        print(f"Discovered {len(symbols)} symbols.")
        
        # Display first 20 symbols to help debug naming
        print("\nFirst 20 symbols (to check naming convention):")
        for s in symbols[:20]:
            print(f" - {s['name']} ({s['type']})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.disconnect()

if __name__ == "__main__":
    discover_tags()
