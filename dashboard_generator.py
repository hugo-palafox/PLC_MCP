import json
import os
from pathlib import Path
from grafanalib.core import (
    Dashboard, TimeSeries, GaugePanel, 
    Target, GridPos, RowPanel, Stat
)
from grafanalib._gen import DashboardEncoder

def generate_industrial_dashboard(machine_name, tags_config):
    """
    Generates a Grafana Dashboard JSON using grafanalib.
    
    :param machine_name: Name of the machine
    :param tags_config: Dictionary of tags from the machine JSON config
    """
    
    panels = []
    
    # Row 1: OEE and Status Gauges
    # We'll look for specific tags like OEE, RunTime, etc.
    
    y_pos = 0
    
    # OEE Gauge
    panels.append(GaugePanel(
        title="Overall OEE",
        gridPos=GridPos(h=8, w=6, x=0, y=y_pos),
        targets=[Target(expr='Global.fOEE_Overall')], # This is a placeholder for real prometheus/influx queries
        description="Current OEE for the machine"
    ))
    
    # Production Count Stat
    panels.append(Stat(
        title="Total Produced",
        gridPos=GridPos(h=4, w=6, x=6, y=y_pos),
        targets=[Target(expr='Global.nTotalPartsProduced')],
        format="none",
    ))
    
    panels.append(Stat(
        title="Good Parts",
        gridPos=GridPos(h=4, w=6, x=6, y=y_pos + 4),
        targets=[Target(expr='Global.nGoodPartsProduced')],
        format="none",
    ))
    
    # Status Row
    y_pos += 8
    panels.append(TimeSeries(
        title="Production Rate Over Time",
        gridPos=GridPos(h=8, w=24, x=0, y=y_pos),
        targets=[Target(expr='rate(Global.nTotalPartsProduced[5m])')],
    ))

    dashboard = Dashboard(
        title=f"Industrial Dashboard - {machine_name}",
        panels=panels,
    ).auto_panel_ids()
    
    return json.dumps(dashboard, cls=DashboardEncoder, indent=4)

if __name__ == "__main__":
    # Test generation
    test_tags = {
        "Global.fOEE_Overall": {"description": "OEE"},
        "Global.nTotalPartsProduced": {"description": "Total"}
    }
    print(generate_industrial_dashboard("Testing_Machine", test_tags))
