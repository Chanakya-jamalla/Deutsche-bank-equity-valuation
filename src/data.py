"""
Deutsche Bank AG — Input Data
==============================
All figures below are sourced from Deutsche Bank's own public disclosures
(FY2025 Annual Report, Q4/FY2025 results press release, and quarterly
Financial Data Supplements). Each figure is commented with its source so
values can be refreshed each reporting season.

Sources:
- "Deutsche Bank hits 2025 financial targets with record full-year and
  fourth-quarter profits" (db.com, 29 Jan 2026)
- "Deutsche Bank publishes 2025 Annual Report and confirms outlook for 2026"
  (db.com, 12 Mar 2026)
- Deutsche Bank Q1/Q3 2025 Earnings Reports (investor-relations.db.com)

NOTE: This is an educational/portfolio project, not investment advice.
Figures are the best publicly available approximations at the time of
writing and may be refined with exact Annual Report page references.
"""

from dataclasses import dataclass


@dataclass
class DBFinancials:
    # --- Balance sheet (FY2025 year-end) ---
    total_equity_eur_bn: float = 80.2        # Total equity, FY2025 year-end
    shares_outstanding_bn: float = 1.90       # Basic shares outstanding, FY2025 year-end

    # --- Income statement (FY2025) ---
    net_profit_eur_bn: float = 7.1            # Net profit attributable to DB shareholders, FY2025
    net_revenues_eur_bn: float = 32.1         # Net revenues, FY2025
    cost_income_ratio: float = 0.64           # Cost/income ratio, FY2025

    # --- Profitability targets / actuals ---
    post_tax_rote: float = 0.103              # Post-tax Return on Tangible Equity, FY2025
    post_tax_roe: float = 0.093               # Post-tax Return on Equity, FY2025
    cet1_ratio: float = 0.142                 # CET1 capital ratio, FY2025 year-end

    # --- Capital return ---
    dividend_per_share_eur: float = 1.00      # Proposed dividend per share for FY2025

    # --- Market data (approximate, for reference only — update to trade date) ---
    share_price_eur: float = 32.00            # Approx. DB share price used for comparison


def book_value_per_share(fin: DBFinancials) -> float:
    """Book value of equity per share, in EUR."""
    return (fin.total_equity_eur_bn * 1e9) / (fin.shares_outstanding_bn * 1e9)


def net_income_eur_bn(fin: DBFinancials) -> float:
    return fin.net_profit_eur_bn


if __name__ == "__main__":
    fin = DBFinancials()
    print(f"Book value per share: EUR {book_value_per_share(fin):.2f}")
    print(f"FY2025 net profit: EUR {fin.net_profit_eur_bn:.1f}bn")
    print(f"FY2025 RoE: {fin.post_tax_roe:.1%}")
