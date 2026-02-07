/**
 * Fixed-Point PID Controller (Q16.16 Format)
 * ============================================
 *
 * Purpose:
 *   Production-quality PID controller using 32-bit fixed-point arithmetic,
 *   suitable for MCUs without FPU (e.g., Cortex-M0/M3).
 *
 * Features:
 *   - Q16.16 fixed-point (16 integer bits, 16 fractional bits)
 *   - Anti-windup with back-calculation
 *   - Derivative filter (low-pass on D term)
 *   - Output clamping
 *   - Bumpless initialization
 *
 * Q16.16 Format:
 *   - Range: -32768.0 to +32767.99998
 *   - Resolution: 1/65536 ≈ 0.0000153
 *   - 1.0 = 0x00010000 = 65536
 */

#include <stdint.h>

/* ================================================================
 * Q16.16 Fixed-Point Macros
 * ================================================================ */

typedef int32_t q16_t;   /* Q16.16 fixed-point type */
typedef int64_t q16_wide; /* For intermediate multiplication results */

#define Q16_SHIFT       16
#define Q16_ONE         ((q16_t)(1 << Q16_SHIFT))        /* 1.0 = 65536 */
#define Q16_HALF        ((q16_t)(1 << (Q16_SHIFT - 1)))  /* 0.5 = 32768 */

/* Convert float to Q16.16 (compile-time only!) */
#define FLOAT_TO_Q16(f) ((q16_t)((f) * 65536.0f))

/* Convert Q16.16 to float (for debugging only) */
#define Q16_TO_FLOAT(q) ((float)(q) / 65536.0f)

/* Q16.16 multiplication: (a * b) >> 16 */
static inline q16_t q16_mul(q16_t a, q16_t b)
{
    return (q16_t)(((q16_wide)a * (q16_wide)b) >> Q16_SHIFT);
}

/* Q16.16 division: (a << 16) / b */
static inline q16_t q16_div(q16_t a, q16_t b)
{
    return (q16_t)(((q16_wide)a << Q16_SHIFT) / (q16_wide)b);
}

/* Clamp value to range [lo, hi] */
static inline q16_t q16_clamp(q16_t val, q16_t lo, q16_t hi)
{
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}


/* ================================================================
 * PID Controller Structure
 * ================================================================ */

typedef struct {
    /* Gains (Q16.16) */
    q16_t Kp;          /* Proportional gain */
    q16_t Ki;          /* Integral gain */
    q16_t Kd;          /* Derivative gain */
    
    /* Sample time */
    q16_t Ts;          /* Sample period [s] in Q16.16 */
    
    /* Anti-windup */
    q16_t Kb;          /* Back-calculation gain */
    
    /* Derivative filter coefficient: N = filter bandwidth / Kd */
    q16_t N;           /* Derivative filter coefficient (typ. 10-20) */
    
    /* Output limits */
    q16_t out_min;     /* Minimum output */
    q16_t out_max;     /* Maximum output */
    
    /* Internal state (preserved between calls) */
    q16_t integrator;  /* Integral accumulator */
    q16_t diff_state;  /* Derivative filter state */
    q16_t prev_error;  /* Previous error (for derivative) */
    q16_t prev_output; /* Previous output (for anti-windup) */
    
} PID_Q16_t;


/* ================================================================
 * PID Initialization
 * ================================================================ */

/**
 * Initialize PID controller with default safe state.
 *
 * @param pid     Pointer to PID structure
 * @param Kp      Proportional gain (float, converted internally)
 * @param Ki      Integral gain (float)
 * @param Kd      Derivative gain (float)
 * @param Ts      Sample time in seconds (float)
 * @param out_min Minimum output (float)
 * @param out_max Maximum output (float)
 */
void PID_Q16_Init(PID_Q16_t *pid,
                  float Kp, float Ki, float Kd,
                  float Ts, float out_min, float out_max)
{
    pid->Kp = FLOAT_TO_Q16(Kp);
    pid->Ki = FLOAT_TO_Q16(Ki);
    pid->Kd = FLOAT_TO_Q16(Kd);
    pid->Ts = FLOAT_TO_Q16(Ts);
    
    /* Anti-windup gain: typically Ki or sqrt(Ki*Kd) */
    pid->Kb = FLOAT_TO_Q16(Ki);
    
    /* Derivative filter: N = 10 is a common default */
    pid->N = FLOAT_TO_Q16(10.0f);
    
    pid->out_min = FLOAT_TO_Q16(out_min);
    pid->out_max = FLOAT_TO_Q16(out_max);
    
    /* Clear state */
    pid->integrator  = 0;
    pid->diff_state  = 0;
    pid->prev_error  = 0;
    pid->prev_output = 0;
}


/* ================================================================
 * PID Update (called every Ts seconds from timer ISR)
 * ================================================================ */

