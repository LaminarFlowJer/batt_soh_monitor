# Battery-Propulsion CAN Network (PRELIMINARY)

`battery_propulsion.dbc` defines the CAN FD network between the Battery Control Unit (node `BMS`) and the Propulsion Control Unit (node `PCU`).

| Item | Value |
|---|---|
| Protocol | CAN FD (ISO 11898-1:2015) |
| Arbitration bit rate | 500 kbit/s |
| Data bit rate | 2 Mbit/s (BRS on) |
| ID format | Standard 11-bit |
| Messages / signals | 9 / 63 |

| ID | Message | Tx | Cycle (ms) | Send type |
|---|---|---|---|---|
| 0x100 | BMS_PackStatus | BMS | 20 | Cyclic |
| 0x101 | BMS_PowerLimits | BMS | 20 | Cyclic |
| 0x102 | BMS_CellVoltages | BMS | 50 | Cyclic |
| 0x103 | BMS_Temperatures | BMS | 50 | Cyclic |
| 0x104 | BMS_ContactorStatus | BMS | 20 | Cyclic |
| 0x105 | BMS_Faults | BMS | 50 | CyclicAndOnChange |
| 0x200 | PCU_Command | PCU | 10 | Cyclic |
| 0x201 | PCU_PowerDemand | PCU | 20 | Cyclic |
| 0x202 | PCU_Faults | PCU | 50 | CyclicAndOnChange |

All signals are Intel (little-endian). Safety-relevant messages carry a 4-bit rolling counter and a CRC-8 in the last byte.

**Source of truth:** the CAN Model in Flow (CAN Network / CAN Message / CAN Signal items). Regenerate this file from Flow after changes.

> PRELIMINARY - requires engineering validation before use in hardware or software builds.
