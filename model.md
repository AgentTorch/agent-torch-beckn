# Agent-Based Model for Community Solar Energy Networks: Self-Sufficiency Through Decentralized Trading

## 1. Model Components and State Space

### 1.1 Agent Classes and State Variables

#### 1.1.1 Household Agent ($H$)

Each household agent $H_i$ is characterized by the state vector:

$$
H_i = \{id_i, \mathbf{x}_i, c_i, \mathbf{D}_i, F_i, \mathbf{G}_i, B_{\text{cap},i}, B_i(t), E_i(t), S_i, \mathbf{N}_i, \alpha_i, R_i\}
$$

where:

| Variable       | Domain                | Description                                   |
| -------------- | --------------------- | --------------------------------------------- |
| $id_i$         | $\mathbb{N}$          | Unique identifier                             |
| $\mathbf{x}_i$ | $\mathbb{R}^2$        | Location coordinates                          |
| $c_i$          | $\mathbb{N}$          | Community assignment                          |
| $\mathbf{D}_i$ | $\mathbb{R}^{12}$     | Monthly energy demand profile                 |
| $F_i$          | $\mathbb{R}^+$        | Financial capacity                            |
| $\mathbf{G}_i$ | $\mathbb{R}^{12}$     | Monthly generation capacity                   |
| $B_{\text{cap},i}$ | $\mathbb{R}^+$    | Battery capacity                             |
| $B_i(t)$       | $\mathbb{R}^+$        | Current battery charge                        |
| $E_i(t)$       | $\mathbb{R}^+$        | Excess energy available                       |
| $S_i$          | $\{0,1\}$             | Solar installation indicator                  |
| $\mathbf{N}_i$ | $\{0,1\}^{10}$        | Neighbor adoption status                      |
| $\alpha_i$     | $[0,1]$               | Solar adoption propensity                     |
| $R_i$          | $\mathbb{R}$          | Expected return on investment                 |

#### 1.1.2 Community Coordinator ($C$)

Each community coordinator $C_j$ manages local energy distribution:

$$
C_j = \{id_j, g_j, \mathcal{H}_j, M_j(t), P_j(t)\}
$$

where:

| Variable       | Domain         | Description                            |
| -------------- | -------------- | -------------------------------------- |
| $id_j$         | $\mathbb{N}$   | Unique identifier                      |
| $g_j$          | $\mathbb{N}$   | Grid station assignment                |
| $\mathcal{H}_j$ | Set           | Set of household IDs (size 20)         |
| $M_j(t)$       | $\mathbb{R}^+$ | Market clearing price at time t        |
| $P_j(t)$       | $\mathbb{R}$   | Community-wide power balance          |

#### 1.1.3 Grid Station ($\Gamma$)

Each grid station $\Gamma_k$ represents a connection to the main power grid:

$$
\Gamma_k = \{id_k, \kappa_k, \omega_k(t), \lambda_k(t), \delta_k\}
$$

where:

| Variable       | Domain         | Description                |
| -------------- | -------------- | -------------------------- |
| $id_k$         | $\mathbb{N}$   | Unique identifier          |
| $\kappa_k$     | $\mathbb{R}^+$ | Maximum supply capacity    |
| $\omega_k(t)$  | $\mathbb{R}^+$ | Current load               |
| $\lambda_k(t)$ | $\mathbb{R}^+$ | Dynamic pricing function   |
| $\delta_k$     | $[0,1]$        | Grid reliability factor    |

### 2.1 Solar Generation and Storage

The simulation occurs in monthly timesteps with the following substeps:

#### 2.1.1 Solar Energy Generation

For each household $i$ with solar installation ($S_i = 1$), at time $t$:

$$
G_i(t) = \eta_s \cdot A_i \cdot I(t) \cdot (1 - \epsilon_t)
$$

where:
- $\eta_s$ is the solar panel efficiency
- $A_i$ is the installed panel area
- $I(t)$ is the solar irradiance at time $t$
- $\epsilon_t$ is the environmental loss factor

#### 2.1.2 Battery Storage Dynamics

