import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit App Title
st.title("Ticket Growth & Resolution Analysis")

# User Input for Ticket Data
st.sidebar.header("Input Ticket Data")
years = st.sidebar.slider("Select Number of Years", 1, 10, 5)

# Create empty dataframes
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
data_columns = ["Year"] + months

def input_ticket_data(label):
    st.subheader(label)
    df = pd.DataFrame(columns=data_columns)
    for i in range(years):
        year = st.number_input(f"Year {i+1} ({label})", min_value=2000, max_value=2100, step=1, key=f"year_{label}_{i}")
        row = [year] + [st.number_input(f"{month} ({year})", min_value=0, step=1, key=f"{label}_{year}_{month}_{i}") for month in months]
        df.loc[i] = row
    return df

# Collect input data
created_tickets = input_ticket_data("Created Tickets")
rejected_tickets = input_ticket_data("Rejected Tickets")
resolved_tickets = input_ticket_data("Resolved Tickets")

# Merge Data
merged_data = created_tickets.merge(rejected_tickets, on="Year", suffixes=("_Created", "_Rejected"), how="left")
merged_data = merged_data.merge(resolved_tickets, on="Year", suffixes=("", "_Resolved"), how="left")
merged_data.fillna(0, inplace=True)

# Compute Metrics
for month in months:
    created_col = month + "_Created"
    rejected_col = month + "_Rejected"
    resolved_col = month + "_Resolved"
    
    # Ensure columns exist before accessing them
    if rejected_col not in merged_data:
        merged_data[rejected_col] = 0
    if resolved_col not in merged_data:
        merged_data[resolved_col] = 0
    
    merged_data[month + "_Net"] = merged_data[created_col] - (
        merged_data[rejected_col] + merged_data[resolved_col])

merged_data["Total_Created"] = merged_data[[col for col in merged_data.columns if "Created" in col]].sum(axis=1)
merged_data["Total_Rejected"] = merged_data[[col for col in merged_data.columns if "Rejected" in col]].sum(axis=1)
merged_data["Total_Resolved"] = merged_data[[col for col in merged_data.columns if "Resolved" in col]].sum(axis=1)
merged_data["Net_Growth"] = merged_data["Total_Created"] - (merged_data["Total_Rejected"] + merged_data["Total_Resolved"])

# Avoid division by zero in Resolution Rate
merged_data["Resolution_Rate"] = merged_data["Total_Resolved"] / merged_data[["Total_Created"].subtract(merged_data["Total_Rejected"])].replace(0, 1)
merged_data["Resolution_Rate"].fillna(0, inplace=True)

# Display Data
st.subheader("Processed Ticket Data")
st.dataframe(merged_data)

# Plot Net Growth Over Time
st.subheader("Net Ticket Growth Over Time")
fig, ax = plt.subplots()
ax.plot(merged_data["Year"], merged_data["Net_Growth"], marker='o', linestyle='-', label="Net Growth")
ax.set_xlabel("Year")
ax.set_ylabel("Net Ticket Growth")
ax.set_title("Net Ticket Growth Over Time")
ax.grid(True)
st.pyplot(fig)

# Plot Resolution Rate
st.subheader("Ticket Resolution Efficiency Over Time")
fig, ax = plt.subplots()
ax.plot(merged_data["Year"], merged_data["Resolution_Rate"], marker='o', linestyle='-', color='green', label="Resolution Rate")
ax.set_xlabel("Year")
ax.set_ylabel("Resolution Efficiency (%)")
ax.set_title("Ticket Resolution Efficiency Over Time")
ax.set_ylim(0, 1.2)
ax.grid(True)
st.pyplot(fig)

st.write("This application allows users to analyze ticket trends based on user-defined input values.")
