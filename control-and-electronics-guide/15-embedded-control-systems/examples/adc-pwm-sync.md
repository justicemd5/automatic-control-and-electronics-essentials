# Example: ADC-PWM Synchronization for Motor Control

## Purpose
Configure ADC sampling synchronized to PWM center/edges for accurate current measurement in a motor drive, using STM32 as a concrete example.

---

## Why Synchronization Matters

In a PWM-driven motor, the current has a triangular ripple:

```
  PWM:     ┌──────┐        ┌──────┐        ┌──────┐
           │      │        │      │        │      │
  ─────────┘      └────────┘      └────────┘      └─────
  
  Current:  ╱╲    ╱╲        ╱╲    ╱╲        ╱╲    ╱╲
           ╱  ╲  ╱  ╲      ╱  ╲  ╱  ╲      ╱  ╲  ╱  ╲
  ────────╱    ╲╱    ╲────╱    ╲╱    ╲────╱    ╲╱    ╲───
           ↑         ↑    ↑         ↑
           A         B    C         D
  
  A = PWM rising edge   → Current at MINIMUM of ripple ✗
  B = PWM center (high) → Current at AVERAGE           ✓
  C = PWM falling edge  → Current at MAXIMUM of ripple ✗
  D = PWM center (low)  → Current at AVERAGE           ✓
```

**Sampling at center** (B or D) gives the average current without needing to filter the ripple.

---

## Timer Configuration (Center-Aligned PWM)

### STM32 TIM1 in Center-Aligned Mode

```
  Timer Counter (center-aligned mode 1):
  
  ARR ─────────╱╲───────────╱╲───────────
              ╱    ╲       ╱    ╲
             ╱      ╲     ╱      ╲
            ╱        ╲   ╱        ╲
  0 ──────╱────────────╲╱────────────╲────
          │      │      │      │      │
          UF     ↑     OF      ↑     UF
                 │             │
              ADC trig      ADC trig
              (center)      (center)
  
  UF = Update event (underflow, counter = 0)
  OF = Overflow event (counter = ARR)
```

### Register Setup (Pseudocode)

```c
void PWM_ADC_Init(uint32_t pwm_freq_hz)
{
    /* --- Timer 1: Center-aligned PWM --- */
    RCC->APB2ENR |= RCC_APB2ENR_TIM1EN;
    
    /* Center-aligned mode 1 (counter counts up then down) */
    TIM1->CR1 = TIM_CR1_CMS_0;  /* Center-aligned mode */
    
    /* PWM frequency: f_PWM = f_TIM / (2 * ARR) */
    /* For 20 kHz with 168 MHz timer clock: ARR = 4200 */
    uint32_t arr = SystemCoreClock / (2 * pwm_freq_hz);
    TIM1->ARR = arr;
    TIM1->PSC = 0;  /* No prescaler */
    
    /* PWM mode 1 on channels 1, 2, 3 (for 3-phase) */
    TIM1->CCMR1 = (6 << 4) | (6 << 12);  /* OC1M=110, OC2M=110 */
    TIM1->CCMR2 = (6 << 4);               /* OC3M=110 */
    TIM1->CCER  = TIM_CCER_CC1E | TIM_CCER_CC2E | TIM_CCER_CC3E;
    
    /* Dead-time (for H-bridge): 1 µs at 168 MHz ≈ 168 counts */
    TIM1->BDTR = TIM_BDTR_MOE | 168;
    
    /* --- ADC Trigger: at counter = 0 (underflow) --- */
    /* TRGO = update event */
    TIM1->CR2 = TIM_CR2_MMS_1;  /* MMS=010: Update event as TRGO */
    
    TIM1->CR1 |= TIM_CR1_CEN;  /* Start timer */
    
    
    /* --- ADC1: Triggered by TIM1 TRGO --- */
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    
    /* External trigger: TIM1 TRGO, rising edge */
    ADC1->CR2 = ADC_CR2_EXTEN_0     /* Rising edge */
              | (0b0000 << 24)       /* EXTSEL = TIM1 TRGO */
              | ADC_CR2_ADON;
    
    /* Scan mode: read channels 1, 2 (phase A, phase B currents) */
    ADC1->SQR3 = (1 << 0) | (2 << 5);  /* CH1 first, then CH2 */
    ADC1->SQR1 = (1 << 20);             /* 2 conversions */
    ADC1->CR1  = ADC_CR1_SCAN;
    
    /* DMA for automatic transfer */
    ADC1->CR2 |= ADC_CR2_DMA | ADC_CR2_DDS;
    DMA2_Stream0_Init(ADC1_DR_ADDRESS, adc_buffer, 2);
    
    /* Enable ADC interrupt for end of conversion */
    ADC1->CR1 |= ADC_CR1_EOCIE;
    NVIC_EnableIRQ(ADC_IRQn);
}
```

---

## Timing Diagram — Complete Cycle

```
  Time:  0     25µs    50µs    75µs   100µs
         │      │       │       │       │
  PWM:   ┌──────┐       │       ┌──────┐
  (ch1)  │      │       │       │      │
  ───────┘      └───────┘───────┘      └───
         ↑              ↑               ↑
  TIM cnt=0          cnt=ARR         cnt=0
         │              │               │
  ADC:   ╠╗             │               ╠╗
  trig   ║║ Convert     │               ║║
         ╚╝             │               ╚╝
         │  ↓           │               │  ↓
  DMA:   │  Ia,Ib       │               │  Ia,Ib
         │  stored      │               │  stored
         │     │        │               │
  ISR:   │     ╠═╗      │               │
         │     ║ ║ FOC  │               │
         │     ╚═╝      │               │
         │       │      │               │
  PWM    │       ↓      │               │
  update:│    CCR1,2,3  │               │
         │    updated   │               │
         │              │               │
  
  Total latency: ADC conversion (~2µs) + ISR (~10µs) = ~12µs
  This is well within the 50µs PWM period ✓
```

---

## Current Reconstruction (Single-Shunt)

For cost-sensitive applications using only one shunt resistor on the DC bus:

```
  3-Phase Inverter:
                 ┌───┐     ┌───┐     ┌───┐
  DC+ ──────────┤ Sa├──┬──┤ Sb├──┬──┤ Sc├──┬
                 └───┘  │  └───┘  │  └───┘  │
                        A        B        C  ← Phase outputs
                 ┌───┐  │  ┌───┐  │  ┌───┐  │
  DC- ──┬───────┤ Sa'├──┘ ┤ Sb'├──┘ ┤ Sc'├──┘
        │        └───┘     └───┘     └───┘
       ┌┴┐
       │R│ ← Shunt resistor (measures DC bus current)
       └┬┘
        │
       GND
```

The DC bus current equals different phase currents depending on which switches are ON:

| Active Switches | DC Bus Current |
|---|---|
| Sa high, Sb low, Sc low | $I_{dc} = I_a$ |
| Sa high, Sb high, Sc low | $I_{dc} = -I_c$ |
| Sa low, Sb high, Sc low | $I_{dc} = I_b$ |

**Two ADC samples per PWM period** (at different switch states) reconstruct all three phase currents. The ADC triggers are shifted within the PWM period.

⚠️ **Pitfall**: Single-shunt reconstruction fails when duty cycles are too close together (insufficient time between states). Minimum pulse width insertion is required, which adds distortion at low modulation indices.

💡 **Insight**: The ADC-PWM synchronization is arguably the most critical hardware configuration in a motor drive. Getting it wrong by even 1 µs can cause current measurement errors of 10-20%, which directly degrades control performance. Always verify timing with an oscilloscope during bring-up.
