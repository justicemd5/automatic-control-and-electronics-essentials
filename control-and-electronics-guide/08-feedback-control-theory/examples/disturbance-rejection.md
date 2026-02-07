# Example: Disturbance Rejection and Feedforward Control

## Purpose
Analyze how feedback control rejects load disturbances, compare pure feedback vs. feedforward + feedback, and show quantitative improvement.

---

## System Setup

```
  d(t) (disturbance)
       │
  r(s) ──►(+)── e ── C(s) ──►(+)──►── G(s) ──►── y(s)
           −↑                   ↑d               │
            │                                     │
            └─────────────────────────────────────┘
```

**Plant**: $G(s) = \frac{1}{s + 1}$ (first-order, $\tau = 1$ s)

**Controller**: PI controller $C(s) = K_p + \frac{K_i}{s}$

**Disturbance**: Step load applied at the plant input (e.g., sudden load change on a motor)

---

## Transfer Functions

**Output due to reference:**
$$Y_r(s) = \frac{C(s)G(s)}{1 + C(s)G(s)} R(s)$$

**Output due to disturbance:**
$$Y_d(s) = \frac{G(s)}{1 + C(s)G(s)} D(s)$$

---

## Case 1: No Controller (Open Loop)

$$Y_d(s) = G(s) \cdot D(s) = \frac{1}{s+1} \cdot \frac{1}{s} = \frac{1}{s(s+1)}$$

$$y_d(t) = 1 - e^{-t}$$

The disturbance causes a permanent offset of 1.0 in the output.

```
  y(t)
  1.0 ─ ─ ─ ─ ─────────────── ← permanent offset!
               ╱
              ╱
  0   ───────╱
      │      │
      0    disturbance
           applied
```

---

## Case 2: P Controller ($K_p = 9$)

$$L(s) = 9 \cdot \frac{1}{s+1} = \frac{9}{s+1}$$

$$Y_d = \frac{G(s)}{1 + L(s)} D(s) = \frac{1/(s+1)}{1 + 9/(s+1)} = \frac{1}{s + 10}$$

Step response of disturbance rejection:

$$y_d(t) = \frac{1}{10}(1 - e^{-10t}) \to 0.1$$

Steady-state disturbance effect: $y_{d,ss} = G(0) / (1 + L(0)) = 1/10 = 0.1$

**P control reduces disturbance by factor 10**, but residual error of 0.1 remains.

---

## Case 3: PI Controller ($K_p = 9$, $K_i = 20$)

$$C(s) = 9 + \frac{20}{s} = \frac{9s + 20}{s}$$

$$L(s) = \frac{9s + 20}{s(s+1)}$$

Disturbance transfer function:

$$\frac{Y_d(s)}{D(s)} = \frac{1/(s+1)}{1 + (9s+20)/(s(s+1))} = \frac{s}{s^2 + 10s + 20}$$

For a step disturbance $D(s) = 1/s$:

$$Y_d(s) = \frac{1}{s^2 + 10s + 20}$$

$$y_{d,ss} = \lim_{s\to 0} s \cdot Y_d(s) = 0$$

**PI control eliminates the steady-state disturbance effect completely!**

The integral action "winds up" until the error is driven to zero.

```
  y(t)
  
  0.1  ─ ─── P only ──────────────── ← residual error
                  
  0.0  ──────╱╲────────────────────── ← PI (zero SS error!)
            ╱  ╲___________________
           ╱
  0   ────╱
      │   │
      0  disturbance
```

---

## Case 4: Feedforward + Feedback

If the disturbance is measurable, feedforward dramatically improves transient response:

```
                          d(t) measurable
                              │
  r(s) ──►(+)── C(s) ──►(+)──┼──►(+)──► G(s) ──► y(s)
           −↑            ↑    │    ↑               │
            │         C_ff(s)─┘    │d              │
            └──────────────────────────────────────┘
```

**Feedforward controller:**

$$C_{ff}(s) = -\frac{G_d(s)}{G(s)}$$

If $G_d(s) = G(s)$ (disturbance enters at the same point as the control):

$$C_{ff}(s) = -1$$

This means: measure $d$, subtract it from $u$, **perfectly canceling** the disturbance before it affects the output.

### With feedforward + feedback:

$$Y_d(s) = \frac{G(s)(1 + C_{ff}(s))}{1 + C(s)G(s)} D(s) = 0 \quad \text{(if } C_{ff} = -1\text{)}$$

```
  y(t)
  
  0.1  ─ ─── Feedback only ──────── ← transient error
                  
  0.0  ──────────────────────────── ← FF + FB (nearly zero!)
           tiny blip only
  
      │   │
      0  disturbance
```

---

## Comparison Summary

| Method | SS Error | Transient | Requires |
|---|---|---|---|
| Open loop | 100% | Slow | Nothing |
| P control | 10% | Medium | Output sensor |
| PI control | 0% | Medium (with overshoot) | Output sensor |
| PI + Feedforward | 0% | Minimal | Output sensor + disturbance sensor |

---

## Practical Considerations

1. **Feedforward requires a disturbance model**: If $G_d(s)/G(s)$ is improper (more zeros than poles), perfect feedforward is impossible — use an approximation
2. **Feedforward alone has no robustness**: Model errors accumulate without correction. Always combine with feedback
3. **Disturbance must be measurable**: Many disturbances cannot be directly measured (internal friction, parameter drift)
4. **Two degrees of freedom**: Feedforward handles the measurable, predictable part; feedback handles the rest

🔧 **Practical**: In process control, measured disturbance feedforward is standard practice. Example: in a heat exchanger, measure the inlet flow rate change and adjust the steam valve immediately, rather than waiting for the outlet temperature to deviate.

💡 **Insight**: Feedforward is based on **knowledge** (model); feedback is based on **measurement** (error). The best control systems use both.
