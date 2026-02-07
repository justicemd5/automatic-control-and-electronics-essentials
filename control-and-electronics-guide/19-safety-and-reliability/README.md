# 19 — Safety and Reliability

> *Control systems often operate safety-critical equipment. A failure in a motor drive, chemical reactor, or medical device can cause injury or death. This section covers functional safety standards, failure analysis, and the engineering practices that make systems trustworthy.*

---

## 19.1 Functional Safety Concepts

### Safety vs. Reliability

| Concept | Definition | Metric |
|---|---|---|
| **Reliability** | System performs correctly over time | MTBF, failure rate λ |
| **Availability** | System is operational when needed | A = MTBF / (MTBF + MTTR) |
| **Safety** | System doesn't cause harm, even when it fails | PFD, SIL |

**Key insight**: A reliable system is not necessarily safe. A system that never fails is reliable but might still be unsafe if, when it eventually does fail, it causes catastrophic harm.

---

## 19.2 Safety Integrity Levels (SIL) — IEC 61508

### SIL Definitions

| SIL | PFD (Low Demand) | PFH (High Demand / Continuous) | Risk Reduction |
|---|---|---|---|
| **1** | $10^{-2}$ to $10^{-1}$ | $10^{-6}$ to $10^{-5}$ /h | 10 – 100 |
| **2** | $10^{-3}$ to $10^{-2}$ | $10^{-7}$ to $10^{-6}$ /h | 100 – 1,000 |
| **3** | $10^{-4}$ to $10^{-3}$ | $10^{-8}$ to $10^{-7}$ /h | 1,000 – 10,000 |
| **4** | $10^{-5}$ to $10^{-4}$ | $10^{-9}$ to $10^{-8}$ /h | 10,000 – 100,000 |

- **PFD**: Probability of Failure on Demand (safety function fails when called)
- **PFH**: Probability of dangerous Failure per Hour

### Industry-Specific Standards

| Standard | Industry | Based On |
|---|---|---|
| **IEC 61508** | General (base standard) | — |
| **IEC 61511** | Process industry | IEC 61508 |
| **IEC 62061** | Machinery | IEC 61508 |
| **ISO 13849** | Machinery (simplified) | Independent |
| **ISO 26262** | Automotive (ASIL A-D) | IEC 61508 |
| **IEC 62304** | Medical devices | IEC 61508 |
| **DO-178C** | Aviation (DAL A-E) | Independent |

---

## 19.3 Safe State Design

The fundamental question: **What happens when the system fails?**

```
  ┌──────────────────────────────────────────────────┐
  │              Safety Function                      │
  │                                                   │
  │  Normal State ──── Fault Detected ──► Safe State  │
  │                         │                         │
  │                    ┌────┴────┐                    │
  │                    │ Decide: │                    │
  │                    │ Safe    │                    │
  │                    │ State?  │                    │
  │                    └────┬────┘                    │
  │                         │                         │
  │                ┌────────┼────────┐                │
  │                ▼        ▼        ▼                │
  │           De-energize  Brake    Hold              │
  │           (power off)  (stop)   (maintain)        │
  └──────────────────────────────────────────────────┘
```

### Examples of Safe States

| Application | Safe State | Why |
|---|---|---|
| Motor drive | Power off (STO) | Prevents unintended motion |
| Chemical valve | Close (fail-closed) | Prevents uncontrolled release |
| Railway signal | Show red | Prevents collision |
| Elevator | Engage brake | Prevents free-fall |
| Medical ventilator | *No simple safe state!* | Must continue to operate |

⚠️ **Pitfall**: Not all systems have a simple safe state. A ventilator that shuts off kills the patient. These "continuous demand" systems require redundancy and fault-tolerant design rather than simple shutdown.

---

## 19.4 Failure Modes and Effects Analysis (FMEA)

### FMEA Process

```
  For each component:
  1. Identify all failure modes
  2. Determine the effect of each failure
  3. Assess severity, occurrence, and detection
  4. Calculate Risk Priority Number (RPN = S × O × D)
  5. Implement mitigation for high-RPN items
```

### FMEA Example: Motor Controller Temperature Sensor

