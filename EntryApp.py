import streamlit as st
import pandas as pd
import datetime

def initialize_session():
    if "service_units" not in st.session_state:
        st.session_state.service_units = {"Unit A": None, "Unit B": None}  # Predefined service units
    if "selected_unit" not in st.session_state:
        st.session_state.selected_unit = "Unit A"
    if "ticket_data" not in st.session_state:
        st.session_state.ticket_data = {"Created Tickets": {}, "Resolved Tickets": {}, "Rejected Tickets": {}}

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
    end_year = st.number_input("Enter End Year", min_value=start_year, max_value=2100, value=datetime.datetime.now().year)
    
    if service_unit not in st.session_state.ticket_data[data_type]:
        st.session_state.ticket_data[data_type][service_unit] = generate_month_grid(start_year, end_year)
    
    st.subheader(f"Data Entry Grid for {service_unit} - {data_type}")
    df = st.session_state.ticket_data[data_type][service_unit]
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"data_{service_unit}_{data_type}")
    
    # Ensure year column is mandatory
    edited_df.dropna(subset=["Year"], inplace=True)
    edited_df["Year"] = edited_df["Year"].astype(int)
    
    # Store the edited data back into session state
    st.session_state.ticket_data[data_type][service_unit] = edited_df.copy()
    
    # Calculate total months from the first non-zero entry onward
    df_values = edited_df.iloc[:, 1:].values.flatten()
    first_nonzero_index = next((i for i, x in enumerate(df_values) if x > 0), None)
    first_nonzero_year = edited_df.iloc[first_nonzero_index // 12, 0] if first_nonzero_index is not None else start_year
    first_nonzero_month = (first_nonzero_index % 12) + 1 if first_nonzero_index is not None else 1
    
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    total_months = ((current_year - first_nonzero_year) * 12 + current_month - first_nonzero_month + 1) if first_nonzero_index is not None else 0
    
    st.sidebar.write(f"Total Months Counted: {total_months}")
    
    if st.button("Calculate Projection"):
        st.subheader("Projection Results")
        total_created_tickets = edited_df.iloc[:, 1:].sum().sum()
        new_tickets_per_month = total_created_tickets / total_months if total_months > 0 else 0
        total_effort_hours = new_tickets_per_month * effort_per_ticket
        fte_required = total_effort_hours / (160 * time_horizon)  # Assuming 160 hours per FTE per month
        
        net_open_tickets_per_month = total_created_tickets / total_months if total_months > 0 else 0
        growth_rate_per_month = (new_tickets_per_month - net_open_tickets_per_month) / net_open_tickets_per_month if net_open_tickets_per_month > 0 else 0
        avg_monthly_growth_rate = growth_rate_per_month * 100
        avg_yearly_growth_rate = avg_monthly_growth_rate * 12
        yearly_growth_factor = (1 + growth_rate_per_month) ** 12
        yearly_growth_tickets = total_created_tickets * yearly_growth_factor
        
        st.write(f"**New Tickets Per Month:** {new_tickets_per_month:.2f}")
        st.write(f"**Total Created Tickets:** {total_created_tickets}")
        st.write(f"**Total Effort (Hours):** {total_effort_hours:.2f} hours")
        st.write(f"**FTE Required:** {fte_required:.2f} Full-Time Employees")
        st.write(f"**Net Open Tickets/Month:** {net_open_tickets_per_month:.2f}")
        st.write(f"**Growth Rate/Month:** {growth_rate_per_month:.2%}")
        st.write(f"**Average Monthly Growth Rate:** {avg_monthly_growth_rate:.2f}%")
        st.write(f"**Average Yearly Growth Rate:** {avg_yearly_growth_rate:.2f}%")
        st.write(f"**Yearly Growth Factor:** {yearly_growth_factor:.2f}")
        st.write(f"**Yearly Growth Tickets:** {yearly_growth_tickets:.2f}")
    
if __name__ == "__main__":
    main()
