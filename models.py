import pandas as pd
import numpy as np

def generate_projections(
    acres, land_cost_per_acre, planting_cost_per_acre, initial_equipment_cost,
    bamboo_yield_per_acre, bamboo_selling_price_per_ton, annual_maintenance_per_acre, maturity_years,
    biochar_yield_ratio, biochar_production_cost_per_ton, biochar_selling_price_per_ton,
    initial_investment, loan_amount, loan_interest_rate, loan_term_years, tax_rate, projection_years
):
    """
    Generate detailed financial forecasts for a bamboo farm with biochar production.
    """
    # Initial calculations
    total_land_cost = acres * land_cost_per_acre
    total_planting_cost = acres * planting_cost_per_acre
    total_initial_cost = total_land_cost + total_planting_cost + initial_equipment_cost
    starting_cash = initial_investment + loan_amount - total_initial_cost
    
    # Depreciation (straight-line over 5 years for equipment)
    dep_per_year = initial_equipment_cost / 5 if initial_equipment_cost > 0 else 0
    
    # Loan payment calculation (annual annuity)
    if loan_amount > 0 and loan_term_years > 0 and loan_interest_rate > 0:
        pmt = loan_amount * (loan_interest_rate * (1 + loan_interest_rate)**loan_term_years) / ((1 + loan_interest_rate)**loan_term_years - 1)
    else:
        pmt = 0
    
    # Initialize lists for projections
    years_list = list(range(1, projection_years + 1))
    bamboo_revenues = []
    biochar_revenues = []
    total_revenues = []
    total_costs_list = []
    depreciations = []
    loan_payments = []  # New: interest + principal
    interests = []
    ebots = []
    taxes_list = []
    net_incomes = []
    free_cash_flows = []
    cumulative_cash_list = []
    
    # Loan balance tracking
    balance = loan_amount
    cumulative_cash = starting_cash
    
    for year in years_list:
        # Bamboo yield ramps up to maturity
        yield_factor = min(year / maturity_years, 1.0)
        bamboo_yield_t = bamboo_yield_per_acre * acres * yield_factor
        bamboo_rev = bamboo_yield_t * bamboo_selling_price_per_ton
        
        # Biochar from bamboo waste
        biochar_yield_t = bamboo_yield_t * biochar_yield_ratio
        biochar_rev = biochar_yield_t * biochar_selling_price_per_ton
        
        total_rev = bamboo_rev + biochar_rev
        
        # Costs
        maintenance_cost = annual_maintenance_per_acre * acres
        biochar_cost = biochar_yield_t * biochar_production_cost_per_ton
        total_costs = maintenance_cost + biochar_cost
        
        # Depreciation
        dep = dep_per_year if year <= 5 else 0.0
        
        # EBITDA
        ebitda = total_rev - total_costs
        
        # EBIT before interest
        ebit_before_interest = ebitda - dep
        
        # Loan interest and principal
        if year > loan_term_years or balance <= 0:
            interest = 0.0
            principal = 0.0
            loan_payment = 0.0
        else:
            interest = balance * loan_interest_rate
            principal = pmt - interest
            if principal > balance:
                principal = balance
            balance -= principal
            loan_payment = interest + principal
        
        # EBIT after interest
        ebit = ebit_before_interest - interest
        
        # Taxes (only on positive EBIT)
        taxes = max(0, ebit * tax_rate)
        
        # Net Income
        net_income = ebit - taxes
        
        # Free Cash Flow: Net Income + Dep - Principal Repayment
        free_cash_flow = net_income + dep - principal
        
        # Cumulative Cash
        cumulative_cash += free_cash_flow
        
        # Append to lists
        bamboo_revenues.append(bamboo_rev)
        biochar_revenues.append(biochar_rev)
        total_revenues.append(total_rev)
        total_costs_list.append(total_costs)
        depreciations.append(dep)
        interests.append(interest)
        loan_payments.append(loan_payment)  # New
        ebots.append(ebit)
        taxes_list.append(taxes)
        net_incomes.append(net_income)
        free_cash_flows.append(free_cash_flow)
        cumulative_cash_list.append(cumulative_cash)
    
    # Create DataFrame
    df = pd.DataFrame({
        "Year": years_list,
        "Bamboo Revenue": bamboo_revenues,
        "Biochar Revenue": biochar_revenues,
        "Total Revenue": total_revenues,
        "Total Costs": total_costs_list,
        "Depreciation": depreciations,
        "Interest": interests,
        "Loan Payments": loan_payments,  # New
        "EBIT": ebots,
        "Taxes": taxes_list,
        "Net Income": net_incomes,
        "Free Cash Flow": free_cash_flows,
        "Cumulative Cash": cumulative_cash_list
    })
    
    # Round for readability
    df = df.round(2)
    return df