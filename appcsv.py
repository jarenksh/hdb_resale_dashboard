import streamlit as st
import pandas as pd

# Load and process data on the server-side
@st.cache_data
def load_and_process_data():
    data = pd.read_csv('ResalepricesJan2017onwards.csv')
    data['psf'] = data['resale_price'] / (data['floor_area_sqm'] * 10.7639)  # Calculate PSF
   
    # Create a new column 'floor_area_sqf' by converting 'floor_area_sqm' to square feet
    data['floor_area_sqf'] = data['floor_area_sqm'] * 10.7639

    # Create a new column 'sold_year_month' from the 'month' column and drop 'month' column
    data['sold_year_month'] = pd.to_datetime(data['month'])
    data = data.drop(columns='month')

    # Standardize 'flat_type' spellings
    data['flat_type'] = data['flat_type'].str.replace('MULTI-GENERATION', 'MULTI GENERATION')

    # Standardize 'flat_model' names using the correction map
    correction_map = {
        '2-ROOM': '2-room',
        'APARTMENT': 'Apartment',
        'Improved-Maisonette': 'Executive Maisonette',
        'IMPROVED-MAISONETTE': 'Executive Maisonette',
        'IMPROVED': 'Improved',
        'MAISONETTE': 'Maisonette',
        'Model A-Maisonette': 'Maisonette',
        'MODEL A-MAISONETTE': 'Maisonette',
        'MODEL A': 'Model A',
        'MULTI GENERATION': 'Multi Generation',
        'Premium Apartment Loft': 'Premium Apartment',
        'PREMIUM APARTMENT': 'Premium Apartment',
        'Premium Maisonette': 'Executive Maisonette',
        'SIMPLIFIED': 'Simplified',
        'STANDARD': 'Standard',
        'TERRACE': 'Terrace',
        'NEW GENERATION': 'New Generation'
    }
    data = data.replace({'flat_model': correction_map})

    # Create a 'sold_year' column
    data['sold_year'] = data['sold_year_month'].dt.strftime('%Y').astype(int)

    # Derive the number of years of lease remaining
    data['sold_remaining_lease'] = 99 - (data['sold_year'] - data['lease_commence_date'])

    # Derive the number of years of lease remaining in 2024
    data['remaining_lease_in_2024'] = 99 - (2024 - data['lease_commence_date'])

    
    return data

# Filter data based on search criteria
@st.cache_data
def filter_data(data, search_flat_type, search_block, search_town):
    filtered_data = data.copy()
    if search_flat_type:
        filtered_data = filtered_data[filtered_data['flat_type'].str.contains(search_flat_type, case=False, na=False)]
    if search_block:
        filtered_data = filtered_data[filtered_data['block'].str.contains(search_block, case=False, na=False)]
    if search_town:
        filtered_data = filtered_data[filtered_data['town'].str.contains(search_town, case=False, na=False)]
    return filtered_data

# Sort data based on sorting options
@st.cache_data
def sort_data(data, sort_by_price, sort_by_date):
    if sort_by_price == "Highest":
        data = data.sort_values(by='resale_price', ascending=False)
    else:
        data = data.sort_values(by='resale_price', ascending=True)
    if sort_by_date == "Latest":
        data = data.sort_values(by='sold_year_month', ascending=False)
    else:
        data = data.sort_values(by='sold_year_month', ascending=True)
    return data

def calculate_monthly_installment(loan_amount, interest_rate, tenure_years):
    monthly_rate = interest_rate / 100 / 12
    num_payments = tenure_years * 12
    monthly_installment = (loan_amount * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return monthly_installment

# Main Streamlit app
#change to property transaction dashboard
def property_transact():
    # Load and process data on the server-side
    data = load_and_process_data()

    # Sidebar search fields
    st.sidebar.header("Search")
    search_flat_type = st.sidebar.text_input("Search by Flat Type")
    search_block = st.sidebar.text_input("Search by Block")
    search_town = st.sidebar.text_input("Search by Town")

    # Filter data based on search criteria
    filtered_data = filter_data(data, search_flat_type, search_block, search_town)

    # Sorting options
    st.sidebar.header("Sorting Options")
    sort_by_price = st.sidebar.radio("Sort by Resale Price", ["Highest", "Lowest"])
    sort_by_date = st.sidebar.radio("Sort by Transaction Date", ["Latest", "Oldest"])

    # Sort data based on sorting options
    sorted_data = sort_data(filtered_data, sort_by_price, sort_by_date)

    # Pagination
    items_per_page = 20
    total_items = len(sorted_data)
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)
    page_number = st.sidebar.number_input('Page Number', min_value=1, max_value=total_pages, step=1)
    start_idx = (page_number - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_data = sorted_data.iloc[start_idx:end_idx]

    # Main content
    st.title("Filtered Data Table")
    st.subheader(f"No. of Transactions: {total_items}")

    # Show the paginated data in a card-like format
    for idx, row in paginated_data.iterrows():
        st.markdown(f"""
        <div style="background-color:#444; padding:10px; border-radius:5px; margin:10px 0; position:relative;">
            <h4 style="color:white;">{row['block']} {row['street_name']}</h4>
            <p style="color:white; font-size:14px;">{row['town']}</p>
                {row['flat_type']} <span style="font-style:italic;">({row['flat_model']})</span><br>
                Storey: {row['storey_range']}<br>
                Area: {row['floor_area_sqm']} sqm <span style="font-style:italic;">({row['floor_area_sqf']:.2f} sqf)</span><br>
                Built: {row['lease_commence_date']}<br>
                Remaining Lease: {row['sold_remaining_lease']} years<br>
            </p>
            <div style="position:absolute; bottom:10px; right:10px; text-align:right;">
                <p style="color:white;font-size:24px;"><b>Price: ${row['resale_price']}</b></p>
                <p style="color:white;"><b>PSF: ${row['psf']:.2f}</b></p>
                <p style="color:white;"><b>Transaction Date: {row['sold_year_month'].strftime('%Y-%m')}</b></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mortgage_calculator():
    st.title("Mortgage Calculator")
    
    loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, value=100000.0, step=1000.0)
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.1)
    tenure_years = st.number_input("Loan Tenure (Years)", min_value=1, max_value=35, value=30, step=1)

    if st.button("Calculate"):
        monthly_installment = calculate_monthly_installment(loan_amount, interest_rate, tenure_years)
        st.success(f"Your estimated monthly installment is: ${monthly_installment:.2f}")

        # Additional information
        total_payment = monthly_installment * tenure_years * 12
        total_interest = total_payment - loan_amount
        
        st.write(f"Total amount paid over {tenure_years} years: ${total_payment:.2f}")
        st.write(f"Total interest paid: ${total_interest:.2f}")

def main():
    st.sidebar.title("Navigation")
    tabs = ["Property Dashboard", "Mortgage Calculator"]
    choice = st.sidebar.radio("Select a tab:", tabs)

    if choice == "Property Dashboard":
        property_transact()
    elif choice == "Mortgage Calculator":
        mortgage_calculator()

if __name__ == "__main__":
    main()