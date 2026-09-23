# Deutsche Bank AG — Python-Based Equity Valuation & Scenario Analysis

A Python implementation of the **excess return (residual income) model** to value Deutsche Bank AG's equity, with Bull/Base/Bear scenario analysis and sensitivity testing — built as a resume/portfolio project.

## Why this model, for this company

Deutsche Bank is a bank. A standard FCFF/WACC DCF is a poor fit for banks: deposits and leverage are part of the operating business, not a discretionary financing choice, so "free cash flow to the firm" isn't economically meaningful for a lender. The **excess return / residual income model** instead values the bank directly from its equity — the approach used by equity research analysts covering banks.

**Core logic:** a bank only creates shareholder value when its Return on Equity (ROE) exceeds its Cost of Equity (Ke).

```
Value of Equity   = Book Value of Equity (today)
                   + PV of forecast Residual Income
                   + PV of Terminal Value

Residual Income_t = Book Value_(t-1) x (ROE_t - Cost of Equity)

Terminal Value_n  = Residual Income_(n+1) / (Cost of Equity - g)
```

## Project structure

```
db-valuation/
├── README.md
├── requirements.txt
├── main.py                        # run end-to-end, saves charts + CSVs
├── notebooks/
│   └── DB_Valuation_Model.ipynb   # narrative walkthrough with charts
├── src/
│   ├── data.py                    # DB's FY2025 inputs, sourced from public filings
│   ├── model.py                   # the residual income valuation engine (CAPM, RI, sensitivity)
│   └── scenarios.py               # Bull / Base / Bear ROE assumptions
└── outputs/                       # generated CSVs + charts (created on run)
```

## Data sources

All inputs are sourced from Deutsche Bank's own public disclosures:

- *Deutsche Bank hits 2025 financial targets with record full-year and fourth-quarter profits* — db.com, 29 Jan 2026
- *Deutsche Bank publishes 2025 Annual Report and confirms outlook for 2026* — db.com, 12 Mar 2026
- Deutsche Bank Q1/Q3 2025 Earnings Reports & Financial Data Supplements — investor-relations.db.com

Key FY2025 figures used: net profit €7.1bn, total equity ~€80.2bn, ~1.90bn shares outstanding, post-tax RoE 9.3% / RoTE 10.3%, CET1 ratio 14.2%, net revenues €32.1bn, cost/income ratio 64%.

## How to run

```bash
pip install -r requirements.txt

# Option A — script (prints results, saves charts + CSVs to outputs/)
python main.py

# Option B — notebook (narrative walkthrough)
jupyter notebook notebooks/DB_Valuation_Model.ipynb
```

## Methodology notes / assumptions

- **Cost of Equity** is estimated via CAPM (risk-free rate + beta × equity risk premium). All three inputs are illustrative and clearly labelled as adjustable assumptions in `main.py` / the notebook.
- **Scenarios** span a 5-year explicit forecast horizon (FY2026F–FY2030F), with ROE glide paths anchored to Deutsche Bank's own disclosed FY2025 results and management's stated RoTE ambition (>13% by 2028).
- **Terminal value** assumes residual income grows at a modest long-run rate (g) in perpetuity beyond the explicit forecast.
- Book value is used as reported (total equity), not adjusted for AT1 instruments or minority interests — a simplification appropriate for a learning project.

## Limitations

This is an educational/portfolio project, not investment research or advice. Forecast ROE paths, the cost of equity, and the terminal growth rate are all assumptions the user can and should stress-test — the sensitivity table in the notebook exists specifically to show how much the output depends on them.

## Author

Chanakya Jamalla — MSc Finance, Banking & Investment, Technical University of Košice (TUKE)
