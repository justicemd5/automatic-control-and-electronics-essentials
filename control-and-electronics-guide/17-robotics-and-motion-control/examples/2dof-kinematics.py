"""
2-DOF Planar Robot: Forward and Inverse Kinematics
====================================================

Purpose:
    Compute and visualize FK/IK for a 2-link planar manipulator,
    demonstrating the fundamental concepts of robot kinematics.

Robot:
    - Link 1: length L1, angle θ1 from x-axis
    - Link 2: length L2, angle θ2 from link 1
    - End-effector position: (x, y)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# =============================================================================
# Robot Parameters
# =============================================================================
L1 = 1.0   # Link 1 length [m]
L2 = 0.8   # Link 2 length [m]


# =============================================================================
# Forward Kinematics
# =============================================================================
def forward_kinematics(theta1, theta2, l1=L1, l2=L2):
    """
    Compute end-effector position from joint angles.
    
    Parameters:
        theta1: Joint 1 angle [rad] (from x-axis)
        theta2: Joint 2 angle [rad] (from link 1)
    
    Returns:
        x, y: End-effector position
        elbow_x, elbow_y: Elbow (joint 2) position
    """
    # Joint 2 (elbow) position
    elbow_x = l1 * np.cos(theta1)
    elbow_y = l1 * np.sin(theta1)
    
    # End-effector position
    x = elbow_x + l2 * np.cos(theta1 + theta2)
    y = elbow_y + l2 * np.sin(theta1 + theta2)
    
    return x, y, elbow_x, elbow_y


# =============================================================================
# Inverse Kinematics
# =============================================================================
def inverse_kinematics(x, y, l1=L1, l2=L2, elbow='up'):
    """
    Compute joint angles from end-effector position.
    
    Two solutions exist (elbow-up and elbow-down).
    
    Parameters:
        x, y: Desired end-effector position
        elbow: 'up' or 'down' configuration
    
    Returns:
        theta1, theta2: Joint angles [rad]
        reachable: True if position is reachable
    """
    # Check reachability
    d = np.sqrt(x**2 + y**2)
    if d > l1 + l2 or d < abs(l1 - l2):
        return None, None, False
    
    # Cosine law for theta2
    cos_theta2 = (x**2 + y**2 - l1**2 - l2**2) / (2 * l1 * l2)
    cos_theta2 = np.clip(cos_theta2, -1, 1)  # Numerical safety
    
    if elbow == 'up':
        theta2 = -np.arccos(cos_theta2)  # Elbow up (negative θ2)
    else:
        theta2 = np.arccos(cos_theta2)   # Elbow down (positive θ2)
    
    # Theta1 from geometry
    k1 = l1 + l2 * np.cos(theta2)
    k2 = l2 * np.sin(theta2)
    theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)
    
    return theta1, theta2, True


# =============================================================================
# Jacobian
# =============================================================================
def jacobian(theta1, theta2, l1=L1, l2=L2):
    """
    Compute the 2x2 Jacobian matrix.
    
    J relates joint velocities to end-effector velocities:
    [ẋ]   [J11  J12] [θ̇1]
    [ẏ] = [J21  J22] [θ̇2]
    """
    s1 = np.sin(theta1)
    c1 = np.cos(theta1)
    s12 = np.sin(theta1 + theta2)
    c12 = np.cos(theta1 + theta2)
    
    J = np.array([
        [-l1 * s1 - l2 * s12,  -l2 * s12],
        [ l1 * c1 + l2 * c12,   l2 * c12]
    ])
    
    return J


# =============================================================================
# Demonstration
# =============================================================================

# --- 1. Forward Kinematics Examples ---
print("=" * 60)
print("Forward Kinematics Examples")
print("=" * 60)

test_angles = [
    (0, 0, "Fully extended along x-axis"),
    (np.pi/4, 0, "Extended at 45°"),
    (np.pi/2, -np.pi/2, "Elbow bent 90°, reaching right"),
    (np.pi/4, np.pi/4, "Both joints at 45°"),
]

for t1, t2, desc in test_angles:
    x, y, ex, ey = forward_kinematics(t1, t2)
    print(f"  θ1={np.degrees(t1):6.1f}°, θ2={np.degrees(t2):6.1f}° → "
          f"({x:.3f}, {y:.3f})  [{desc}]")


# --- 2. Inverse Kinematics Example ---
print(f"\n{'=' * 60}")
print("Inverse Kinematics: Target (1.0, 0.5)")
print("=" * 60)

xd, yd = 1.0, 0.5
for config in ['up', 'down']:
    t1, t2, ok = inverse_kinematics(xd, yd, elbow=config)
    if ok:
        xv, yv, _, _ = forward_kinematics(t1, t2)
        err = np.sqrt((xv - xd)**2 + (yv - yd)**2)
        print(f"  Elbow-{config:4s}: θ1={np.degrees(t1):7.2f}°, "
              f"θ2={np.degrees(t2):7.2f}°  (verify: ({xv:.4f}, {yv:.4f}), "
              f"error={err:.2e})")


# --- 3. Jacobian and Singularity Analysis ---
print(f"\n{'=' * 60}")
print("Jacobian Analysis")
print("=" * 60)

t1, t2 = np.radians(45), np.radians(-30)
J = jacobian(t1, t2)
det_J = np.linalg.det(J)
print(f"  At θ1=45°, θ2=-30°:")
print(f"  J = [{J[0,0]:7.4f}  {J[0,1]:7.4f}]")
print(f"      [{J[1,0]:7.4f}  {J[1,1]:7.4f}]")
print(f"  det(J) = {det_J:.4f}")

# Singularity (arm fully extended)
J_sing = jacobian(0, 0)
det_sing = np.linalg.det(J_sing)
print(f"\n  At θ1=0°, θ2=0° (SINGULARITY — arm extended):")
print(f"  det(J) = {det_sing:.6f}  ← Near zero = singular!")


# =============================================================================
# Visualization
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# --- Plot 1: Two IK solutions ---
ax = axes[0]
ax.set_title('Inverse Kinematics: Two Solutions', fontsize=12)

xd, yd = 1.0, 0.5
for config, color, ls in [('up', 'blue', '-'), ('down', 'red', '--')]:
    t1, t2, _ = inverse_kinematics(xd, yd, elbow=config)
    x, y, ex, ey = forward_kinematics(t1, t2)
    
    # Draw links
    ax.plot([0, ex, x], [0, ey, y], f'{color[0]}o-', linewidth=3,
            markersize=8, label=f'Elbow {config}', linestyle=ls)

ax.plot(xd, yd, 'g*', markersize=20, label='Target')
ax.add_patch(Circle((0, 0), L1 + L2, fill=False, linestyle=':', alpha=0.3))
ax.add_patch(Circle((0, 0), abs(L1 - L2), fill=False, linestyle=':', alpha=0.3))
ax.set_xlim(-0.5, 2.0)
ax.set_ylim(-1.0, 1.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.legend()
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')

# --- Plot 2: Workspace visualization ---
ax = axes[1]
ax.set_title('Reachable Workspace', fontsize=12)

# Sample workspace
theta1_range = np.linspace(-np.pi, np.pi, 200)
theta2_range = np.linspace(-np.pi, np.pi, 200)
T1, T2 = np.meshgrid(theta1_range, theta2_range)

X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)

ax.scatter(X.flatten(), Y.flatten(), s=0.1, alpha=0.1, c='blue')
ax.add_patch(Circle((0, 0), L1 + L2, fill=False, color='red', linestyle='--',
                      label=f'Outer: r={L1+L2}'))
ax.add_patch(Circle((0, 0), abs(L1 - L2), fill=False, color='orange',
                      linestyle='--', label=f'Inner: r={abs(L1-L2)}'))
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 2.2)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=9)
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')

# --- Plot 3: Jacobian determinant (manipulability) ---
ax = axes[2]
ax.set_title('Manipulability (|det(J)|)', fontsize=12)

t1_grid = np.linspace(-np.pi, np.pi, 100)
t2_grid = np.linspace(-np.pi, np.pi, 100)
T1g, T2g = np.meshgrid(t1_grid, t2_grid)

# det(J) = L1 * L2 * sin(θ2)
det_J_grid = np.abs(L1 * L2 * np.sin(T2g))

c = ax.contourf(np.degrees(T1g), np.degrees(T2g), det_J_grid, levels=20, cmap='viridis')
plt.colorbar(c, ax=ax, label='|det(J)|')
ax.contour(np.degrees(T1g), np.degrees(T2g), det_J_grid, levels=[0.01],
           colors='red', linewidths=2)
ax.set_xlabel('θ1 [°]')
ax.set_ylabel('θ2 [°]')
ax.text(0, 5, 'Singular\n(θ2=0°)', color='red', ha='center', fontsize=10)
ax.text(0, -175, 'Singular\n(θ2=±180°)', color='red', ha='center', fontsize=10)

plt.tight_layout()
plt.savefig('2dof-kinematics.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nKey Observations:")
print("  1. Two IK solutions exist for each reachable point (elbow up/down)")
print("  2. Workspace is an annular ring between r=|L1-L2| and r=L1+L2")
print(f"  3. Singularity at θ2=0° or ±180° (det(J)=L1·L2·sin(θ2)=0)")
print("  4. Maximum manipulability at θ2=±90° (best dexterity)")
