import os
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from daf_tab.daf import daf_yomi_tab
from parsha_tab.parsha_home import parsha_tab
from yerushalmi_tab.yerushalmi_home import yerushalmi_tab
from mishnah_yomi_tab.mishnah_yomi_home import mishnah_yomi_tab
from haftarah_tab.haftarah_home import haftarah_tab
from nine_two_nine_tab.nine_two_nine_home import nine_two_nine_tab
from scores_tab.scores_home import scores_tab
import login_info

# Use numpy's triu function
triu = np.triu

# Get the directory of the current script
base_dir = os.path.dirname(__file__)

# Load the data from the parquet files
calendar_data_path = os.path.join(base_dir, 'learning_calendar_2024_2025.parquet')
calendar_df = pd.read_parquet(calendar_data_path)

# Updated paths for Daf Yomi, Parsha, Haftarah, and 929 Parquet files
daf_yomi_path = os.path.join(base_dir, 'merged_daf_yomi_data.parquet')
parsha_path = os.path.join(base_dir, 'merged_parsha_data.parquet')
haftarah_path = os.path.join(base_dir, 'merged_haftarah_data.parquet')
nine_two_nine_path = os.path.join(base_dir, 'merged_929_data.parquet')

# Load the dataframes with error handling
try:
    daf_yomi_df = pd.read_parquet(daf_yomi_path)
except FileNotFoundError:
    st.error(f"File not found: {daf_yomi_path}")
    daf_yomi_df = pd.DataFrame()

try:
    parsha_df = pd.read_parquet(parsha_path)
except FileNotFoundError:
    st.error(f"File not found: {parsha_path}")
    parsha_df = pd.DataFrame()

try:
    haftarah_df = pd.read_parquet(haftarah_path)
except FileNotFoundError:
    st.error(f"File not found: {haftarah_path}")
    haftarah_df = pd.DataFrame()

try:
    nine_two_nine_df = pd.read_parquet(nine_two_nine_path)
except FileNotFoundError:
    st.error(f"File not found: {nine_two_nine_path}")
    nine_two_nine_df = pd.DataFrame()

# Define the Seders and their corresponding tractates
seder_tractates = {
    "Zeraim": ["Berakhot"],
    "Moed": ["Shabbat", "Eruvin", "Pesachim", "Rosh Hashanah", "Yoma", "Sukkah", "Beitzah", "Taanit", "Megillah", "Moed Katan", "Chagigah"],
    "Nashim": ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin"],
    "Nezikin": ["Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", "Makkot", "Shevuot", "Avodah Zarah", "Horayot"],
    "Kodashim": ["Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", "Temurah", "Keritot", "Meilah", "Tamid"],
    "Tahorot": ["Niddah"]
}

# Define the range of dafs (pages) for each tractate
daf_ranges = {
    "Berakhot": range(2, 64),
    "Shabbat": range(2, 157),
    "Eruvin": range(2, 106),
    "Pesachim": range(2, 121),
    "Yoma": range(2, 89),
    "Sukkah": range(2, 57),
    "Beitzah": range(2, 41),
    "Rosh Hashanah": range(2, 36),
    "Taanit": range(2, 32),
    "Megillah": range(2, 32),
    "Moed Katan": range(2, 29),
    "Chagigah": range(2, 27),
    "Yevamot": range(2, 122),
    "Ketubot": range(2, 112),
    "Nedarim": range(2, 91),
    "Nazir": range(2, 67),
    "Sotah": range(2, 49),
    "Gittin": range(2, 90),
    "Kiddushin": range(2, 82),
    "Bava Kamma": range(2, 120),
    "Bava Metzia": range(2, 120),
    "Bava Batra": range(2, 176),
    "Sanhedrin": range(2, 113),
    "Makkot": range(2, 24),
    "Shevuot": range(2, 49),
    "Avodah Zarah": range(2, 76),
    "Horayot": range(2, 14),
    "Zevachim": range(2, 121),
    "Menachot": range(2, 110),
    "Chullin": range(2, 142),
    "Bekhorot": range(2, 61),
    "Arakhin": range(2, 35),
    "Temurah": range(2, 34),
    "Keritot": range(2, 28),
    "Meilah": range(2, 22),
    "Tamid": range(2, 10),
    "Middot": range(2, 5),
    "Niddah": range(2, 74)
}

# Initialize session state
login_info.initialize_session_state()

# Function to reset session state
def reset_session_state():
    for key in list(st.session_state.keys()):
        if key not in ['username', 'password', 'logged_in', 'selected_date']:
            del st.session_state[key]

# Function to save scores
def save_score(username, category, score):
    scores_file_path = os.path.join(base_dir, 'scores_tab', 'scores.parquet')
    today = datetime.today().strftime('%Y-%m-%d')
    new_score = pd.DataFrame([[username, category, score, today]], columns=['username', 'category', 'score', 'date'])
    try:
        scores_df = pd.read_parquet(scores_file_path)
        scores_df = pd.concat([scores_df, new_score], ignore_index=True)
    except FileNotFoundError:
        scores_df = new_score
    scores_df.to_parquet(scores_file_path, index=False)

# Sidebar for view selection
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select View", ["Home", "Daf Yomi", "Parsha", "Yerushalmi", "929", "Mishnah Yomi", "Haftarah", "Scores"], on_change=reset_session_state)

# Columns for date input and radio button
col1, col2 = st.columns([2, 1])
with col1:
    selected_date = st.date_input("Select a Date", datetime.strptime(st.session_state.selected_date, '%Y-%m-%d'))
    st.session_state.selected_date = selected_date.strftime('%Y-%m-%d')
with col2:
    date_option = st.radio("Date Option", ["Specific Date", "All Dates"])

# Format the selected date
formatted_date = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').strftime('%d %b %Y')

# Display the content of the selected view
if view == "Home":
    st.title("Daily Torah Quiz")
    if st.session_state.logged_in:
        st.write(f"Welcome {st.session_state.username}!")
    else:
        st.write("Welcome to the Daily Torah Quiz! Use the sidebar to navigate to Daf Yomi, Parsha, Yerushalmi, 929, Mishnah Yomi, or Haftarah quizzes.")
        st.write("Login or create a username below:")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_info.login(username, password)
        if st.button("Continue as Guest"):
            st.session_state.logged_in = True
            st.session_state.username = "Guest"
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password (optional)", type="password")
        if st.button("Register"):
            login_info.register(new_username, new_password)
elif view == "Daf Yomi":
    daf_yomi_tab(st, calendar_df, daf_yomi_df, seder_tractates, daf_ranges, date_option)
elif view == "Parsha":
    parsha_tab(st, calendar_df, date_option, parsha_path)
elif view == "Yerushalmi":
    yerushalmi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option)
elif view == "Mishnah Yomi":
    mishnah_yomi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option)
elif view == "Haftarah":
    haftarah_tab(st, calendar_df, date_option, haftarah_path)
elif view == "929":
    nine_two_nine_tab(st, calendar_df, nine_two_nine_df, date_option)
elif view == "Scores":
    scores_tab()

if st.session_state.logged_in and st.button("Logout"):
    login_info.logout()