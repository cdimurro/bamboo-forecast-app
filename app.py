import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import altair as alt

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
    land_area_acres = st.number_input("1. Land area for bamboo cultivation (acres)", min_value=0.1, max_value=100.0, value=5.0)
    land_cost_per_acre = st.number_input("2. Land acquisition or lease cost per acre ($)", min_value=0.0, value=4000.0)
    soil_prep_cost_per_acre = st.number_input("3. Soil preparation and testing cost per acre ($)", min_value=0.0, value=3000.0)
    seedling_cost_per_unit = st.number_input("4. Bamboo seedling or propagule cost per unit ($)", min_value=0.0, value=2.0)
    planting_density = st.number_input("5. Planting density (plants per acre)", min_value=0.0, value=600.0)
    planting_labor_per_acre = st.number_input("6. Initial planting labor cost per acre ($)", min_value=0.0, value=400.0)
    growth_period = st.number_input("7. Growth period to first harvest (years)", min_value=1, max_value=10, value=4)
    harvest_cycle_freq = st.number_input("8. Harvest cycle frequency (times per year)", min_value=0.0, value=1.0)
    annual_yield_per_acre = st.number_input("9. Annual bamboo biomass yield per acre (tons)", min_value=0.0, value=20.0)
    fertilizer_cost_per_acre_yr = st.number_input("10. Fertilizer application cost per acre per year ($)", min_value=0.0, value=100.0)
    irrigation_install_cost = st.number_input("11. Irrigation system installation cost ($ total)", min_value=0.0, value=6000.0)  # Adjusted for 5 acres
    annual_irrigation_maint = st.number_input("12. Annual water and irrigation maintenance cost ($)", min_value=0.0, value=500.0)
    pest_control_per_acre_yr = st.number_input("13. Pest and disease control cost per acre per year ($)", min_value=0.0, value=30.0)
    weed_mgmt_per_acre_yr = st.number_input("14. Weed management and maintenance labor cost per acre per year ($)", min_value=0.0, value=50.0)
    harvesting_cost_per_ton = st.number_input("15. Harvesting labor and equipment cost per ton ($)", min_value=0.0, value=30.0)
    internal_trans_cost_per_ton = st.number_input("16. Internal transportation cost from field to processing site per ton ($)", min_value=0.0, value=5.0)

with st.expander("Biochar Production Inputs"):
    pct_to_biochar = st.number_input("17. Percentage of harvested bamboo allocated to biochar production (%)", min_value=0.0, max_value=100.0, value=50.0)
    biochar_conversion_eff = st.number_input("18. Biochar conversion efficiency (tons of biochar per ton of bamboo)", min_value=0.0, max_value=1.0, value=0.25)
    pyrolysis_equip_cost = st.number_input("19. Pyrolysis or kiln equipment purchase cost ($)", min_value=0.0, value=1000.0)
    equip_install_cost = st.number_input("20. Equipment installation and setup cost ($)", min_value=0.0, value=2000.0)
    biochar_prod_capacity = st.number_input("21. Biochar production capacity (tons per year)", min_value=0.0, value=50.0)
    energy_cost_per_ton = st.number_input("22. Energy input cost for pyrolysis process per ton ($)", min_value=0.0, value=5.0)
    labor_cost_per_ton_biochar = st.number_input("23. Labor cost for biochar production per ton ($)", min_value=0.0, value=10.0)
    equip_maint_per_yr = st.number_input("24. Equipment maintenance and repair cost per year ($)", min_value=0.0, value=200.0)
    byproduct_value_per_ton_bamboo = st.number_input("25. By-product recovery value (e.g., syngas, bio-oil) per ton of bamboo processed ($)", min_value=0.0, value=50.0)  # Assumed net value

with st.expander("Sales and Revenue Inputs"):
    bamboo_price_per_ton = st.number_input("26. Selling price of raw bamboo per ton ($)", min_value=0.0, value=100.0)
    biochar_price_per_ton = st.number_input("27. Selling price of biochar per ton ($)", min_value=0.0, value=600.0)
    annual_bamboo_sales_vol = st.number_input("28. Projected annual sales volume for raw bamboo (tons)", min_value=0.0, value=50.0)  # Initial, will be overridden by calc if harvest
    annual_biochar_sales_vol = st.number_input("29. Projected annual sales volume for biochar (tons)", min_value=0.0, value=25.0)
    annual_sales_growth = st.number_input("30. Annual sales growth rate (%)", min_value=0.0, value=5.0)
    carbon_credit_price = st.number_input("31. Carbon credit or offset price per ton of CO2 sequestered ($)", min_value=0.0, value=50.0)
    co2_seq_per_ton_biochar = st.number_input("32. CO2 sequestration rate per ton of biochar (tons CO2)", min_value=0.0, value=2.5)

with st.expander("Operating Expenses Inputs"):
    admin_office_exp_annual = st.number_input("33. Administrative and office expenses (annual $)", min_value=0.0, value=2000.0)
    marketing_exp_pct_rev = st.number_input("34. Marketing and sales promotion expenses (% of revenue)", min_value=0.0, value=1.0)
    insurance_premiums = st.number_input("35. Insurance premiums for operations and assets ($ annual)", min_value=0.0, value=1000.0)
    reg_compliance_initial = st.number_input("36. Regulatory compliance and permit costs (initial $)", min_value=0.0, value=1000.0)
    reg_compliance_annual = st.number_input("36b. Regulatory compliance and permit costs (annual $)", min_value=0.0, value=100.0)  # Split for model
    product_trans_cost_per_ton = st.number_input("37. Product transportation and logistics cost per ton ($)", min_value=0.0, value=5.0)

