"""
Trajectory Planning: Trapezoidal and S-Curve Profiles
======================================================

Purpose:
    Generate smooth motion profiles for robot joints or
    linear axes, comparing trapezoidal (constant acceleration)
    and S-curve (limited jerk) profiles.
"""

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Trapezoidal Velocity Profile
# =============================================================================
def trapezoidal_profile(q_start, q_end, v_max, a_max, dt=0.001):
    """
    Generate trapezoidal velocity profile.
    
    Phases:
        1. Acceleration (constant a_max)
        2. Cruise (constant v_max)
        3. Deceleration (constant -a_max)
    
    Returns:
        t, pos, vel, acc: Time-series arrays
    """
    distance = abs(q_end - q_start)
    sign = np.sign(q_end - q_start)
    
    # Time to accelerate to v_max
    t_accel = v_max / a_max
    
    # Distance during acceleration + deceleration
    d_accel = v_max * t_accel  # = v_max² / a_max
    
    if d_accel > distance:
        # Triangular profile (can't reach v_max)
        t_accel = np.sqrt(distance / a_max)
        v_peak = a_max * t_accel
        t_cruise = 0
        t_total = 2 * t_accel
    else:
        # Full trapezoidal
        v_peak = v_max
        d_cruise = distance - d_accel
        t_cruise = d_cruise / v_max
        t_total = 2 * t_accel + t_cruise
    
    t = np.arange(0, t_total + dt, dt)
    pos = np.zeros_like(t)
    vel = np.zeros_like(t)
    acc = np.zeros_like(t)
    
    for i, ti in enumerate(t):
        if ti <= t_accel:
            # Acceleration phase
            acc[i] = a_max
            vel[i] = a_max * ti
            pos[i] = 0.5 * a_max * ti**2
        elif ti <= t_accel + t_cruise:
            # Cruise phase
            acc[i] = 0
            vel[i] = v_peak
            pos[i] = 0.5 * a_max * t_accel**2 + v_peak * (ti - t_accel)
        else:
            # Deceleration phase
            td = ti - t_accel - t_cruise
            acc[i] = -a_max
            vel[i] = v_peak - a_max * td
            pos[i] = (0.5 * a_max * t_accel**2 +
                       v_peak * t_cruise +
                       v_peak * td - 0.5 * a_max * td**2)
    
    # Apply direction and offset
    pos = q_start + sign * pos
    vel = sign * vel
    acc = sign * acc
    
    return t, pos, vel, acc


# =============================================================================
# S-Curve (7-Segment) Velocity Profile
# =============================================================================
def s_curve_profile(q_start, q_end, v_max, a_max, j_max, dt=0.001):
    """
    Generate S-curve (limited jerk) velocity profile.
    
    7 Phases:
        1. Increasing acceleration (jerk = +j_max)
        2. Constant acceleration (jerk = 0)
        3. Decreasing acceleration (jerk = -j_max)
        4. Cruise (zero acceleration)
        5. Increasing deceleration (jerk = -j_max)
        6. Constant deceleration (jerk = 0)
        7. Decreasing deceleration (jerk = +j_max)
    
    Returns:
        t, pos, vel, acc, jerk: Time-series arrays
    """
    distance = abs(q_end - q_start)
    sign = np.sign(q_end - q_start)
    
    # Time for jerk phase
    tj = a_max / j_max  # Time to reach max accel
    
    # Velocity gained during accel (phases 1-3)
    # v_accel = a_max * (tj + ta) where ta = time at constant accel
    # If ta = 0 (triangular accel): v_accel = a_max * tj = a_max² / j_max
    
    v_accel_min = a_max * tj  # Velocity from jerk phases only (no constant accel phase)
    
    if v_accel_min >= v_max:
        # Can't reach a_max; reduce tj
        tj = np.sqrt(v_max / j_max)
        ta = 0
        v_peak = j_max * tj**2
    else:
        ta = (v_max - v_accel_min) / a_max  # Time at constant acceleration
        v_peak = v_max
    
    # Distance during acceleration phases
    d_accel = v_peak * (tj + ta)  # Approximate; exact is more complex
    
    # Cruise time
    if 2 * d_accel > distance:
        # Reduce v_max (simplified: fall back to proportional reduction)
        ratio = distance / (2 * d_accel)
        v_peak *= ratio
        ta = max(0, (v_peak - a_max * tj) / a_max)
    
    t_cruise = max(0, (distance - 2 * d_accel) / v_peak) if v_peak > 0 else 0
    
    # Total time
    t_total = 2 * (2 * tj + ta) + t_cruise
    
    # Generate profile by integrating jerk
    t = np.arange(0, t_total + dt, dt)
    jerk = np.zeros_like(t)
    acc = np.zeros_like(t)
    vel = np.zeros_like(t)
    pos = np.zeros_like(t)
    
    # Phase boundaries
    t1 = tj                           # End of jerk-up
    t2 = tj + ta                      # End of constant accel
    t3 = 2 * tj + ta                  # End of jerk-down
    t4 = t3 + t_cruise                # End of cruise
    t5 = t4 + tj                      # End of jerk-down (decel)
    t6 = t4 + tj + ta                 # End of constant decel
    t7 = t4 + 2 * tj + ta            # End of jerk-up (decel)
    
    for i in range(1, len(t)):
        ti = t[i]
        
        if ti <= t1:
            jerk[i] = j_max
        elif ti <= t2:
            jerk[i] = 0
        elif ti <= t3:
            jerk[i] = -j_max
        elif ti <= t4:
            jerk[i] = 0
        elif ti <= t5:
            jerk[i] = -j_max
        elif ti <= t6:
            jerk[i] = 0
        else:
            jerk[i] = j_max
        
        # Integrate
        acc[i] = acc[i-1] + jerk[i] * dt
        vel[i] = vel[i-1] + acc[i] * dt
        pos[i] = pos[i-1] + vel[i] * dt
    
    # Clip small negative velocities (numerical artifact)
    vel = np.maximum(vel, 0)
    
    pos = q_start + sign * pos
    vel = sign * vel
    acc = sign * acc
    jerk = sign * jerk
    
    return t, pos, vel, acc, jerk


