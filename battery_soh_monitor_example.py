"""Example Battery State of Health monitor for an eVTOL aircraft.

This script continuously evaluates battery telemetry when the aircraft is in
an operational mode. It raises issue messages when values are out of tolerance,
including temperature and electrical behavior anomalies.

Run indefinitely:
    python battery_soh_monitor_example.py

Run for a short demo period:
    python battery_soh_monitor_example.py --duration-seconds 10
"""

from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Iterator, List, Optional


class AircraftMode(str, Enum):
    OFF = "off"
    MAINTENANCE = "maintenance"
    PREFLIGHT = "preflight"
    TAXI = "taxi"
    TAKEOFF = "takeoff"
    CLIMB = "climb"
    CRUISE = "cruise"
    DESCENT = "descent"
    LANDING = "landing"
    EMERGENCY = "emergency"


OPERATIONAL_MODES = {
    AircraftMode.PREFLIGHT,
    AircraftMode.TAXI,
    AircraftMode.TAKEOFF,
    AircraftMode.CLIMB,
    AircraftMode.CRUISE,
    AircraftMode.DESCENT,
    AircraftMode.LANDING,
    AircraftMode.EMERGENCY,
}


@dataclass(frozen=True)
class BatteryTelemetry:
    timestamp: datetime
    aircraft_mode: AircraftMode
    temperature_c: float
    pack_voltage_v: float
    pack_current_a: float
    cell_voltage_delta_v: float
    insulation_resistance_kohm: float


@dataclass(frozen=True)
class BatteryThresholds:
    min_temp_c: float = 5.0
    max_temp_c: float = 90.0
    max_discharge_current_a: float = 320.0
    max_charge_current_a: float = 180.0
    min_pack_voltage_v: float = 560.0
    high_load_current_a: float = 220.0
    min_loaded_voltage_v: float = 600.0
    max_cell_delta_v: float = 0.050
    min_insulation_resistance_kohm: float = 800.0


class BatterySOHMonitor:
    """Evaluates telemetry and reports battery SOH issues."""

    def __init__(self, thresholds: BatteryThresholds | None = None) -> None:
        self.thresholds = thresholds or BatteryThresholds()

    def detect_issues(self, telemetry: BatteryTelemetry) -> List[str]:
        """Return a list of issue descriptions for any out-of-tolerance values."""
        t = self.thresholds
        issues: List[str] = []

        if telemetry.temperature_c < t.min_temp_c:
            issues.append(
                f"battery temperature too low: {telemetry.temperature_c:.1f} C "
                f"(min {t.min_temp_c:.1f} C)"
            )
        if telemetry.temperature_c > t.max_temp_c:
            issues.append(
                f"battery temperature too high: {telemetry.temperature_c:.1f} C "
                f"(max {t.max_temp_c:.1f} C)"
            )

        if telemetry.pack_current_a > t.max_discharge_current_a:
            issues.append(
                f"discharge current exceeds limit: {telemetry.pack_current_a:.1f} A "
                f"(max {t.max_discharge_current_a:.1f} A)"
            )
        if telemetry.pack_current_a < -t.max_charge_current_a:
            issues.append(
                f"charge current exceeds limit: {abs(telemetry.pack_current_a):.1f} A "
                f"(max {t.max_charge_current_a:.1f} A)"
            )

        if telemetry.pack_voltage_v < t.min_pack_voltage_v:
            issues.append(
                f"pack voltage below minimum: {telemetry.pack_voltage_v:.1f} V "
                f"(min {t.min_pack_voltage_v:.1f} V)"
            )
        if (
            telemetry.pack_current_a > t.high_load_current_a
            and telemetry.pack_voltage_v < t.min_loaded_voltage_v
        ):
            issues.append(
                "excessive voltage sag under high load: "
                f"{telemetry.pack_voltage_v:.1f} V at {telemetry.pack_current_a:.1f} A"
            )

        if telemetry.cell_voltage_delta_v > t.max_cell_delta_v:
            issues.append(
                f"cell imbalance too large: {telemetry.cell_voltage_delta_v:.3f} V "
                f"(max {t.max_cell_delta_v:.3f} V)"
            )

        if telemetry.insulation_resistance_kohm < t.min_insulation_resistance_kohm:
            issues.append(
                "insulation resistance below safe limit: "
                f"{telemetry.insulation_resistance_kohm:.1f} kohm "
                f"(min {t.min_insulation_resistance_kohm:.1f} kohm)"
            )

        return issues

    def build_issue_message(self, telemetry: BatteryTelemetry, issues: List[str]) -> str:
        """Build one issue message line for alerting/logging."""
        joined = "; ".join(issues)
        ts = telemetry.timestamp.isoformat()
        return (
            f"[{ts}] BATTERY_ISSUE mode={telemetry.aircraft_mode.value}: {joined}"
        )


