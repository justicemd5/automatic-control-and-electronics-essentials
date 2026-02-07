/*
 * Digital PID Controller — Production-Quality C Implementation
 * ==============================================================
 *
 * Purpose:
 *     Implement a robust digital PID controller in C suitable for
 *     embedded deployment. Includes anti-windup, derivative filter,
 *     output clamping, and bumpless transfer.
 *
 * Algorithm: Velocity (incremental) form PID with:
 *     - Integral anti-windup (clamping method)
 *     - Derivative filter (N = 10, first-order)
 *     - Derivative on measurement (not on error, avoids setpoint kick)
 *     - Output saturation with back-calculation anti-windup
 *
 * Usage:
 *     PID_Controller pid;
 *     PID_Init(&pid, 2.0, 10.0, 0.05, 0.001, -10.0, 10.0);
 *     // In control loop:
 *     float output = PID_Update(&pid, setpoint, measurement);
 */

#include <math.h>
#include <stdbool.h>

/* ========================================================================= */
/*  Data Structure                                                            */
/* ========================================================================= */

typedef struct {
    /* Gains */
    float Kp;           /* Proportional gain */
    float Ki;           /* Integral gain */
    float Kd;           /* Derivative gain */
    
    /* Timing */
    float Ts;           /* Sample period [s] */
    
    /* Output limits */
    float out_min;      /* Minimum output (actuator lower limit) */
    float out_max;      /* Maximum output (actuator upper limit) */
    
    /* Derivative filter coefficient */
    float N;            /* Derivative filter constant (typically 10-20) */
    
    /* Internal state (persistent between calls) */
    float integral;     /* Integral accumulator */
    float prev_error;   /* Previous error (for integral) */
    float prev_meas;    /* Previous measurement (for derivative) */
    float diff_filtered;/* Filtered derivative term */
    float prev_output;  /* Previous output (for anti-windup) */
    
    /* Status flags */
    bool  initialized;  /* First-call flag */
    bool  saturated;    /* Output is currently saturated */
} PID_Controller;


/* ========================================================================= */
/*  Initialization                                                            */
/* ========================================================================= */

void PID_Init(PID_Controller *pid,
              float Kp, float Ki, float Kd,
              float Ts,
              float out_min, float out_max)
{
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
    pid->Ts = Ts;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->N = 10.0f;  /* Derivative filter constant */
    
    /* Clear internal state */
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_meas = 0.0f;
    pid->diff_filtered = 0.0f;
    pid->prev_output = 0.0f;
    pid->initialized = false;
    pid->saturated = false;
}


/* ========================================================================= */
/*  PID Update (call once per sample period)                                  */
/* ========================================================================= */