The battery state of charge follows:

$$
B_i(t+1) = B_i(t) + \eta_b [G_i(t) - D_i(t)]_+ - \frac{[D_i(t) - G_i(t)]_+}{\eta_b}
$$

subject to:

$$
0 \leq B_i(t) \leq B_{\text{max},i}
$$

where:
- $\eta_b$ is the battery round-trip efficiency
- $[x]_+ = \max(0,x)$
- $B_{\text{max},i}$ is the battery capacity

#### 2.1.3 Available Trading Energy

For each household $i$ at time $t$:

$$
E_i(t) = [G_i(t) + \frac{B_i(t)}{\Delta t} - D_i(t)]_+
$$

where $\Delta t$ is the trading interval.

### 2.2 Market Mechanism

#### 2.2.1 Community-Level Market Clearing

The community coordinator performs market clearing every $\Delta t$, by calculating the aggregate supply and demand:

$$
S_j(t) = \sum_{i \in \mathcal{H}_j} E_i(t) \\
D_j(t) = \sum_{i \in \mathcal{H}_j} [D_i(t) - G_i(t) - \frac{B_i(t)}{\Delta t}]_+
$$

As well as the market clearing price:

$$
M_j(t) = \begin{cases}
\lambda_{\text{base}} & \text{if } S_j(t) \geq D_j(t) \\
\lambda_{\text{base}} + \phi(D_j(t) - S_j(t)) & \text{otherwise}
\end{cases}
$$

where $\phi(\cdot)$ is a price adjustment function.

### 2.3 Grid Interaction

The grid stations calculate the net community power balance:

$$
P_j(t) = S_j(t) - D_j(t)
$$

following which they calculate the energy demand from each community:

$$
G_{\text{net},j}(t) = \begin{cases}
-P_j(t) & \text{if } P_j(t) < 0 \text{ (import)} \\
\min(P_j(t), \kappa_{\text{export}}) & \text{if } P_j(t) > 0 \text{ (export)}
\end{cases}
$$

And follow the below logic for station load management for each station $k$:

$$
\omega_k(t+1) = \omega_k(t) + \sum_{j \in \mathcal{C}_k} G_{\text{net},j}(t)
$$

subject to:

$$
0 \leq \omega_k(t) \leq \kappa_k
$$

## 3. Environmental Parameters and Optimization

### 3.1 System Parameters

The simulation environment includes the following parameters that can be optimized:

#### 3.1.1 Cost Parameters

1. Installation Cost Optimization:

$$
C_{\text{install}}^* = \arg\min_{C} \sum_{i \in \mathcal{H}} \left(\frac{C}{F_i} - \frac{\sum_{t=1}^T R_i(t)}{(1+r)^t}\right)
$$

   where:
   - $C$ is the installation cost
   - $R_i(t)$ is the revenue at time $t$
   - $r$ is the discount rate
   - $T$ is the planning horizon

2. Maintenance Cost Optimization:

$$
C_{\text{maintain}}^* = \arg\min_{C_m} \sum_{t=1}^T \frac{C_m + \lambda(C_m)\cdot L(t)}{(1+r)^t}
$$

   where:
   - $\lambda(C_m)$ is the failure rate as a function of maintenance cost
   - $L(t)$ is the loss function for system failures

#### 3.1.2 Pricing Optimization

1. Grid Base Price:

$$
\lambda_{\text{base}}^* = \arg\max_{\lambda} \left(\sum_{t=1}^T R_{\text{grid}}(t,\lambda) - \sum_{j \in \mathcal{C}} P_j(t)\right)
$$

   subject to:

$$
\frac{1}{|\mathcal{H}|}\sum_{i \in \mathcal{H}} \frac{\lambda \cdot D_i(t)}{F_i} \leq \theta_{\text{afford}}
$$

   where:
   - $R_{\text{grid}}(t,\lambda)$ is grid revenue
   - $\theta_{\text{afford}}$ is the affordability threshold

2. Distribution Efficiency:

