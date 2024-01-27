import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def calculate_profit_area(z_buyers, mc_price, total_quantity):
    def demand_price(x):
        return z_buyers[0] * x + z_buyers[1]

    max_profit = 0
    max_profit_quantity = 0
    price_at_max_profit = 0

    for q in np.linspace(0, total_quantity, 10000):
        price = demand_price(q)
        profit_margin = price - mc_price
        profit = profit_margin * q

        # Check if this quantity gives a higher profit
        if profit > max_profit:
            max_profit = profit
            max_profit_quantity = q
            price_at_max_profit = price

    return max_profit_quantity, max_profit, price_at_max_profit

def calculate_elasticity(z_buyers, q):
    # Corrected elasticity calculation
    price = z_buyers[0] * q + z_buyers[1]
    elasticity = (z_buyers[0] * q) / price
    return elasticity

def plot_data(buyers_data, sellers_data, show_buyer_data, show_seller_data, show_marginal_cost_line, show_supply_curve_1, show_supply_curve_2, show_equilibrium_data, show_max_profit_area):
    plt.figure(figsize=(18, 9))

    total_quantity_supplied = sellers_data['tons_to_sell'].sum()
    buyers_sorted = buyers_data.sort_values(by='Willingness_to_Pay', ascending=False).reset_index(drop=True)

    buyer_quantities_new = np.arange(1, len(buyers_sorted) + 1)
    z_buyers = np.polyfit(buyer_quantities_new, buyers_sorted['Willingness_to_Pay'], 1)
    p_buyers = np.poly1d(z_buyers)

    if show_buyer_data:
        plt.plot(buyer_quantities_new, buyers_sorted['Willingness_to_Pay'], marker='o', linestyle='-', color='grey', label='Willingness to Buy')
    
    plt.plot(buyer_quantities_new, p_buyers(buyer_quantities_new), linestyle='--', color='blue', linewidth=2, label='Demand Best Fit Line')

    sellers_sorted = sellers_data.sort_values(by='Cost_to_Sell', ascending=True)
    sellers_sorted['Cumulative_Tons'] = sellers_sorted['tons_to_sell'].cumsum()

    if show_seller_data:
        plt.plot(sellers_sorted['Cumulative_Tons'], sellers_sorted['Cost_to_Sell'], marker='o', linestyle='-', color='grey', label='Willingness to Sell')

    mc_price = 200
    if show_marginal_cost_line:
        plt.axhline(y=mc_price, color='grey', linestyle=':', label='Marginal Cost (Price = 200)', xmax=buyer_quantities_new[-1])

    if show_supply_curve_1:
        filtered_sellers = sellers_sorted[sellers_sorted['Cumulative_Tons'] <= 1000]
        z_sellers = np.polyfit(filtered_sellers['Cumulative_Tons'], filtered_sellers['Cost_to_Sell'], 1)
        p_sellers = np.poly1d(z_sellers)
        plt.plot(filtered_sellers['Cumulative_Tons'], p_sellers(filtered_sellers['Cumulative_Tons']), linestyle='--', color='orange', linewidth=2, label='Supply Curve 1')

    #if show_supply_curve_2:
    #    range_filtered_sellers = sellers_sorted[(sellers_sorted['Cost_to_Sell'] >= 136) & (sellers_sorted['Cost_to_Sell'] <= 401)]
    #    if not range_filtered_sellers.empty:
    #        z_sellers_2 = np.polyfit(range_filtered_sellers['Cumulative_Tons'], range_filtered_sellers['Cost_to_Sell'], 1)
    #        p_sellers_2 = np.poly1d(z_sellers_2)
    #        plt.plot(range_filtered_sellers['Cumulative_Tons'], p_sellers_2(range_filtered_sellers['Cumulative_Tons']), linestyle='--', color='purple', linewidth=2, label='Supply Curve 2')

    # Calculate the equilibrium quantity and price
    equilibrium_quantity = np.roots(z_buyers - z_sellers)[0]
    equilibrium_price = np.polyval(z_buyers, equilibrium_quantity)

    if show_equilibrium_data:
        plt.axvline(x=equilibrium_quantity, color='green', linestyle=':', label='Equilibrium Quantity')
        plt.axhline(y=equilibrium_price, color='red', linestyle=':', label='Equilibrium Price')
        plt.plot(equilibrium_quantity, equilibrium_price, 'go', label='Equilibrium Point')

    max_profit_quantity, max_profit, price_to_maximize_profit = calculate_profit_area(z_buyers, mc_price, total_quantity_supplied)

    # Calculate elasticity at maximum profit point
    elasticity_at_max_profit = calculate_elasticity(z_buyers, max_profit_quantity)

    if show_max_profit_area:
        plt.fill_between([0, max_profit_quantity], mc_price, price_to_maximize_profit, color='green', alpha=0.3, label='Max Profit Area')
        plt.plot(max_profit_quantity, price_to_maximize_profit, 'gs', label='Max Profit Point')
    
    plt.title('Market Demand and Supply Curves')
    plt.xlabel('Quantity')
    plt.ylabel('Price (USD)')
    plt.legend(loc='upper right')

    return plt, equilibrium_quantity, equilibrium_price, max_profit, elasticity_at_max_profit, price_to_maximize_profit

