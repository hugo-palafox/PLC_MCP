"""
Dashboard Preview Generator
Creates an HTML visualization of the Grafana dashboard without needing Grafana.
"""
import json
from pathlib import Path

def generate_html_preview(dashboard_json_path):
    """Generate an HTML preview of a Grafana dashboard."""
    
    with open(dashboard_json_path, 'r') as f:
        dashboard = json.load(f)
    
    title = dashboard.get('title', 'Dashboard')
    panels = dashboard.get('panels', [])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title} - Preview</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0b0c0e;
            color: #d8d9da;
            margin: 0;
            padding: 20px;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #fff;
            margin-bottom: 30px;
        }}
        .panel-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .panel {{
            background: #181b1f;
            border: 1px solid #2d3035;
            border-radius: 4px;
            padding: 15px;
            min-height: 150px;
        }}
        .panel-title {{
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 10px;
            color: #d8d9da;
        }}
        .panel-type {{
            font-size: 11px;
            color: #6e7781;
            margin-bottom: 10px;
        }}
        .panel-content {{
            font-size: 32px;
            font-weight: 300;
            color: #52c41a;
            margin-top: 20px;
        }}
        .gauge {{
            width: 100%;
            height: 120px;
            background: linear-gradient(90deg, #52c41a 0%, #faad14 50%, #f5222d 100%);
            border-radius: 60px 60px 0 0;
            position: relative;
            margin-top: 20px;
        }}
        .gauge::after {{
            content: 'OEE';
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            color: #6e7781;
        }}
        .timeseries {{
            width: 100%;
            height: 120px;
            background: linear-gradient(180deg, rgba(82, 196, 26, 0.2) 0%, transparent 100%);
            border-bottom: 2px solid #52c41a;
            position: relative;
            margin-top: 20px;
        }}
        .timeseries::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: #2d3035;
        }}
        .stat {{
            font-size: 48px;
            font-weight: 200;
            color: #1890ff;
            text-align: center;
            margin-top: 30px;
        }}
        .targets {{
            background: #0d1117;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 11px;
            color: #6e7781;
        }}
        .wide {{
            grid-column: span 4;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>{title}</h1>
        <div class="panel-grid">
"""
    
    for panel in panels:
        panel_title = panel.get('title', 'Untitled')
        panel_type = panel.get('type', 'unknown')
        targets = panel.get('targets', [])
        grid_pos = panel.get('gridPos', {})
        
        # Determine panel width
        width = grid_pos.get('w', 6)
        is_wide = width >= 12
        
        html += f'<div class="panel {"wide" if is_wide else ""}">\n'
        html += f'  <div class="panel-title">{panel_title}</div>\n'
        html += f'  <div class="panel-type">Type: {panel_type}</div>\n'
        
        # Render based on panel type
        if panel_type == 'gauge':
            html += '  <div class="gauge"></div>\n'
        elif panel_type == 'stat':
            html += '  <div class="stat">--</div>\n'
        elif panel_type == 'timeseries':
            html += '  <div class="timeseries"></div>\n'
        
        # Show targets
        if targets:
            html += '  <div class="targets">\n'
            for target in targets:
                expr = target.get('expr', 'N/A')
                html += f'    <div>Query: {expr}</div>\n'
            html += '  </div>\n'
        
        html += '</div>\n'
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html

if __name__ == "__main__":
    # Generate preview for Testing_Machine dashboard
    dashboard_path = Path("dashboards/Testing_Machine_dashboard.json")
    
    if not dashboard_path.exists():
        print("Dashboard not found. Generating...")
        import subprocess
        subprocess.run([".venv/Scripts/python.exe", "dashboard_generator.py"])
    
    html = generate_html_preview(dashboard_path)
    
    preview_path = Path("dashboards/Testing_Machine_preview.html")
    with open(preview_path, 'w') as f:
        f.write(html)
    
    print(f"Preview generated: {preview_path}")
    print(f"Open in browser: file:///{preview_path.absolute()}")
