import pandas as pd
import numpy as np
import numpy_financial as npf

def generate_projections(
    land_area, land_cost_per_ha, soil_prep_cost_per_ha, seedling_cost_per_unit, planting_density,
    planting_labor_per_ha, growth_period, harvest_cycle_freq, annual_yield_per_ha, fertilizer_cost_per_ha_yr,
    irrigation_install_cost, annual_irrigation_maint, pest_control_per_ha_yr, weed_mgmt_per_ha_yr, harvesting_cost_per_ton,
    internal_trans_cost_per_ton, pct_to_biochar, biochar_conversion_eff, pyrolysis_equip_cost, equip_install_cost,
    biochar_prod_capacity, energy_cost_per_ton, labor_cost_per_ton_biochar, equip_maint_per_yr, byproduct_value_per_ton_bamboo,
    bamboo_price_per_ton, biochar_price_per_ton, annual_bamboo_sales_vol, annual_biochar_sales_vol, annual_sales_growth,
    carbon_credit_price, co2_seq_per_ton_biochar, admin_office_exp_annual, marketing_exp_pct_rev, insurance_premiums,
    reg_compliance_initial, reg_compliance_annual, product_trans_cost_per_ton, total_initial_capex, working_capital_req,
    debt_financing_amt, interest_rate_debt, loan_repayment_term, equity_investment, depreciation_rate, corporate_tax_rate,
    inflation_rate_costs, inflation_rate_revenue, discount_rate_npv, projection_horizon, capacity_util_rate
):
    """
    Generate detailed financial forecasts for a bamboo and biochar business based on provided inputs.
    Returns a tuple: (projections_df, npv, irr)
    """
    # Year 0: Initial investments
    total_initial_investment = total_initial_capex + working_capital_req + reg_compliance_initial
    initial_cash_out = -total_initial_investment
    initial_financing = equity_investment + debt_financing_amt
    net_cash_year0 = initial_cash_out + initial_financing

    # Assume straight-line depreciation annual amount
    annual_depreciation = total_initial_capex * (depreciation_rate / 100)

    # Loan parameters
    annual_principal_payment = debt_financing_amt / loan_repayment_term if loan_repayment_term > 0 else 0
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

    # IRR
    try:
        irr = npf.irr(df["Free Cash Flow"]) * 100
    except:
        irr = "N/A"

    return df, npv, irr