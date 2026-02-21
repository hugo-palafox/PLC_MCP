// WebSocket connection
const socket = io();

// DOM elements
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const responseArea = document.getElementById('responseArea');
const metricsGrid = document.getElementById('metricsGrid');
const statusText = document.getElementById('statusText');
const connectionStatus = document.getElementById('connectionStatus');
const welcomeMessage = document.querySelector('.welcome-message');
const machineSelect = document.getElementById('machineSelect');

// Current machine
let currentMachine = 'Testing_Machine';

// Connection status
socket.on('connect', () => {
    console.log('Connected to server');
    statusText.textContent = 'Connected to PLC';
    connectionStatus.querySelector('.status-dot').classList.remove('disconnected');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    statusText.textContent = 'Disconnected';
    connectionStatus.querySelector('.status-dot').classList.add('disconnected');
});

// Machine selection confirmed
socket.on('machine_selected', (data) => {
    console.log('Machine selected:', data.machine_id);
});

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    sendBtn.innerHTML = '<div class="loading"></div>';
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message,
                machine_id: currentMachine
            })
        });

        const data = await response.json();

        // Show response
        responseArea.textContent = data.response;
        responseArea.classList.add('visible');

        // Render AI-generated visualization
        if (data.use_ai && data.ai_visualization) {
            hideWelcome();
            renderAIVisualization(data.ai_visualization, data.metrics_data || {});
        } else if (data.error) {
            showError(data.error);
        }

    } catch (error) {
        console.error('Error:', error);
        responseArea.textContent = 'Error: Could not communicate with server';
        responseArea.classList.add('visible');
    } finally {
        sendBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>`;
        sendBtn.disabled = false;
        userInput.value = '';
    }
}

function renderAIVisualization(vizCode, metricsData) {
    console.log('Rendering AI visualization:', vizCode);
    console.log('Metrics data:', metricsData);

    // Clear existing content
    metricsGrid.innerHTML = '';

    // Create container for AI-generated code
    const vizContainer = document.createElement('div');
    vizContainer.className = 'ai-generated-viz';

    // Inject HTML with template replacement
    if (vizCode.html) {
        let html = vizCode.html;

        // Replace template variables like {{ data.Global2.fOEE_Overall.toFixed(4) }}
        html = html.replace(/\{\{\s*data\.([^}]+)\s*\}\}/g, (match, path) => {
            // Parse the path to get metric name and method calls
            const parts = path.split('.');
            let value = null;

            // Try to find the metric in metricsData
            for (const [metricName, metricInfo] of Object.entries(metricsData)) {
                if (path.includes(metricName) || metricName.includes(parts[0])) {
                    value = metricInfo.value;
                    break;
                }
            }

            // If not found, try direct path match
            if (value === null && parts.length > 0) {
                const searchKey = parts[parts.length - 2]; // e.g., "fOEE_Overall"
                for (const [metricName, metricInfo] of Object.entries(metricsData)) {
                    if (metricName.includes(searchKey) || metricInfo.tag?.includes(searchKey)) {
                        value = metricInfo.value;
                        break;
                    }
                }
            }

            // Format the value
            if (value !== null && value !== undefined) {
                // Check if path includes toFixed
                const toFixedMatch = path.match(/toFixed\((\d+)\)/);
                if (toFixedMatch && typeof value === 'number') {
                    return value.toFixed(parseInt(toFixedMatch[1]));
                }
                return value;
            }

            return `<span class="data-placeholder" title="${path}">N/A</span>`;
        });

        vizContainer.innerHTML = html;
    }

    // Inject CSS
    if (vizCode.css) {
        const style = document.createElement('style');
        style.textContent = vizCode.css;
        style.setAttribute('data-ai-generated', 'true');
        document.head.appendChild(style);
    }

    // Add to DOM first
    metricsGrid.appendChild(vizContainer);

    // Execute JavaScript (if any)
    if (vizCode.js) {
        try {
            console.log('Executing AI-generated JavaScript');
            // Create safe execution context with metricsData available
            const executeAICode = new Function('vizContainer', 'metricsData', vizCode.js);
            executeAICode(vizContainer, metricsData);
        } catch (error) {
            console.error('Error executing AI-generated JavaScript:', error);
            vizContainer.innerHTML += `
                <div class="error-message">
                    <h3>⚠️ Visualization Error</h3>
                    <p>Failed to render AI-generated visualization</p>
                    <pre>${error.message}</pre>
                </div>
            `;
        }
    }
}

function showError(errorMessage) {
    metricsGrid.innerHTML = `
        <div class="error-container">
            <div class="error-icon">⚠️</div>
            <h2>Error</h2>
            <p>${errorMessage}</p>
        </div>
    `;
}

function hideWelcome() {
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
}

// Load available machines
async function loadMachines() {
    try {
        const response = await fetch('/api/machines');
        const data = await response.json();

        if (data.machines && data.machines.length > 0) {
            machineSelect.innerHTML = '';

            data.machines.forEach(machine => {
                const option = document.createElement('option');
                option.value = machine.id;
                option.textContent = `${machine.name} (${machine.type})`;
                machineSelect.appendChild(option);
            });

            // Set default
            currentMachine = data.machines[0].id;
            machineSelect.value = currentMachine;

            console.log(`Loaded ${data.machines.length} machines`);
        }
    } catch (error) {
        console.error('Error loading machines:', error);
    }
}

// Handle machine selection change
machineSelect?.addEventListener('change', (e) => {
    currentMachine = e.target.value;
    socket.emit('select_machine', { machine_id: currentMachine });

    // Clear dashboard and show welcome
    metricsGrid.innerHTML = '';
    if (welcomeMessage) {
        welcomeMessage.style.display = 'block';
    }

    // Remove AI-generated styles
    document.querySelectorAll('style[data-ai-generated]').forEach(style => style.remove());

    console.log(`Switched to machine: ${currentMachine}`);
});

// Handle Enter key
userInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Suggestion button helper
function askQuestion(question) {
    userInput.value = question;
    sendMessage();
}

// Load on page ready
document.addEventListener('DOMContentLoaded', () => {
    loadMachines();
    console.log('AI-powered dashboard loaded');
});
