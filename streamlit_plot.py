import streamlit as st
import json
import requests
import pandas as pd
import time

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

# length_data = length_data/100

if st.session_state.clicked:

    df = pd.read_pickle("500dataframe.pkl")
    st.dataframe(df)

