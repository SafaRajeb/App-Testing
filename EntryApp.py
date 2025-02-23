import streamlit as st
import pandas as pd
import datetime

def initialize_session():
    if "service_units" not in st.session_state:
        st.session_state.service_units = {"Unit A": None, "Unit B": None}  # Predefined service units
    if "selected_unit" not in st.session_state:
        st.session_state.selected_unit = "Unit A"
    if "ticket_data" not in st.session_state:
        st.session_state.ticket_data = {}

def generate_month_grid(start_year, end_year):
    columns = ["Year"] + [datetime.date(2000, i, 1).strftime('%B') for i in range(1, 13)]
    rows = [[year] + [0] * 12 for year in range(start_year, end_year + 1)]
    return pd.DataFrame(rows, columns=columns)

def main():
    st.set_page_config(layout="wide")  # Set wide layout for better visibility
    st.title("Ticket Projection Model")
    initialize_session()
    
    # Select Service Unit
    st.sidebar.header("Service Unit Selection")
    service_unit = st.sidebar.selectbox("Select Service Unit", list(st.session_state.service_units.keys()))
    st.session_state.selected_unit = service_unit
    
    st.sidebar.header("Data Entry Type")
    data_type = st.sidebar.radio("Select Data Type", ["Created Tickets", "Resolved Tickets", "Rejected Tickets"])
    
    st.sidebar.header("Key Inputs")
    effort_per_ticket = st.sidebar.number_input("Effort per Ticket (Hours)", min_value=0.1, step=0.1)
    time_horizon = st.sidebar.number_input("Time Horizon (Months)", min_value=1, step=1)
    
    # Define the data entry grid
    start_year = st.number_input("Enter Start Year", min_value=2000, max_value=2100, value=datetime.datetime.now().year)
    end_year = st.number_input("Enter End Year", min_value=start_year, max_value=2100, value=start_year)
    
    if service_unit not in st.session_state.ticket_data:
        st.session_state.ticket_data[service_unit] = generate_month_grid(start_year, end_year)
    
    st.subheader(f"Data Entry Grid for {service_unit} - {data_type}")
    df = st.session_state.ticket_data[service_unit]
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"data_{service_unit}_{data_type}")
    
    # Ensure year column is mandatory
    edited_df.dropna(subset=["Year"], inplace=True)
    edited_df["Year"] = edited_df["Year"].astype(int)
    
    # Store the edited data back into session state
    st.session_state.ticket_data[service_unit] = edited_df.copy()
    
    # Get current month and count months from start
    current_month = datetime.datetime.now().month
    total_months = (end_year - start_year) * 12 + current_month if start_year < end_year else current_month
    st.sidebar.write(f"Total Months Counted: {total_months}")
    
    if st.button("Calculate Projection"):
        st.subheader("Projection Results")
        new_tickets_per_month = total_months  # Since it depends on counting input months
        total_effort_hours = new_tickets_per_month * effort_per_ticket
        fte_required = total_effort_hours / (160 * time_horizon)  # Assuming 160 hours per FTE per month
        
        st.write(f"**New Tickets Per Month:** {new_tickets_per_month}")
        st.write(f"**Total Effort (Hours):** {total_effort_hours:.2f} hours")
        st.write(f"**FTE Required:** {fte_required:.2f} Full-Time Employees")
    
if __name__ == "__main__":
    main()
