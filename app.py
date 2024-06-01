import streamlit as st
import pandas as pd

# Load and process data on the server-side
@st.cache_data
def load_and_process_data():
    data = pd.read_parquet('HDB_resale_20240525.parquet.gzip')
    data['psf'] = data['resale_price'] / (data['floor_area_sqm'] * 10.7639)  # Calculate PSF
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

# Main Streamlit app
def main():
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
    items_per_page = 10
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

if __name__ == "__main__":
    main()