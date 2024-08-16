# Household Solar Energy Model Card for AgentTorch

## Model Details
- **Name:** Household Solar Energy Market Model
- **Version:** 0.4.0
- **Type:** Agent-based model (ABM) environment
- **Framework:** AgentTorch v0.4.0
- **Execution Mode:** Simulation with visualization

## Intended Use
- **Primary Use:** Simulate a decentralized energy market with households producing and consuming solar energy
- **Intended Users:** Energy economists, policymakers, urban planners, and researchers studying renewable energy adoption and market dynamics

## Model Architecture
- **Simulation Duration:** 1 episode, 50 steps per episode, 5 substeps per step
- **Agent Types:**
  - BAP (Buyer App): 96,383 agents
  - BPP (Battery/Panel Provider): 49,354 agents
  - BG (Routing Grid Gateway): 1 agent
- **Objects:** Up to 99,999 orders

## Components

### Agents
1. **BAP (Buyer App):**
   - Properties: ID, position (street number), resource demand, current order, wallet
   - Behaviors: Search and select BPP, consume service, pay for service

2. **BPP (Battery/Panel Provider):**
   - Properties: ID, position, revenue, price, max capacity, available capacity
   - Behaviors: Confirm orders, provide service, restock capacity

3. **BG (Routing Grid Gateway):**
   - Properties: ID, network traffic
   - Behaviors: Manage network traffic (not explicitly defined in substeps)

### Objects
- **Order:**
  - Properties: ID, BAP ID, BPP ID, quantity, status

### Environment Variables
- Last created order ID

## Simulation Substeps
1. **Search and Select:** BAPs search for and select appropriate BPPs
2. **Confirm:** BPPs confirm orders
3. **Fulfill:** BAPs receive service from BPPs
4. **Pay:** BAPs pay for the service
5. **Restock:** BPPs restock their service capacity, BAPs receive income

## Input Data
- BAP positions (from file)
- BPP positions (from file)
- BPP max capacities (from file)

## Model Parameters
- **BAP:**
  - Initial resource demand: Random between 420-1313 kWh
  - Initial wallet: Random between 100-1000 (currency units)

- **BPP:**
  - Initial price: Random between 0.25-0.5 (currency units per kWh)
  - Initial available capacity: Random between 2000-4000 (units)

## Key Features
- Decentralized energy market simulation
- Dynamic pricing and capacity management for energy providers
- Spatial component with agent positions affecting interactions
- Order creation and fulfillment process

## Output Data
- Order statuses and quantities
- BAP resource consumption and wallet balances
- BPP revenues and available capacities
- Network traffic (via BG agent)

## Technical Specifications
- **Programming Language:** Python
- **Dependencies:** AgentTorch v0.4.0 framework, PyTorch
- **Compute Requirements:** CPU (as specified in config)
- **Visualization:** Enabled

## Limitations
- Simplified representation of energy production and consumption
- Does not account for time-of-day or seasonal variations in solar energy production
- Fixed number of agents without dynamic entry/exit from the market
- Simplified pricing model that may not capture all real-world factors

## Ethical Considerations
- Model simplifications may not accurately represent all aspects of real-world energy markets
- Results should be interpreted cautiously when applied to energy policy or investment decisions
- Privacy considerations when using location-based data for agent positioning

## References
- AgentTorch GitHub repository: [github.com/AgentTorch/AgentTorch](https://github.com/AgentTorch/AgentTorch)
- [Additional references for decentralized energy market models]
