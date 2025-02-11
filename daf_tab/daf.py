import random
import re
import streamlit as st
import pandas as pd

def get_surrounding_dafs(daf, n=3, talmud_dict=None):
    keys = list(talmud_dict.keys())
    index = keys.index(daf)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

def daf_yomi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option, shulchan_arukh_df, rashi_on_tractates_df):
    st.header("Daf Yomi Quiz")

    # Initialize session state
    if 'selected_seder' not in st.session_state:
        st.session_state.selected_seder = None
    if 'selected_tractate' not in st.session_state:
        st.session_state.selected_tractate = None
    if 'selected_daf' not in st.session_state:
        st.session_state.selected_daf = None

    # Check if calendar_df is not empty and contains 'Date' column
    if calendar_df.empty or 'Date' not in calendar_df.columns:
        st.error("The 'Date' column is missing in the calendar DataFrame.")
        return

    # Extract the Daf for the given date
    if date_option == "Specific Date":
        selected_date = st.session_state.selected_date
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Daf Yomi')]
        if not filtered_calendar_df.empty:
            selected_daf = filtered_calendar_df.iloc[0]['Display Value (en)']
            daf_list = [selected_daf]
            selected_tractate = selected_daf.split()[0]
            selected_seder = next(seder for seder, tractates in seder_tractates.items() if selected_tractate in tractates)
            seder_list = [selected_seder]
        else:
            st.write(f"No data available for the selected date: {selected_date}")
            st.write("Available dates in calendar_df:")
            st.write(calendar_df['Date'].unique())
            return
    else:
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Daf Yomi'].drop_duplicates(subset=['Display Value (en)'])
        daf_list = filtered_calendar_df['Display Value (en)'].tolist()
        seder_list = list(seder_tractates.keys())

    # Extract the Parsha for the given date
    selected_row = calendar_df[(calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Parashat Hashavua')]
    if not selected_row.empty:
        selected_parsha = selected_row.iloc[0]['Display Value (en)']
    else:
        st.write(f"No data available for the selected date: {selected_date}")
        st.write("Available dates in calendar_df:")
        st.write(calendar_df['Date'].unique())
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_seder = st.selectbox("Select a Seder", seder_list, index=0, key="seder_talmud")
    with col2:
        if date_option == "Specific Date":
            tractate_list = [selected_tractate] if selected_seder else []
        else:
            tractate_list = seder_tractates[selected_seder]
        selected_tractate = st.selectbox("Select a Tractate", tractate_list, key="tractate_talmud")
    with col3:
        if date_option == "Specific Date":
            daf_list = [selected_daf] if selected_tractate else []
        else:
            daf_list = [f"{selected_tractate} {daf}" for daf in daf_ranges[selected_tractate]]
        selected_daf = st.selectbox("Select a Daf", daf_list, key="daf_talmud")

    # Create a DataFrame from talmud_dict
    talmud_data = []
    for daf, texts in talmud_dict.items():
        for text in texts:
            talmud_data.append([daf, selected_seder, selected_tractate, text, "", "Talmud"])
    talmud_df = pd.DataFrame(talmud_data, columns=['Daf', 'Seder', 'Tractate', 'Text', 'Incorrect Answers', 'Source'])

    # Filter the DataFrame to only include rows where Daf matches the selected Daf
    filtered_talmud_df = talmud_df[talmud_df['Daf'] == selected_daf]

    # Filter shulchan_arukh_df to only include rows where Daf matches the selected Daf
    shulchan_arukh_df['Source'] = 'Shulchan Arukh'
    filtered_shulchan_arukh_df = shulchan_arukh_df[shulchan_arukh_df['Daf'] == selected_daf]

    # Filter rashi_on_tractates_df to only include rows where Daf matches the selected Daf
    rashi_on_tractates_df['Source'] = 'Rashi'
    filtered_rashi_df = rashi_on_tractates_df[rashi_on_tractates_df['Daf'] == selected_daf]

    # Concatenate the filtered DataFrames
    combined_df = pd.concat([filtered_talmud_df, filtered_shulchan_arukh_df, filtered_rashi_df])

    # Check if "Rashi" is in the combined DataFrame
    if "Rashi" in combined_df['Source'].values:
        st.write("Rashi is in the combined DataFrame.")
    else:
        st.write("Rashi is not in the combined DataFrame.")

    # Display the combined DataFrame
    st.dataframe(combined_df)

# Example usage
calendar_df = pd.DataFrame()  # Replace with actual DataFrame
talmud_dict = {}  # Replace with actual dictionary
seder_tractates = {}  # Replace with actual dictionary
daf_ranges = {}  # Replace with actual dictionary
shulchan_arukh_df = pd.DataFrame()  # Replace with actual DataFrame
rashi_on_tractates_df = pd.DataFrame()  # Replace with actual DataFrame
date_option = "Specific Date"  # or "All Dates"

daf_yomi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option, shulchan_arukh_df, rashi_on_tractates_df)