"""
Deutsche Bank AG — Python-Based Equity Valuation & Scenario Analysis
======================================================================
Run with:  python main.py

Produces:
  - Console summary of fair value per share under Bull/Base/Bear scenarios
  - outputs/charts/scenario_comparison.png
  - outputs/charts/residual_income_path.png
  - outputs/charts/sensitivity_heatmap.png
  - outputs/valuation_summary.csv
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.data import DBFinancials, book_value_per_share
from src.model import cost_of_equity_capm, run_residual_income_model, sensitivity_table
from src.scenarios import BASE_CASE, BULL_CASE, BEAR_CASE, ALL_SCENARIOS

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
CHART_DIR = os.path.join(OUT_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
NAVY = "#1F3864"
GREY = "#8C8C8C"
GREEN = "#2E7D32"
RED = "#B00020"


def main():
    fin = DBFinancials()

    # --- Cost of equity (CAPM) ---
    risk_free_rate = 0.025      # ~German 10Y Bund yield, illustrative
    beta = 1.25                 # DB's beta has historically run above 1 given its IB/markets mix
    equity_risk_premium = 0.055  # long-run European equity risk premium, illustrative
    ke = cost_of_equity_capm(risk_free_rate, beta, equity_risk_premium)

    print("=" * 70)
    print("DEUTSCHE BANK AG — EXCESS RETURN (RESIDUAL INCOME) VALUATION")
    print("=" * 70)
    print(f"Book value of equity (FY2025):     EUR {fin.total_equity_eur_bn:.1f}bn")
    print(f"Shares outstanding:                 {fin.shares_outstanding_bn:.2f}bn")
    print(f"Book value per share:                EUR {book_value_per_share(fin):.2f}")
    print(f"Cost of equity (CAPM):                {ke:.2%}  "
          f"(Rf {risk_free_rate:.1%} + Beta {beta:.2f} x ERP {equity_risk_premium:.1%})")
    print(f"Reference share price:               EUR {fin.share_price_eur:.2f}")
    print("-" * 70)

    results = {}
    for scenario in ALL_SCENARIOS:
        result = run_residual_income_model(
            book_value_0_eur_bn=fin.total_equity_eur_bn,
            cost_of_equity=ke,
            scenario=scenario,
            shares_outstanding_bn=fin.shares_outstanding_bn,
        )
        results[scenario.name] = result
        upside = (result["fair_value_per_share_eur"] / fin.share_price_eur) - 1
        print(f"{scenario.name:12s}  Fair value/share: EUR {result['fair_value_per_share_eur']:6.2f}  "
              f"({upside:+.1%} vs current price)")

    print("-" * 70)

    # --- Save summary CSV ---
    summary_rows = []
    for name, r in results.items():
        summary_rows.append({
            "Scenario": name,
            "Fair Value per Share (EUR)": round(r["fair_value_per_share_eur"], 2),
            "Implied Value of Equity (EUR bn)": round(r["value_of_equity_eur_bn"], 1),
            "Upside/Downside vs Market Price": round(
                (r["fair_value_per_share_eur"] / fin.share_price_eur) - 1, 4
            ),
        })
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(OUT_DIR, "valuation_summary.csv"), index=False)
    print(f"Saved: outputs/valuation_summary.csv")

    # === Chart 1: Scenario comparison (bar chart) ===
    fig, ax = plt.subplots(figsize=(7, 4.5))
    names = list(results.keys())
    values = [results[n]["fair_value_per_share_eur"] for n in names]
    colors = [RED, NAVY, GREEN] if "Bear" in names[2] or True else [NAVY] * 3
    bar_colors = {"Bear Case": RED, "Base Case": NAVY, "Bull Case": GREEN}
    ax.bar(names, values, color=[bar_colors[n] for n in names], width=0.5)
    ax.axhline(fin.share_price_eur, color=GREY, linestyle="--", linewidth=1.2,
               label=f"Current price (EUR {fin.share_price_eur:.2f})")
    for i, v in enumerate(values):
        ax.text(i, v + 0.5, f"EUR {v:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylabel("Fair Value per Share (EUR)")
    ax.set_title("Deutsche Bank AG — Implied Fair Value by Scenario\n(Excess Return / Residual Income Model)")
    ax.legend(loc="upper left", frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "scenario_comparison.png"), dpi=150)
    plt.close()
    print("Saved: outputs/charts/scenario_comparison.png")

    # === Chart 2: Residual income path (Base case) ===
    base_result = results["Base Case"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(base_result["years"], base_result["residual_incomes"], color=NAVY, width=0.5,
           label="Residual Income (EUR bn)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Forecast Year")
    ax.set_ylabel("Residual Income (EUR bn)")
    ax.set_title("Base Case — Forecast Residual Income (2026F–2030F)\nResidual Income = Book Value x (ROE - Cost of Equity)")
    ax.set_xticks(base_result["years"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "residual_income_path.png"), dpi=150)
    plt.close()
    print("Saved: outputs/charts/residual_income_path.png")

    # === Chart 3: Sensitivity heatmap (Cost of Equity x Terminal Growth) ===
    ke_range = [ke - 0.01, ke - 0.005, ke, ke + 0.005, ke + 0.01]
    g_range = [0.010, 0.015, 0.020, 0.025, 0.030]
    sens_df = sensitivity_table(
        book_value_0_eur_bn=fin.total_equity_eur_bn,
        scenario=BASE_CASE,
        shares_outstanding_bn=fin.shares_outstanding_bn,
        ke_range=ke_range,
        g_range=g_range,
    )
    sens_df.to_csv(os.path.join(OUT_DIR, "sensitivity_table.csv"))
    print("Saved: outputs/sensitivity_table.csv")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(sens_df.values, cmap="RdYlGn", aspect="auto")
    ax.set_xticks(range(len(sens_df.columns)))
    ax.set_xticklabels(sens_df.columns)
    ax.set_yticks(range(len(sens_df.index)))
    ax.set_yticklabels(sens_df.index)
    ax.set_xlabel("Terminal Growth Rate (g)")
    ax.set_ylabel("Cost of Equity (Ke)")
    ax.set_title("Sensitivity — Fair Value per Share (EUR)\nBase Case")
    for i in range(len(sens_df.index)):
        for j in range(len(sens_df.columns)):
            ax.text(j, i, f"{sens_df.values[i, j]:.1f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, label="EUR / share")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "sensitivity_heatmap.png"), dpi=150)
    plt.close()
    print("Saved: outputs/charts/sensitivity_heatmap.png")

    print("=" * 70)
    print("Done.")


if __name__ == "__main__":
    main()
