import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

# Title
st.title("Interactive Financial Model for Bamboo and Biochar Business")

# Instructions
st.markdown("""
This app allows you to input values for a financial model evaluating a small bamboo and biochar business.
Adjust the inputs below and click 'Generate Forecasts' to see the financial projections.
Defaults are based on real-world data approximations as of 2025.
""")

# Organize inputs into sections using expanders
with st.expander("Land and Cultivation Inputs"):
    land_area = st.number_input("1. Land area for bamboo cultivation (hectares)", min_value=0.1, max_value=100.0, value=2.0)
    land_cost_per_ha = st.number_input("2. Land acquisition or lease cost per hectare ($)", min_value=0.0, value=10000.0)
    soil_prep_cost_per_ha = st.number_input("3. Soil preparation and testing cost per hectare ($)", min_value=0.0, value=8000.0)
    seedling_cost_per_unit = st.number_input("4. Bamboo seedling or propagule cost per unit ($)", min_value=0.0, value=2.0)
    planting_density = st.number_input("5. Planting density (plants per hectare)", min_value=0.0, value=1130.0)
    planting_labor_per_ha = st.number_input("6. Initial planting labor cost per hectare ($)", min_value=0.0, value=1000.0)
    growth_period = st.number_input("7. Growth period to first harvest (years)", min_value=1, max_value=10, value=4)
    harvest_cycle_freq = st.number_input("8. Harvest cycle frequency (times per year)", min_value=0.0, value=1.0)
    annual_yield_per_ha = st.number_input("9. Annual bamboo biomass yield per hectare (tons)", min_value=0.0, value=20.0)
    fertilizer_cost_per_ha_yr = st.number_input("10. Fertilizer application cost per hectare per year ($)", min_value=0.0, value=400.0)
    irrigation_install_cost = st.number_input("11. Irrigation system installation cost ($ total)", min_value=0.0, value=6000.0)  # For 2 ha, $3000/ha
    annual_irrigation_maint = st.number_input("12. Annual water and irrigation maintenance cost ($)", min_value=0.0, value=1000.0)
    pest_control_per_ha_yr = st.number_input("13. Pest and disease control cost per hectare per year ($)", min_value=0.0, value=100.0)
    weed_mgmt_per_ha_yr = st.number_input("14. Weed management and maintenance labor cost per hectare per year ($)", min_value=0.0, value=200.0)
    harvesting_cost_per_ton = st.number_input("15. Harvesting labor and equipment cost per ton ($)", min_value=0.0, value=30.0)
    internal_trans_cost_per_ton = st.number_input("16. Internal transportation cost from field to processing site per ton ($)", min_value=0.0, value=5.0)

with st.expander("Biochar Production Inputs"):
    pct_to_biochar = st.number_input("17. Percentage of harvested bamboo allocated to biochar production (%)", min_value=0.0, max_value=100.0, value=50.0)
    biochar_conversion_eff = st.number_input("18. Biochar conversion efficiency (tons of biochar per ton of bamboo)", min_value=0.0, max_value=1.0, value=0.25)
    pyrolysis_equip_cost = st.number_input("19. Pyrolysis or kiln equipment purchase cost ($)", min_value=0.0, value=20000.0)
    equip_install_cost = st.number_input("20. Equipment installation and setup cost ($)", min_value=0.0, value=5000.0)
    biochar_prod_capacity = st.number_input("21. Biochar production capacity (tons per year)", min_value=0.0, value=50.0)
    energy_cost_per_ton = st.number_input("22. Energy input cost for pyrolysis process per ton ($)", min_value=0.0, value=10.0)
    labor_cost_per_ton_biochar = st.number_input("23. Labor cost for biochar production per ton ($)", min_value=0.0, value=20.0)
    equip_maint_per_yr = st.number_input("24. Equipment maintenance and repair cost per year ($)", min_value=0.0, value=1000.0)
    byproduct_value_per_ton_bamboo = st.number_input("25. By-product recovery value (e.g., syngas, bio-oil) per ton of bamboo processed ($)", min_value=0.0, value=50.0)  # Assumed net value

with st.expander("Sales and Revenue Inputs"):
    bamboo_price_per_ton = st.number_input("26. Selling price of raw bamboo per ton ($)", min_value=0.0, value=100.0)
    biochar_price_per_ton = st.number_input("27. Selling price of biochar per ton ($)", min_value=0.0, value=400.0)
    annual_bamboo_sales_vol = st.number_input("28. Projected annual sales volume for raw bamboo (tons)", min_value=0.0, value=20.0)  # Initial, will be overridden by calc if harvest
    annual_biochar_sales_vol = st.number_input("29. Projected annual sales volume for biochar (tons)", min_value=0.0, value=10.0)
    annual_sales_growth = st.number_input("30. Annual sales growth rate (%)", min_value=0.0, value=10.0)
    carbon_credit_price = st.number_input("31. Carbon credit or offset price per ton of CO2 sequestered ($)", min_value=0.0, value=10.0)
    co2_seq_per_ton_biochar = st.number_input("32. CO2 sequestration rate per ton of biochar (tons CO2)", min_value=0.0, value=2.5)