def main():
    st.title('Case 2: Corn Demand and Supply')

    # Load data
    default_file_path = 'https://raw.githubusercontent.com/mikejrodd/iet_case1/main/case_2.xlsx'
    data_sheet = pd.read_excel(default_file_path, sheet_name='data')
    buyers_data = data_sheet[['BUYERS', 'Unnamed: 1']].iloc[1:]
    buyers_data.columns = ['Buyer', 'Willingness_to_Pay']
    buyers_data['Willingness_to_Pay'] = pd.to_numeric(buyers_data['Willingness_to_Pay'])

    sellers_data = data_sheet[['SELLERS', 'Unnamed: 4', 'Unnamed: 5']].iloc[1:]
    sellers_data.columns = ['Seller', 'tons_to_sell', 'Cost_to_Sell']
    sellers_data['tons_to_sell'] = pd.to_numeric(sellers_data['tons_to_sell'])
    sellers_data['Cost_to_Sell'] = pd.to_numeric(sellers_data['Cost_to_Sell'])

    # UI elements
    show_buyer_data = st.checkbox('Show Buyer Data', value=True)
    show_seller_data = st.checkbox('Show Seller Data', value=True)
    show_marginal_cost_line = st.checkbox('Show Marginal Cost Line ($200)', value=False)
    show_supply_curve_1 = st.checkbox('Show Supply Curve 1', value=True)
    show_supply_curve_2 = st.checkbox('Show Supply Curve 2', value=False)
    show_equilibrium_data = st.checkbox('Show Equilibrium Data', value=False)
    show_max_profit_area = st.checkbox('Show Max Profit Area', value=False)

    # Plotting
    fig, equilibrium_quantity, equilibrium_price, max_profit, elasticity_at_max_profit, price_to_maximize_profit = plot_data(
        buyers_data, sellers_data, show_buyer_data, show_seller_data, show_marginal_cost_line, 
        show_supply_curve_1, show_supply_curve_2, show_equilibrium_data, show_max_profit_area)
    st.pyplot(fig)

    # Display results
    if show_equilibrium_data:
        st.write(f"Equilibrium Price: {equilibrium_price:.2f} USD")
        st.write(f"Equilibrium Quantity: {equilibrium_quantity:.2f} units")
    st.write(f"Max Profit Available: {max_profit:.2f} USD")
    st.write(f"Price to Maximize Profit: {price_to_maximize_profit:.2f} USD")
    st.write(f"Elasticity at Max Profit Quantity: {elasticity_at_max_profit:.2f}")

if __name__ == "__main__":
    main()

