# Example: FMEA for Variable Frequency Drive (VFD)

## Purpose
Perform a systematic Failure Modes and Effects Analysis on a Variable Frequency Drive (motor inverter), identifying critical failure modes and their mitigations.

---

## System: 3-Phase Variable Frequency Drive

```
  AC Mains ──► Rectifier ──► DC Bus ──► Inverter ──► Motor
                  │             │           │
               ┌──┴──┐     ┌───┴───┐   ┌──┴──┐
               │Diodes│     │DC Bus │   │IGBTs│
               │Bridge│     │Caps   │   │× 6  │
               └─────┘     └───────┘   └──┬──┘
                                          │
  Control: MCU ──► Gate Drivers ──────────┘
           │
  Sensors: DC Bus Voltage, Phase Currents (×2), Temperature, Encoder
```

---

## FMEA Table

### Power Stage

| # | Component | Failure Mode | Cause | Local Effect | System Effect | S | O | D | RPN | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IGBT (upper) | Short circuit | Overcurrent, gate failure, cosmic ray | Shoot-through (upper + lower on) | DC bus short → explosion, fire | **10** | 3 | 2 | **60** | Desat detection (< 2 µs), fuse, STO |
| 2 | IGBT (upper) | Open circuit | Bond wire lift, thermal fatigue | Phase output disconnected | Motor loses one phase, vibrates | 6 | 3 | 4 | 72 | Phase current monitoring |
| 3 | IGBT (lower) | Short circuit | Same as #1 | Shoot-through | Same as #1 | **10** | 3 | 2 | **60** | Same as #1 |
| 4 | DC bus capacitor | Short circuit | Overvoltage, aging, dielectric failure | DC bus short circuit | Fuse blows, loss of function | 7 | 2 | 3 | 42 | Fuse, overvoltage protection |
| 5 | DC bus capacitor | Open/degraded | Dry-out, aging | Increased ripple, reduced filtering | Overcurrent ripple, overheating | 5 | 4 | 5 | 100 | Ripple monitoring, ESR check |
| 6 | Gate driver | No output | Supply failure, IC fault | IGBT stays off | Motor phase lost | 6 | 2 | 4 | 48 | Gate driver supply monitoring |
| 7 | Gate driver | Stuck on | IC failure | IGBT stays on → potential shoot-through | Same as #1 | **10** | 1 | 3 | 30 | Hardware interlock (dead-time) |

### Sensors

| # | Component | Failure Mode | Cause | Local Effect | System Effect | S | O | D | RPN | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| 8 | Current sensor | Offset drift | Temperature, aging | Wrong current reading | Torque error, possible overcurrent | 7 | 4 | 4 | **112** | Self-calibration at startup, plausibility check |
| 9 | Current sensor | Open circuit | Wire break | Reads zero | Loss of current control, overcurrent | 9 | 2 | 3 | 54 | Out-of-range detection |
| 10 | Current sensor | Gain error | Component tolerance | Scaled current wrong | Torque error | 5 | 3 | 5 | 75 | Periodic calibration |
| 11 | DC bus voltage | Reads low | Divider resistor drift | Overmodulation attempted | Distorted output, overcurrent | 6 | 2 | 4 | 48 | Cross-check with rectified AC |
| 12 | Temperature sensor | Open | Broken wire, connector | Reads "cold" (no protection) | Overheating undetected → IGBT failure | **9** | 3 | 3 | **81** | Pull-up for wire break, dual sensor |
| 13 | Encoder | Missing pulses | EMI, connector | Position error | Motor loses synchronization, stalls | 7 | 4 | 3 | **84** | Plausibility check, sensorless backup |

### Control (Software/MCU)

| # | Component | Failure Mode | Cause | Local Effect | System Effect | S | O | D | RPN | Mitigation |
|---|---|---|---|---|---|---|---|---|---|---|
| 14 | MCU | Program counter corruption | EMI, cosmic ray, latch-up | Executes wrong code | Unpredictable motor behavior | **10** | 1 | 4 | 40 | Watchdog, safety MCU, STO |
| 15 | MCU | ADC stuck | Silicon defect, ESD damage | Wrong sensor reading | Incorrect control action | 8 | 1 | 3 | 24 | ADC self-test, cross-check |
| 16 | PWM timer | Wrong duty cycle | Register corruption | Wrong voltage output | Overcurrent or loss of control | 8 | 1 | 3 | 24 | PWM readback verification |
| 17 | Software | PID integral windup | Edge case in code | Large control overshoot | Motor overcurrent, mechanical damage | 7 | 3 | 4 | 84 | Anti-windup, output clamping |
| 18 | Software | Division by zero | Speed = 0, sensor failure | Exception / crash | Loss of control | 8 | 2 | 3 | 48 | Defensive coding, watchdog |

---

## Risk Priority Analysis

### Top RPNs (Action Required)

| Rank | # | Failure | RPN | Required Action |
|---|---|---|---|---|
| 1 | 8 | Current sensor offset | 112 | Auto-calibration + plausibility |
| 2 | 5 | DC cap degradation | 100 | Health monitoring algorithm |
| 3 | 13 | Encoder pulse loss | 84 | Sensorless fallback mode |
| 4 | 17 | PID windup | 84 | Anti-windup + output limits |
| 5 | 12 | Temp sensor open | 81 | Wire-break detection + dual sensor |

### Safety-Critical Failures (S ≥ 9)

| # | Failure | S | Mitigation Status |
|---|---|---|---|
| 1, 3 | IGBT short (shoot-through) | 10 | Desat detection + hardware dead-time + STO |
| 14 | MCU corruption | 10 | Watchdog + STO (hardware) |
| 9 | Current sensor open | 9 | Out-of-range detect → STO within 1 ms |
| 12 | Temp sensor open | 9 | Pull-up detect + thermal model backup |

---

## Implementation of Top Mitigations

### 1. Desaturation Detection (for IGBT Short Circuit)

```
  Time from fault to shutdown: < 2 µs
  
  Normal:     VCE_sat < 2V ← IGBT fully on
  Fault:      VCE > 7V    ← IGBT in linear region (SHORT!)
  
  ┌──────────────┐
  │ Gate Driver   │
  │               │
  │  VCE ──►│Compare│──► Fault!
  │         │> 7V? │    │
  │         └──────┘    ▼
  │              Turn OFF gate
  │              (soft turnoff to limit di/dt)
  └──────────────┘
  
  Response: Gate driver turns off IGBT within 2 µs
  → Prevents thermal destruction of IGBT
  → Limits fault current to safe level
```

### 2. Current Sensor Plausibility

```
  Three checks run every control cycle:
  
  1. Range check:  |I_phase| < I_max + margin
  2. Sum check:    |Ia + Ib + Ic| < threshold  (Kirchhoff: should sum to ~0)
  3. Symmetry:     |Ia| ≈ |Ib| ≈ |Ic| during steady state
  
  Any violation → fault counter++ → shutdown after N consecutive failures
```

💡 **Insight**: The FMEA is a living document. It should be updated whenever the design changes, and reviewed after every field failure. The goal is not to eliminate all failures (impossible), but to ensure every dangerous failure is detected and mitigated to an acceptable risk level.

⚠️ **Pitfall**: FMEA alone is not sufficient for safety certification. It identifies single-point failures but doesn't systematically analyze common-cause failures (both channels of a dual sensor failing for the same reason). Use Fault Tree Analysis (FTA) to complement FMEA for SIL 3+ systems.
