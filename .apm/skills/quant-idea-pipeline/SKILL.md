---
name: quant-idea-pipeline
description: >-
  Use for every quant trading idea, from data provider check to the user's
  decision. Five roles move each idea through fixed gates; the Quant Reviewer
  reviews every gate; a GitHub issue records everything done.
---
# Quant idea pipeline

Version: 1.0 (2026-11-21)

## Roles
- Quant Data Scientist: provider check, ideas and research tests (maker).
- Data Science Reviewer: independent skeptic of the data science work.
- Backtester (Quant Developer): structured event-driven backtest (maker).
- Quant Risk Analyst: Monte Carlo and stress tests.
- Quant Reviewer: reviews every gate, all roles' work. Gives PASS or FAIL before any gate closes.

## Rules
- No role passes a gate for its own work. A gate closes only after the Quant Reviewer's PASS.
- Pass levels are set per idea in the locked plan before results are seen, then never changed.
- Every attempt is counted and logged, including failures.
- Reviewers review only; they never edit or fix the maker's work.
- Rejected ideas are closed with the reason, never deleted.
- The GitHub issue is the record. If it isn't on the issue, it didn't happen.

## GitHub record
- One issue per idea, titled "[Strategy] TRADING_XXXX: <name>", labelled `strategy` plus the current gate label: `gate-0-data`, `gate-a1`, `gate-a2`, `gate-a3`, `gate-b1`, `gate-b2`, `gate-b3`, `gate-decision`. Add `in_progress` while work is underway.
- The issue body holds the idea card. Edit it only to add links; never rewrite past content.
- Each gate gets a maker comment (what was done, evidence links, date) and a Quant Reviewer comment (PASS or FAIL with numbered reasons).
- End states: `done` (the user approved it), `killed` (closed with the reason), `archive` (parked).
- Code goes on a branch with a pull request linked to the issue. Never push to the main branch.

## Gates
| Gate | Maker | Extra reviewer | Tests | Output |
|---|---|---|---|---|
| 0 Data provider check | Quant Data Scientist | none | Provider integration tests | Provider report on its own issue |
| A1 Hypothesis and locked plan | Quant Data Scientist | none | none | Idea card and locked plan |
| A2 Research test | Quant Data Scientist | none | Unit tests, T1-T3, Data science work check self-check | Research report, decision log |
| A3 Independent review | Data Science Reviewer | none | T4, Data science work check | PASS or FAIL and handoff note |
| B1 Spec and build | Backtester | none | Unit tests, spec matches handoff | Spec, pull request, results |
| B2 Match and stress | Quant Risk Analyst | Data Science Reviewer (match check) | T5, T6, Stage A vs B comparison | Stress report |
| B3 Final out-of-sample | Backtester | Data Science Reviewer (watches) | T7 | Final results, one-page summary |
| Decision | the user | none | none | done, killed or archive |

The Quant Reviewer reviews every gate in this table before it closes.

## Gate 0: Data provider check (before any ideation; repeat when the provider or its setup changes)
Integration tests with real calls:
- Connection: sign-in works; errors and rate limits are handled without crashing.
- Coverage: every ticker, field and date range in the plan is returned.
- Correctness: spot-check prices, splits and dividends against a second source.
- Delisted stocks: included, or the gap is recorded.
- Point-in-time: fundamentals and index members as known on each date, or the gap is recorded.
- Gaps and duplicates: missing days, repeated rows and odd values are reported.
- Repeatable: the same request twice gives the same data; snapshot date recorded.
No idea starts Stage A until Gate 0 passes. Known gaps go into every idea's locked plan.

## Locked plan (Gate A1)
Hypothesis: why the edge exists, who is on the losing side, what would disprove it. Data split by date into in-sample, validation and out-of-sample (held back until B3). Benchmark, trading costs, slippage, maximum attempts, and the pass level for each test.

## Unit tests (every gate that writes code)
- Every function used has unit tests: signals, indicators, position sizing, costs, return and drawdown calculations, date handling.
- Each test checks a hand-worked result on small made-up data, including edge cases: empty data, one row, missing values, a stock split, first and last dates.
- Test what the code produces, not how it's written.
- No look-ahead test: a signal on any date doesn't change when later data is added.
- Tests run automatically on every pull request and must pass before merging. Every fixed bug adds a test that would have caught it.

## Tests
- T1 In-sample: build and tune on in-sample data only; log every version tried.
- T2 Walk-forward: tune on one window, test on the next unseen window, roll forward and repeat. Report each window separately and combined.
- T3 Parameter sensitivity: move each main parameter a step up and down; report a table. A real edge holds up nearby.
- T4 Luck tests: random entries with the same number of trades and holding period, repeated many times; shuffled signal dates, repeated many times; report the share of runs that did as well or better. Adjust for the number of versions tried (for example, deflated Sharpe ratio).
- T5 Monte Carlo: reshuffle trade order many times; bootstrap daily returns into many alternative histories. Report the worst case and a typical bad case for drawdown, yearly return and ending value.
- T6 Stress: rerun over crisis periods separately; double costs and slippage; delay each trade one bar; remove the biggest winners.
- T7 Final out-of-sample: run the frozen version once on held-back data. No changes afterwards. Failure means kill.

Every test: same costs, slippage and cash limits; no leverage, margin or short selling; record code version, data snapshot, random seed and number of repeats; compare with the benchmark over the same dates.

## Failing a gate
The reviewer gives numbered reasons and the evidence that would change the verdict. The maker may fix and resubmit up to 3 times, then the idea is killed or the user is asked. A failure at B3 is always a kill. If any check is beyond a reviewer's skill, they mark it CANNOT CHECK and flag it for the user.

## Writing
Plain, concise English. End every comment with a legend of any abbreviations used.

## Change log
- 1.0 (2026-11-21): first versioned release.
