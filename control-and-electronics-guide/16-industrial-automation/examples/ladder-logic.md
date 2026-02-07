# Example: Motor Start/Stop Circuit in Ladder Diagram

## Purpose
Implement a classic motor start/stop control circuit with safety interlocks using IEC 61131-3 Ladder Diagram, the most common PLC programming language.

---

## Specification

Control a 3-phase motor with:
- **Start** pushbutton (momentary, NO contact)
- **Stop** pushbutton (momentary, NC contact — fail-safe)
- **Emergency stop** (NC, hardwired + PLC monitored)
- **Overload relay** (NC contact, opens on thermal fault)
- **Running indicator** light
- **Fault indicator** light

---

## I/O Assignment

| Tag | Address | Type | Description |
|---|---|---|---|
| `PB_Start` | I:0.0 | DI | Start pushbutton (NO) |
| `PB_Stop` | I:0.1 | DI | Stop pushbutton (NC) |
| `E_Stop` | I:0.2 | DI | Emergency stop (NC) |
| `OL_Relay` | I:0.3 | DI | Overload relay (NC) |
| `Motor_FB` | I:0.4 | DI | Motor contactor feedback |
| `Motor_Out` | Q:0.0 | DO | Motor contactor coil |
| `Run_Light` | Q:0.1 | DO | Green running light |
| `Fault_Light` | Q:0.2 | DO | Red fault light |

---

## Ladder Diagram

### Rung 1: Motor Start/Stop with Seal-In

```
      PB_Stop    E_Stop    OL_Relay   PB_Start        Motor_Out
  ──┤ ├────────┤ ├────────┤ ├────────┤ ├──────────────( )──
      (NC)      (NC)       (NC)       (NO)              │
                                                         │
                                        Motor_Out        │
  ──────────────────────────────────────┤ ├──────────────┘
                                        (seal-in)
```

**How it works:**
1. All NC contacts (Stop, E-Stop, Overload) must be closed (safe)
2. Press Start → `Motor_Out` energizes
3. `Motor_Out` seal-in contact maintains the circuit after Start is released
4. Pressing Stop, E-Stop, or overload trip → breaks the seal → motor stops

### Rung 2: Running Indicator

```
      Motor_Out                                 Run_Light
  ──┤ ├───────────────────────────────────────( )──
```

### Rung 3: Fault Detection

```
      OL_Relay                                  Fault_Light
  ──┤/├───────────────────────────────────────( )──
      (NC, so /├ means "normally closed opened" = fault)
  
      Motor_Out    Motor_FB                     Fault_Light
  ──┤ ├──────────┤/├──────────────── TON ─────( )──
                   (NO)              T=2s
                   
  (If motor commanded ON but feedback not received within 2s → fault)
```

---

## Structured Text Equivalent

For comparison, the same logic in Structured Text (ST):

```pascal
PROGRAM MotorControl
VAR
    PB_Start   : BOOL;    (* I:0.0 *)
    PB_Stop    : BOOL;    (* I:0.1, NC contact → TRUE when not pressed *)
    E_Stop     : BOOL;    (* I:0.2, NC → TRUE when safe *)
    OL_Relay   : BOOL;    (* I:0.3, NC → TRUE when healthy *)
    Motor_FB   : BOOL;    (* I:0.4 *)
    Motor_Out  : BOOL;    (* Q:0.0 *)
    Run_Light  : BOOL;    (* Q:0.1 *)
    Fault_Light: BOOL;    (* Q:0.2 *)
    
    SealIn     : BOOL;    (* Internal seal-in latch *)
    FB_Timer   : TON;     (* Feedback timeout timer *)
END_VAR

(* === Safety chain === *)
IF NOT PB_Stop OR NOT E_Stop OR NOT OL_Relay THEN
    SealIn := FALSE;    (* Break seal on any stop condition *)
END_IF;

(* === Start logic === *)
IF PB_Start AND PB_Stop AND E_Stop AND OL_Relay THEN
    SealIn := TRUE;     (* Latch on start *)
END_IF;

(* === Output === *)
Motor_Out := SealIn;

(* === Indicators === *)
Run_Light := Motor_Out;

(* === Fault detection === *)
(* Overload fault *)
Fault_Light := NOT OL_Relay;

(* Feedback timeout: motor commanded but no feedback *)
FB_Timer(IN := Motor_Out AND NOT Motor_FB, PT := T#2s);
IF FB_Timer.Q THEN
    Fault_Light := TRUE;
    SealIn := FALSE;    (* Trip on feedback fault *)
END_IF;

END_PROGRAM
```

---

## Timing Diagram

```
  Time:   0     1s    2s    3s    4s    5s    6s    7s    8s
  
  PB_Start: ──┐ ┌──────────────────────────────────────────
              └─┘  (momentary press at t=0.5)
              
  PB_Stop:  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┐ ┌━━━━━━━━━━━━
            (NC = normally HIGH)            └─┘ (press at t=5)
  
  Motor_Out: ──┐                           ┌───────────────
               └───────────────────────────┘
              t=0.5                        t=5
              (starts)                     (stops)
  
  Run_Light: ──┐                           ┌───────────────
               └───────────────────────────┘
               (follows Motor_Out)
```

---

## Safety Considerations

### Why NC (Normally Closed) for Stop Circuits?

```
  NC contact:  ──┤ ├──    Wire break → Circuit OPENS → Motor STOPS → SAFE ✓
  
  NO contact:  ──┤/├──    Wire break → Circuit OPENS → Motor STAYS → DANGEROUS ✗
```

**Fail-safe principle**: A wire break, connector failure, or contact weld should always result in the **safe state** (motor off).

### Emergency Stop Categories (IEC 60204-1)

| Category | Action | Implementation |
|---|---|---|
| **0** | Immediate power disconnect | Hardwired contactor, not PLC-controlled |
| **1** | Controlled stop, then disconnect | PLC decelerates, then disconnects |
| **2** | Controlled stop, power maintained | PLC stops motion, power remains for braking |

⚠️ **Pitfall**: Category 0 E-stop must be hardwired — it cannot rely on the PLC being functional. The PLC monitors the E-stop for alarm/logging, but the physical safety circuit operates independently.

🔧 **Practical**: In modern safety systems, a dedicated Safety PLC (e.g., Siemens F-CPU, Allen-Bradley GuardLogix) handles safety functions with redundant processors and certified safety function blocks.
