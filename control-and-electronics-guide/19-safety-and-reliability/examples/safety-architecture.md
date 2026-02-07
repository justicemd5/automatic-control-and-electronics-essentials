# Example: Dual-Channel Safety System Architecture

## Purpose
Design a dual-channel (1oo2D) safety system for a machine press, demonstrating the architectural requirements for SIL 3 compliance.

---

## Application: Hydraulic Press Safety

A hydraulic press must stop within 50 ms if the light curtain is broken while the ram is moving downward.

```
  ┌─────────────┐
  │ Hydraulic   │
  │ Press Ram   │
  │    ▼▼▼▼▼    │
  │             │
  │  ╔═════╗   │
  │  ║Part ║   │  ← Danger zone
  │  ╚═════╝   │
  │             │
  │ ▓▓▓ Die ▓▓▓│
  └─────────────┘
  │             │
  TX ─ ─ ─ ─ RX   ← Light curtain
  TX ─ ─ ─ ─ RX     (safety-rated)
```

---

## Architecture: 1oo2D (Category 4 / SIL 3)

```
  Light            Channel A              AND          Hydraulic
  Curtain    ┌────────────────────┐     Logic         Valve
  ┌──────┐   │  ┌──────┐  ┌────┐ │                   ┌──────┐
  │Input │──►│  │Safety │  │Out │─┼──┐   ┌─────┐     │Valve │
  │Module│   │  │CPU A  │  │  A │ │  ├──►│ AND │────►│  1   │
  │  A   │   │  └──┬───┘  └────┘ │  │   │     │     │(NC)  │
  └──────┘   │     │ Cross-check  │  │   └──┬──┘     └──────┘
             │     │ ↕↕↕↕↕↕↕↕↕↕  │  │      │
  ┌──────┐   │  ┌──┴───┐  ┌────┐ │  │   ┌──┴──┐     ┌──────┐
  │Input │──►│  │Safety │  │Out │─┼──┘   │ AND │────►│Valve │
  │Module│   │  │CPU B  │  │  B │ │      │     │     │  2   │
  │  B   │   │  └──────┘  └────┘ │      └─────┘     │(NC)  │
  └──────┘   └────────────────────┘                   └──────┘
                 Safety Controller
  
  Key:
  • Two independent input modules read the light curtain
  • Two independent CPUs process the safety logic
  • Both CPUs must agree on "safe" to allow operation
  • Either CPU detecting a fault → BOTH outputs shut off
  • Two normally-closed (NC) valves in series → fail-safe
```

---

## Design Requirements

### Hardware Independence

| Aspect | Requirement | Implementation |
|---|---|---|
| CPU | Different silicon | CPU A: Cortex-M4, CPU B: Cortex-M0+ |
| Clock | Independent oscillators | Separate crystals, cross-checked |
| Power | Independent supplies | Separate regulators from same bus |
| Inputs | Separate input circuits | Different ADC channels, different conditioning |
| Outputs | Independent drivers | Separate MOSFET drivers + feedback |
| PCB | Separate power planes | Galvanic separation where possible |

### Software Diversity

```
  CPU A (Primary):                 CPU B (Checker):
  
  ┌──────────────────┐            ┌──────────────────┐
  │ Read Input A     │            │ Read Input B     │
  │ (direct ADC)     │            │ (comparator)     │
  │                  │            │                  │
  │ Safety Logic     │            │ Safety Logic     │
  │ (state machine)  │            │ (Boolean logic)  │
  │                  │            │                  │
  │ Send result ────►│◄── ──────►│◄── Send result   │
  │ to cross-check   │  Compare   │ to cross-check   │
  │                  │            │                  │
  │ If match:        │            │ If match:        │
  │   Drive Output A │            │   Drive Output B │
  │ If mismatch:     │            │ If mismatch:     │
  │   SAFE STATE     │            │   SAFE STATE     │
  └──────────────────┘            └──────────────────┘
  
  Different algorithms → protects against systematic software faults
```

⚠️ **Pitfall**: Using identical software on both CPUs is NOT sufficient for SIL 3. A software bug in one copy exists in both copies. True diversity requires different algorithms, different compilers, or different development teams. At minimum, use different compilers and different coding approaches.

---

## Cross-Check Protocol

Every 1 ms, the two CPUs exchange and verify:

```
  CPU A → CPU B: {sequence_number, input_state_A, output_state_A, CRC}
  CPU B → CPU A: {sequence_number, input_state_B, output_state_B, CRC}
  
  Checks performed:
  1. CRC valid?                          → Detects communication errors
  2. Sequence number incrementing?       → Detects stuck/dead CPU
  3. Input states agree?                 → Detects input circuit fault
  4. Output states agree?                → Detects output fault
  5. Response within timeout (5 ms)?     → Detects CPU hang
  
  ANY check failure → Both CPUs → SAFE STATE
```

---

## Timing Analysis

```
  Event:           Light curtain broken
  
  t = 0 ms:        Light curtain output changes
  t = 2 ms:        Input module detects change (scan time)
  t = 3 ms:        CPU A reads input, processes logic
  t = 4 ms:        CPU B reads input, processes logic
  t = 5 ms:        Cross-check complete, outputs commanded OFF
  t = 6 ms:        Output modules de-energize solenoids
  t = 8 ms:        Hydraulic valves start closing
  t = 30 ms:       Valves fully closed
  t = 45 ms:       Press ram decelerates to stop
  
  Total: ≈ 45 ms < 50 ms requirement  ✓
```

---

## Diagnostic Tests (Run Continuously)

| Test | Frequency | Detects | Method |
|---|---|---|---|
| Cross-check | 1 ms | CPU fault, disagreement | Exchange + compare |
| Watchdog | 10 ms | CPU hang | Independent WDT on each CPU |
| RAM test | 100 ms | Memory bit flips | March C- algorithm (partial, rotating) |
| ROM CRC | 1 s | Code corruption | CRC-32 over full flash |
| Input test | Every cycle | Input stuck | Pulse test on light curtain |
| Output test | Every cycle | Output stuck | Read back output state |
| Clock check | 10 ms | Clock drift | CPUs compare timestamps |

### Diagnostic Coverage Summary

$$DC_{total} = \frac{\sum \lambda_{detected}}{\sum \lambda_{dangerous}} = \frac{0.95 \lambda_A + 0.95 \lambda_B}{\lambda_A + \lambda_B} = 95\%$$

This DC + 1oo2 architecture enables SIL 3.

---

## Output Stage: Dual-Valve with Monitoring

```
  Output A ──►┌─────────┐
              │Solenoid │──► Valve 1 (NC) ──┐
              │Driver A │                    ├──► Hydraulic
  Output B ──►┌─────────┐                    │    Power
              │Solenoid │──► Valve 2 (NC) ──┘
              │Driver B │
  
  Monitoring:
  • Pressure switch downstream verifies valves actually closed
  • Valve position sensors (reed switches) confirm mechanical state
  • If valve fails to close within 50 ms → fault state, disable machine
  
  Annual test: Manual proof test of each valve independently
```

---

## Key Design Principles

1. **Fail-safe by default**: NC valves, de-energize = safe
2. **Independence**: Separate CPUs, inputs, outputs, power
3. **Diversity**: Different algorithms, different hardware
4. **Diagnostics**: Continuous cross-checking, output monitoring
5. **Proof testing**: Annual full functional test of each channel

💡 **Insight**: The cost of a dual-channel safety system is roughly 2× the single-channel version. For a $500 controller, this means $1000 — trivial compared to the cost of a workplace injury ($50,000-$500,000+) or the cost of a product recall. Safety is always the cheapest option in the long run.
