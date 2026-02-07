# Example: Neural Network for System Identification

## Purpose
Use a neural network to learn the dynamics of a nonlinear system from input-output data, demonstrating data-driven modeling as an alternative to first-principles modeling.

---

## The Problem

You have a nonlinear system (e.g., a chemical reactor) where the physics is too complex for a first-principles model. But you have lots of operational data:

```
  u(t) ──► [Unknown Nonlinear System] ──► y(t)
  
  Given: Input-output data {u(k), y(k)} for k = 1, ..., N
  Goal:  Learn a model ŷ(k+1) = f(y(k), y(k-1), ..., u(k), u(k-1), ...)
```

---

## Approach: NARX Neural Network

**Nonlinear AutoRegressive with eXogenous inputs**:

$$\hat{y}(k+1) = f_{NN}\left(y(k), y(k-1), \ldots, y(k-n_y), u(k), u(k-1), \ldots, u(k-n_u)\right)$$

```
  Input layer        Hidden layers      Output
  ┌──────────┐      ┌──────────┐      ┌──────┐
  │ y(k)     │─────►│          │─────►│      │
  │ y(k-1)   │─────►│  Dense   │      │ ŷ(k+1)│
  │ y(k-2)   │─────►│  64 ReLU │─────►│      │
  │ u(k)     │─────►│          │      └──────┘
  │ u(k-1)   │─────►│  Dense   │
  │ u(k-2)   │─────►│  32 ReLU │
  └──────────┘      └──────────┘
  
  Regressor depth: n_y = 3, n_u = 3
  → 6 inputs, 2 hidden layers (64 + 32), 1 output
```

---

## Data Generation (Simulated True System)

For this example, the "true" system is a Hammerstein model (nonlinear static + linear dynamics):

$$y(k) = 0.8 y(k-1) - 0.3 y(k-2) + 1.5 u_{NL}(k-1) + 0.5 u_{NL}(k-2)$$

Where $u_{NL} = u + 0.3u^2 - 0.1u^3$ (input nonlinearity)

### Training Data

```
  Input: Random binary signal (PRBS) + random amplitude
  Duration: 5000 samples at Ts = 0.1s
  SNR: 30 dB (add measurement noise)
  
  u(k):  ┌─┐   ┌───┐ ┌─┐     ┌─────┐
         │ │   │   │ │ │     │     │
  ───────┘ └───┘   └─┘ └─────┘     └───
  
  y(k):  ╱╲   ╱───╲ ╱╲     ╱─────╲
        ╱  ╲ ╱     ╲╱  ╲   ╱       ╲
  ─────╱    ╲╱            ╲─╱         ╲──
```

### Train/Test Split

- Training: Samples 1-4000 (80%)
- Validation: Samples 4001-5000 (20%)

---

## Training Process

### Loss Function

Mean Squared Error (MSE):

$$L = \frac{1}{N} \sum_{k=1}^{N} \left( y(k) - \hat{y}(k) \right)^2$$

### Training Hyperparameters

| Parameter | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | 0.001 (with decay) |
| Batch size | 64 |
| Epochs | 200 |
| Early stopping | Patience = 20 epochs |
| Regularization | L2 weight decay = 1e-4 |

### Training Progress

```
  Loss (MSE)
  0.5│╲
     │ ╲
  0.1│  ╲───── Training loss
     │    ╲╲
  0.01│     ╲──────── Validation loss
     │       ╲─────────── Best model here
  0.005│        ╲
     │           ─────────── Overfit starts
     │                   ─── (validation rises)
     └────────────────────────── Epoch
     0   20   50   100  150  200
     
  Stop at epoch 120 (early stopping)
```

---

## Results

### One-Step Prediction (on validation set)

```
  y(k)
  3│                 ╱╲
  2│    ╱╲          ╱  ╲         ╱╲
  1│   ╱  ╲        ╱    ╲      ╱  ╲
  0│──╱────╲──────╱──────╲────╱────╲──
 -1│         ╲  ╱                    ╲╱
 -2│          ╲╱
   │
   │  ── True     ● NN prediction (nearly perfect overlap)
```

| Metric | Value |
|---|---|
| Validation MSE | 0.0032 |
| Validation RMSE | 0.057 |
| R² score | 0.997 |
| Max absolute error | 0.18 |

### Free-Run (Multi-Step) Prediction

Feed predictions back as inputs (no measured data):

$$\hat{y}(k+1) = f_{NN}(\hat{y}(k), \hat{y}(k-1), \ldots, u(k), u(k-1), \ldots)$$

```
  y(k)
  3│                 ╱╲
  2│    ╱╲          ╱  ╲─── True
  1│   ╱  ╲        ╱    ╲
  0│──╱────╲──────╱──────╲──
 -1│  ╱      ╲  ╱          ╲── NN (drift after ~50 steps)
 -2│╱          ╲╱
   │
   └───────────────────── Time steps
   0   20   40   60   80  100
```

Free-run performance degrades after ~50 steps because errors compound. This is expected and normal.

| Prediction Horizon | RMSE |
|---|---|
| 1 step | 0.057 |
| 10 steps | 0.12 |
| 50 steps | 0.45 |
| 100 steps | 0.89 |

---

## Using the NN Model for Control

### Option A: NN Model + MPC

Use the NN as the prediction model inside an MPC controller:

```
  Reference ──► MPC ──► u ──► Real System ──► y
                 │                              │
                 └──► NN Model (for prediction) │
                      ŷ(k+1) = f_NN(...)        │
                                                 │
                 └──────────── Measurement ◄─────┘
```

This is the most practical approach: the NN handles the nonlinearity, MPC handles constraints and optimization.

### Option B: NN for Gain Scheduling

Use the NN to estimate plant parameters, then schedule PID gains:

$$\hat{K}_{plant}, \hat{\tau}_{plant} = g_{NN}(\text{operating point})$$
$$K_p, K_i, K_d = \text{tune}(\hat{K}_{plant}, \hat{\tau}_{plant})$$

### Option C: Direct NN Controller (Less Common)

Train a separate NN to directly output control actions. Harder to guarantee stability.

---

## Practical Considerations

### Data Quality

| Issue | Effect | Mitigation |
|---|---|---|
| Insufficient excitation | Model doesn't learn full dynamics | Use PRBS or multisine input |
| Outliers | Corrupt model | Robust loss function, outlier removal |
| Sensor noise | Limits accuracy | Increase data, filter inputs |
| Operating point bias | Model only works near training data | Collect data across full range |
| Correlated inputs | Identifiability issues | Ensure input spectrum is broadband |

### How Much Data?

Rule of thumb: At least **10-20× the number of model parameters** data points.

For our 6-input, 64-32-1 network: $6 \times 64 + 64 + 64 \times 32 + 32 + 32 \times 1 + 1 = 2529$ parameters

→ Need at least 25,000 – 50,000 data points for reliable training.

⚠️ **Pitfall**: NN models have no built-in uncertainty quantification. They may make confident but wrong predictions outside the training data range. Always validate the model across the full operating envelope, and consider using Gaussian Processes or Bayesian NNs if uncertainty bounds are needed.

💡 **Insight**: The most successful industrial applications of ML for control don't replace the controller — they replace the *model*. Physics-based models are hard to build for complex systems (combustion engines, chemical reactors, building HVAC). ML can learn these models from data, and then proven control methods (PID, MPC) run on top. This "ML model + classical control" approach combines the strengths of both paradigms.