$$
\eta^* = \arg\max_{\eta} \left(\sum_{j \in \mathcal{C}} \text{CSSR}_j(\eta) - c(\eta)\right)
$$

   where:
   - $\text{CSSR}_j(\eta)$ is the Community Self-Sufficiency Ratio
   - $c(\eta)$ is the cost function for achieving efficiency $\eta$

### 3.3 Performance Metrics

The optimization process is evaluated using:

1. Community Self-Sufficiency Ratio:

$$
\text{CSSR}_j(T) = 1 - \frac{\sum_{t \in T} G_{\text{net},j}(t)^+}{\sum_{t \in T} \sum_{i \in \mathcal{H}_j} D_i(t)}
$$

2. Peak Import Reduction:

$$
\text{PIR}_j(T) = 1 - \frac{\max_{t \in T} G_{\text{net},j}(t)^+}{\max_{t \in T_0} G_{\text{net},j}(t)^+}
$$

3. Storage Utilization Factor:

$$
\text{SUF}_j(T) = \frac{1}{|T|} \sum_{t \in T} \frac{\sum_{i \in \mathcal{H}_j} B_i(t)}{\sum_{i \in \mathcal{H}_j} B_{\text{max},i}}
$$

4. System-wide Optimization Metric:

$$
\Phi = w_1\text{CSSR} + w_2\text{PIR} + w_3\text{SUF} - w_4\text{Cost}
$$

   where $w_i$ are importance weights determined through sensitivity analysis.

## 4. Experiments

### 4.1 Behind-the-Meter vs Community Solar Installation

#### Hypothesis 
Shared ownership through community solar installations reduces financial barriers to entry and increases overall solar adoption rates compared to individual behind-the-meter installations.

#### Extended State Space

1. Environment State Vector $\mathcal{E}$:

$$
\mathcal{E} = \{\ldots, C_s, b_{\text{min}}, M_s, \eta_b, \eta_c\}
$$

where:
- $C_s$: Community solar installation cost
- $b_{\text{min}}$: Minimum buy-in amount
- $M_s$: Shared maintenance cost
- $\eta_b$: BTM efficiency factor
- $\eta_c$: Community solar efficiency factor

2. Extended Household State $H_i'$:

$$
H_i' = \{H_i, \sigma_i, \tau_i\}
$$

where:
- $\sigma_i \in [0,1]$: Ownership share in community installation
- $\tau_i \in \{\text{btm}, \text{community}, \text{none}\}$: Installation type

3. Extended Community State $C_j'$:
$$
C_j' = \{C_j, K_j, \Sigma_j, \Sigma_j^a\}
$$

where:
- $K_j$: Shared generation capacity
- $\Sigma_j$: Total ownership shares
- $\Sigma_j^a$: Available shares

#### Modified System Dynamics

1. Solar Generation Function:

$$
G_i(t) = \begin{cases}
\eta_b \cdot g_i(t) & \text{if } \tau_i = \text{btm} \\
\eta_c \cdot \sigma_i \cdot K_j \cdot s(t) & \text{if } \tau_i = \text{community} \\
0 & \text{otherwise}
\end{cases}
$$

where:
- $g_i(t)$: Individual generation capacity
- $s(t)$: Solar irradiance at time $t$

2. Adoption Decision Function:

$$
\tau_i(t+1) = \begin{cases}
\text{btm} & \text{if } F_i \geq C_{\text{install}} \land R_i > r_{\text{min}} \\
\text{community} & \text{if } F_i \geq b_{\text{min}} \land \Sigma_j^a > 0 \\
\text{none} & \text{otherwise}
\end{cases}
$$

### 4.2 LMP-Based Solar Generation Incentives

#### Extended State Space

1. Environment Parameters:

$$
\mathcal{E}' = \{\mathcal{E}, \mu_p, \mu_s, \mathcal{T}_p, \mathcal{T}_s\}
$$

where:
- $\mu_p$: Peak price multiplier
- $\mu_s$: Shoulder price multiplier
- $\mathcal{T}_p$: Set of peak hours
- $\mathcal{T}_s$: Set of shoulder hours

