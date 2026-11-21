---
name: data-science-work-check
description: >-
  Use to scrutinize a quant data science result (backtest, model, signal or
  formula) before it is reported or approved. The maker runs it as a self-check
  before handing off; a reviewer runs it to give PASS or FAIL.
---
# Data science work check

Version: 1.0 (2026-11-21)

## Who uses it
- Maker: run every item on your own work before handing off. Fix what you can; list what you couldn't.
- Reviewer: run every item independently. Review only; never edit or fix the maker's work. Assume there is a hidden flaw until the evidence rules it out. Check down to the finest detail; never skim.

## Inputs needed
The code or report link, the data and date range, the decision log (every attempt, including failures), and the exact commands used. If any is missing, the result is FAIL: missing input.

## 1. Reproducibility
- Rerun from a clean start using only the stated code, data and commands.
- Every key number must match. If it doesn't, report each difference and its size.
- Check that settings like random seeds, software versions and data snapshot dates are recorded.

## 2. Backtest errors
- Look-ahead bias: any input used before it was actually available.
- Survivorship bias: stocks that were later delisted are missing.
- Timing: signals use only information known at that time, trades happen on the next possible price, and dates and time zones line up.
- Data: gaps, duplicates, wrong stock-split or dividend adjustments, and outliers.
- Trading costs and slippage (the difference between the expected price and the actual fill) are included and realistic.
- Position sizes never go above the cash available (no leverage, margin or short selling).
- Multiple testing: the number of attempts is stated, and results are judged allowing for luck from trying many times.

## 3. Formula and calculation checks
- Recompute every headline figure independently, such as returns, drawdown, Sharpe ratio and win rate, and compare with the reported value.
- Check each formula line by line: inputs, units, annualization, compounding, sign, and off-by-one errors in dates or rows.
- Check a few individual trades by hand from the raw data through to profit or loss.

## 4. Devil's advocate (what if)
List the strongest case against the result, then ask:
- What if the market regime changes (crash, rising rates, low volatility)?
- What if costs, slippage or delays double?
- What if a key assumption or data source is wrong?
- What if the edge is luck or overfitting (a model fitted too closely to past data)?
- What if the biggest winning trades are removed?
- What risk is missing from the report entirely?
Say how each scenario would change the result, and test the most serious ones where the data allows.

## Verdict
- Mark each item PASS, FAIL or CANNOT CHECK, with evidence.
- Overall PASS only if nothing fails. For each FAIL, give the numbered reason and the evidence that would change the verdict.
- If an item is beyond your skill, mark it CANNOT CHECK and flag it for the user. Never guess a PASS.
- After 3 failed review rounds on the same work, stop and report both views to the user.

## Report
Write in plain, concise English. End with a legend of any abbreviations used.

## Change log
- 1.0 (2026-11-21): first versioned release.
