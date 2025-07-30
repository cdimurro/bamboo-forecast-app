from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import numpy as np
import plotly.express as px
from models import generate_projections

# Initialize the Dash app
app = Dash(__name__)
server = app.server  # For Heroku deployment

# Define the layout
app.layout = html.Div([
    html.H1("Bamboo Business Financial Forecasts App", style={'textAlign': 'center'}),
    html.P("This app helps forecast finances for starting a bamboo farm with biochar production. Adjust inputs and submit to generate forecasts.", style={'textAlign': 'center'}),
    
    # Input sections with expanders
    html.Div([
        html.H3("Land & Setup", style={'marginTop': '20px'}),
        html.Div([
            dcc.Input(id='acres', type='number', value=5.0, min=1.0, step=1.0, placeholder="Number of Acres"),
            dcc.Input(id='land-cost-per-acre', type='number', value=8000.0, min=0.0, step=100.0, placeholder="Land Cost per Acre ($)"),
            dcc.Input(id='planting-cost-per-acre', type='number', value=1500.0, min=0.0, step=100.0, placeholder="Planting Cost per Acre ($)"),
            dcc.Input(id='initial-equipment-cost', type='number', value=10000.0, min=0.0, step=100.0, placeholder="Initial Equipment Cost ($)"),
        ], style={'margin': '10px'}),
    ]),
    
    html.Div([
        html.H3("Bamboo Operations"),
        html.Div([
            dcc.Input(id='bamboo-yield-per-acre', type='number', value=15.0, min=0.0, step=1.0, placeholder="Mature Bamboo Yield per Acre (tons/year)"),
            dcc.Input(id='bamboo-selling-price-per-ton', type='number', value=150.0, min=0.0, step=10.0, placeholder="Bamboo Selling Price per Ton ($)"),
            dcc.Input(id='annual-maintenance-per-acre', type='number', value=1000.0, min=0.0, step=100.0, placeholder="Annual Maintenance Cost per Acre ($)"),
            dcc.Slider(id='maturity-years', min=1, max=5, value=3, marks={i: str(i) for i in range(1, 6)}, step=1),
        ], style={'margin': '10px'}),
    ]),
    
    html.Div([
        html.H3("Biochar Operations"),
        html.Div([
            dcc.Slider(id='biochar-yield-ratio', min=0.0, max=50.0, value=30.0, marks={i: str(i) for i in range(0, 51, 10)}, step=1, tooltip={"placement": "bottom"}),
            dcc.Input(id='biochar-production-cost-per-ton', type='number', value=300.0, min=0.0, step=50.0, placeholder="Biochar Production Cost per Ton ($)"),
            dcc.Input(id='biochar-selling-price-per-ton', type='number', value=500.0, min=0.0, step=50.0, placeholder="Biochar Selling Price per Ton ($)"),
        ], style={'margin': '10px'}),
    ]),
    
    html.Div([
        html.H3("Financing & General"),
        html.Div([
            dcc.Input(id='initial-investment', type='number', value=100000.0, min=0.0, step=1000.0, placeholder="Initial Equity Investment ($)"),
            dcc.Input(id='loan-amount', type='number', value=50000.0, min=0.0, step=1000.0, placeholder="Loan Amount ($)"),
            dcc.Slider(id='loan-interest-rate', min=0.0, max=20.0, value=8.0, marks={i: str(i) for i in range(0, 21, 5)}, step=0.1),
            dcc.Slider(id='loan-term-years', min=1, max=30, value=15, marks={i: str(i) for i in range(0, 31, 5)}, step=1),
            dcc.Slider(id='tax-rate', min=0.0, max=50.0, value=25.0, marks={i: str(i) for i in range(0, 51, 10)}, step=0.1),
            dcc.Slider(id='projection-years', min=1, max=20, value=10, marks={i: str(i) for i in range(0, 21, 5)}, step=1),
        ], style={'margin': '10px'}),
    ]),
    
    html.Button('Generate Forecasts', id='submit-button', n_clicks=0, style={'margin': '20px'}),
    
    html.Div(id='output-table'),
    html.Div(id='output-charts'),
    
    dcc.Download(id="download-data")
], style={'padding': '20px', 'fontFamily': 'Arial'})

