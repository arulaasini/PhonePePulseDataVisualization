import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import json

# Set up the SQLAlchemy engine to connect to the database
server = "ASHWADHAASINI\SQLEXPRESS"
database = "PHONEPE"
driver = "ODBC Driver 17 for SQL Server"
engine = create_engine(f"mssql+pyodbc://{server}/{database}?driver={driver}")

# Set up the title and description of the app
st.title("WELCOME TO PHONEPE PULSE!")
st.write("A visualization tool of PhonePe Pulse")

# Fetch the distinct states from the database and store them in a pandas dataframe
df_states = pd.read_sql_query("SELECT DISTINCT States FROM Aggregatedtransactiondatatouse", engine)

# Create the Streamlit sidebar for State, Transaction Year, and Quarter selection
selected_state = st.sidebar.selectbox('Select State', df_states)
df_years = pd.read_sql_query("SELECT DISTINCT Transaction_Year FROM Aggregatedtransactiondatatouse", engine)
selected_transaction_year = st.sidebar.selectbox('Select Transaction Year', df_years['Transaction_Year'].tolist())
df_quarters = pd.read_sql_query("SELECT DISTINCT Quarters FROM Aggregatedtransactiondatatouse", engine)
selected_quarter = st.sidebar.selectbox('Select Quarter', df_quarters['Quarters'].tolist())

# Fetch the data from the SQL Server database based on the selected State, Transaction Year, and Quarter
query_template = f"SELECT Transaction_Count, Transaction_Amount FROM Aggregatedtransactiondatatouse WHERE States='{selected_state}' AND Transaction_Year={selected_transaction_year} AND Quarters={selected_quarter}"
df_data = pd.read_sql_query(query_template, engine)

# Display the fetched data in Streamlit
if not df_data.empty:
    transaction_count = df_data['Transaction_Count'].iloc[0]
    transaction_amount = df_data['Transaction_Amount'].iloc[0]
    st.write(f"Transaction Count for {selected_state}, {selected_transaction_year} {selected_quarter}: {transaction_count}")
    st.write(f"Transaction Amount for {selected_state}, {selected_transaction_year} {selected_quarter}: {transaction_amount}")
else:
    st.write(f"No data found for {selected_state}, {selected_transaction_year} {selected_quarter}")

# Define a query to fetch data from the aggregateduserdatatouse table
query = "SELECT States, Transaction_Year, Registered_Users, User_Counts, User_Percentage FROM aggregateduserdatatouse"

# Execute the query and load the data into a Pandas DataFrame
df = pd.read_sql(query, engine)

# Create a sidebar for the dropdown list of chart types
st.sidebar.header("Select chart type")
chart_type = st.sidebar.selectbox("", ["Bar chart", "Line chart", "Pie chart", "Histogram", "Bubble chart"])

# Create the chart based on the selected type
if chart_type == "Bar chart":
    fig = px.bar(df, x="States", y="Registered_Users", color="Transaction_Year", barmode="group")
elif chart_type == "Line chart":
    fig = px.line(df, x="States", y="Registered_Users", color="Transaction_Year")
elif chart_type == "Pie chart":
    fig = px.pie(df, values="Registered_Users", names="States")
elif chart_type == "Histogram":
    fig = px.histogram(df, x="Registered_Users")
elif chart_type == "Bubble chart":
    fig = px.scatter(df, x="States", y="Registered_Users", size="User_Counts", color="Transaction_Year")
    fig.update_layout(xaxis_title="States", yaxis_title="Registered Users")
else:
    st.error("Invalid chart type selected")

# Display the chart in Streamlit
st.plotly_chart(fig)

# Define SQL query
query = ("SELECT TOP 3 Entity_Name, Transaction_Amount "
         "FROM toptransactiontouse "
         "WHERE States = ? "
         "AND Transaction_Year = ? "
         "AND Quarters = ? "
         "ORDER BY Transaction_Amount DESC")

# Streamlit app
st.title('Top 3 Transactions')
states = df_states  # Replace with actual state names
state_name = st.selectbox('Select a state', states)

transaction_years = [2018, 2019, 2021, 2022]  # Replace with actual transaction years
transaction_year = st.selectbox('Select a transaction year', transaction_years)

quarters = [1, 2, 3, 4]  # Replace with actual quarters
quarter = st.selectbox('Select a quarter', quarters)

# Execute SQL query
if st.button('Get Top 3 Transactions'):
    # Pass parameters as tuple to the `params` argument of `pd.read_sql_query()`
    params = (state_name, transaction_year, quarter)
    df_top_transactions = pd.read_sql_query(query, engine, params=params)

# SQL Query to retrieve data
query = 'SELECT RegisteredUsers, Transaction_Year, States FROM mapusertouse'
data = pd.read_sql(query, engine)

fig = px.choropleth(
    data,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locations='States',
    color='RegisteredUsers',
    color_continuous_scale='green'
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig)
