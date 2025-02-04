import streamlit as st
import pandas as pd
import random
import os

# Get the directory of the current script
base_dir = os.path.dirname(__file__)

# Load the data from the parquet files
talmud_data_path = os.path.join(base_dir, 'talmud_topics.parquet')
torah_data_path = os.path.join(base_dir, 'torah_topics.parquet')

talmud_df = pd.read_parquet(talmud_data_path)
torah_df = pd.read_parquet(torah_data_path)

# Split the topics into lists
talmud_df['Topics'] = talmud_df['Topics'].apply(lambda x: x.split(', '))
torah_df['Topics'] = torah_df['Topics'].apply(lambda x: x.split(', '))

# Create dictionaries for easy access
talmud_dict = talmud_df.set_index('Daf')['Topics'].to_dict()
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
st.title("Topics Quiz")

# Create tabs
tab1, tab2 = st.tabs(["Talmud Topics", "Torah Topics"])

with tab1:
    st.header("Talmud Topics Quiz")

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

    # Dropdown for selecting a Daf
    selected_daf = st.selectbox("Select a Daf", list(talmud_dict.keys()), index=0)

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
    st.header("Torah Topics Quiz")

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

    # Dropdown for selecting a Parsha
    selected_parsha = st.selectbox("Select a Parsha", list(torah_dict.keys()), index=0)

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