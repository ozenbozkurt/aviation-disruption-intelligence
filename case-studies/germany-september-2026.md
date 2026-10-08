# Germany Network Performance — September 2026

A recruiter-facing case study built from 30 daily observations retrieved from the
public **EUROCONTROL Data app beta API**.

The goal is not to claim a safety-critical prediction. It is to show how an
aviation operations analyst can combine multiple network-performance signals,
rank unusual days transparently, and decide what evidence to investigate next.

## Executive summary

**Period:** 2026-09-01 to 2026-09-30  
**Observed days:** 30  
**Average daily flights:** 9,254  
**Total ATFM delay:** 175,369 minutes  
**Average ATFM delay per flight:** 0.626 minutes  
**Average arrival punctuality:** 76.95%  
**Average departure punctuality:** 70.93%

The strongest analytical finding is that the day with the **largest ATFM delay
per flight was not the day with the highest combined disruption index**.

- **16 September** had the month's highest ATFM delay per flight: **1.688 min/flight**.
- **9 September** ranked as the highest combined disruption day: **94.8/100**,
  because elevated ATFM delay coincided with materially weaker arrival and
  departure punctuality.

That distinction is useful operationally: one metric can identify one form of
network pressure, while a multi-signal screen can surface days with broader
performance deterioration.

## Five highest-ranked days

| Date | Index | Flights | ATFM delay (min) | ATFM delay / flight | Arrival punctuality | Departure punctuality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-09-09 | 94.8 | 9,532 | 12,450 | 1.306 | 68.84% | 64.01% |
| 2026-09-16 | 87.9 | 9,388 | 15,842 | 1.688 | 75.32% | 68.52% |
| 2026-09-10 | 86.2 | 9,688 | 9,887 | 1.020 | 73.59% | 65.67% |
| 2026-09-25 | 84.5 | 9,739 | 9,486 | 0.974 | 73.69% | 63.85% |
| 2026-09-04 | 81.9 | 9,426 | 8,674 | 0.920 | 74.88% | 63.59% |

## Five lowest-ranked days

| Date | Index | Flights | ATFM delay (min) | ATFM delay / flight | Arrival punctuality | Departure punctuality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-09-29 | 6.9 | 9,092 | 1,922 | 0.211 | 80.92% | 76.64% |
| 2026-09-15 | 10.3 | 9,169 | 2,875 | 0.314 | 82.06% | 76.95% |
| 2026-09-30 | 21.6 | 9,374 | 3,647 | 0.389 | 80.20% | 75.80% |
| 2026-09-02 | 22.4 | 9,325 | 3,650 | 0.391 | 81.22% | 75.31% |
| 2026-09-06 | 26.7 | 9,090 | 2,730 | 0.300 | 77.77% | 72.22% |

## Method

The **period-relative disruption index** ranks every observed day within the
selected month using:

- 50% — ATFM delay per flight rank
- 25% — arrival punctuality deterioration rank
- 25% — departure punctuality deterioration rank

Traffic volume is shown as operational context but is deliberately **not**
scored. A high-volume day is not automatically a disrupted day.

The score is relative to this 30-day sample. It is not an absolute benchmark
for Germany, EUROCONTROL, an airline, or an airport.

## Analyst interpretation

### Observation 1 — 9 September shows broader deterioration

9 September did not have the highest ATFM delay per flight, but it combined
**1.306 min/flight** with **68.84% arrival punctuality** and **64.01% departure
punctuality**. That combination pushed it above 16 September in the multi-signal
ranking.

### Observation 2 — 16 September is the ATFM-delay outlier

16 September produced **15,842 ATFM delay minutes** and **1.688 min/flight**, the
highest delay-per-flight value in the sample. Its punctuality values were weak,
but not as weak as 9 September's.

### Observation 3 — traffic volume is not enough to explain disruption

The five highest-ranked days were busy, but the index intentionally does not
interpret traffic volume as a cause. A credible causal explanation would need
additional evidence.

## What I would investigate next

For the highest-ranked days, an operations analyst should next examine:

1. weather and convective activity,
2. ATC capacity restrictions and regulations,
3. airport capacity or infrastructure constraints,
4. strikes or industrial action,
5. demand peaks and schedule concentration,
6. delay-cause categories and affected airports / flows.

Those sources would allow us to move from **"what deteriorated?"** to the harder
question: **"why did it deteriorate?"**

## How I would explain this in an interview

> I started with a single ATFM-delay metric, but I noticed that it could label a
> day as relatively healthy even when punctuality was poor. I changed the
> approach to a transparent period-relative index combining ATFM delay per
> flight with arrival and departure punctuality. In September 2026 Germany data,
> 16 September had the highest ATFM delay per flight, while 9 September ranked
> as the broader disruption day because punctuality also deteriorated. I would
> not claim the index explains the cause; the next step would be joining weather,
> capacity and delay-cause data.

That distinction — **measurement first, causal hypothesis second** — is central
to responsible operational analytics.

## Reproducibility and limitations

The repository includes a GitHub Actions workflow that can rebuild the input
dataset and case-study bundle from the EUROCONTROL Data app beta API.

This analysis is a portfolio and learning exercise. It is **not validated for
dispatch, operational control, flight safety, or go/no-go decisions**.

**Source:** https://data-app.eurocontrol.int/api