float PID_Update(PID_Controller *pid, float setpoint, float measurement)
{
    float error = setpoint - measurement;
    
    /* ------------------------------------------------------------------- */
    /* Handle first call: initialize previous values                        */
    /* ------------------------------------------------------------------- */
    if (!pid->initialized) {
        pid->prev_error = error;
        pid->prev_meas = measurement;
        pid->initialized = true;
    }
    
    /* ------------------------------------------------------------------- */
    /* Proportional term                                                    */
    /* ------------------------------------------------------------------- */
    float P = pid->Kp * error;
    
    /* ------------------------------------------------------------------- */
    /* Integral term with anti-windup                                       */
    /*                                                                      */
    /* Only integrate if:                                                    */
    /*   - Output is NOT saturated, OR                                      */
    /*   - The integration would REDUCE the output magnitude                */
    /* ------------------------------------------------------------------- */
    bool integrate = true;
    if (pid->saturated) {
        /* Check if integration direction opposes saturation direction */
        if ((pid->prev_output >= pid->out_max && error > 0) ||
            (pid->prev_output <= pid->out_min && error < 0)) {
            integrate = false;  /* Stop winding up! */
        }
    }
    
    if (integrate) {
        /* Trapezoidal integration (more accurate than rectangular) */
        pid->integral += pid->Ki * pid->Ts * 0.5f * (error + pid->prev_error);
    }
    
    float I = pid->integral;
    
    /* ------------------------------------------------------------------- */
    /* Derivative term (on measurement, NOT on error)                       */
    /*                                                                      */
    /* Using derivative-on-measurement avoids the "derivative kick"         */
    /* that occurs when the setpoint changes abruptly.                      */
    /*                                                                      */
    /* Filtered derivative: D(z) = Kd*N / (1 + N*Ts/(z-1))                */
    /* ------------------------------------------------------------------- */
    float d_meas = -(measurement - pid->prev_meas) / pid->Ts;
    
    /* First-order filter on derivative */
    float alpha = pid->N * pid->Ts / (1.0f + pid->N * pid->Ts);
    pid->diff_filtered = alpha * d_meas + (1.0f - alpha) * pid->diff_filtered;
    
    float D = pid->Kd * pid->diff_filtered;
    
    /* ------------------------------------------------------------------- */
    /* Combine and clamp output                                             */
    /* ------------------------------------------------------------------- */
    float output = P + I + D;
    
    /* Output saturation */
    pid->saturated = false;
    if (output > pid->out_max) {
        output = pid->out_max;
        pid->saturated = true;
    } else if (output < pid->out_min) {
        output = pid->out_min;
        pid->saturated = true;
    }
    
    /* ------------------------------------------------------------------- */
    /* Save state for next iteration                                        */
    /* ------------------------------------------------------------------- */
    pid->prev_error = error;
    pid->prev_meas = measurement;
    pid->prev_output = output;
    
    return output;
}


/* ========================================================================= */
/*  Utility: Reset integrator (for mode changes)                              */
/* ========================================================================= */

void PID_Reset(PID_Controller *pid)
{
    pid->integral = 0.0f;
    pid->prev_error = 0.0f;
    pid->prev_meas = 0.0f;
    pid->diff_filtered = 0.0f;
    pid->prev_output = 0.0f;
    pid->initialized = false;
    pid->saturated = false;
}


/* ========================================================================= */
/*  Utility: Change gains online (bumpless)                                   */
/* ========================================================================= */

void PID_SetGains(PID_Controller *pid, float Kp, float Ki, float Kd)
{
    /* When changing gains, adjust integral to maintain current output */
    /* (bumpless transfer) */
    float P_old = pid->Kp * pid->prev_error;
    float P_new = Kp * pid->prev_error;
    pid->integral += (P_old - P_new);  /* Compensate for proportional change */
    
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
}


/* ========================================================================= */
/*  Example Usage (main)                                                      */
/* ========================================================================= */

#include <stdio.h>

int main(void)
{
    PID_Controller pid;
    
    /* Initialize: Kp=2, Ki=10, Kd=0.05, Ts=1ms, limits=[-10, 10] */
    PID_Init(&pid, 2.0f, 10.0f, 0.05f, 0.001f, -10.0f, 10.0f);
    
    /* Simulate a simple first-order plant: tau*dy/dt + y = K*u */
    float plant_tau = 0.1f;   /* Time constant */
    float plant_K = 1.0f;     /* DC gain */
    float y = 0.0f;           /* Plant output */
    float setpoint = 1.0f;    /* Step reference */
    
    printf("Time[s], Setpoint, Output, Control, Error\n");
    
    for (int k = 0; k < 1000; k++) {
        float t = k * pid.Ts;
        
        /* Controller */
        float u = PID_Update(&pid, setpoint, y);
        
        /* Plant simulation (Forward Euler) */
        float dydt = (plant_K * u - y) / plant_tau;
        y += dydt * pid.Ts;
        
        /* Print every 10 samples */
        if (k % 10 == 0) {
            printf("%.3f, %.3f, %.4f, %.4f, %.4f\n",
                   t, setpoint, y, u, setpoint - y);
        }
    }
    
    return 0;
}
