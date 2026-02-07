# Example: Controllability and Observability Analysis

## Purpose
Demonstrate how to check controllability and observability for a given state-space system and interpret the results physically.

---

## System: DC Motor Position Control

State variables:
- $x_1 = \theta$ (angular position)
- $x_2 = \dot{\theta}$ (angular velocity)
- $x_3 = i$ (armature current)

$$A = \begin{bmatrix} 0 & 1 & 0 \\ 0 & -B/J & K_t/J \\ 0 & -K_b/L & -R/L \end{bmatrix}, \quad B = \begin{bmatrix} 0 \\ 0 \\ 1/L \end{bmatrix}$$

$$C = \begin{bmatrix} 1 & 0 & 0 \end{bmatrix} \quad \text{(measuring position only)}$$

**Numerical values** ($J = 0.01$, $B = 0.1$, $K_t = K_b = 0.01$, $R = 1$, $L = 0.5$):

$$A = \begin{bmatrix} 0 & 1 & 0 \\ 0 & -10 & 1 \\ 0 & -0.02 & -2 \end{bmatrix}, \quad B = \begin{bmatrix} 0 \\ 0 \\ 2 \end{bmatrix}, \quad C = \begin{bmatrix} 1 & 0 & 0 \end{bmatrix}$$

---

## Controllability Check

$$\mathcal{C} = \begin{bmatrix} B & AB & A^2B \end{bmatrix}$$

$$AB = \begin{bmatrix} 0 \\ 2 \\ -4 \end{bmatrix}, \quad A^2B = \begin{bmatrix} 2 \\ -28 \\ 7.96 \end{bmatrix}$$

$$\mathcal{C} = \begin{bmatrix} 0 & 0 & 2 \\ 0 & 2 & -28 \\ 2 & -4 & 7.96 \end{bmatrix}$$

$$\det(\mathcal{C}) = 0(2 \times 7.96 - (-28)(-4)) - 0(\ldots) + 2(0 - 4) = -8 \neq 0$$

$$\text{rank}(\mathcal{C}) = 3 = n \quad \implies \quad \text{System is CONTROLLABLE} \; ✓$$

**Physical interpretation**: The voltage input $u$ drives current $i$, which creates torque $K_t i$, which accelerates the rotor $\ddot{\theta}$. All three states are coupled to the input through the chain of dynamics.

---

## Observability Check

$$\mathcal{O} = \begin{bmatrix} C \\ CA \\ CA^2 \end{bmatrix}$$

$$CA = \begin{bmatrix} 0 & 1 & 0 \end{bmatrix}, \quad CA^2 = \begin{bmatrix} 0 & -10 & 1 \end{bmatrix}$$

$$\mathcal{O} = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & -10 & 1 \end{bmatrix}$$

$$\det(\mathcal{O}) = 1 \cdot (1 \times 1 - 0 \times (-10)) = 1 \neq 0$$

$$\text{rank}(\mathcal{O}) = 3 = n \quad \implies \quad \text{System is OBSERVABLE} \; ✓$$

**Physical interpretation**: By measuring only position $\theta$, we can infer velocity $\dot{\theta}$ (from the derivative) and current $i$ (from the second derivative and the model).

---

## Uncontrollable System Example

Consider adding an unconnected thermal mode:

$$A' = \begin{bmatrix} 0 & 1 & 0 & 0 \\ 0 & -10 & 1 & 0 \\ 0 & -0.02 & -2 & 0 \\ 0 & 0 & 0 & -0.01 \end{bmatrix}, \quad B' = \begin{bmatrix} 0 \\ 0 \\ 2 \\ 0 \end{bmatrix}$$

The 4th state (temperature) has eigenvalue $\lambda_4 = -0.01$ but **no connection to the input** ($B'_4 = 0$). The controllability matrix will have rank 3 < 4.

⚠️ **Pitfall**: An uncontrollable mode cannot be moved by feedback. If it's unstable, the system **cannot be stabilized** by any state-feedback controller. If it's stable but slow, the controller cannot speed it up.

---

## Unobservable System Example

If instead we measure only current ($C' = [0\;0\;1]$):

$$\mathcal{O}' = \begin{bmatrix} 0 & 0 & 1 \\ 0 & -0.02 & -2 \\ 0 & 0.196 & 3.96 \end{bmatrix}$$

The first column is all zeros → $\text{rank}(\mathcal{O}') < 3$ → **position $\theta$ is unobservable** from current measurement alone.

**Physical interpretation**: Current doesn't carry information about absolute position — only about acceleration. The position information is lost due to the integration.

---

## PBH Test (Alternative)

A mode $\lambda_i$ is controllable iff:

$$\text{rank}\begin{bmatrix} \lambda_i I - A & B \end{bmatrix} = n$$

A mode $\lambda_i$ is observable iff:

$$\text{rank}\begin{bmatrix} \lambda_i I - A \\ C \end{bmatrix} = n$$

This test identifies **which specific modes** are uncontrollable/unobservable.

---

## Summary

| Property | Test | Requirement | Enables |
|---|---|---|---|
| Controllability | $\text{rank}(\mathcal{C}) = n$ | Can reach all states | Pole placement, stabilization |
| Observability | $\text{rank}(\mathcal{O}) = n$ | Can estimate all states | Observer design |
| Stabilizability | Uncontrollable modes stable | Weaker than controllability | Practical stabilization |
| Detectability | Unobservable modes stable | Weaker than observability | Practical observer design |

💡 **Insight**: In practice, a system doesn't need to be fully controllable/observable — it only needs to be **stabilizable** and **detectable**. If the uncontrollable/unobservable modes are already stable, the system can still be controlled effectively.
