import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import ollama
from grafanalib.core import (
    Dashboard, TimeSeries, GaugePanel, 
    Target, GridPos, Stat, StateTimeline
)
from grafanalib._gen import DashboardEncoder

logger = logging.getLogger("ai-dashboard-generator")

class AIDashboardGenerator:
    """AI-powered dashboard generator using DeepSeek LLM for intelligent panel selection and layout."""
    
    def __init__(self, model: str = "deepseek-r1:latest"):
        self.model = model
        self.client = ollama.Client(host='http://127.0.0.1:11434', timeout=120)
        
    def analyze_tags(self, tags_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use DeepSeek to analyze PLC tags and suggest optimal panel configurations.
        
        :param tags_dict: Dictionary of tags with their metadata
        :return: AI analysis with panel recommendations
        """
        # Prepare tag information for AI analysis
        tag_info = []
        for tag_name, tag_meta in tags_dict.items():
            tag_info.append({
                "name": tag_name,
                "type": tag_meta.get("type", "UNKNOWN"),
                "description": tag_meta.get("description", "")
            })
        
        prompt = f"""You are an industrial automation dashboard expert. Analyze these PLC tags and design an optimal Grafana dashboard layout.

PLC Tags:
{json.dumps(tag_info, indent=2)}

For each tag, determine:
1. **Panel type**: Choose from:
   - "gauge" (for percentages, ratios, 0-100 values like OEE)
   - "stat" (for counters, totals, current values)
   - "timeseries" (for trends over time, rates)
   - "statetimeline" (for boolean/status values)

2. **Panel title**: Human-readable name (not the raw tag path)

3. **Size**: 
   - width: 1-24 (Grafana uses 24-column grid)
   - height: 4-12 (typical panel heights)

4. **Priority**: 1-10 (10 = most important, should be at top)

5. **Category**: Group similar metrics (e.g., "oee", "production", "quality", "status", "performance")

6. **Thresholds** (for gauges): Array of threshold values if applicable

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "panels": [
    {{
      "tag": "exact.tag.name",
      "type": "gauge",
      "title": "Human Readable Title",
      "width": 8,
      "height": 8,
      "priority": 10,
      "category": "oee",
      "thresholds": [0.7, 0.85]
    }}
  ],
  "layout_strategy": "priority_based"
}}"""

        try:
            logger.info(f"Analyzing {len(tag_info)} tags with DeepSeek...")
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Grafana dashboard expert. Return only valid JSON, no markdown formatting, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                format="json"  # Request JSON output
            )
            
            # Extract JSON from response
            content = response['message']['content']
            
            # Parse the AI response
            ai_analysis = json.loads(content)
            logger.info(f"AI analysis complete: {len(ai_analysis.get('panels', []))} panels suggested")
            return ai_analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to basic analysis
            return self._fallback_analysis(tags_dict)
    
    def _fallback_analysis(self, tags_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based fallback if AI fails."""
        panels = []
        priority = 10
        
        for tag_name, tag_meta in tags_dict.items():
            tag_type = tag_meta.get("type", "").upper()
            description = tag_meta.get("description", tag_name)
            
            # Simple heuristics
            if "OEE" in tag_name.upper() or "EFFICIENCY" in tag_name.upper():
                panel_type = "gauge"
                width, height = 8, 8
                category = "oee"
            elif "BOOL" in tag_type or "STATUS" in tag_name.upper():
                panel_type = "statetimeline"
                width, height = 12, 4
                category = "status"
            elif "TOTAL" in tag_name.upper() or "COUNT" in tag_name.upper():
                panel_type = "stat"
                width, height = 6, 4
                category = "production"
            else:
                panel_type = "timeseries"
                width, height = 12, 6
                category = "other"
            
            panels.append({
                "tag": tag_name,
                "type": panel_type,
                "title": description,
                "width": width,
                "height": height,
                "priority": priority,
                "category": category,
                "thresholds": [0.7, 0.85] if panel_type == "gauge" else []
            })
            priority = max(1, priority - 1)
        
        return {"panels": panels, "layout_strategy": "priority_based"}
    
    def _create_panel(self, panel_config: Dict[str, Any]) -> Any:
        """Create a Grafana panel based on AI configuration."""
        panel_type = panel_config["type"]
        tag = panel_config["tag"]
        title = panel_config["title"]
        width = panel_config["width"]
        height = panel_config["height"]
        
        # Grid position will be set later during layout
        grid_pos = GridPos(h=height, w=width, x=0, y=0)
        
        if panel_type == "gauge":
            return GaugePanel(
                title=title,
                gridPos=grid_pos,
                targets=[Target(expr=tag)],
                description=f"Gauge for {tag}"
            )
        elif panel_type == "stat":
            return Stat(
                title=title,
                gridPos=grid_pos,
                targets=[Target(expr=tag)],
                format="none"
            )
        elif panel_type == "timeseries":
            return TimeSeries(
                title=title,
                gridPos=grid_pos,
                targets=[Target(expr=tag)]
            )
        elif panel_type == "statetimeline":
            return StateTimeline(
                title=title,
                gridPos=grid_pos,
                targets=[Target(expr=tag)]
            )
        else:
            # Default to stat
            return Stat(
                title=title,
                gridPos=grid_pos,
                targets=[Target(expr=tag)],
                format="none"
            )
    
    def _optimize_layout(self, panel_configs: List[Dict[str, Any]]) -> List[Any]:
        """
        Optimize panel layout based on priority and category.
        Returns list of panels with optimized grid positions.
        """
        # Sort by priority (highest first)
        sorted_configs = sorted(panel_configs, key=lambda p: p["priority"], reverse=True)
        
        panels = []
        current_y = 0
        current_x = 0
        row_height = 0
        
        for config in sorted_configs:
            width = config["width"]
            height = config["height"]
            
            # Check if panel fits in current row
            if current_x + width > 24:
                # Move to next row
                current_y += row_height
                current_x = 0
                row_height = 0
            
            # Create panel with optimized position
            panel = self._create_panel(config)
            panel.gridPos = GridPos(h=height, w=width, x=current_x, y=current_y)
            panels.append(panel)
            
            # Update position tracking
            current_x += width
            row_height = max(row_height, height)
        
        return panels
    
    def generate_dashboard(self, machine_name: str, tags_dict: Dict[str, Any]) -> str:
        """
        Generate a complete Grafana dashboard JSON using AI analysis.
        
        :param machine_name: Name of the machine
        :param tags_dict: Dictionary of tags with metadata
        :return: Dashboard JSON string
        """
        logger.info(f"Generating AI-powered dashboard for {machine_name}...")
        
        # Step 1: AI analyzes tags
        ai_analysis = self.analyze_tags(tags_dict)
        
        # Step 2: Create panels with optimized layout
        panel_configs = ai_analysis.get("panels", [])
        panels = self._optimize_layout(panel_configs)
        
        # Step 3: Create dashboard
        dashboard = Dashboard(
            title=f"AI-Generated Dashboard - {machine_name}",
            panels=panels,
            tags=["ai-generated", "industrial", machine_name.lower()],
            refresh="5s",
            timezone="browser"
        ).auto_panel_ids()
        
        # Step 4: Convert to JSON
        dashboard_json = json.dumps(dashboard, cls=DashboardEncoder, indent=2)
        
        logger.info(f"Dashboard generated with {len(panels)} panels")
        return dashboard_json


def test_ai_generator():
    """Test the AI dashboard generator with sample tags."""
    test_tags = {
        "Global.fOEE_Overall": {
            "type": "REAL",
            "description": "Overall Equipment Effectiveness"
        },
        "Global.nTotalPartsProduced": {
            "type": "DINT",
            "description": "Total Parts Produced"
        },
        "Global.nGoodPartsProduced": {
            "type": "DINT",
            "description": "Good Parts Count"
        },
        "Global.bMachineRunning": {
            "type": "BOOL",
            "description": "Machine Running Status"
        },
        "Global.fProductionRate": {
            "type": "REAL",
            "description": "Current Production Rate"
        }
    }
    
    generator = AIDashboardGenerator()
    dashboard_json = generator.generate_dashboard("Testing_Machine", test_tags)
    
    # Save to file
    output_path = Path(__file__).parent / "dashboards" / "AI_Testing_Machine_dashboard.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        f.write(dashboard_json)
    
    print(f"✅ AI Dashboard generated: {output_path}")
    print(f"Dashboard preview:\n{dashboard_json[:500]}...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_ai_generator()