# Callback to generate and display forecasts
@app.callback(
    [Output('output-table', 'children'),
     Output('output-charts', 'children'),
     Output('download-data', 'data')],
    [Input('submit-button', 'n_clicks')],
    [State('acres', 'value'),
     State('land-cost-per-acre', 'value'),
     State('planting-cost-per-acre', 'value'),
     State('initial-equipment-cost', 'value'),
     State('bamboo-yield-per-acre', 'value'),
     State('bamboo-selling-price-per-ton', 'value'),
     State('annual-maintenance-per-acre', 'value'),
     State('maturity-years', 'value'),
     State('biochar-yield-ratio', 'value'),
     State('biochar-production-cost-per-ton', 'value'),
     State('biochar-selling-price-per-ton', 'value'),
     State('initial-investment', 'value'),
     State('loan-amount', 'value'),
     State('loan-interest-rate', 'value'),
     State('loan-term-years', 'value'),
     State('tax-rate', 'value'),
     State('projection-years', 'value')]
)
def update_output(n_clicks, acres, land_cost_per_acre, planting_cost_per_acre, initial_equipment_cost,
                  bamboo_yield_per_acre, bamboo_selling_price_per_ton, annual_maintenance_per_acre, maturity_years,
                  biochar_yield_ratio, biochar_production_cost_per_ton, biochar_selling_price_per_ton,
                  initial_investment, loan_amount, loan_interest_rate, loan_term_years, tax_rate, projection_years):
    if n_clicks > 0:
        # Generate projections
        df = generate_projections(
            float(acres) if acres else 0, float(land_cost_per_acre) if land_cost_per_acre else 0,
            float(planting_cost_per_acre) if planting_cost_per_acre else 0, float(initial_equipment_cost) if initial_equipment_cost else 0,
            float(bamboo_yield_per_acre) if bamboo_yield_per_acre else 0, float(bamboo_selling_price_per_ton) if bamboo_selling_price_per_ton else 0,
            float(annual_maintenance_per_acre) if annual_maintenance_per_acre else 0, float(maturity_years) if maturity_years else 0,
            float(biochar_yield_ratio) if biochar_yield_ratio else 0, float(biochar_production_cost_per_ton) if biochar_production_cost_per_ton else 0,
            float(biochar_selling_price_per_ton) if biochar_selling_price_per_ton else 0,
            float(initial_investment) if initial_investment else 0, float(loan_amount) if loan_amount else 0,
            float(loan_interest_rate) if loan_interest_rate else 0, float(loan_term_years) if loan_term_years else 0,
            float(tax_rate) if tax_rate else 0, float(projection_years) if projection_years else 0
        )
        
        # Table output
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([html.Tr([html.Td(f"${val:,.2f}" if isinstance(val, (int, float)) else val) for val in row]) for row in df.values])
        ], style={'width': '100%', 'margin': '20px 0'})
        
        # Charts output
        charts = [
            dcc.Graph(figure=px.line(df, x="Year", y=["Bamboo Revenue", "Biochar Revenue", "Total Revenue"], title="Revenue Projections")),
            dcc.Graph(figure=px.line(df, x="Year", y=["Total Costs", "Loan Payments", "Taxes"], title="Costs and Expenses")),
            dcc.Graph(figure=px.bar(df, x="Year", y=["Net Income", "Free Cash Flow"], title="Net Income and Free Cash Flow", barmode="group")),
            dcc.Graph(figure=px.line(df, x="Year", y="Cumulative Cash", title="Cumulative Cash Flow"))
        ]
        
        # Download data
        csv_data = df.to_csv(index=False)
        
        return table, charts, dcc.send_bytes(csv_data.encode(), filename="bamboo_business_forecasts.csv")
    return html.Div("Click 'Generate Forecasts' to see results."), [], None

# Run the app
if __name__ == '__main__':
    app.run(debug=True)