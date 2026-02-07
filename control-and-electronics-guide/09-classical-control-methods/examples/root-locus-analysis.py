"""
Root Locus Analysis
====================

Purpose:
    Plot the root locus of a feedback system, determine the gain
    for desired closed-loop pole locations, and verify the design
    with step response simulation.

System:
    G(s) = 1 / [s(s+1)(s+5)]
    
Design Goal:
    Find K for closed-loop damping ratio ζ = 0.5

Expected Behavior:
    - Root locus starts at open-loop poles (0, -1, -5)
    - Branches move toward infinity along asymptotes
    - Gain K selected where locus crosses ζ = 0.5 line
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


# =============================================================================
# Plant Definition
# =============================================================================
# G(s) = 1 / [s(s+1)(s+5)] = 1 / (s^3 + 6s^2 + 5s)
num_G = [1]
den_G = [1, 6, 5, 0]

# Open-loop poles and zeros
poles = np.roots(den_G)
zeros = np.roots(num_G)

print("Open-Loop Analysis:")
print(f"  Poles: {poles}")
print(f"  Zeros: {zeros}")
print(f"  Number of poles (n): {len(poles)}")
print(f"  Number of zeros (m): {len(zeros)}")


# =============================================================================
# Root Locus Rules
# =============================================================================
n = len(poles)
m = len(zeros)

# Asymptotes
n_asymptotes = n - m
angles = [(2*q + 1) * 180 / n_asymptotes for q in range(n_asymptotes)]
centroid = (np.sum(poles.real) - np.sum(zeros.real)) / n_asymptotes

print(f"\nRoot Locus Rules:")
print(f"  Number of branches: {n}")
print(f"  Asymptotes: {n_asymptotes}")
print(f"  Asymptote angles: {angles}°")
print(f"  Centroid: σ_a = {centroid:.2f}")


# =============================================================================
# Compute Root Locus (Manual Computation)
# =============================================================================
# For each K, find roots of: den_G + K * num_G = 0
# i.e., s^3 + 6s^2 + 5s + K = 0

K_values = np.linspace(0, 50, 5000)
root_array = np.zeros((len(K_values), n), dtype=complex)

for i, K in enumerate(K_values):
    char_poly = den_G.copy()
    char_poly[-1] += K  # Add K to constant term
    root_array[i, :] = np.roots(char_poly)

# Sort roots by proximity to previous roots for smooth lines
for i in range(1, len(K_values)):
    for j in range(n):
        distances = np.abs(root_array[i, :] - root_array[i-1, j])
        closest = np.argmin(distances)
        if closest != j:
            root_array[i, [j, closest]] = root_array[i, [closest, j]]


# =============================================================================
# Find K for ζ = 0.5
# =============================================================================
zeta_target = 0.5
theta_target = np.arccos(zeta_target)  # Angle of ζ line from negative real axis

# For each K, find the dominant (closest to imaginary axis) complex pole pair
K_design = None
poles_design = None

for i, K in enumerate(K_values):
    roots = root_array[i, :]
    complex_roots = roots[np.abs(roots.imag) > 0.01]
    
    if len(complex_roots) >= 2:
        # Find the pair closest to the imaginary axis
        dominant = complex_roots[np.argmax(complex_roots.real)]
        zeta = -dominant.real / np.abs(dominant)
        
        if abs(zeta - zeta_target) < 0.01:
            K_design = K
            poles_design = roots
            break

if K_design is not None:
    print(f"\nDesign Result:")
    print(f"  K for ζ = {zeta_target}: K = {K_design:.2f}")
    print(f"  Closed-loop poles:")
    for p in poles_design:
        if abs(p.imag) < 0.001:
            print(f"    s = {p.real:.3f}")
        else:
            print(f"    s = {p.real:.3f} ± j{abs(p.imag):.3f}")
    
    dominant = poles_design[np.abs(poles_design.imag) > 0.01]
    if len(dominant) > 0:
        dom = dominant[0]
        wn = np.abs(dom)
        zeta_actual = -dom.real / wn
        print(f"  ωn = {wn:.2f} rad/s, ζ = {zeta_actual:.3f}")
else:
    print("\n  Could not find K for target ζ. Using K = 10.")
    K_design = 10
    char_poly_design = den_G.copy()
    char_poly_design[-1] += K_design
    poles_design = np.roots(char_poly_design)


# =============================================================================
# Plot Root Locus
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 8))

# Plot root locus branches
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
for j in range(n):
    ax.plot(root_array[:, j].real, root_array[:, j].imag,
            color=colors[j % len(colors)], linewidth=1.5, alpha=0.8)

# Plot open-loop poles
ax.plot(poles.real, poles.imag, 'rx', markersize=12, markeredgewidth=3,
        label='Open-loop poles')

# Plot ζ = 0.5 lines
theta = np.arccos(zeta_target)
r = np.linspace(0, 6, 100)
ax.plot(-r * np.cos(theta), r * np.sin(theta), 'g--', alpha=0.5,
        label=f'ζ = {zeta_target} line')
ax.plot(-r * np.cos(theta), -r * np.sin(theta), 'g--', alpha=0.5)

# Plot design point
if poles_design is not None:
    ax.plot(poles_design.real, poles_design.imag, 'ko', markersize=10,
            markerfacecolor='yellow', markeredgewidth=2,
            label=f'Design point (K={K_design:.1f})')

# Plot asymptotes
for angle in angles:
    angle_rad = np.radians(angle)
    r_asym = np.linspace(0, 8, 100)
    ax.plot(centroid + r_asym * np.cos(angle_rad),
            r_asym * np.sin(angle_rad),
            'k:', alpha=0.3)
ax.plot(centroid, 0, 'k+', markersize=15, markeredgewidth=2,
        label=f'Centroid (σ={centroid:.2f})')

ax.set_xlabel('Real Axis')
ax.set_ylabel('Imaginary Axis')
ax.set_title('Root Locus: G(s) = 1/[s(s+1)(s+5)]')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xlim(-7, 2)
ax.set_ylim(-4, 4)
ax.set_aspect('equal')
ax.axhline(y=0, color='k', linewidth=0.5)
ax.axvline(x=0, color='k', linewidth=0.5)

plt.tight_layout()
plt.savefig('root-locus.png', dpi=150, bbox_inches='tight')
plt.show()


# =============================================================================
# Step Response at Design Gain
# =============================================================================
num_CL = [K_design]
den_CL = den_G.copy()
den_CL[-1] += K_design

T_cl = signal.TransferFunction(num_CL, den_CL)
t = np.linspace(0, 8, 1000)
t_out, y_out = signal.step(T_cl, T=t)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(t_out, y_out, 'b-', linewidth=2)
ax2.axhline(y=1.0, color='k', linestyle=':', alpha=0.5)
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('Output')
ax2.set_title(f'Closed-Loop Step Response (K = {K_design:.1f})')
ax2.grid(True, alpha=0.3)

# Annotate metrics
overshoot = (np.max(y_out) - 1) * 100
tp = t_out[np.argmax(y_out)]
ax2.annotate(f'Overshoot: {overshoot:.1f}%\nPeak time: {tp:.2f}s',
             xy=(tp, np.max(y_out)), fontsize=11,
             xytext=(tp + 1, np.max(y_out)),
             arrowprops=dict(arrowstyle='->', color='red'),
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.savefig('root-locus-step.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nStep Response Metrics:")
print(f"  Overshoot: {overshoot:.1f}%")
print(f"  Peak time: {tp:.2f} s")
