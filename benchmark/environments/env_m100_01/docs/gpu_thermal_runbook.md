# Marconi100 GPU Thermal Runbook

## IPMI thermal metrics (ipmi_pub plugin)
- `gpuN_core_temp` — GPU N core temperature (°C); N ∈ {0, 1, 3, 4}
- `gpuN_mem_temp`  — GPU N HBM2 memory temperature (°C)
- `ambient`        — node inlet temperature (°C)
- `fanX_Y`         — chassis fan speed (RPM)

## Normal ranges (per real M100 telemetry)
- GPU core temp: 30–70°C under load
- Throttle threshold: 84°C (Volta GV100 thermal slowdown)
- Critical: 90°C

## Response
1. Query telemetry for `gpuN_core_temp` across the rack.
2. The node whose GPU exceeds 84°C while peers stay <70°C is the hotspot.
3. Drain the node: `scontrol update nodename=<node> state=drain reason=thermal`.
4. Inspect the GPU cooling path; check `fanX_Y` saturation as a corroborating signal.
