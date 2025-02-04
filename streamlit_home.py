import streamlit as st
import pandas as pd
import random
import os
from datetime import datetime

# Get the directory of the current script
base_dir = os.path.dirname(__file__)

# Load the data from the parquet files
talmud_data_path = os.path.join(base_dir, 'talmud_topics.parquet')
torah_data_path = os.path.join(base_dir, 'torah_topics.parquet')
calendar_data_path = os.path.join(base_dir, 'learning_calendar_2024_2025.parquet')
talmud_df = pd.read_parquet(talmud_data_path)
torah_df = pd.read_parquet(torah_data_path)
calendar_df = pd.read_parquet(calendar_data_path)

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

# Function to get surrounding dafs
def get_surrounding_dafs(daf, n=3):
    keys = list(talmud_dict.keys())
    index = keys.index(daf)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

# Function to get surrounding parshas
def get_surrounding_parshas(parsha, n=3):
    keys = list(torah_dict.keys())
    index = keys.index(parsha)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

# Streamlit app
st.title("Daily Torah Quiz")

# Create tabs
tab1, tab2 = st.tabs(["Daf Yomi Topics", "Parsha Topics"])

with tab1:
    st.header("Daf Yomi Quiz")

    # Initialize session state
    if 'selected_daf' not in st.session_state:
        st.session_state.selected_daf = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'options' not in st.session_state:
        st.session_state.options = None
    if 'correct_topic' not in st.session_state:
        st.session_state.correct_topic = None
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.today().strftime('%Y-%m-%d')

    # Columns for date input and radio button
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_date = st.date_input("Select a Date", datetime.strptime(st.session_state.selected_date, '%Y-%m-%d'), key="date_talmud")
        st.session_state.selected_date = selected_date.strftime('%Y-%m-%d')
    with col2:
        date_option = st.radio("Date Option", ["Specific Date", "All Dates"], key="date_option")

    # Format the selected date
    formatted_date = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').strftime('%d %b %Y')

    if date_option == "Specific Date":
        # Filter calendar data for the selected date and title "Daf Yomi"
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == st.session_state.selected_date) & (calendar_df['Title (en)'] == 'Daf Yomi')]
    else:
        # Filter calendar data for all dates and title "Daf Yomi"
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Daf Yomi']

    # Dropdown for selecting a Daf
    daf_list = filtered_calendar_df['Display Value (en)'].tolist()
    selected_daf = st.selectbox("Select a Daf", daf_list, index=0, key="daf_talmud")

    def generate_talmud_question(daf):
        correct_topics = talmud_dict[daf]
        correct_topic = random.choice(correct_topics)
        surrounding_dafs = get_surrounding_dafs(daf)
        surrounding_topics = {topic for daf in surrounding_dafs for topic in talmud_dict[daf] if topic not in correct_topics}
        incorrect_topics = random.sample(list(surrounding_topics), 3)
        options = incorrect_topics + [correct_topic]
        random.shuffle(options)
        return f"Which topic is discussed in {daf}?", options, correct_topic

    if st.session_state.question is None or st.session_state.selected_daf != selected_daf:
        st.session_state.selected_daf = selected_daf
        st.session_state.question, st.session_state.options, st.session_state.correct_topic = generate_talmud_question(selected_daf)
        st.session_state.answered = False

    # Display the question
    st.write(st.session_state.question)
    st.session_state.selected_option = st.radio("Choose an option:", st.session_state.options)

    # Check the answer
    if st.button("Submit"):
        st.session_state.answered = True
        if st.session_state.selected_option == st.session_state.correct_topic:
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct answer is: {st.session_state.correct_topic}")

    # Next question button
    if st.session_state.answered and st.button("Next Question"):
        st.session_state.question, st.session_state.options, st.session_state.correct_topic = generate_talmud_question(selected_daf)
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.rerun()

with tab2:
    st.header("Parsha Quiz")

    # Initialize session state
    if 'selected_parsha' not in st.session_state:
        st.session_state.selected_parsha = None
    if 'question_torah' not in st.session_state:
        st.session_state.question_torah = None
    if 'options_torah' not in st.session_state:
        st.session_state.options_torah = None
    if 'correct_topic_torah' not in st.session_state:
        st.session_state.correct_topic_torah = None
    if 'answered_torah' not in st.session_state:
        st.session_state.answered_torah = False
    if 'selected_option_torah' not in st.session_state:
        st.session_state.selected_option_torah = None
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.today().strftime('%Y-%m-%d')

    # Columns for date input and radio button
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_date = st.date_input("Select a Date", datetime.strptime(st.session_state.selected_date, '%Y-%m-%d'), key="date_torah")
        st.session_state.selected_date = selected_date.strftime('%Y-%m-%d')
    with col2:
        date_option_torah = st.radio("Date Option", ["Specific Date", "All Dates"], key="date_option_torah")

    # Format the selected date
    formatted_date = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').strftime('%d %b %Y')

    if date_option_torah == "Specific Date":
        # Filter calendar data for the selected date and title "Parashat Hashavua"
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == st.session_state.selected_date) & (calendar_df['Title (en)'] == 'Parashat Hashavua')]
    else:
        # Filter calendar data for all dates and title "Parashat Hashavua"
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Parashat Hashavua']

    # Dropdown for selecting a Parsha
    parsha_list = filtered_calendar_df['Display Value (en)'].tolist()
    selected_parsha = st.selectbox("Select a Parsha", parsha_list, index=0, key="parsha_torah")

    def generate_torah_question(parsha):
        correct_topics = torah_dict[parsha]
        correct_topic = random.choice(correct_topics)
        surrounding_parshas = get_surrounding_parshas(parsha)
        surrounding_topics = {topic for parsha in surrounding_parshas for topic in torah_dict[parsha] if topic not in correct_topics}
        incorrect_topics = random.sample(list(surrounding_topics), 3)
        options = incorrect_topics + [correct_topic]
        random.shuffle(options)
        return f"Which topic is discussed in {parsha}?", options, correct_topic

    if st.session_state.question_torah is None or st.session_state.selected_parsha != selected_parsha:
        st.session_state.selected_parsha = selected_parsha
        st.session_state.question_torah, st.session_state.options_torah, st.session_state.correct_topic_torah = generate_torah_question(selected_parsha)
        st.session_state.answered_torah = False

    # Display the question
    st.write(st.session_state.question_torah)
    st.session_state.selected_option_torah = st.radio("Choose an option:", st.session_state.options_torah)

    # Check the answer
    if st.button("Submit", key="submit_torah"):
        st.session_state.answered_torah = True
        if st.session_state.selected_option_torah == st.session_state.correct_topic_torah:
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct answer is: {st.session_state.correct_topic_torah}")

    # Next question button
    if st.session_state.answered_torah and st.button("Next Question", key="next_torah"):
        st.session_state.question_torah, st.session_state.options_torah, st.session_state.correct_topic_torah = generate_torah_question(selected_parsha)
        st.session_state.answered_torah = False
        st.session_state.selected_option_torah = None
        st.rerun()