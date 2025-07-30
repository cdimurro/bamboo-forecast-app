# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from models import generate_projections

st.title("Bamboo Business Financial Forecasts App")

st.write("This app helps forecast finances for starting a bamboo farm with biochar production. Enter details below and generate forecasts.")

# User inputs - Grouped sections
with st.expander("Land & Setup"):
    acres = st.number_input("Number of Acres:", min_value=1.0, value=5.0, step=1.0)
    land_cost_per_acre = st.number_input("Land Cost per Acre ($):", min_value=0.0, value=8000.0, step=100.0)
    planting_cost_per_acre = st.number_input("Initial Planting Cost per Acre ($):", min_value=0.0, value=1500.0, step=100.0)
    initial_equipment_cost = st.number_input("Initial Equipment Cost ($):", min_value=0.0, value=10000.0, step=100.0)

with st.expander("Bamboo Operations"):
    bamboo_yield_per_acre = st.number_input("Mature Bamboo Yield per Acre (tons/year):", min_value=0.0, value=15.0, step=1.0)
    bamboo_selling_price_per_ton = st.number_input("Bamboo Selling Price per Ton ($):", min_value=0.0, value=150.0, step=10.0)
    annual_maintenance_per_acre = st.number_input("Annual Maintenance Cost per Acre ($):", min_value=0.0, value=1000.0, step=100.0)
    maturity_years = st.slider("Years to Full Bamboo Maturity:", min_value=1, max_value=5, value=3)

with st.expander("Biochar Operations"):
    biochar_yield_ratio = st.slider("Biochar Yield from Bamboo Waste (% of bamboo tonnage):", min_value=0.0, max_value=50.0, value=10.0) / 100
    biochar_production_cost_per_ton = st.number_input("Biochar Production Cost per Ton ($):", min_value=0.0, value=300.0, step=50.0)
    biochar_selling_price_per_ton = st.number_input("Biochar Selling Price per Ton ($):", min_value=0.0, value=500.0, step=50.0)

with st.expander("Financing & General"):
    initial_investment = st.number_input("Initial Equity Investment ($):", min_value=0.0, value=100000.0, step=1000.0)
    loan_amount = st.number_input("Loan Amount ($):", min_value=0.0, value=50000.0, step=1000.0)
    loan_interest_rate = st.slider("Loan Interest Rate (%):", min_value=0.0, max_value=20.0, value=8.0) / 100
    loan_term_years = st.slider("Loan Term (Years):", min_value=1, max_value=30, value=15)
    tax_rate = st.slider("Tax Rate (%):", min_value=0.0, max_value=50.0, value=25.0) / 100
    projection_years = st.slider("Years to Project:", min_value=1, max_value=20, value=10)
    price_growth_rate = st.slider("Annual Price Growth Rate for Bamboo & Biochar (%):", min_value=0.0, max_value=10.0, value=0.0) / 100

if st.button("Generate Forecasts"):
    # Generate projections
    df = generate_projections(
        acres, land_cost_per_acre, planting_cost_per_acre, initial_equipment_cost,
        bamboo_yield_per_acre, bamboo_selling_price_per_ton, annual_maintenance_per_acre, maturity_years,
        biochar_yield_ratio, biochar_production_cost_per_ton, biochar_selling_price_per_ton,
        initial_investment, loan_amount, loan_interest_rate, loan_term_years, tax_rate, projection_years
    )
    
    # Display table
    st.header("Projected Financials")
    st.dataframe(df.style.format("${:,.2f}", subset=df.columns[1:]))  # Format as currency
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button("Download Forecasts as CSV", csv, "bamboo_business_forecasts.csv", "text/csv")
    
    # Display charts
    st.header("Visualizations")
    
    # Revenue Breakdown
    fig_revenues = px.line(df, x="Year", y=["Bamboo Revenue", "Biochar Revenue", "Total Revenue"], title="Revenue Projections")
    st.plotly_chart(fig_revenues)
    
    # Costs Breakdown
    fig_costs = px.line(df, x="Year", y=["Total Costs", "Loan Payments", "Taxes"], title="Costs and Expenses")
    st.plotly_chart(fig_costs)
    
    # Net Income and Cash Flow
    fig_income_cash = px.bar(df, x="Year", y=["Net Income", "Free Cash Flow"], title="Net Income and Free Cash Flow", barmode="group")
    st.plotly_chart(fig_income_cash)
    
    # Cumulative Cash
    fig_cum_cash = px.line(df, x="Year", y="Cumulative Cash", title="Cumulative Cash Flow")
    st.plotly_chart(fig_cum_cash)