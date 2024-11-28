import streamlit as st
import json
import requests
import pandas as pd
from streamlit_agraph import agraph, Config, Node, Edge
import time
import datetime
from moralis import evm_api
import plotly.express as px
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Blockchain Analysis",
    page_icon="💲",
    layout="wide",
    # initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)
st.title("Blockchain Analysis")

final_df = pd.DataFrame()
# api_key = $API_KEY

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

with st.form('values'):
    col1,col2 = st.columns([1, 1],gap="medium")
    with col1:
        wallet = st.text_input("Enter wallet address")
    with col2:
        length_data = st.slider(label = "How much data you want to fetch ?", min_value = 100, max_value = 500, value= 100, step=100)
        length_data = length_data//100

    a, b, c, d, e, f, g, h, i = st.columns(9, vertical_alignment="bottom")
    with e:
        submit = st.form_submit_button('Analyze ⏳',on_click=click_button, use_container_width=True)

def remove_first_duplicates(df):
    
    # Get all column names
    cols = df.columns.tolist()
    
    # Create a dictionary to store indices of duplicate columns
    # Key: column name, Value: list of indices where this column name appears
    col_indices = {}
    
    for idx, col in enumerate(cols):
        if col not in col_indices:
            col_indices[col] = [idx]
        else:
            col_indices[col].append(idx)
    
    # Identify indices to drop (first occurrence of duplicates)
    indices_to_drop = []
    for col, indices in col_indices.items():
        if len(indices) > 1:  # If column name appears more than once
            indices_to_drop.append(indices[0])  # Add first occurrence index
    
    # Create list of column indices to keep
    keep_indices = [i for i in range(len(cols)) if i not in indices_to_drop]
    
    # Return DataFrame with only the kept columns
    return df.iloc[:, keep_indices]

def data_making(data):
        
        result = data['result']

        df = pd.DataFrame(result)

        df = df.drop(['erc20_transfers', 'native_transfers', 'nft_transfers'], axis='columns').copy()

        result_length = len(result)

        default_data = {'token_name': None,
        'token_symbol': None,
        'token_logo': None,
        'token_decimals': None,
        'from_address_entity': None,
        'from_address_entity_logo': None,
        'from_address': None,
        'from_address_label': None,
        'to_address_entity': None,
        'to_address_entity_logo': None,
        'to_address': None,
        'to_address_label': None,
        'address': None,
        'log_index': None,
        'value': None,
        'possible_spam': None,
        'verified_contract': None,
        'security_score': None,
        'direction': None,
        'value_formatted': None}

        transfers = []

        for x in range(result_length):
            if len(data['result'][x]['erc20_transfers'])!=0:
                transfers.append(data['result'][x]['erc20_transfers'][0])
            elif len(data['result'][x]['native_transfers'])!=0:
                transfers.append(data['result'][x]['native_transfers'][0])
            else :
                transfers.append(default_data)

        df1 = pd.DataFrame(transfers)
        combined_data = pd.concat([df.reset_index(drop=True), df1.reset_index(drop=True)], axis=1)

        combined_data = remove_first_duplicates(combined_data)
        return combined_data

def df_cleaning(df):

    column_list = df.columns.tolist()

    column_df = []

    if column_list.count('hash') > 0:
        column_df.append('hash')
    if column_list.count('block_timestamp') > 0:
        column_df.append('block_timestamp')
    if column_list.count('summary') > 0:
        column_df.append('summary')
    if column_list.count('token_name') > 0:
        column_df.append('token_name')
    if column_list.count('from_address_entity') > 0:
        column_df.append('from_address_entity')
    if column_list.count('from_address') > 0:
        column_df.append('from_address')
    if column_list.count('to_address_entity') > 0:
        column_df.append('to_address_entity')
    if column_list.count('to_address') > 0:
        column_df.append('to_address')
    if column_list.count('possible_spam') > 0:
        column_df.append('possible_spam')
    if column_list.count('verified_contract') > 0:
        column_df.append('verified_contract')
    if column_list.count('direction') > 0:
        column_df.append('direction')
    if column_list.count('value_formatted') > 0:
        column_df.append('value_formatted')
    
    df = df[column_df]
    return df

def date(df):
    df['block_timestamp'] = pd.to_datetime(df['block_timestamp'])
    df['block_timestamp'] = df['block_timestamp'].dt.date
    return df


@st.cache_data
def api_query(length_data, wallet):

    final_df = pd.DataFrame()
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjViZGZkYTA5LTU0ZTMtNGJjOC04ZTQwLWFjNzFjM2MwZDIzZSIsIm9yZ0lkIjoiNDE1MzYzIiwidXNlcklkIjoiNDI2ODY0IiwidHlwZSI6IlBST0pFQ1QiLCJ0eXBlSWQiOiJkOTJjNDE5Ny0xMjNiLTQxYWItODY4Zi05Y2E4NTI3YWJkNDUiLCJpYXQiOjE3MzI0ODQzNjEsImV4cCI6NDg4ODI0NDM2MX0.IM-G4-A5nqQkwJtS1Acim_xRRWV7I8gQAs0tsUgNDig"

    cursor = ""
    # api
    for x in range(length_data):
        params = {
            "chain": "eth",
            "include_internal_transactions": False,
            "nft_metadata": False,
            "order": "DESC",
            "cursor": cursor,
            "address": wallet,
        }
        data = evm_api.wallets.get_wallet_history(
            api_key=api_key,
            params=params,
        )
        cursor = data["cursor"]
        
        df = data_making(data)
        final_df = pd.concat([final_df, df], ignore_index=True)
        
    final_df = df_cleaning(final_df)
    return final_df

