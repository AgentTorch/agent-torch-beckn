# Mapping the Beckn Protocol to AgentTorch

## Beckn Architecture

The core components of the Beckn Protocol include:

### 1. Network Participants

- **BAP (Beckn Application Provider)**: Client-side applications
- **BPP (Beckn Provider Platform)**: Provider-side platforms
- **BG (Beckn Gateway)**: Intermediary for discovery and communication

### 2. Core Schema

- **Catalog**: Collection of items or services offered by a provider
- **Item**: Individual product or service
- **Order**: Transaction details
- **Fulfillment**: Delivery or service execution details
- **Rating**: Feedback mechanism

### 3. Operations

- **search**: Discover products or services
- **select**: Choose specific items to order
- **init**: Initiate an order
- **confirm**: Finalize a transaction
- **track**: Monitor order status
- **cancel**: Cancel an order
- **update**: Modify order/transaction details
- **rating**: Provide feedback
- **support**: Request assistance

## AgentTorch Architecture

Please see the
[architecture document](https://github.com/AgentTorch/AgentTorch/blob/master/docs/architecture.md)
for AgentTorch.

## Mapping

### 1. Network Participants as AgentTorch Agents

BAP, BPP, and BG will be considered agents, that interact with each other in the
simulation.

- **BAP (Beckn Application Provider)**

  - intent
  - current_order
  - items_ordered
  - feedback_provided
  - requests_made
  - money_spent

- **BPP (Beckn Provider Platform)**

  - network_traffic
  - revenue_earned
  - search_to_select_to_order
  - cancelled_orders

- **BG (Beckn Gateway)**
  - (object)

### 2. Core Schema as AgentTorch Objects

Catalog, Item, Order, Fulfillment, and Rating will be considered as objects.
These objects encapsulate the data structures defined in the Beckn Protocol.

### 3. Operations as AgentTorch Substeps

Each Beckn action (search, select, init, etc.) is mapped to an AgentTorch
substep, that is executed to move the simulation forward.

### 4. Beckn Network as AgentTorch Network

The BAP-Gateway-BPP network is structured
[as shown](https://github.com/beckn/beckn-onix/blob/main/docs/user_guide.md#sample-deployment-diagram).

This will be represented in AgentTorch using a pair of heterogeneous
`agent_object` networks, of the BAPs and BGs, as well as the BPPs and BGs.

---

> [!NOTE]
>
> All the Beckn operations are asynchronous by definition. This means that when
> a `select` API call is made by a BAP to a BPP, the BPP will only respond to
> the BAP with an acknowledgement of the received request. The actual response
> will be sent back in a `on_select` API call from the BPP to the BAP. However,
> for simplicity, we will assume that the API calls are synchronous in the
> simulation.
