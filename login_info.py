import os
import pandas as pd
import streamlit as st
from datetime import datetime

# Path to the Parquet file for storing user credentials
base_dir = os.path.dirname(__file__)
user_credentials_path = os.path.join(base_dir, 'user_credentials.parquet')

# Initialize session state for user information
def initialize_session_state():
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'password' not in st.session_state:
        st.session_state.password = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().strftime('%Y-%m-%d')

# Function to handle login
def login(username, password):
    if os.path.exists(user_credentials_path):
        user_df = pd.read_parquet(user_credentials_path)
        if not user_df[(user_df['username'] == username) & ((user_df['password'] == password) | (user_df['password'] == ""))].empty:
            st.session_state.username = username
            st.session_state.password = password
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password")
    else:
        st.error("No registered users found")

# Function to handle logout
def logout():
    st.session_state.username = None
    st.session_state.password = None
    st.session_state.logged_in = False

# Function to handle registration
def register(username, password):
    if os.path.exists(user_credentials_path):
        user_df = pd.read_parquet(user_credentials_path)
        if not user_df[user_df['username'] == username].empty:
            st.error("Username already exists")
            return
    else:
        user_df = pd.DataFrame(columns=['username', 'password'])

    new_user = pd.DataFrame({'username': [username], 'password': [password]})
    user_df = pd.concat([user_df, new_user], ignore_index=True)
    user_df.to_parquet(user_credentials_path, index=False)
    st.success("User registered successfully")