def filtering_data(df, token):
    
    filter_pattern = r'^(Sent|Received) [A-Za-z0-9 .:]+(to|from) [A-Za-z0-9 .:]+$'
    df = df[df['summary'].str.match(filter_pattern)]
    df = df[~df['summary'].str.contains('NFT', na=False)]
    df['token_name'] = df.apply(
        lambda row: token if ( token in row['summary'] and ('Sent' in row['summary'] or 'Received' in row['summary']))
        else row['token_name'], axis=1
    )
    df['verified_contract'] = df['verified_contract'].astype(bool)
    df.loc[df['token_name'] == 'POL', 'verified_contract'] = True

    df = df[df['verified_contract'] == True]

    df = df.drop(["verified_contract", "possible_spam"], axis = 1)

    return df

if st.session_state.clicked:

    token = "ETH"

    # api_query
    # df = api_query(length_data, wallet)

    with st.expander("Click to load raw data..."):
        df = pd.read_pickle('/Users/aritra/Documents/SIH/otherwallet_eth_moreprocessing.pkl')
        st.dataframe(df)
        
    df_plot = df.copy()

    col1, col2 = st.columns([1, 1],gap="small")

    with col1 :

        options = st.multiselect(
            "Filter data parameters",
            options=["Incoming", "Outgoing", "Only Peer to Peer", "Filter SPAM" ],  # Options to select from
            default=["Filter SPAM", "Only Peer to Peer"],          # Default selected options
        )

        if options.count('Only Peer to Peer') > 0 and options.count('Filter SPAM') > 0 :
            df_plot = filtering_data(df_plot, token)

        if options.count('Incoming') > 0:
            df_plot = df_plot[df_plot['direction'] == "receive"]

        if options.count('Outgoing') > 0:
            df_plot = df_plot[df_plot['direction'] == "send"]

        df_plot = df_plot.reset_index(drop=True)
        
    with col2 :
        max_date = df_plot['block_timestamp'][0]
        min_date = df_plot['block_timestamp'][len(df_plot['block_timestamp'])-1]

        d = st.date_input(
            "Select time frame",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )
        df_plot = df_plot[df_plot['block_timestamp'].between(d[0], d[1])]

    st.dataframe(df_plot)



    


    col1, col2, col3 = st.columns([1, 1, 1],gap="small")
    col4, col5, col6 = st.columns([1, 1, 1],gap="small")

    with col1 :
        fig = px.pie(df_plot, names='from_address_entity')
        st.write(fig)
    with col2 :
        fig = px.pie(df_plot, names='to_address_entity')
        st.write(fig)
    with col3 :
        fig = px.pie(df_plot, names='direction')
        st.write(fig)

    df_wallet = df_plot.copy() 


    # first try 
    # st.dataframe(df_wallet)
    # st.write("### Data Preview")
    # # Create a directed graph
    # G_wallet = nx.DiGraph()

    # # Add edges with labels for entities
    # for _, row in df_wallet.iterrows():
    #     from_label = f"{row['from_address']} ({row['from_address_entity']})" if pd.notna(row['from_address_entity']) else row['from_address']
    #     to_label = f"{row['to_address']} ({row['to_address_entity']})" if pd.notna(row['to_address_entity']) else row['to_address']
    #     G_wallet.add_edge(from_label, to_label)

    # # Generate the graph visualization
    # plt.figure(figsize=(15, 10))
    # pos_wallet = nx.spring_layout(G_wallet, k=0.3, seed=42)  # Positioning the nodes
    # nx.draw(
    #     G_wallet, pos_wallet, with_labels=True, node_size=500, node_color="lightgreen", font_size=8, font_weight="bold", edge_color="black"
    # )
    # plt.title("Blockchain Transactions Graph", fontsize=15)

    # # Show the graph in Streamlit
    # st.pyplot(plt)


    # second try 



    # Prepare nodes and edges for streamlit-agraph
    nodes = []
    edges = []
    added_nodes = set()

    for _, row in df_wallet.iterrows():
        from_label = f"{row['from_address']} ({row['from_address_entity']})" if pd.notna(row['from_address_entity']) else row['from_address']
        to_label = f"{row['to_address']} ({row['to_address_entity']})" if pd.notna(row['to_address_entity']) else row['to_address']

        if from_label not in added_nodes:
            nodes.append(Node(id=from_label, label=from_label, color="green"))
            added_nodes.add(from_label)
        if to_label not in added_nodes:
            nodes.append(Node(id=to_label, label=to_label, color="blue"))
            added_nodes.add(to_label)

        edges.append(Edge(source=from_label, target=to_label))

    # Streamlit app
    st.title("Blockchain Transactions Graph")
    
    # config = Config(width=1000, height=800, directed=True, nodeHighlightBehavior=True, highlightColor="yellow",
    #                 collapsible=True, node={'color': 'lightgreen', 'size': 400}, link={'labelProperty': 'label'})
    config = Config(width=750,
                height=950,
                directed=True, 
                physics=True, 
                hierarchical=False,
                # **kwargs
                )

    agraph(nodes=nodes, edges=edges, config=config)

    
