# Example: Flip-Flop Timing Analysis and Metastability

## Purpose

Understand the critical timing parameters of digital sequential circuits, calculate maximum operating frequency, and learn about metastability — the most insidious failure mode in digital design.

---

## Setup Time and Hold Time

### Definitions

- **Setup time ($t_{su}$)**: Minimum time the data input D must be stable BEFORE the active clock edge
- **Hold time ($t_h$)**: Minimum time the data input D must be stable AFTER the active clock edge
- **Clock-to-Q delay ($t_{cq}$)**: Time from clock edge to valid output Q

### Timing Diagram

```
          t_su         t_h
       ◄────────►◄──────────►
       │ STABLE  │  STABLE   │
       │ DATA    │  DATA     │
  D:   ═════════════════════════════
       │         │            │
  CLK: ─────────┐│            │──────
                └┤            │
                 ↑            │
            Clock Edge        │
                              │
  Q:   ──────────────────┐    │
                  t_cq   └═══════════
                ◄───────►
                
  VIOLATION ZONE: If D changes during [t_su before edge] to [t_h after edge],
  the flip-flop behavior is UNDEFINED (metastability risk!)
```

---

## Maximum Clock Frequency Calculation

### Circuit Under Analysis

```
  ┌──────┐    Combinational    ┌──────┐
  │ FF_A │    Logic Path       │ FF_B │
  │      ├───►[logic delay]───►│      │
  │   Q  │    t_comb           │  D   │
  └──┬───┘                     └──┬───┘
     │                            │
  CLK├────────────────────────────┤CLK
```

### Timing Constraint

For FF_B to correctly capture data:

$$T_{clk} \geq t_{cq,A} + t_{comb,max} + t_{su,B}$$

Therefore:

$$\boxed{f_{max} = \frac{1}{t_{cq,A} + t_{comb,max} + t_{su,B}}}$$

### Numerical Example

Given:
- $t_{cq}$ = 0.5 ns (flip-flop clock-to-Q)
- $t_{comb,max}$ = 3.2 ns (worst-case combinational delay)
- $t_{su}$ = 0.3 ns (setup time)

$$T_{clk,min} = 0.5 + 3.2 + 0.3 = 4.0 \text{ ns}$$

$$f_{max} = \frac{1}{4.0 \times 10^{-9}} = 250 \text{ MHz}$$

### Hold Time Check

Also verify:

$$t_{cq,A} + t_{comb,min} \geq t_{h,B}$$

If the minimum delay through logic is too small, hold time is violated even with a slow clock. This is a **non-frequency-dependent failure** — it either works or it doesn't.

Given $t_{comb,min} = 0.1$ ns, $t_h = 0.2$ ns:

$$0.5 + 0.1 = 0.6 \geq 0.2$$ ✓ (Hold time satisfied)

---

## Metastability

### What Is Metastability?

When a flip-flop's setup or hold time is violated, the output Q can enter a **metastable state** — a voltage between logic 0 and logic 1 — for an unpredictable duration.

```
  Normal operation:
  Q: ──────┐
           └──────── (clean transition)
  
  Metastable:
  Q: ──────╮
           │~~~~~~╮  (oscillates/drifts before resolving)
                  └──────── 
           ◄──────►
           Metastable
           duration (random!)
```

### When Does It Happen?

Metastability occurs when an **asynchronous signal** crosses into a clock domain — the data may change exactly at the clock edge, violating setup/hold time.

Common scenarios:
- External button press (human timing is asynchronous)
- Signals crossing between different clock domains
- External sensor inputs sampled by a synchronous system

### Mean Time Between Failures (MTBF)

$$\text{MTBF} = \frac{e^{t_{resolve} / \tau}}{T_0 \cdot f_{clk} \cdot f_{data}}$$

Where:
- $t_{resolve}$: resolution time allowed (increases with slower clock)
- $\tau$: metastability time constant (technology-dependent, ~20-50 ps)
- $T_0$: setup time window parameter
- $f_{clk}$: clock frequency
- $f_{data}$: rate of asynchronous data changes

💡 **Insight**: MTBF increases **exponentially** with available resolution time. Each additional synchronizer flip-flop adds one clock period of resolution time.

---

## Mitigation: Synchronizer Chain

```
  Async    ┌──────┐    ┌──────┐    Synchronized
  Input ──►│ FF_1 ├───►│ FF_2 ├───► Output
           │      │    │      │    (safe to use)
           └──┬───┘    └──┬───┘
              │           │
  CLK ────────┴───────────┘
  
  FF_1 may go metastable, but it has one full clock period
  to resolve before FF_2 samples it.
```

### Two-Flip-Flop Synchronizer (Standard Practice)

For most applications, two synchronizer flip-flops provide adequate MTBF:

**Example calculation:**
- $f_{clk}$ = 100 MHz, $f_{data}$ = 1 MHz
- With 2-stage synchronizer: MTBF > 10^15 hours (effectively infinite)
- With 1-stage (no synchronizer): MTBF ~ hours to days (unacceptable!)

### Three-Stage Synchronizer

For safety-critical or very high-speed designs, use three flip-flops. Each additional stage multiplies MTBF by $e^{T_{clk}/\tau}$ (typically $10^6$ to $10^9$ times).

---

## Design Rules

| Rule | Reason |
|---|---|
| Never use asynchronous inputs directly | Metastability risk |
| Always synchronize external signals | Two FF minimum |
| Include reset synchronizer | Reset release must be synchronous |
| Use FIFOs for clock domain crossing | Handles multi-bit data safely |
| Don't rely on "it usually works" | Metastability is probabilistic — it WILL fail eventually |

⚠️ **Pitfall**: Multi-bit signals (e.g., a counter value) cannot be synchronized with simple flip-flops — different bits may resolve at different times, creating invalid intermediate values. Use Gray coding or asynchronous FIFOs for multi-bit clock domain crossings.
