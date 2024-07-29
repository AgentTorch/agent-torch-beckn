# Solar Network Model

## Outline

This model simulates a solar network in which households can decide to either buy solar
panels and act as providers (BPPs) of clean energy, or decide to use the energy provided
by other providers instead of installing solar panels themselves (BAPs).

The substeps are defined as follows, in the given order:

##### `search`/`select`/`order`

BAPs check their current resource level (here, the energy required for a month), and then
find the closest BPP that can provide that much energy.

They then select the BPP, and place an order for the same.

##### `confirm`/`fulfill`

BPPs reduce their availability based on the incoming orders, and confirm the orders they
can fulfill.

They then fulfill the order by providing energy to the BAP.

##### `pay`

The BAP deducts the amount to pay from the wallet, and the BPP adds that amount to their
revenue.

##### `restock`

The BPPs replenish the available energy based on the sizes of their solar panel
installations. This makes use of several assumptions:

1. Flat roofs generate ~11k MWh of AC electricty per roof, per year.
2. Sloped roofs' generation varies based on the direction they are facing, but it can be
   assumed to be ~7k MWh of AC electricity per roof, per year.

> These numbers are wildly approximated based on data from Google's
> [Project Sunroof](https://sunroof.withgoogle.com/), and are only for demo purposes.

---

> [!NOTE]
>
> The following improvements can be made to this model to make it more useful:
>
> - Add a BPP property, `capital_expense`, which keeps track of the initial cost of
>   installing a solar panel.
> - Allow BAPs to build positive or negative opinions of solar panels, which lead to them
>   buying their own solar panels, or not placing orders at all.
