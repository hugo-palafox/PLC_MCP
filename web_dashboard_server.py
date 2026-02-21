from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import time
import threading
import os
import json
from pathlib import Path
from drivers.beckhoff import TwinCATDriver
from drivers.mock import MockDriver
from ai_viz_generator import AIVisualizationGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("plc-bridge.web-dashboard")

# Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# PLC Configuration
USE_MOCK = os.getenv("PLC_MODE", "LIVE").upper() == "MOCK"
PLC_IP = "199.4.42.250"

# Store current machine per session
active_machines = {}  # {session_id: machine_id}

# Initialize AI generator
ai_viz_gen = AIVisualizationGenerator()

def get_available_machines():
    """Get list of available machine configurations."""
    settings_dir = Path(__file__).parent / "plc_settings"
    machines = []
    
    for config_file in settings_dir.glob("*.json"):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                machines.append({
                    'id': config_file.stem,
                    'name': config.get('MachineName', config_file.stem),
                    'type': config.get('Type', 'Unknown')
                })
        except Exception as e:
            logger.error(f"Error loading {config_file}: {e}")
    
    return sorted(machines, key=lambda x: x['name'])

def get_plc_driver():
    """Get PLC driver instance."""
    if USE_MOCK:
        driver = MockDriver()
    else:
        driver = TwinCATDriver(f"{PLC_IP}.1.1")
    
    if not driver.connect():
        logger.error("Failed to connect to PLC")
        return None
    return driver

def load_machine_config(machine_id='Testing_Machine'):
    """Load machine configuration by ID."""
    config_path = Path(__file__).parent / "plc_settings" / f"{machine_id}.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config for {machine_id}: {e}")
        return {"Tags": {}}

@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')

@app.route('/api/machines', methods=['GET'])
def get_machines():
    """Get list of available machines."""
    try:
        machines = get_available_machines()
        return jsonify({'machines': machines})
    except Exception as e:
        logger.error(f"Error getting machines: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate AI visualizations."""
    try:
        user_message = request.json.get('message', '')
        machine_id = request.json.get('machine_id', 'Testing_Machine')
        logger.info(f"Received message: '{user_message}' for machine: {machine_id}")
        
        driver = get_plc_driver()
        if not driver:
            return jsonify({
                'response': 'Error: Could not connect to PLC',
                'error': 'PLC connection failed'
            }), 500
        
        try:
            config = load_machine_config(machine_id)
            tags = config.get('Tags', {})
            
            # Read all tags (including arrays)
            data = {}
            for tag_name, tag_meta in tags.items():
                try:
                    if tag_meta.get('is_array', False):
                        plc_type = driver._get_plc_type(tag_meta['type'])
                        array_size = tag_meta.get('array_size', 1)
                        data[tag_name] = driver.read_array(tag_name, plc_type, array_size)
                    else:
                        data[tag_name] = driver.read_tag(tag_name)
                except Exception as e:
                    logger.warning(f"Failed to read {tag_name}: {e}")
                    data[tag_name] = None
            
            # Prepare metrics data for AI
            metrics_data = {}
            for tag_name, tag_meta in tags.items():
                description = tag_meta.get('description', tag_name)
                metrics_data[description] = {
                    'value': data.get(tag_name),
                    'type': tag_meta.get('type'),
                    'tag': tag_name,
                    'is_array': tag_meta.get('is_array', False)
                }
            
            # Generate AI visualization
            try:
                viz_code = ai_viz_gen.generate_visualization(user_message, metrics_data)
                
                return jsonify({
                    'response': f'Generated visualization for: {user_message}',
                    'ai_visualization': viz_code,
                    'metrics_data': metrics_data,  # Include raw data for template replacement
                    'use_ai': True
                })
            except Exception as e:
                logger.error(f"AI visualization generation failed: {e}")
                return jsonify({
                    'response': f'Error generating visualization: {str(e)}',
                    'error': str(e)
                }), 500
            
        finally:
            driver.disconnect()
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': 'An error occurred',
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    session_id = request.sid
    active_machines[session_id] = 'Testing_Machine'  # Default machine
    logger.info(f'Client {session_id} connected')
    emit('connected', {'data': 'Connected to PLC Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = request.sid
    if session_id in active_machines:
        del active_machines[session_id]
    logger.info(f'Client {session_id} disconnected')

@socketio.on('select_machine')
def handle_machine_selection(data):
    """Handle machine selection from client."""
    session_id = request.sid
    machine_id = data.get('machine_id', 'Testing_Machine')
    active_machines[session_id] = machine_id
    logger.info(f"Client {session_id} selected machine: {machine_id}")
    emit('machine_selected', {'machine_id': machine_id})

if __name__ == '__main__':
    logger.info(f"Starting PLC Dashboard Server (Mode: {'MOCK' if USE_MOCK else 'LIVE'})")
    logger.info("Dashboard available at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
