import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
 #   data = pd.read_csv('ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv')
    data = pd.read_parquet('HDB_resale_20240525.parquet.gzip')
    data['psf'] = data['resale_price'] / (data['floor_area_sqm'] * 10.7639)  # Calculate PSF
 #   data['month'] = pd.to_datetime(data['month'])  # Ensure the transaction_date is in datetime format
    return data

data = load_data()

# Sidebar search fields
st.sidebar.header("Search")

# Search by flat_type
search_flat_type = st.sidebar.text_input("Search by Flat Type")

# Search by block
search_block = st.sidebar.text_input("Search by Block")

# Search by town
search_town = st.sidebar.text_input("Search by Town")

# Apply search
filtered_data = data.copy()
if search_flat_type:
    filtered_data = filtered_data[filtered_data['flat_type'].str.contains(search_flat_type, case=False, na=False)]
if search_block:
    filtered_data = filtered_data[filtered_data['block'].str.contains(search_block, case=False, na=False)]
if search_town:
    filtered_data = filtered_data[filtered_data['town'].str.contains(search_town, case=False, na=False)]


# Sorting options
st.sidebar.header("Sorting Options")

sort_by_price = st.sidebar.radio("Sort by Resale Price", ["Highest", "Lowest"])
sort_by_date = st.sidebar.radio("Sort by Transaction Date", ["Latest", "Oldest"])

# Apply sorting
if sort_by_price == "Highest":
    filtered_data = filtered_data.sort_values(by='resale_price', ascending=False)
else:
    filtered_data = filtered_data.sort_values(by='resale_price', ascending=True)

if sort_by_date == "Latest":
    filtered_data = filtered_data.sort_values(by='sold_year_month', ascending=False)
else:
    filtered_data = filtered_data.sort_values(by='sold_year_month', ascending=True)

# Pagination
items_per_page = 10
total_items = len(filtered_data)
total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)
page_number = st.sidebar.number_input('Page Number', min_value=1, max_value=total_pages, step=1)

start_idx = (page_number - 1) * items_per_page
end_idx = start_idx + items_per_page
paginated_data = filtered_data.iloc[start_idx:end_idx]

# Main content
st.title("Filtered Data Table")
# Display the number of transactions
st.subheader(f"No. of Transactions: {total_items}")

# Show the filtered and sorted data
#st.dataframe(filtered_data)

# Optionally, you can also display the filtered data in a static table format
#st.table(filtered_data)

# Show the filtered and sorted data in a card-like format
for idx, row in filtered_data.iterrows():
    st.markdown(f"""
    <div style="background-color:#444; padding:10px; border-radius:5px; margin:10px 0;">
        <h4 style="color:white;">{row['block']} {row['town']}</h4>
        <p style="color:white;">
            {row['flat_type']}<br>
            Storey: {row['storey_range']}<br>
            Area: {row['floor_area_sqm']} sqm<br>
            Built: {row['lease_commence_date']}<br>
            Remaining Lease: {row['sold_remaining_lease']}<br>
            <b>Price: ${row['resale_price']}</b><br>
            <b>PSF: ${row['psf']:.2f}</b><br>
            <b>Date: {row['sold_year_month'].strftime('%Y-%m')}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)