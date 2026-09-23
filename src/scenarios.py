"""
Scenario Assumptions
=====================
Three scenarios spanning a 5-year explicit forecast horizon (FY2026-FY2030).
ROE paths are anchored to Deutsche Bank's own disclosed targets:
  - FY2025 actual post-tax RoTE: 10.3% / RoE: 9.3%
  - Management's stated ambition: post-tax RoTE > 13% by 2028

Base case assumes a gradual, realistic glide path toward (not all the way
to) management's target. Bull/Bear flex that glide path up and down.
These are assumptions for a student project, not analyst forecasts —
adjust them freely.
"""

from src.model import ScenarioAssumptions

BASE_CASE = ScenarioAssumptions(
    name="Base Case",
    roe_path=[0.095, 0.100, 0.105, 0.110, 0.112],  # gradual improvement toward ~11%
    payout_ratio=0.50,      # ~50% of earnings distributed (dividends + buybacks)
    terminal_growth=0.02,   # long-run nominal growth, in line with eurozone GDP/inflation
)

BULL_CASE = ScenarioAssumptions(
    name="Bull Case",
    roe_path=[0.100, 0.110, 0.120, 0.128, 0.130],  # approaches management's >13% ambition
    payout_ratio=0.60,      # higher payout as capital generation strengthens
    terminal_growth=0.025,
)

BEAR_CASE = ScenarioAssumptions(
    name="Bear Case",
    roe_path=[0.085, 0.085, 0.088, 0.090, 0.090],  # stalls below cost of equity
    payout_ratio=0.40,      # capital retained defensively
    terminal_growth=0.015,
)

ALL_SCENARIOS = [BASE_CASE, BULL_CASE, BEAR_CASE]