with st.expander("Operating Expenses Inputs"):
    admin_office_exp_annual = st.number_input("33. Administrative and office expenses (annual $)", min_value=0.0, value=5000.0)
    marketing_exp_pct_rev = st.number_input("34. Marketing and sales promotion expenses (% of revenue)", min_value=0.0, value=2.0)
    insurance_premiums = st.number_input("35. Insurance premiums for operations and assets ($ annual)", min_value=0.0, value=2000.0)
    reg_compliance_initial = st.number_input("36. Regulatory compliance and permit costs (initial $)", min_value=0.0, value=1000.0)
    reg_compliance_annual = st.number_input("36b. Regulatory compliance and permit costs (annual $)", min_value=0.0, value=300.0)  # Split for model
    product_trans_cost_per_ton = st.number_input("37. Product transportation and logistics cost per ton ($)", min_value=0.0, value=15.0)

with st.expander("Financial Structure Inputs"):
    total_initial_capex = st.number_input("38. Total initial capital expenditure ($)", min_value=0.0, value=100000.0)  # Approx sum: land 20k, soil 16k, seedlings ~4.5k, labor 2k, irrig 6k, equip 25k, etc.
    working_capital_req = st.number_input("39. Working capital requirement ($)", min_value=0.0, value=10000.0)
    debt_financing_amt = st.number_input("40. Debt financing amount ($)", min_value=0.0, value=60000.0)
    interest_rate_debt = st.number_input("41. Interest rate on debt (%)", min_value=0.0, value=6.0)
    loan_repayment_term = st.number_input("42. Loan repayment term (years)", min_value=1, max_value=50, value=15)
    equity_investment = st.number_input("43. Equity investment amount ($)", min_value=0.0, value=60000.0)
    depreciation_rate = st.number_input("44. Depreciation rate for equipment and assets (%)", min_value=0.0, value=7.0)
    corporate_tax_rate = st.number_input("45. Corporate tax rate (%)", min_value=0.0, value=21.0)
    inflation_rate_costs = st.number_input("46. Inflation rate for operating costs (%)", min_value=0.0, value=3.0)
    inflation_rate_revenue = st.number_input("47. Inflation rate for revenue prices (%)", min_value=0.0, value=3.0)
    discount_rate_npv = st.number_input("48. Discount rate for net present value calculations (%)", min_value=0.0, value=10.0)
    projection_horizon = st.number_input("49. Financial projection horizon (years)", min_value=1, max_value=50, value=10)
    capacity_util_rate = st.number_input("50. Capacity utilization rate (%)", min_value=0.0, max_value=100.0, value=70.0)