| Component | Failure Mode | Effect | S | O | D | RPN | Mitigation |
|---|---|---|---|---|---|---|---|
| NTC Thermistor | Open circuit | Reads ∞ Ω → false "cold" → no protection | 9 | 3 | 3 | 81 | Detect out-of-range, dual sensor |
| NTC Thermistor | Short circuit | Reads 0 Ω → false "hot" → nuisance shutdown | 3 | 2 | 2 | 12 | Detect out-of-range |
| ADC | Stuck at max | Reads "cold" → no protection | 9 | 1 | 4 | 36 | Periodic ADC self-test |
| ADC | Stuck at min | Reads "hot" → nuisance shutdown | 3 | 1 | 4 | 12 | Periodic ADC self-test |
| Wire | Broken | Open → false reading | 8 | 4 | 3 | 96 | Wire break detection (pull-up) |
| Software | Wrong scaling | Incorrect temperature → wrong decision | 7 | 2 | 5 | 70 | Unit test, code review |

*S = Severity (1-10), O = Occurrence (1-10), D = Detection difficulty (1-10)*

See: [examples/fmea-motor-drive.md](examples/fmea-motor-drive.md)

---

## 19.5 Redundancy Architectures

### Common Architectures

```
  1oo1 (Single channel):
  ┌──────┐
  │  Ch1 │──► Output
  └──────┘
  PFD ≈ λ·T     (worst)
  
  
  1oo2 (Parallel / OR):
  ┌──────┐
  │  Ch1 │──┐
  └──────┘  ├──► Output (trips if EITHER channel trips)
  ┌──────┐  │
  │  Ch2 │──┘
  └──────┘
  PFD ≈ (λ·T)²  (much better)
  Nuisance trips: higher (either can trip)
  
  
  2oo2 (Series / AND):
  ┌──────┐
  │  Ch1 │──┐
  └──────┘  ├──► Output (trips if BOTH channels trip)
  ┌──────┐  │
  │  Ch2 │──┘
  └──────┘
  PFD ≈ 2·λ·T   (worse than 1oo1!)
  Nuisance trips: lower (both must agree)
  
  
  2oo3 (Triple Modular Redundancy / Voting):
  ┌──────┐
  │  Ch1 │──┐
  └──────┘  │
  ┌──────┐  ├──► Voter ──► Output (majority wins)
  │  Ch2 │──┤
  └──────┘  │
  ┌──────┐  │
  │  Ch3 │──┘
  └──────┘
  PFD ≈ 3·(λ·T)²   (excellent safety AND availability)
```

### Architecture Selection

| Architecture | Safety | Availability | Cost | Use Case |
|---|---|---|---|---|
| 1oo1 | Low | Medium | $ | Non-critical |
| 1oo2 | High | Lower | $$ | Safety shutdown |
| 2oo3 | Very High | Very High | $$$ | Nuclear, aviation |

---

## 19.6 Diagnostic Coverage

Diagnostics detect faults before they become dangerous:

| Technique | Detects | Coverage |
|---|---|---|
| Watchdog timer | CPU hang | 60% |
| RAM check (march test) | Memory corruption | 90% |
| ROM CRC | Code corruption | 99% |
| ADC self-test | ADC failure | 90% |
| Cross-comparison (2 channels) | Any single failure | 99% |
| Plausibility check | Sensor drift/offset | 70% |

$$DC = \frac{\lambda_{detected}}{\lambda_{total}} \times 100\%$$

Higher DC allows higher SIL with simpler architecture.

---

## 19.7 Safe Torque Off (STO) — IEC 61800-5-2

The most common safety function in motor drives:

```
  Normal Operation:              STO Activated:
  
  ┌─────┐  PWM  ┌─────┐         ┌─────┐       ┌─────┐
  │ MCU │──────►│Gate │──►Motor  │ MCU │──────►│Gate │──X Motor
  │     │       │Drive│         │     │       │Drive│ (no pulses)
  └─────┘       └──┬──┘         └─────┘       └──┬──┘
                   │                              │
                ┌──┴──┐                        ┌──┴──┐
                │POWER│                        │POWER│
                │  ON │                        │ OFF │ ← Hardware
                └─────┘                        └─────┘   disconnect
  
  STO removes the gate drive power supply, making it physically
  impossible for the power stage to energize the motor — regardless
  of what the software does.
```

---

## Examples

| File | Description |
|---|---|
| [fmea-motor-drive.md](examples/fmea-motor-drive.md) | Complete FMEA for a motor drive |
| [sil-calculation.md](examples/sil-calculation.md) | SIL verification calculation |
| [safety-architecture.md](examples/safety-architecture.md) | Dual-channel safety system design |

---

**Previous → [18-communication-interfaces](../18-communication-interfaces/README.md)**  
**Next → [20-advanced-topics](../20-advanced-topics/README.md)**