#### Modified System Dynamics

1. Locational Marginal Price:

$$
\lambda_k(t) = \lambda_{\text{base}} \cdot \begin{cases}
\mu_p & \text{if } t \bmod 24 \in \mathcal{T}_p \\
\mu_s & \text{if } t \bmod 24 \in \mathcal{T}_s \\
1 & \text{otherwise}
\end{cases}
$$

2. Market Clearing Price:

$$
M_j(t) = \min(\lambda_k(t) \cdot 0.95, \lambda_{\text{base}} \cdot \frac{D_j(t)}{S_j(t)})
$$

3. Battery Storage Optimization:

$$
B_i(t+1) = \begin{cases}
\min(B_{\text{cap},i}, B_i(t) + E_i(t)) & \text{if } \lambda_k(t+1) > 1.5\lambda_k(t) \\
B_i(t) + \eta_b[G_i(t) - D_i(t)]_+ - \frac{[D_i(t) - G_i(t)]_+}{\eta_b} & \text{otherwise}
\end{cases}
$$

### 4.3 Social Influence on Solar Adoption

#### Extended State Space

1. Environment Parameters:

$$
\mathcal{E}'' = \{\mathcal{E}, R_{\text{ref}}, r_{\text{inf}}, \theta_n\}
$$

where:
- $R_{\text{ref}}$: Referral reward amount
- $r_{\text{inf}}$: Influence radius
- $\theta_n$: Neighbor adoption threshold

2. Extended Household State:

$$
H_i'' = \{H_i', \mathbf{r}_i, \rho_i, \omega_i, \phi_i\}
$$

where:
- $\mathbf{r}_i$: Vector of referrals made
- $\rho_i$: Number of successful referrals
- $\omega_i$: Accumulated rewards
- $\phi_i$: ID of influencing household

#### Modified System Dynamics

1. Social Influence Function:

$$
\Psi_i(t) = \frac{\sum_{j \in \mathcal{N}_i} \mathbb{1}[S_j(t) = 1]}{|\mathcal{N}_i|}
$$

where $\mathcal{N}_i$ is the set of neighbors within radius $r_{\text{inf}}$

2. Adoption Probability:

$$
P(S_i(t+1) = 1) = \min(1, \alpha_i + \beta \Psi_i(t)\mathbb{1}[\Psi_i(t) \geq \theta_n] + \gamma\mathbb{1}[\phi_i > 0])
$$

where:
- $\beta$: Neighbor influence factor (0.3)
- $\gamma$: Referral influence factor (0.2)

3. Reward Update Function:

For successful adoption at time $t$:

$$
\omega_{\phi_i}(t+1) = \omega_{\phi_i}(t) + R_{\text{ref}}
$$

### Performance Metrics

1. Installation Type Ratio:

$$
\text{ITR}(t) = \frac{\sum_{i} \mathbb{1}[\tau_i(t) = \text{community}]}{\sum_{i} \mathbb{1}[\tau_i(t) \in \{\text{btm}, \text{community}\}]}
$$

2. Peak Generation Response:

$$
\text{PGR}(t) = \frac{\sum_{h \in \mathcal{T}_p} G_{\text{total}}(h)}{\sum_{h=0}^{23} G_{\text{total}}(h)}
$$

3. Social Network Effect:

$$
\text{SNE}(t) = \frac{\sum_{i} \mathbb{1}[S_i(t) = 1 \land \phi_i > 0]}{\sum_{i} \mathbb{1}[S_i(t) = 1]}
$$

4. System-wide Metrics:

$$
\begin{aligned}
\text{FAI}(t) &= \frac{\sum_{i} \mathbb{1}[F_i \geq b_{\text{min}}]}{|\mathcal{H}|} \\
\text{PES}(t) &= \frac{\Delta G_{\text{total}}(t)/G_{\text{total}}(t)}{\Delta \lambda(t)/\lambda(t)} \\
\text{RE}(t) &= \frac{\sum_{i} \rho_i(t)}{\sum_{i} |\mathbf{r}_i(t)|}
\end{aligned}
$$

