import os
import pandas as pd
import streamlit as st
from datetime import datetime
from daf import daf_yomi_tab
from parsha import parsha_tab

# Get the directory of the current script
base_dir = os.path.dirname(__file__)

# Load the data from the parquet files
talmud_data_path = os.path.join(base_dir, 'talmud_topics.parquet')
torah_data_path = os.path.join(base_dir, 'torah_topics.parquet')
calendar_data_path = os.path.join(base_dir, 'learning_calendar_2024_2025.parquet')
sefer_hachinuch_path = os.path.join(base_dir, 'sefer_hachinuch.parquet')
kitzur_related_path = os.path.join(base_dir, 'kitzur_related_by_parsha.parquet')
shulchan_arukh_path = os.path.join(base_dir, 'shulchan_arukh_references_by_daf.parquet')

talmud_df = pd.read_parquet(talmud_data_path)
torah_df = pd.read_parquet(torah_data_path)
calendar_df = pd.read_parquet(calendar_data_path)
sefer_hachinuch_df = pd.read_parquet(sefer_hachinuch_path)
kitzur_related_df = pd.read_parquet(kitzur_related_path)
shulchan_arukh_df = pd.read_parquet(shulchan_arukh_path)

# Split the topics into lists
talmud_df['Topics'] = talmud_df['Topics'].apply(lambda x: x.split(', '))
torah_df['Topics'] = torah_df['Topics'].apply(lambda x: x.split(', '))

# Combine topics for 'a' and 'b' suffixes under the same key
combined_talmud_dict = {}
for daf, topics in talmud_df.set_index('Daf')['Topics'].to_dict().items():
    base_daf = daf[:-1] if daf[-1] in ['a', 'b'] else daf
    if base_daf not in combined_talmud_dict:
        combined_talmud_dict[base_daf] = set()
    combined_talmud_dict[base_daf].update(topics)

# Convert sets to lists
talmud_dict = {k: list(v) for k, v in combined_talmud_dict.items()}
torah_dict = torah_df.set_index('Parsha')['Topics'].to_dict()

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

# Streamlit app
st.title("Daily Torah Quiz")

# Initialize session state for progress tracking
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.today().strftime('%Y-%m-%d')
if 'active_view' not in st.session_state:
    st.session_state.active_view = "Daf Yomi"

# Sidebar for view selection
st.sidebar.title("Navigation")
view = st.sidebar.radio("Select View", ["Daf Yomi", "Parsha"])

# Reset questions and answers when switching views
if st.session_state.active_view != view:
    st.session_state.correct_answers = 0
    st.session_state.total_questions = 0
    st.session_state.question = None
    st.session_state.options = None
    st.session_state.correct_topic = None
    st.session_state.full_text = None
    st.session_state.answered = False
    st.session_state.active_view = view

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
if st.session_state.active_view == "Daf Yomi":
    daf_yomi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option, shulchan_arukh_df)
elif st.session_state.active_view == "Parsha":
    parsha_tab(st, calendar_df, torah_dict, torah_df, date_option, sefer_hachinuch_df, kitzur_related_df)

# Display progress bar at the bottom
progress = st.session_state.correct_answers / st.session_state.total_questions if st.session_state.total_questions > 0 else 0
st.progress(progress)
st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.total_questions} ({progress * 100:.2f}%)")