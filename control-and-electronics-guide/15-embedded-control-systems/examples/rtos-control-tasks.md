# Example: Multi-Rate Control with FreeRTOS

## Purpose
Design a real-time control system with multiple control loops running at different rates, managed by FreeRTOS tasks and priorities.

---

## System Architecture

A servo drive with three control loops at different rates:

```
  ┌─────────────────────────────────────────────────────┐
  │                  FreeRTOS Kernel                     │
  │                                                     │
  │  Priority 5 (Highest)                               │
  │  ┌─────────────────────────────┐                    │
  │  │ Current Loop Task (20 kHz)  │ ← Timer ISR trigger│
  │  │ • Read phase currents       │                    │
  │  │ • Park/Clarke transform     │                    │
  │  │ • PI current regulators     │                    │
  │  │ • Inverse Park + SVM        │                    │
  │  │ • Update PWM                │                    │
  │  └─────────────────────────────┘                    │
  │                                                     │
  │  Priority 3                                         │
  │  ┌─────────────────────────────┐                    │
  │  │ Speed Loop Task (1 kHz)     │ ← Software timer   │
  │  │ • Read encoder              │                    │
  │  │ • Speed estimation          │                    │
  │  │ • PID speed controller      │                    │
  │  │ • Output → current setpoint │                    │
  │  └─────────────────────────────┘                    │
  │                                                     │
  │  Priority 2                                         │
  │  ┌─────────────────────────────┐                    │
  │  │ Position Loop Task (100 Hz) │ ← Software timer   │
  │  │ • Trajectory generation     │                    │
  │  │ • Position PID              │                    │
  │  │ • Output → speed setpoint   │                    │
  │  └─────────────────────────────┘                    │
  │                                                     │
  │  Priority 1 (Lowest)                                │
  │  ┌─────────────────────────────┐                    │
  │  │ Communication Task (10 Hz)  │ ← Periodic         │
  │  │ • Process CAN/Ethernet msgs │                    │
  │  │ • Update setpoints          │                    │
  │  │ • Send telemetry            │                    │
  │  └─────────────────────────────┘                    │
  └─────────────────────────────────────────────────────┘
```

---

## FreeRTOS Implementation

### Task Creation

```c
/* Task handles */
TaskHandle_t hCurrentTask, hSpeedTask, hPositionTask, hCommTask;

/* Shared data (protected by critical section or queue) */
volatile float iq_setpoint = 0;    /* Speed → Current loop */
volatile float speed_setpoint = 0;  /* Position → Speed loop */

void app_main(void)
{
    /* Create tasks */
    xTaskCreate(CurrentLoopTask,  "Current",  512, NULL, 5, &hCurrentTask);
    xTaskCreate(SpeedLoopTask,    "Speed",    512, NULL, 3, &hSpeedTask);
    xTaskCreate(PositionLoopTask, "Position", 512, NULL, 2, &hPositionTask);
    xTaskCreate(CommTask,         "Comm",    1024, NULL, 1, &hCommTask);
    
    /* Start scheduler */
    vTaskStartScheduler();
}
```

### Current Loop (20 kHz — Highest Priority)

```c
void CurrentLoopTask(void *param)
{
    TickType_t xLastWake = xTaskGetTickCount();
    
    for (;;) {
        /* Wait for timer notification (ISR → task) */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        /* 1. Read ADC (phase currents) */
        float ia = read_adc_current_a();
        float ib = read_adc_current_b();
        
        /* 2. Clarke transform (abc → αβ) */
        float i_alpha = ia;
        float i_beta = (ia + 2*ib) / SQRT3;
        
        /* 3. Park transform (αβ → dq) */
        float theta_e = get_electrical_angle();
        float id =  i_alpha * cosf(theta_e) + i_beta * sinf(theta_e);
        float iq = -i_alpha * sinf(theta_e) + i_beta * cosf(theta_e);
        
        /* 4. PI controllers */
        float vd = PI_Update(&pi_d, 0.0f, id);          /* id_ref = 0 */
        float vq = PI_Update(&pi_q, iq_setpoint, iq);    /* From speed loop */
        
        /* 5. Inverse Park + Space Vector Modulation */
        float v_alpha =  vd * cosf(theta_e) - vq * sinf(theta_e);
        float v_beta  =  vd * sinf(theta_e) + vq * cosf(theta_e);
        SVM_Update(v_alpha, v_beta);
    }
}

/* Timer ISR triggers the current loop */
void TIM1_UP_IRQHandler(void)
{
    TIM1->SR &= ~TIM_SR_UIF;
    
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    vTaskNotifyGiveFromISR(hCurrentTask, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### Speed Loop (1 kHz)

```c
void SpeedLoopTask(void *param)
{
    TickType_t xLastWake = xTaskGetTickCount();
    
    for (;;) {
        vTaskDelayUntil(&xLastWake, pdMS_TO_TICKS(1));  /* 1 ms period */
        
        /* 1. Read encoder and estimate speed */
        float position = read_encoder_position();
        float speed = estimate_speed(position);
        
        /* 2. PID speed controller */
        float iq_cmd = PID_Update(&pid_speed, speed_setpoint, speed);
        
        /* 3. Pass to current loop (atomic write) */
        taskENTER_CRITICAL();
        iq_setpoint = iq_cmd;
        taskEXIT_CRITICAL();
    }
}
```

---

## Timing Analysis

### Worst-Case Execution Time (WCET)

| Task | Period | WCET | CPU Load | Deadline |
|---|---|---|---|---|
| Current (20 kHz) | 50 µs | 15 µs | 30% | 50 µs |
| Speed (1 kHz) | 1 ms | 30 µs | 3% | 1 ms |
| Position (100 Hz) | 10 ms | 200 µs | 2% | 10 ms |
| Communication (10 Hz) | 100 ms | 2 ms | 2% | 100 ms |
| **Total CPU** | — | — | **37%** | — |

### Rate Monotonic Analysis (RMA)

For 4 tasks, the schedulability bound is:

$$U \leq 4(2^{1/4} - 1) = 0.757 = 75.7\%$$

Our total utilization = 37% < 75.7% → **Schedulable** ✓

### Preemption Timeline

```
  Time [µs]: 0        50       100      150      200
             │        │        │        │        │
  Current:   ╠═══╣    ╠═══╣    ╠═══╣    ╠═══╣    ╠═══╣
  Speed:     ·        ·        ·        ·        ·
  Position:  ·        ·        ·        ·        ·
  
  At t = 1000 µs (1 ms):
  Current:   ╠═══╣    ← Still runs first (higher priority)
  Speed:         ╠════╣ ← Runs after current completes
  
  At t = 10000 µs (10 ms):
  Current:   ╠═══╣
  Speed:         ╠════╣
  Position:           ╠══════════╣ ← Lowest priority, runs last
```

---

## Common Pitfalls

⚠️ **Priority Inversion**: If the communication task holds a mutex needed by the current loop, the high-priority task blocks on a low-priority task. **Solution**: Use priority inheritance mutexes or, better, message queues.

⚠️ **Stack Overflow**: Each task needs its own stack. Undersized stacks cause hard faults. Use `uxTaskGetStackHighWaterMark()` to check.

⚠️ **Floating-Point Context**: On Cortex-M4F, the FPU registers must be saved during context switches. FreeRTOS handles this with `configUSE_TASK_FPU_SUPPORT`, but verify it's enabled.

💡 **Insight**: The cascaded structure (position → speed → current) is universal in servo drives. Each inner loop is ~10× faster than its outer loop. This bandwidth separation ensures stability even with the discrete-time interactions between loops.