def simulate_telemetry_stream(seed: Optional[int] = None) -> Iterator[BatteryTelemetry]:
    """Produce sample telemetry with occasional injected faults."""
    rng = random.Random(seed)
    mode_plan = [
        AircraftMode.OFF,
        AircraftMode.PREFLIGHT,
        AircraftMode.TAXI,
        AircraftMode.TAKEOFF,
        AircraftMode.CLIMB,
        AircraftMode.CRUISE,
        AircraftMode.DESCENT,
        AircraftMode.LANDING,
        AircraftMode.MAINTENANCE,
    ]

    idx = 0
    while True:
        mode = mode_plan[(idx // 25) % len(mode_plan)]
        idx += 1

        temperature_c = rng.gauss(34.0, 2.5)
        pack_current_a = max(0.0, rng.gauss(170.0, 45.0))
        pack_voltage_v = 700.0 - (pack_current_a * 0.28) + rng.gauss(0.0, 5.0)
        cell_delta_v = max(0.001, rng.gauss(0.018, 0.006))
        insulation_resistance_kohm = rng.gauss(1400.0, 120.0)

        if mode == AircraftMode.TAKEOFF and rng.random() < 0.22:
            pack_current_a = rng.uniform(330.0, 380.0)
            pack_voltage_v = rng.uniform(530.0, 600.0)

        if mode in {AircraftMode.CLIMB, AircraftMode.CRUISE} and rng.random() < 0.15:
            temperature_c = rng.uniform(56.0, 67.0)

        if mode in OPERATIONAL_MODES and rng.random() < 0.08:
            cell_delta_v = rng.uniform(0.052, 0.090)

        if mode in OPERATIONAL_MODES and rng.random() < 0.06:
            insulation_resistance_kohm = rng.uniform(350.0, 760.0)

        yield BatteryTelemetry(
            timestamp=datetime.now(timezone.utc),
            aircraft_mode=mode,
            temperature_c=temperature_c,
            pack_voltage_v=pack_voltage_v,
            pack_current_a=pack_current_a,
            cell_voltage_delta_v=cell_delta_v,
            insulation_resistance_kohm=insulation_resistance_kohm,
        )


def monitor_battery_soh(
    stream: Iterable[BatteryTelemetry],
    poll_interval_s: float = 1.0,
    duration_seconds: Optional[float] = None,
) -> None:
    """Continuously monitor battery SOH during operational aircraft modes."""
    monitor = BatterySOHMonitor()
    start = time.monotonic()

    for telemetry in stream:
        if telemetry.aircraft_mode in OPERATIONAL_MODES:
            issues = monitor.detect_issues(telemetry)
            if issues:
                print(monitor.build_issue_message(telemetry, issues))
        else:
            print(
                f"[{telemetry.timestamp.isoformat()}] "
                f"mode={telemetry.aircraft_mode.value}: monitoring inactive"
            )

        if duration_seconds is not None and (time.monotonic() - start) >= duration_seconds:
            break
        time.sleep(poll_interval_s)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example continuous battery SOH monitor for eVTOL operations."
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Seconds between telemetry checks (default: 1.0).",
    )
    parser.add_argument(
        "--duration-seconds",
        type=float,
        default=None,
        help="Optional duration for demo runs. Omit to run indefinitely.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=7,
        help="Random seed for repeatable telemetry simulation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stream = simulate_telemetry_stream(seed=args.seed)
    monitor_battery_soh(
        stream=stream,
        poll_interval_s=args.poll_interval,
        duration_seconds=args.duration_seconds,
    )


if __name__ == "__main__":
    main()