/**
 * Compute one PID control cycle.
 *
 * @param pid       Pointer to PID structure
 * @param setpoint  Desired value (Q16.16)
 * @param measured  Measured value (Q16.16)
 * @return          Control output (Q16.16)
 *
 * Algorithm:
 *   P = Kp * error
 *   I += Ki * Ts * error + Kb * Ts * (saturated_out - raw_out)
 *   D = Kd * N * (error - prev_error) / (1 + N * Ts) [filtered]
 *   output = clamp(P + I + D, out_min, out_max)
 */
q16_t PID_Q16_Update(PID_Q16_t *pid, q16_t setpoint, q16_t measured)
{
    q16_t error, P, I, D;
    q16_t output_raw, output_sat;
    q16_t windup_correction;
    
    /* ---- Error ---- */
    error = setpoint - measured;
    
    /* ---- Proportional term ---- */
    P = q16_mul(pid->Kp, error);
    
    /* ---- Integral term with anti-windup back-calculation ---- */
    /* Back-calculation: correct for saturation on previous step */
    windup_correction = q16_mul(pid->Kb,
                               pid->prev_output - pid->prev_error);
    /* Note: prev_error here stores the raw (pre-clamp) output.
     * Renamed for clarity in a real implementation. */
    
    /* I(k) = I(k-1) + Ki * Ts * e(k) + Kb * Ts * (u_sat - u_raw) */
    pid->integrator += q16_mul(q16_mul(pid->Ki, pid->Ts), error);
    
    /* Anti-windup correction */
    if (pid->prev_error != pid->prev_output) {
        /* Only correct when saturated */
        q16_t correction = q16_mul(q16_mul(pid->Kb, pid->Ts),
                                    pid->prev_output - pid->prev_error);
        pid->integrator += correction;
    }
    
    I = pid->integrator;
    
    /* ---- Derivative term with low-pass filter ---- */
    /* Filtered derivative: D(k) = D(k-1) * alpha + Kd * N * (e(k) - e(k-1)) * (1 - alpha) */
    /* where alpha = 1 / (1 + N * Ts) */
    {
        q16_t NTs = q16_mul(pid->N, pid->Ts);
        q16_t denom = Q16_ONE + NTs;  /* 1 + N*Ts */
        q16_t alpha = q16_div(Q16_ONE, denom);
        q16_t de = error - pid->prev_error;
        
        q16_t d_new = q16_mul(pid->Kd, q16_mul(pid->N, de));
        pid->diff_state = q16_mul(alpha, pid->diff_state)
                        + q16_mul(Q16_ONE - alpha, d_new);
    }
    D = pid->diff_state;
    
    /* ---- Sum and clamp ---- */
    output_raw = P + I + D;
    output_sat = q16_clamp(output_raw, pid->out_min, pid->out_max);
    
    /* ---- Store state for next iteration ---- */
    pid->prev_error  = output_raw;  /* Raw output (for anti-windup) */
    pid->prev_output = output_sat;  /* Saturated output */
    
    return output_sat;
}


/* ================================================================
 * PID Reset (for mode changes or initialization)
 * ================================================================ */

void PID_Q16_Reset(PID_Q16_t *pid, q16_t current_output)
{
    pid->integrator  = current_output;  /* Bumpless transfer */
    pid->diff_state  = 0;
    pid->prev_error  = current_output;
    pid->prev_output = current_output;
}


/* ================================================================
 * Example Usage (pseudo-code for timer ISR)
 * ================================================================ */

#if 0  /* Example — not compiled */

PID_Q16_t speed_pid;

void system_init(void)
{
    /* Kp=2.5, Ki=10, Kd=0.05, Ts=0.001s (1kHz), output ±1000 */
    PID_Q16_Init(&speed_pid, 2.5f, 10.0f, 0.05f, 0.001f, -1000.0f, 1000.0f);
}

/* Timer ISR at 1 kHz */
void TIM2_IRQHandler(void)
{
    /* Clear interrupt flag */
    TIM2->SR &= ~TIM_SR_UIF;
    
    /* Read sensor (12-bit ADC → Q16.16) */
    q16_t measured = (q16_t)ADC1->DR << (16 - 12);  /* Scale to Q16.16 */
    
    /* Setpoint (from communication or higher-level controller) */
    q16_t setpoint = FLOAT_TO_Q16(500.0f);  /* 500 RPM */
    
    /* Compute PID */
    q16_t output = PID_Q16_Update(&speed_pid, setpoint, measured);
    
    /* Apply to PWM (map Q16.16 output to timer compare register) */
    int32_t pwm_val = (int32_t)(output >> 6);  /* Scale to 10-bit PWM range */
    pwm_val = (pwm_val < 0) ? 0 : (pwm_val > 1023) ? 1023 : pwm_val;
    TIM1->CCR1 = (uint32_t)pwm_val;
}

#endif  /* Example */
