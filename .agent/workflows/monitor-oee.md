---
description: Automated OEE performance check and shift report generation.
---

# Workflow: Shift OEE Monitoring

This workflow performs a recurring check of the PLC's OEE metrics and generates an artifact report.

## Steps

1. **Fetch Data**
   // turbo
   Use the `read_all_oee_tags` tool to get the latest snapshot.

2. **Analyze Trends**
   Compare `fOEE_Overall` against the shift target (85%).

3. **Check Faults**
   If `Global.bMachineInFault` is TRUE, perform a `list_plc_tags` to find any specific error strings.

4. **Generate Artifact**
   Create a markdown report (`shift_report.md`) summarizing:
   - Current OEE Performance.
   - Total Parts vs Target.
   - Any active downtime incidents.

5. **Log to Changelog**
   // turbo
   Update `changelog.md` using the `changelog` skill to note that a monitoring cycle was completed.
