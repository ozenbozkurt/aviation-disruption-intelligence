# Period-relative Operational Disruption Index

This project now ranks days with a transparent, **period-relative** index.

## Formula

- ATFM delay per flight rank: **50%**
- arrival punctuality deterioration rank: **25%**
- departure punctuality deterioration rank: **25%**

Traffic volume is shown next to the score but is **not** part of the score.
High demand may create pressure, but a busy day is not automatically a
disrupted day.

The score is 0-100 **within the selected date range**. It is therefore useful
for answering:

> Which days in this sample looked most operationally disrupted?

It is not an absolute industry benchmark and it must not be used for dispatch,
flight-safety, or go/no-go decisions.

## Why this is better than one metric

ATFM delay per flight captures flow-management disruption, but a day can still
show poor passenger-facing performance through arrival or departure
punctuality. Combining all three signals gives a more balanced screening view.

The next analytical step is to investigate causes with additional evidence
(weather, capacity, ATC restrictions, strikes, airport constraints, demand
peaks) rather than treating the index itself as a causal model.
