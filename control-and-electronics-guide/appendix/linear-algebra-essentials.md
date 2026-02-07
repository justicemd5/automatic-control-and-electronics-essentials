# Linear Algebra Essentials

## Why Linear Algebra in Control?

Modern control theory is built on linear algebra:
- **State-space models**: $\dot{x} = Ax + Bu$ — matrix equations
- **Stability**: Determined by eigenvalues of $A$
- **Controllability/Observability**: Rank of specific matrices
- **Kalman filter**: Matrix operations (covariance propagation)
- **LQR**: Solving the Riccati equation

---

## Vectors and Matrices

### Notation

$$x = \begin{bmatrix} x_1 \\ x_2 \\ \vdots \\ x_n \end{bmatrix} \in \mathbb{R}^n, \qquad A = \begin{bmatrix} a_{11} & a_{12} & \cdots \\ a_{21} & a_{22} & \cdots \\ \vdots & & \ddots \end{bmatrix} \in \mathbb{R}^{m \times n}$$

### Key Operations

| Operation | Notation | Requirement |
|---|---|---|
| Addition | $A + B$ | Same dimensions |
| Scalar multiply | $\alpha A$ | — |
| Matrix multiply | $AB$ | Cols of $A$ = Rows of $B$ |
| Transpose | $A^T$ | $(AB)^T = B^T A^T$ |
| Inverse | $A^{-1}$ | Square, $\det(A) \neq 0$ |

---

## Determinant

### 2×2

$$\det\begin{bmatrix} a & b \\ c & d \end{bmatrix} = ad - bc$$

### 3×3 (Sarrus' rule or cofactor expansion)

$$\det(A) = a_{11}(a_{22}a_{33} - a_{23}a_{32}) - a_{12}(a_{21}a_{33} - a_{23}a_{31}) + a_{13}(a_{21}a_{32} - a_{22}a_{31})$$

### Properties

- $\det(AB) = \det(A)\det(B)$
- $\det(A^{-1}) = 1/\det(A)$
- $\det(A^T) = \det(A)$
- $\det(\alpha A) = \alpha^n \det(A)$ for $n \times n$ matrix

---

## Eigenvalues and Eigenvectors

### Definition

$$Av = \lambda v$$

$\lambda$ is an eigenvalue, $v$ is the corresponding eigenvector.

### Finding Eigenvalues

Solve the **characteristic equation**:

$$\det(A - \lambda I) = 0$$

For a 2×2 matrix $A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$:

$$\lambda^2 - (a+d)\lambda + (ad-bc) = 0$$

$$\lambda = \frac{(a+d) \pm \sqrt{(a+d)^2 - 4(ad-bc)}}{2}$$

### Connection to Control

| Eigenvalue Property | Control Meaning |
|---|---|
| $\text{Re}(\lambda) < 0$ for all $\lambda$ | System is **stable** |
| $\text{Re}(\lambda) > 0$ for any $\lambda$ | System is **unstable** |
| $\text{Re}(\lambda) = 0$ | Marginally stable (on the boundary) |
| $\text{Im}(\lambda) \neq 0$ | Oscillatory mode |
| $|\text{Re}(\lambda)|$ large | Fast mode |
| $|\text{Re}(\lambda)|$ small | Slow mode |

---

## Matrix Properties for Control

### Rank

The rank of $A$ is the number of linearly independent rows (or columns).

$$\text{rank}(A) \leq \min(m, n)$$

**Full rank** = $\text{rank}(A) = \min(m, n)$

### Controllability Matrix

$$\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}$$

System is **controllable** if and only if $\text{rank}(\mathcal{C}) = n$.

### Observability Matrix

$$\mathcal{O} = \begin{bmatrix} C \\ CA \\ CA^2 \\ \vdots \\ CA^{n-1} \end{bmatrix}$$

System is **observable** if and only if $\text{rank}(\mathcal{O}) = n$.

---

## Matrix Exponential

The solution to $\dot{x} = Ax$ is:

$$x(t) = e^{At} x(0)$$

Where:

$$e^{At} = I + At + \frac{(At)^2}{2!} + \frac{(At)^3}{3!} + \cdots$$

### For Diagonal Matrix

If $A = \text{diag}(\lambda_1, \lambda_2, \ldots, \lambda_n)$:

$$e^{At} = \text{diag}(e^{\lambda_1 t}, e^{\lambda_2 t}, \ldots, e^{\lambda_n t})$$

### For Diagonalizable Matrix

If $A = T \Lambda T^{-1}$ where $\Lambda = \text{diag}(\lambda_i)$:

$$e^{At} = T e^{\Lambda t} T^{-1}$$

---

## Positive Definite Matrices

A symmetric matrix $P = P^T$ is **positive definite** ($P > 0$) if:

$$x^T P x > 0 \quad \forall x \neq 0$$

Equivalently: all eigenvalues of $P$ are positive.

### Why It Matters

- **Lyapunov stability**: $V(x) = x^T P x$ is a valid Lyapunov function if $P > 0$
- **LQR cost weights**: $Q \geq 0$, $R > 0$ ensure meaningful cost
- **Kalman filter**: Covariance matrix $P$ must remain positive definite

### Testing

- Check eigenvalues: all $\lambda_i > 0$
- Check leading principal minors (Sylvester's criterion)
- For 2×2: $a > 0$ and $ad - b^2 > 0$

---

## Key Matrix Decompositions

| Decomposition | Form | Use in Control |
|---|---|---|
| **Eigendecomposition** | $A = T\Lambda T^{-1}$ | Modal analysis, decoupling |
| **SVD** | $A = U\Sigma V^T$ | Rank, conditioning, MIMO analysis |
| **Schur** | $A = QTQ^T$ | Stable eigenvalue computation |
| **Cholesky** | $A = LL^T$ | Covariance matrices, efficient solving |
| **QR** | $A = QR$ | Least squares, numerical stability |

### Singular Value Decomposition (SVD)

$$A = U \Sigma V^T$$

- $U$: left singular vectors (orthogonal)
- $\Sigma$: diagonal matrix of singular values $\sigma_1 \geq \sigma_2 \geq \cdots \geq 0$
- $V$: right singular vectors (orthogonal)

**In MIMO control**: Singular values of $G(j\omega)$ give the maximum and minimum gain at each frequency — essential for robust control analysis.

---

## Solving Linear Equations

### $Ax = b$

| Situation | Solution |
|---|---|
| $A$ square, non-singular | $x = A^{-1}b$ (use LU decomposition in practice) |
| Overdetermined ($m > n$) | Least squares: $x = (A^T A)^{-1} A^T b$ |
| Underdetermined ($m < n$) | Minimum norm: $x = A^T(AA^T)^{-1}b$ |

⚠️ **Never** compute $A^{-1}$ explicitly in numerical code. Use `numpy.linalg.solve(A, b)` or matrix factorizations instead. Computing the inverse is slower and numerically less stable.

---

## Quick Reference: NumPy/SciPy

```python
import numpy as np
from scipy.linalg import expm, solve_continuous_are

# Eigenvalues
eigenvalues, eigenvectors = np.linalg.eig(A)

# Matrix exponential
eAt = expm(A * t)

# Rank
r = np.linalg.matrix_rank(A)

# Determinant
d = np.linalg.det(A)

# Solve Ax = b (preferred over inv)
x = np.linalg.solve(A, b)

# SVD
U, sigma, Vt = np.linalg.svd(A)

# Riccati equation (for LQR)
P = solve_continuous_are(A, B, Q, R)
```

---

**← Back to [Appendix](README.md)**
