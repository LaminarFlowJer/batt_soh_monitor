# batt_soh_monitor

Example battery state-of-health monitor script for an eVTOL aircraft:

- File: `battery_soh_monitor_example.py`
- Monitors continuously in operational modes (`preflight`, `taxi`, `takeoff`, `climb`, `cruise`, `descent`, `landing`, `emergency`)
- Checks:
  - battery temperature out of tolerance
  - electrical behavior anomalies (current limits, low voltage, voltage sag, cell imbalance, insulation resistance)
- Emits `BATTERY_ISSUE` messages with timestamp/mode/details when out-of-tolerance conditions are detected

## Run

```bash
python3 battery_soh_monitor_example.py
```

Short demo run:

```bash
python3 battery_soh_monitor_example.py --duration-seconds 10
```
