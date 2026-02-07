# Example: Block Diagram Reduction — Step by Step

## Purpose

Demonstrate the systematic reduction of a complex block diagram to a single transfer function using block diagram algebra rules.

---

## Problem Statement

Find the closed-loop transfer function $\frac{Y(s)}{R(s)}$ for the following system:

```
                          D(s)
                           │
                           ▼
  R(s)──►(+)──► G₁(s) ──►(+)──► G₂(s) ──►──┬──► Y(s)
          (-)                                 │
           ▲                                  │
           └──────────── H(s) ◄───────────────┘
```

Where:
- $G_1(s)$: Controller transfer function
- $G_2(s)$: Plant transfer function
- $H(s)$: Sensor/feedback transfer function
- $D(s)$: Disturbance input
- $R(s)$: Reference input

---

## Step-by-Step Reduction

### Step 1: Identify the Forward Path and Feedback Path

**Forward path** (from $R$ to $Y$): $G_1(s) \cdot G_2(s)$

**Feedback path** (from $Y$ back to the summing junction): $H(s)$

### Step 2: Apply the Closed-Loop Formula

For the reference input $R(s)$, with disturbance $D(s) = 0$:

$$\frac{Y(s)}{R(s)} = \frac{G_1(s) G_2(s)}{1 + G_1(s) G_2(s) H(s)}$$

### Step 3: Find the Disturbance Transfer Function

For the disturbance input $D(s)$, with reference $R(s) = 0$:

The disturbance enters *after* $G_1$ but *before* $G_2$. The forward path from $D$ to $Y$ is just $G_2(s)$, and the loop gain is still $G_1(s) G_2(s) H(s)$.

$$\frac{Y(s)}{D(s)} = \frac{G_2(s)}{1 + G_1(s) G_2(s) H(s)}$$

### Step 4: Complete Output Expression (Superposition)

Since the system is linear, we can superpose:

$$Y(s) = \frac{G_1(s) G_2(s)}{1 + G_1(s) G_2(s) H(s)} R(s) + \frac{G_2(s)}{1 + G_1(s) G_2(s) H(s)} D(s)$$

---

## Numerical Example

Let:
- $G_1(s) = 10$ (proportional controller)
- $G_2(s) = \frac{1}{s + 1}$ (first-order plant)
- $H(s) = 1$ (unity feedback)

### Reference-to-Output Transfer Function

$$T(s) = \frac{10 \cdot \frac{1}{s+1}}{1 + 10 \cdot \frac{1}{s+1} \cdot 1} = \frac{\frac{10}{s+1}}{\frac{s+1+10}{s+1}} = \frac{10}{s + 11}$$

**Interpretation:**
- Open-loop pole at $s = -1$ (time constant = 1 sec)
- Closed-loop pole at $s = -11$ (time constant = 1/11 ≈ 0.09 sec)
- Feedback made the system **11× faster**
- DC gain: $T(0) = 10/11 ≈ 0.91$ — there is steady-state error (not unity)

### Disturbance-to-Output Transfer Function

$$\frac{Y(s)}{D(s)} = \frac{\frac{1}{s+1}}{\frac{s+11}{s+1}} = \frac{1}{s + 11}$$

**Interpretation:**
- DC gain from disturbance: $1/11 ≈ 0.09$
- Disturbance is attenuated by a factor of 11 compared to open-loop
- Higher controller gain $G_1$ → more disturbance rejection

---

## Common Block Diagram Manipulations

### Moving a Pickoff Point Forward (Past a Block)

```
  Before:                          After:
  ──► G(s) ──►──┬──►              ──► G(s) ──►──┬──►
                │                                │
                ▼                      ┌──────┐  ▼
              (branch)                 │ 1/G(s)│◄─┘
                                       └──────┘
```

When you move a pickoff point **forward** past $G(s)$, you must add $\frac{1}{G(s)}$ in the branch.

### Moving a Summing Junction Forward (Past a Block)

```
  Before:                          After:
  X──►(+)──► G(s) ──►            X──► G(s) ──►(+)──►
       ▲                                        ▲
       │                              ┌──────┐  │
       Z                        Z ──► │ G(s) │──┘
                                      └──────┘
```

When you move a summing junction **forward** past $G(s)$, you must add $G(s)$ in the other branch.

---

## Verification Technique: Mason's Gain Formula

For complex diagrams, Mason's formula provides the transfer function directly from the signal flow graph:

$$T = \frac{\sum_k P_k \Delta_k}{\Delta}$$

Where:
- $P_k$ = gain of the $k$-th forward path
- $\Delta = 1 - \sum L_i + \sum L_i L_j - \cdots$ (loop gains)
- $\Delta_k$ = cofactor for path $k$

For our example:
- Forward path: $P_1 = G_1 G_2$
- Loop gain: $L_1 = -G_1 G_2 H$
- $\Delta = 1 + G_1 G_2 H$
- $\Delta_1 = 1$ (no non-touching loops)

$$T = \frac{G_1 G_2}{1 + G_1 G_2 H}$$ ✓

---

## Expected Results

- The closed-loop transfer function has the characteristic polynomial $1 + G_1 G_2 H$ in the denominator
- Higher loop gain reduces sensitivity to disturbances and parameter variations
- The closed-loop poles (roots of the characteristic polynomial) determine stability and transient behavior
- These reduction rules apply to ANY linear, time-invariant system regardless of physical domain