# Button to generate forecasts
if st.button("Generate Financial Forecasts"):
    # Calculations
    # Year 0: Initial investments
    total_initial_investment = total_initial_capex + working_capital_req + reg_compliance_initial
    initial_cash_out = -total_initial_investment
    initial_financing = equity_investment + debt_financing_amt
    net_cash_year0 = initial_cash_out + initial_financing

    # Assume straight-line depreciation annual amount
    annual_depreciation = total_initial_capex * (depreciation_rate / 100)

    # Loan parameters
    annual_principal_payment = debt_financing_amt / loan_repayment_term
    interest_rate = interest_rate_debt / 100

    # Prepare DataFrame for projections
    years = list(range(1, projection_horizon + 1))
    data = {
        "Year": years,
        "Revenue Bamboo": [0] * projection_horizon,
        "Revenue Biochar": [0] * projection_horizon,
        "Revenue Carbon Credits": [0] * projection_horizon,
        "Revenue Byproducts": [0] * projection_horizon,
        "Total Revenue": [0] * projection_horizon,
        "Operating Costs": [0] * projection_horizon,
        "EBITDA": [0] * projection_horizon,
        "Depreciation": [annual_depreciation] * projection_horizon,
        "EBIT": [0] * projection_horizon,
        "Interest Expense": [0] * projection_horizon,
        "EBT": [0] * projection_horizon,
        "Taxes": [0] * projection_horizon,
        "Net Income": [0] * projection_horizon,
        "Cash Flow from Operations": [0] * projection_horizon,
        "Capex": [0] * projection_horizon,  # Assume no additional
        "Debt Principal Payment": [annual_principal_payment if y <= loan_repayment_term else 0 for y in years],
        "Free Cash Flow": [0] * projection_horizon,
    }
    df = pd.DataFrame(data)

    # Calculate for each year
    remaining_debt = debt_financing_amt
    max_harvest = land_area * annual_yield_per_ha * (capacity_util_rate / 100) * harvest_cycle_freq
    for i, year in enumerate(years):
        if year < growth_period:
            bamboo_vol = 0
            biochar_vol = 0
        else:
            # Use projected sales vols, adjusted for growth and capacity
            bamboo_vol = min(annual_bamboo_sales_vol * (1 + annual_sales_growth / 100) ** (year - growth_period), max_harvest * (100 - pct_to_biochar) / 100)
            biochar_vol = min(annual_biochar_sales_vol * (1 + annual_sales_growth / 100) ** (year - growth_period), min(max_harvest * pct_to_biochar / 100 * biochar_conversion_eff, biochar_prod_capacity))

        harvest_tons = bamboo_vol + (biochar_vol / biochar_conversion_eff)  # Total bamboo harvested

        # Revenues with inflation
        rev_bamboo = bamboo_vol * bamboo_price_per_ton * (1 + inflation_rate_revenue / 100) ** (year - 1)
        rev_biochar = biochar_vol * biochar_price_per_ton * (1 + inflation_rate_revenue / 100) ** (year - 1)
        rev_carbon = biochar_vol * co2_seq_per_ton_biochar * carbon_credit_price * (1 + inflation_rate_revenue / 100) ** (year - 1)
        rev_byproducts = (biochar_vol / biochar_conversion_eff) * byproduct_value_per_ton_bamboo * (1 + inflation_rate_revenue / 100) ** (year - 1)

        total_rev = rev_bamboo + rev_biochar + rev_carbon + rev_byproducts

        # Operating costs with inflation
        cost_inflation_factor = (1 + inflation_rate_costs / 100) ** (year - 1)
        fixed_costs = (admin_office_exp_annual + annual_irrigation_maint + equip_maint_per_yr + insurance_premiums + reg_compliance_annual) * cost_inflation_factor
        variable_cultivation = (fertilizer_cost_per_ha_yr + pest_control_per_ha_yr + weed_mgmt_per_ha_yr) * land_area * cost_inflation_factor
        harvest_costs = harvest_tons * (harvesting_cost_per_ton + internal_trans_cost_per_ton) * cost_inflation_factor
        biochar_prod_costs = (biochar_vol / biochar_conversion_eff) * (energy_cost_per_ton + labor_cost_per_ton_biochar) * cost_inflation_factor
        trans_costs = (bamboo_vol + biochar_vol) * product_trans_cost_per_ton * cost_inflation_factor
        marketing_costs = total_rev * (marketing_exp_pct_rev / 100)

        total_opex = fixed_costs + variable_cultivation + harvest_costs + biochar_prod_costs + trans_costs + marketing_costs

        ebitda = total_rev - total_opex
        ebit = ebitda - annual_depreciation
        interest = remaining_debt * interest_rate
        ebt = ebit - interest
        taxes = max(0, ebt) * (corporate_tax_rate / 100)
        net_income = ebt - taxes

        cfo = net_income + annual_depreciation  # Simplified, no changes in working cap
        principal = min(annual_principal_payment, remaining_debt)
        fcf = cfo - 0 - principal  # No additional capex

        remaining_debt = max(0, remaining_debt - principal)

        # Fill DF
        df.at[i, "Revenue Bamboo"] = rev_bamboo
        df.at[i, "Revenue Biochar"] = rev_biochar
        df.at[i, "Revenue Carbon Credits"] = rev_carbon
        df.at[i, "Revenue Byproducts"] = rev_byproducts
        df.at[i, "Total Revenue"] = total_rev
        df.at[i, "Operating Costs"] = total_opex
        df.at[i, "EBITDA"] = ebitda
        df.at[i, "Depreciation"] = annual_depreciation
        df.at[i, "EBIT"] = ebit
        df.at[i, "Interest Expense"] = interest
        df.at[i, "EBT"] = ebt
        df.at[i, "Taxes"] = taxes
        df.at[i, "Net Income"] = net_income
        df.at[i, "Cash Flow from Operations"] = cfo
        df.at[i, "Debt Principal Payment"] = principal
        df.at[i, "Free Cash Flow"] = fcf

    # Year 0 row
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

    # NPV calculation
    discount_rate = discount_rate_npv / 100
    npv = npf.npv(discount_rate, df["Free Cash Flow"])

    # IRR - need to handle if possible
    try:
        irr = npf.irr(df["Free Cash Flow"]) * 100
    except:
        irr = "N/A"

    # Display results
    st.subheader("Financial Projections")
    st.dataframe(df.style.format("{:.2f}"))

    st.subheader("Key Metrics")
    st.metric("Net Present Value (NPV)", f"${npv:,.2f}")
    st.metric("Internal Rate of Return (IRR %)", f"{irr:.2f}" if isinstance(irr, float) else irr)
    st.metric("Total Revenue over Horizon", f"${df['Total Revenue'].sum():,.2f}")
    st.metric("Total Net Income over Horizon", f"${df['Net Income'].sum():,.2f}")