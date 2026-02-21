# Rule: PLC Safety, Integrity & Interpretation Guardrails

## 1. Data Integrity & Privacy
- **Scope:** All tasks involving the `industrial-plc-bridge` MCP server.
- **Constraint:** Never attempt to guess or hallucinate a 'write' command.
- **Validation:** When reading tags, always cross-reference the value with the status code returned by ADS.
- **Privacy:** Do not log raw PLC memory addresses; only use symbolic names (e.g., Global.fTemperature).

## 2. Safety-Critical States
- **Fault Monitoring:** If `Global.bMachineInFault` is `TRUE`, the agent must immediately prioritize identifying the cause by checking related sensors.
- **E-Stop Awareness:** Never suggest "restarting" or "resetting" a machine if a fault is active.
- **Read-Only Verification:** The agent shall never attempt to construct a write command.

## 2. OEE Interpretation Rules
- **Availability:** If `fOEE_Availability` drops below 80%, suggest checking `fDownTimeUnplanned` for recent spikes.
- **Performance:** Analyze `fCurrentCycleTime` vs `fIdealCycleTime` (1.5s). If the actual is > 2.0s, flag a possible mechanical slowdown.
- **Quality:** If `nRejectedParts` increases by more than 5 in an hour, recommend a quality inspection.

## 3. Communication Standards
- **Real-Time Context:** Always mention the last update timestamp when reporting values.
- **Clarity:** Use human-friendly terms (e.g., "The machine has stopped" vs "Global.bMachineRunning is false").
