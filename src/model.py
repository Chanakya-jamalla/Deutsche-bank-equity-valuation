"""
Excess Return (Residual Income) Valuation Model
=================================================
For banks, a standard FCFF/WACC DCF is a poor fit — capital structure
(deposits, leverage) is part of the business model, not a financing
choice, and "free cash flow" is not economically meaningful for a
lender. The excess return / residual income model instead values a
bank directly from its equity, which is the standard approach used by
equity research analysts covering banks.

Core idea
---------
A bank only creates value for shareholders when it earns a Return on
Equity (ROE) above its Cost of Equity (Ke). The model values equity as:

    Value of Equity = Book Value of Equity (today)
                       + PV of forecast Residual Income
                       + PV of Terminal Value

    Residual Income_t = Net Income_t - (Ke * Book Value_{t-1})
                       = Book Value_{t-1} * (ROE_t - Ke)

    Book Value_t = Book Value_{t-1} + Net Income_t - Dividends_t
                 = Book Value_{t-1} * (1 + ROE_t * (1 - payout_ratio))

    Terminal Value_n = Residual Income_{n+1} / (Ke - g)
"""

from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd


def cost_of_equity_capm(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """CAPM cost of equity: Ke = Rf + Beta * ERP"""
    return risk_free_rate + beta * equity_risk_premium


@dataclass
class ScenarioAssumptions:
    name: str
    roe_path: List[float]      # forecast ROE for each explicit year, e.g. 5 years
    payout_ratio: float        # % of net income paid out as dividends/buybacks
    terminal_growth: float     # long-run growth rate of residual income (g)


def run_residual_income_model(
    book_value_0_eur_bn: float,
    cost_of_equity: float,
    scenario: ScenarioAssumptions,
    shares_outstanding_bn: float,
) -> dict:
    """
    Runs a multi-year excess return valuation for one scenario.
    Returns a dict with the year-by-year path and the resulting
    value of equity / implied fair value per share.
    """
    years = len(scenario.roe_path)
    book_values = [book_value_0_eur_bn]
    residual_incomes = []
    net_incomes = []

    bv_prev = book_value_0_eur_bn
    for t in range(years):
        roe_t = scenario.roe_path[t]
        net_income_t = bv_prev * roe_t
        residual_income_t = bv_prev * (roe_t - cost_of_equity)

        # Retained earnings grow book value; the rest is paid out
        retained_t = net_income_t * (1 - scenario.payout_ratio)
        bv_t = bv_prev + retained_t

        net_incomes.append(net_income_t)
        residual_incomes.append(residual_income_t)
        book_values.append(bv_t)
        bv_prev = bv_t

    # Discount explicit-period residual income back to today
    discount_factors = [(1 + cost_of_equity) ** -(t + 1) for t in range(years)]
    pv_residual_incomes = [ri * df for ri, df in zip(residual_incomes, discount_factors)]

    # Terminal value: residual income grows at g in perpetuity beyond year n
    terminal_roe = scenario.roe_path[-1]
    ri_terminal_next = book_values[-1] * (terminal_roe - cost_of_equity)
    # Grow one more year at terminal growth for the "year n+1" residual income
    ri_n_plus_1 = ri_terminal_next * (1 + scenario.terminal_growth)
    terminal_value = ri_n_plus_1 / (cost_of_equity - scenario.terminal_growth)
    pv_terminal_value = terminal_value * discount_factors[-1]

    value_of_equity = book_value_0_eur_bn + sum(pv_residual_incomes) + pv_terminal_value
    fair_value_per_share = (value_of_equity * 1e9) / (shares_outstanding_bn * 1e9)

    return {
        "scenario": scenario.name,
        "years": list(range(1, years + 1)),
        "roe_path": scenario.roe_path,
        "book_values": book_values[1:],
        "net_incomes": net_incomes,
        "residual_incomes": residual_incomes,
        "pv_residual_incomes": pv_residual_incomes,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "value_of_equity_eur_bn": value_of_equity,
        "fair_value_per_share_eur": fair_value_per_share,
    }


def sensitivity_table(
    book_value_0_eur_bn: float,
    scenario: ScenarioAssumptions,
    shares_outstanding_bn: float,
    ke_range: List[float],
    g_range: List[float],
) -> pd.DataFrame:
    """Fair value per share across a grid of Cost of Equity x Terminal growth."""
    rows = []
    for ke in ke_range:
        row = []
        for g in g_range:
            local_scenario = ScenarioAssumptions(
                name=scenario.name,
                roe_path=scenario.roe_path,
                payout_ratio=scenario.payout_ratio,
                terminal_growth=g,
            )
            result = run_residual_income_model(
                book_value_0_eur_bn, ke, local_scenario, shares_outstanding_bn
            )
            row.append(round(result["fair_value_per_share_eur"], 2))
        rows.append(row)

    df = pd.DataFrame(
        rows,
        index=[f"{ke:.1%}" for ke in ke_range],
        columns=[f"{g:.1%}" for g in g_range],
    )
    df.index.name = "Cost of Equity"
    df.columns.name = "Terminal Growth"
    return df