# =============================================================================
# Generate and Compare Profiles
# =============================================================================
# Motion parameters
q_start = 0.0      # Start position [rad or m]
q_end = 2.0        # End position
v_max = 1.5        # Max velocity [rad/s or m/s]
a_max = 5.0        # Max acceleration [rad/s² or m/s²]
j_max = 50.0       # Max jerk [rad/s³ or m/s³] (S-curve only)

# Generate profiles
t_trap, p_trap, v_trap, a_trap = trapezoidal_profile(q_start, q_end, v_max, a_max)
t_scurve, p_scurve, v_scurve, a_scurve, j_scurve = s_curve_profile(
    q_start, q_end, v_max, a_max, j_max)

print("Motion Profile Comparison")
print("=" * 50)
print(f"Distance:    {q_end - q_start:.1f} units")
print(f"v_max:       {v_max:.1f} units/s")
print(f"a_max:       {a_max:.1f} units/s²")
print(f"j_max:       {j_max:.1f} units/s³ (S-curve)")
print(f"\nTrapezoidal: {t_trap[-1]:.3f} s total")
print(f"S-curve:     {t_scurve[-1]:.3f} s total")
print(f"S-curve overhead: {(t_scurve[-1]/t_trap[-1] - 1)*100:.1f}%")


# =============================================================================
# Plot
# =============================================================================
fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=False)
fig.suptitle('Motion Profile Comparison: Trapezoidal vs S-Curve', fontsize=14)

# Position
axes[0].plot(t_trap, p_trap, 'b-', linewidth=2, label='Trapezoidal')
axes[0].plot(t_scurve, p_scurve, 'r--', linewidth=2, label='S-Curve')
axes[0].set_ylabel('Position')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Velocity
axes[1].plot(t_trap, v_trap, 'b-', linewidth=2, label='Trapezoidal')
axes[1].plot(t_scurve, v_scurve, 'r--', linewidth=2, label='S-Curve')
axes[1].axhline(y=v_max, color='gray', linestyle=':', alpha=0.5)
axes[1].set_ylabel('Velocity')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Acceleration
axes[2].plot(t_trap, a_trap, 'b-', linewidth=2, label='Trapezoidal')
axes[2].plot(t_scurve, a_scurve, 'r--', linewidth=2, label='S-Curve')
axes[2].axhline(y=a_max, color='gray', linestyle=':', alpha=0.5)
axes[2].axhline(y=-a_max, color='gray', linestyle=':', alpha=0.5)
axes[2].set_ylabel('Acceleration')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].annotate('Discontinuous!\n(infinite jerk)', 
                  xy=(t_trap[np.argmax(np.abs(np.diff(a_trap)))]*1.0, a_max),
                  xytext=(0.5, a_max * 0.6),
                  arrowprops=dict(arrowstyle='->', color='blue'),
                  color='blue', fontsize=10)

# Jerk (S-curve only, plus "infinite" spikes for trapezoidal)
axes[3].plot(t_scurve, j_scurve, 'r-', linewidth=2, label='S-Curve jerk')
# Show trapezoidal "jerk" as impulses
trap_jerk = np.diff(a_trap) / np.diff(t_trap)
axes[3].plot(t_trap[:-1], np.clip(trap_jerk, -200, 200), 'b-', 
             linewidth=1, alpha=0.5, label='Trapezoidal jerk (clipped)')
axes[3].axhline(y=j_max, color='gray', linestyle=':', alpha=0.5)
axes[3].axhline(y=-j_max, color='gray', linestyle=':', alpha=0.5)
axes[3].set_ylabel('Jerk')
axes[3].set_xlabel('Time [s]')
axes[3].legend()
axes[3].grid(True, alpha=0.3)
axes[3].set_ylim(-j_max * 2, j_max * 2)

plt.tight_layout()
plt.savefig('trajectory-profiles.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nKey Differences:")
print("  Trapezoidal: Simpler, faster, but infinite jerk at transitions")
print("               → Excites mechanical resonances, vibration")
print("  S-curve:     Limited jerk → smoother motion, less vibration")
print("               → 10-20% longer motion time (typical)")
print("               → Preferred for precision applications")