with st.expander("Financial Structure Inputs"):
    equity_investment = st.number_input("Initial capital injection ($)", min_value=0.0, value=60000.0)
    debt_financing_amt = st.number_input("Bank loan amount ($)", min_value=0.0, value=60000.0)
    interest_rate_debt = st.number_input("Interest rate on debt (%)", min_value=0.0, value=6.0)
    loan_repayment_term = st.number_input("Loan repayment term (years)", min_value=1, max_value=50, value=15)
    loan_origination_fee_pct = st.number_input("Loan origination fee (% of loan amount)", min_value=0.0, value=1.0)
    annual_bank_fee = st.number_input("Annual bank servicing fee ($)", min_value=0.0, value=200.0)
    projection_horizon = st.number_input("Number of years to model", min_value=1, max_value=30, value=15)
    additional_land_acres = st.number_input("Additional land purchase (acres, optional)", min_value=0.0, value=5.0)
    additional_land_year = st.number_input("Year of additional land purchase", min_value=1, max_value=30, value=8)

# Hardcoded values for simplification
total_initial_capex = 50000.0  # Adjusted lower for better business case
working_capital_req = 5000.0
depreciation_rate = 7.0
corporate_tax_rate = 21.0
inflation_rate_costs = 3.0
inflation_rate_revenue = 3.0
discount_rate_npv = 10.0
capacity_util_rate = 70.0

# Button to generate forecasts
if st.button("Generate Financial Forecasts"):
    # Calculations
    # Add loan origination fee to initial costs
    loan_origination_fee = debt_financing_amt * (loan_origination_fee_pct / 100)

    # Year 0: Initial investments
    total_initial_investment = total_initial_capex + working_capital_req + reg_compliance_initial + loan_origination_fee
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
        "Capex": [0] * projection_horizon,  # Assume no additional except for land
        "Debt Principal Payment": [annual_principal_payment if y <= loan_repayment_term else 0 for y in years],
        "Free Cash Flow": [0] * projection_horizon,
    }
    df = pd.DataFrame(data)

    # Calculate for each year
    remaining_debt = debt_financing_amt
    current_land_area = land_area_acres
    additional_land_cost = 0.0
    for i, year in enumerate(years):
        if additional_land_acres > 0 and year == additional_land_year:
            additional_land_cost = additional_land_acres * (land_cost_per_acre + soil_prep_cost_per_acre + planting_labor_per_acre + seedling_cost_per_unit * planting_density)
            df.at[i, "Capex"] = additional_land_cost
            current_land_area += additional_land_acres

        if year < growth_period:
            bamboo_vol = 0
            biochar_vol = 0
        else:
            max_harvest = current_land_area * annual_yield_per_acre * (capacity_util_rate / 100) * harvest_cycle_freq
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
        fixed_costs = (admin_office_exp_annual + annual_irrigation_maint + equip_maint_per_yr + insurance_premiums + reg_compliance_annual + annual_bank_fee) * cost_inflation_factor
        variable_cultivation = (fertilizer_cost_per_acre_yr + pest_control_per_acre_yr + weed_mgmt_per_acre_yr) * current_land_area * cost_inflation_factor
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
        fcf = cfo - df.at[i, "Capex"] - principal  # Include capex for additional land

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

    # IRR with fallback
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

    st.subheader("Financial Charts")

    # Filter df to exclude Year 0 for charts, as it may skew visuals
    chart_df = df[df['Year'] > 0].set_index('Year')

    # Line chart for Revenue, Expenses, Net Income
    st.markdown("### Key Financial Metrics Over Time")
    st.line_chart(chart_df[['Total Revenue', 'Operating Costs', 'Net Income']])

    # Bar chart for Revenue Breakdown
    st.markdown("### Revenue Breakdown")
    st.bar_chart(chart_df[['Revenue Bamboo', 'Revenue Biochar', 'Revenue Carbon Credits', 'Revenue Byproducts']])

    # Line chart for Cash Flow Projections
    st.markdown("### Cash Flow Projections")
    st.line_chart(chart_df[['Cash Flow from Operations', 'Free Cash Flow']])

    # Area chart for Profitability (EBITDA and Free Cash Flow)
    st.markdown("### Profitability Metrics")
    st.area_chart(chart_df[['EBITDA', 'Free Cash Flow']])

    # PDF Download Button
    def create_pdf(df, npv, irr):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 50, "Financial Projections Report")

        # Key Metrics
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 80, f"NPV: ${npv:,.2f}")
        c.drawString(100, height - 100, f"IRR: {irr:.2f}%" if isinstance(irr, float) else f"IRR: {irr}")
        c.drawString(100, height - 120, f"Total Revenue: ${df['Total Revenue'].sum():,.2f}")
        c.drawString(100, height - 140, f"Total Net Income: ${df['Net Income'].sum():,.2f}")

        # Projections Table
        c.setFont("Helvetica", 10)
        y = height - 170
        col_width = 35
        row_height = 10
        # Headers
        for idx, col in enumerate(df.columns):
            c.drawString(50 + idx * col_width, y, col)
        y -= row_height
        # Rows
        for index, row in df.iterrows():
            for idx, value in enumerate(row):
                c.drawString(50 + idx * col_width, y, f"{value:.2f}")
            y -= row_height
            if y < 50:  # Add new page if needed
                c.showPage()
                y = height - 50

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    pdf_bytes = create_pdf(df, npv, irr)

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="financial_report.pdf",
        mime="application/pdf"
    )