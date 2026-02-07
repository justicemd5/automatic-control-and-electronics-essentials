# Example: PID Controller Design Walkthrough

## Purpose
Design a PID controller for a DC motor speed control system step-by-step, showing each tuning action and its effect on the closed-loop response.

---

## Plant Model

DC motor transfer function (speed/voltage):

$$G(s) = \frac{\omega(s)}{V(s)} = \frac{K}{(\tau_e s + 1)(\tau_m s + 1)}$$

**Parameters:**
- $K = 10$ rad/s/V (DC gain)
- $\tau_e = 0.01$ s (electrical time constant)
- $\tau_m = 0.1$ s (mechanical time constant)

$$G(s) = \frac{10}{(0.01s + 1)(0.1s + 1)} = \frac{10}{0.001s^2 + 0.11s + 1}$$

Open-loop step response: slow rise to 10 rad/s per volt, no oscillation.

---

## Step 1: Proportional-Only (P) Controller

$$C(s) = K_p$$

**Closed-loop:**

$$T(s) = \frac{K_p G(s)}{1 + K_p G(s)} = \frac{10 K_p}{0.001s^2 + 0.11s + 1 + 10K_p}$$

| $K_p$ | DC Gain $T(0)$ | SS Error | Rise Time | Overshoot |
|---|---|---|---|---|
| 0.1 | 0.50 | 50% | Slow | None |
| 1.0 | 0.91 | 9.1% | Medium | Slight |
| 10.0 | 0.99 | 1.0% | Fast | ~20% |
| 100.0 | 0.999 | 0.1% | Very fast | ~50% |

⚠️ **Pitfall**: Increasing $K_p$ reduces steady-state error but never eliminates it, and eventually causes excessive overshoot and instability.

```
  Step Response (P-only):
  
  ω(t)
  r ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ← setpoint
      ╱──────────────────── Kp = 100 (overshoot, oscillation)
     ╱  ╱────────────────── Kp = 10 (slight overshoot)
    ╱  ╱   ╱─────────────── Kp = 1 (slow, large SS error)
   ╱  ╱   ╱
  └──────────────────────────────────── t
```

---

## Step 2: Add Integral Action (PI Controller)

$$C(s) = K_p + \frac{K_i}{s} = K_p\left(1 + \frac{1}{T_i s}\right)$$

Choose $K_p = 5$, then tune $K_i$:

$$T_i = \frac{K_p}{K_i}$$

**Design rule**: Set $T_i \approx \tau_m = 0.1$ s (cancel the dominant plant pole).

$$K_i = \frac{K_p}{T_i} = \frac{5}{0.1} = 50$$

$$C(s) = 5 + \frac{50}{s} = \frac{5s + 50}{s} = \frac{5(s + 10)}{s}$$

The zero at $s = -10$ cancels the plant pole at $s = -1/\tau_m = -10$.

**Result:**
- Steady-state error: **0** (integral action ensures this!)
- Rise time: ~0.03s (fast)
- Overshoot: ~15% (acceptable for many applications)

```
  Step Response (PI):
  
  ω(t)
  r ─ ─ ─ ─ ─╱╲─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ← setpoint
             ╱  ╲──────────────────── PI: zero SS error
            ╱
           ╱
  └──────────────────────────────────── t
         │◄──── ~0.03s ────►│
```

---

## Step 3: Add Derivative Action (Full PID)

$$C(s) = K_p + \frac{K_i}{s} + K_d s$$

The derivative term adds damping, reducing overshoot:

$$K_d = K_p \cdot T_d$$

**Design rule**: $T_d \approx \tau_e / 4 = 0.0025$ s

$$K_d = 5 \times 0.0025 = 0.0125$$

### Practical PID with Derivative Filter

Pure derivative amplifies noise. Add a first-order filter:

$$C(s) = K_p + \frac{K_i}{s} + \frac{K_d s}{1 + \frac{K_d}{N K_p}s}$$

Where $N = 10\text{–}20$ limits high-frequency gain.

**Final PID:** $K_p = 5$, $K_i = 50$, $K_d = 0.0125$, $N = 10$

```
  Step Response Comparison:
  
  ω(t)
  r ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  ← setpoint
             ╱───────────────────── PID: fast, minimal overshoot
            ╱╲──────────────────── PI: some overshoot
           ╱   ╱─────────────────── P-only: steady-state error
  └──────────────────────────────── t
```

---

## Step 4: Verify Stability Margins

With PID and plant:

$$L(s) = C(s) \cdot G(s) = \frac{(5s^2 + 50s + 0.0125s^2 \cdot ...)}{s \cdot (0.001s^2 + 0.11s + 1)}$$

**Check on Bode plot:**
- Gain crossover frequency $\omega_c$: where $|L(j\omega)| = 0$ dB
- Phase margin: $PM = 180° + \angle L(j\omega_c)$

Target: $PM \geq 45°$, $GM \geq 10$ dB

---

## Tuning Summary

### Ziegler-Nichols Ultimate Gain Method

1. Set $K_i = 0$, $K_d = 0$
2. Increase $K_p$ until sustained oscillation → $K_u$ (ultimate gain), $T_u$ (ultimate period)
3. Apply table:

| Controller | $K_p$ | $T_i$ | $T_d$ |
|---|---|---|---|
| P | $0.5 K_u$ | — | — |
| PI | $0.45 K_u$ | $T_u / 1.2$ | — |
| PID | $0.6 K_u$ | $T_u / 2$ | $T_u / 8$ |

### Practical Tuning Order

1. **Start with P**: Find $K_p$ that gives acceptable response speed
2. **Add I**: Set $T_i$ to eliminate steady-state error (start high, decrease)
3. **Add D**: Set $T_d$ to reduce overshoot (start low, increase carefully)
4. **Verify margins**: Check gain and phase margins
5. **Test disturbance rejection**: Apply load step
6. **Anti-windup**: Implement integrator saturation for actuator limits

💡 **Insight**: In practice, ~80% of PID loops in industry use only PI control. The derivative term is omitted because of noise sensitivity. D is mainly useful when the plant has significant phase lag or the sensor is low-noise.
