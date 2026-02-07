# Example: Nyquist Stability Criterion — Worked Example

## Purpose
Apply the Nyquist stability criterion to determine the stability of a feedback system, especially one where Bode analysis alone is ambiguous.

---

## System

$$L(s) = \frac{K}{s(s+1)(s+2)}$$

### Open-Loop Poles

$s = 0, -1, -2$ → All in LHP or on imaginary axis → $P = 0$ (no open-loop RHP poles)

---

## Step 1: Compute $L(j\omega)$

$$L(j\omega) = \frac{K}{j\omega(j\omega+1)(j\omega+2)}$$

Rationalize:

$$L(j\omega) = \frac{K}{j\omega(j\omega+1)(j\omega+2)} = \frac{K}{(j\omega)(2 - \omega^2 + j3\omega)}$$

$$= \frac{K}{(-3\omega^2) + j(2\omega - \omega^3)}$$

Real part: $\text{Re}[L] = \frac{K(-3\omega^2)}{9\omega^4 + (2\omega - \omega^3)^2}$

Imaginary part: $\text{Im}[L] = \frac{-K(2\omega - \omega^3)}{9\omega^4 + (2\omega - \omega^3)^2}$

---

## Step 2: Key Points on the Nyquist Plot

| Frequency | $|L(j\omega)|$ | $\angle L(j\omega)$ | Nyquist Point |
|---|---|---|---|
| $\omega \to 0^+$ | $\to \infty$ | $-90°$ | Far down on negative imaginary axis |
| $\omega = 1$ | $K/(1 \cdot \sqrt{2} \cdot \sqrt{5})$ | $-90° - 45° - 26.6° = -161.6°$ | Third quadrant |
| $\omega = \sqrt{2}$ | ... | $-180°$ ← **phase crossover!** | Crosses negative real axis |
| $\omega \to \infty$ | $\to 0$ | $-270°$ | Approaches origin from below |

### Phase Crossover Frequency

At $\omega_\pi$ where $\angle L = -180°$:

$$\angle L = -90° - \arctan(\omega) - \arctan(\omega/2) = -180°$$
$$\arctan(\omega) + \arctan(\omega/2) = 90°$$

Using the identity: $\arctan(a) + \arctan(b) = 90°$ when $ab = 1$:

$$\omega \cdot \frac{\omega}{2} = 1 \implies \omega^2 = 2 \implies \omega_\pi = \sqrt{2}$$

### Magnitude at Phase Crossover

$$|L(j\sqrt{2})| = \frac{K}{\sqrt{2} \cdot \sqrt{1+2} \cdot \sqrt{4+2}} = \frac{K}{\sqrt{2} \cdot \sqrt{3} \cdot \sqrt{6}} = \frac{K}{6}$$

---

## Step 3: Apply Nyquist Criterion

The Nyquist plot crosses the negative real axis at $(-K/6, 0)$.

```
  Nyquist Plot:
  
  Im
   │
   │         ω = 0⁺ (start, going down)
   │         │
   │         ▼
   │
  ─┼─────(−K/6)─────────────── Re
   │    ↑                     
   │    │ crosses real axis    
   │    │ at ω = √2           
   │         
   │         ω → ∞ (approaches origin)
```

**For stability** ($P = 0$): The plot must NOT encircle $(-1, 0)$.

This requires:

$$\frac{K}{6} < 1 \implies K < 6$$

---

## Step 4: Stability Results

| Gain $K$ | $-K/6$ | Encircles $(-1,0)$? | Stable? |
|---|---|---|---|
| $K = 1$ | $-0.167$ | No | ✓ Stable |
| $K = 3$ | $-0.500$ | No | ✓ Stable |
| $K = 6$ | $-1.000$ | Passes through! | Marginally stable |
| $K = 12$ | $-2.000$ | Yes (2 CW) | ✗ Unstable (2 RHP poles) |

### Gain Margin

$$GM = \frac{1}{|L(j\omega_\pi)|} = \frac{1}{K/6} = \frac{6}{K}$$

For $K = 3$: $GM = 2 = 6$ dB  
For $K = 1$: $GM = 6 = 15.6$ dB

---

## Verification with Routh Criterion

Characteristic equation: $s^3 + 3s^2 + 2s + K = 0$

Routh array:

| $s^3$ | 1 | 2 |
|---|---|---|
| $s^2$ | 3 | K |
| $s^1$ | $(6-K)/3$ | 0 |
| $s^0$ | K | — |

**Stability conditions:**
1. $K > 0$ ← from $s^0$ row
2. $(6-K)/3 > 0 \implies K < 6$ ← from $s^1$ row

$$\boxed{0 < K < 6}$$

This confirms the Nyquist result exactly!

---

## When Nyquist is Essential

⚠️ **Pitfall**: The Nyquist criterion handles cases that Bode/Routh cannot:

1. **Open-loop unstable systems** ($P > 0$): Nyquist counts encirclements to determine if feedback stabilizes the system
2. **Non-minimum phase systems**: Bode plot phase doesn't tell the full story
3. **Time delays**: $e^{-sT}$ wraps the Nyquist plot, potentially creating additional encirclements

💡 **Insight**: For open-loop stable systems, the Nyquist criterion reduces to: "The Nyquist plot must stay to the right of $(-1, 0)$" — which is equivalent to checking gain and phase margins on a Bode plot.
