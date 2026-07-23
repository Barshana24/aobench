# Marconi100 Cooling Runbook

## Metrics
- `ambient` (ipmi) — node inlet (intake) air temperature (°C)
- `Supply_Air_Temperature` (vertiv) — CRAC supply (cold) air temperature (°C)
- `Return_Air_Temperature` (vertiv) — CRAC return (warm) air temperature (°C)

## Normal ranges (per real M100 telemetry)
- Inlet (ambient): 18–26°C
- Warning: >28°C
- Critical: >32°C

## Single-node vs rack-wide
- ONE node's ambient rising → node-local airflow blockage; drain that node.
- ALL nodes in a rack rising together → cooling-unit fault feeding that rack.
  Escalate to facilities; do not drain individual nodes.

## Response (rack-wide)
1. Confirm `ambient` is elevated across the whole rack, not one node.
2. Check the cooling unit / liquid loop serving that rack.
3. Reduce rack load if inlet approaches 32°C while cooling is restored.
