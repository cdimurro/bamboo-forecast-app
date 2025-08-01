import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from scipy.optimize import newton  # Add this import for robust IRR

# ... (All input expanders remain the same; no changes needed)

# Hardcoded values (unchanged)
total_initial_capex = 50000.0
working_capital_req = 5000.0
depreciation_rate = 7.0
corporate_tax_rate = 21.0
inflation_rate_costs = 3.0
inflation_rate_revenue = 3.0
discount_rate_npv = 10.0
capacity_util_rate = 70.0

# Button to generate forecasts
if st.button("Generate Financial Forecasts"):
    # Add loan origination fee to initial costs
    loan_origination_fee = debt_financing_amt * (loan_origination_fee_pct / 100)

    # Year 0: Initial investments - Adjusted for equity IRR
    total_initial_investment = total_initial_capex + working_capital_req + reg_compliance_initial + loan_origination_fee
    net_cash_year0 = -equity_investment  # Change: Only equity as negative outflow; debt assumed to fund investment but not added as inflow

    # ... (annual_depreciation, loan parameters unchanged)

    # Prepare DataFrame (unchanged)
    # ...

    # Calculate for each year (unchanged, including additional land logic)
    # ...

    # Year 0 row - Update Free Cash Flow to net_cash_year0
    year0 = pd.DataFrame({
        "Year": [0],
        "Revenue Bamboo": [0],
        "Revenue Biochar": [0],
        "Revenue Carbon Credits": [0],
        "Revenue Byproducts": [0],
        "Total Revenue": [0],
        "Operating Costs": [0],
        "EBITDA": [0],
        "Depreciation": [0],
        "EBIT": [0],
        "Interest Expense": [0],
        "EBT": [0],
        "Taxes": [0],
        "Net Income": [0],
        "Cash Flow from Operations": [net_cash_year0],
        "Capex": [total_initial_capex],
        "Debt Principal Payment": [0],
        "Free Cash Flow": [net_cash_year0],
    })
    df = pd.concat([year0, df], ignore_index=True)

    # NPV calculation (unchanged)
    discount_rate = discount_rate_npv / 100
    npv = npf.npv(discount_rate, df["Free Cash Flow"])

    # IRR - Use robust solver with guess
    def calculate_irr(cashflows):
        def npv_func(r):
            return sum(cf / (1 + r)**t for t, cf in enumerate(cashflows))
        try:
            return newton(npv_func, 0.1) * 100  # Guess 10%
        except:
            return "N/A"
    irr = calculate_irr(df["Free Cash Flow"].tolist())

    # ... (Display results unchanged)