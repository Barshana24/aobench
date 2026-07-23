# Marconi100 Node Power Policy

## IPMI power metrics (ipmi_pub plugin)
- `total_power`       — whole-node power draw (W)
- `psN_input_power`   — power-supply N input power (W)
- `pN_power`          — CPU socket N package power (W)

## Reference levels (per real M100 telemetry)
- Typical node draw: ~640W (idle/moderate), up to ~1820W at full GPU load
- Sustained per-node alert threshold: 1300W
- A single node >> rack median for >15 min indicates a power anomaly

## Response
1. Query telemetry for `total_power` across the rack; rank nodes by recent mean.
2. Flag any node whose sustained draw exceeds the rack baseline by >100%.
3. Cross-check `psN_input_power` to confirm it is real draw, not a sensor fault.
4. Correlate with the running job; apply a power cap or reschedule.
