import streamlit as st
import pandas as pd

st.title("WA House Cost Calculator")

st.markdown("""
- [Transfer taxes in Washington](https://listwithclever.com/real-estate-blog/washington-state-real-estate-transfer-taxes-an-in-depth-guide/) 2.75% on homes between $1,525,000.01 and $3,025,000
- Loan origination fee is usually around 0.5% to 1.5%
- Escrow fees are usually 1% to 2%
- Title insurance in Washington State usually costs about 0.5% to 1.0% of the total property purchase price

[washington-state-closing-cost](https://sweethomespokane.com/washington-state-closing-costs/)
- Buyer’s Closing Cost (2% to 5%)
- Seller’s Closing Cost (6% to 10%)            
            
Property tax on Mercer Island: 0.61% per year
    https://www.ownwell.com/trends/washington/king-county/mercer-island
""")
            
# Add text inputs for buyerCostRatio, sellerCostRatio, buyerPrice, and sellPrice
buyer_cost_ratio = st.number_input("Buyer Cost Ratio (%)", value=5.0) / 100
seller_cost_ratio = st.number_input("Seller Cost Ratio (%)", value=7.0) / 100
buyer_price = st.number_input("Buyer Price (10k)", value=300) * 10000

down_payment_ratio = st.number_input("Down Payment Ratio (%)", value=20) / 100

stock_increase_ratio = st.number_input("Stock Increase Ratio (%)", value=7.0) / 100

house_increase_ratio = st.number_input("House Increase Ratio (%)", value=7.0) /100

property_tax_ratio = st.number_input("Property Tax Ratio (%)", value=0.61) / 100

interest_rate = st.number_input("Mortgage Interest Rate (%)", value=6.5) / 100


down_payment = buyer_price * down_payment_ratio 
closing_buyer_cost = buyer_price * buyer_cost_ratio
closing_cost = down_payment + closing_buyer_cost

st.write(f"Closing cost: {closing_cost:,} ")
st.write(f" - Down payment: {down_payment:,} ")
st.write(f" - Buyer Cost: {closing_buyer_cost:,} ")
st.write(f" House Increase Ratio: {house_increase_ratio}%")

# Add inputs for mortgage interest rate and loan term
loan_term_30 = 30
loan_term_15 = 15

def calculate_mortgage_payment(principal, annual_interest_rate, years):
    monthly_interest_rate = annual_interest_rate / 12
    number_of_payments = years * 12
    if monthly_interest_rate == 0:
        return principal / number_of_payments
    return principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)

# Calculate amortization schedule
def calculate_amortization_schedule(principal, annual_interest_rate, years, buyer_price, house_increase_ratio, init_payment, stock_increase_ratio, property_tax_ratio, buyer_cost_ratio, seller_cost_ratio):
    
    st.write(f"Principal: {principal:,} at {annual_interest_rate * 100}% for {years} years init_payment: {init_payment:,}") 
    st.write(f"Buyer Price: {buyer_price:,}  House Increase Ratio: {house_increase_ratio}  Stock Increase Ratio: {stock_increase_ratio}  Property Tax Ratio: {property_tax_ratio}  Buyer Cost Ratio: {buyer_cost_ratio}  Seller Cost Ratio: {seller_cost_ratio}")
    monthly_interest_rate = annual_interest_rate / 12

    number_of_payments = years * 12
    monthly_payment = calculate_mortgage_payment(principal, annual_interest_rate, years)
    
    schedule = []
    accumulated_principal = 0
    accumulated_interest = 0
    remaining_balance = principal
    
    house_price = buyer_price
    accumulated_property_tax = 0
    accumulated_investment = init_payment
    stock_investment = init_payment

    buyer_cost = buyer_price * (1 + buyer_cost_ratio)

    house_begin_price = house_price

    for month in range(1, number_of_payments + 1):
        current_interest = remaining_balance * monthly_interest_rate
        current_principal = monthly_payment - current_interest
        accumulated_principal += current_principal
        accumulated_interest += current_interest
        remaining_balance -= current_principal

        house_price += house_begin_price * house_increase_ratio / 12
        property_tax = house_begin_price * property_tax_ratio / 12

        house_gain = house_price - buyer_cost - house_price * seller_cost_ratio - accumulated_property_tax - accumulated_interest

        accumulated_property_tax += property_tax
        accumulated_investment += current_interest + current_principal + property_tax

        stock_investment += stock_investment * stock_increase_ratio / 12

        stock_investment += current_interest + current_principal + property_tax

        schedule.append({
            "Month": month,
            "Accumulated Principal": accumulated_principal,
            "Accumulated Interest": accumulated_interest,
            "Current Interest": current_interest,
            "Current Principal": current_principal,
            "Remaining Balance": remaining_balance,
            "House Price": house_price,
            "Property Tax": property_tax,
            "Accumulated Property Tax": accumulated_property_tax,
            "Accumulated House Investment": accumulated_investment,
            "Stock Investment": stock_investment,
            "Stock Gain": stock_investment - accumulated_investment,
            "House Diff": house_price - buyer_price,
            "House Gain": house_gain,
            "House Gain - Stock Gain": house_gain - (stock_investment - accumulated_investment),
        })

        if (month > 0 and month % 12 == 0):
            house_begin_price = house_price

        
    return schedule

# Set float format to not show fractions
pd.options.display.float_format = '{:,.1f}'.format

loan_amount = buyer_price - down_payment

# Generate amortization schedules for 30-year and 15-year fixed mortgages
schedule_30 = calculate_amortization_schedule(loan_amount, interest_rate, loan_term_30, buyer_price, house_increase_ratio, closing_cost, stock_increase_ratio, property_tax_ratio, buyer_cost_ratio, seller_cost_ratio)
schedule_15 = calculate_amortization_schedule(loan_amount, interest_rate, loan_term_15, buyer_price, house_increase_ratio, closing_cost, stock_increase_ratio, property_tax_ratio, buyer_cost_ratio, seller_cost_ratio)

# Display amortization schedules
st.subheader("30-Year Fixed Mortgage Amortization Schedule")
df_30 = pd.DataFrame(schedule_30)
st.dataframe(df_30)

st.subheader("15-Year Fixed Mortgage Amortization Schedule")
df_15 = pd.DataFrame(schedule_15)
st.dataframe(df_15)