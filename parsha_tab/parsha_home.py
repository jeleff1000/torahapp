import streamlit as st
import pandas as pd
from .parsha_questions import generate_combined_question
from datetime import datetime
import os

def save_score(username, category, score):
    base_dir = os.path.dirname(__file__)
    scores_file_path = os.path.join(base_dir, '..', 'scores_tab', 'scores.parquet')
    today = datetime.today().strftime('%Y-%m-%d')
    new_score = pd.DataFrame([[username, category, score, today]], columns=['username', 'category', 'score', 'date'])
    try:
        scores_df = pd.read_parquet(scores_file_path)
        scores_df = pd.concat([scores_df, new_score], ignore_index=True)
    except FileNotFoundError:
        scores_df = new_score
    scores_df.to_parquet(scores_file_path, index=False)

def preprocess_df(df):
    for column in df.columns:
        df[column] = df[column].apply(lambda x: str(x) if not pd.isna(x) else x)
    return df

def clean_values(df):
    for column in df.columns:
        df[column] = df[column].apply(lambda x: x.replace("['", "").replace("']", "") if isinstance(x, str) else x)
    return df

def parsha_tab(st, calendar_df, date_option, parsha_path):
    st.header("Parsha Quiz")

    # Load the parsha DataFrame
    parsha_df = pd.read_parquet(parsha_path)

    # Initialize session state
    if 'selected_parsha' not in st.session_state:
        st.session_state.selected_parsha = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'options' not in st.session_state:
        st.session_state.options = None
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'questions_df' not in st.session_state:
        st.session_state.questions_df = pd.DataFrame()  # Initialize as empty DataFrame
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date_option
    if 'source_filters' not in st.session_state:
        st.session_state.source_filters = {
            'Quotes': True,
            'Rashi': True,
            'Topics': True,
            'Mitzvot': True,
            'Halachot': True
        }

    # Reset question bank if date option changes
    if 'previous_date_option' not in st.session_state:
        st.session_state.previous_date_option = date_option
    if st.session_state.previous_date_option != date_option:
        st.session_state.previous_date_option = date_option
        st.session_state.question = None
        st.session_state.options = None
        st.session_state.correct_answer = None
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.session_state.questions_df = pd.DataFrame()
        st.session_state.total_questions = 0
        st.session_state.correct_answers = 0

    # Checkbox filters for each source category
    with st.expander("Filter by Source"):
        cols = st.columns(len(st.session_state.source_filters))
        for i, (source, value) in enumerate(st.session_state.source_filters.items()):
            with cols[i]:
                st.session_state.source_filters[source] = st.checkbox(source, value=value)
        if st.button("Apply Filters"):
            st.session_state.question = None  # Reset the current question
            st.rerun()

    if date_option == "All Dates":
        # Allow user to select any book and parsha
        books = parsha_df['book'].unique()
        selected_book = st.selectbox("Select a Book", books)
        parshas = parsha_df[parsha_df['book'] == selected_book]['parsha'].unique()
        selected_parsha = st.selectbox("Select a Parsha", parshas)
    else:
        # Extract the Parsha for the given date
        selected_date = st.session_state.selected_date
        selected_row = calendar_df[(calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Parashat Hashavua')]
        if not selected_row.empty:
            selected_parsha = selected_row.iloc[0]['Display Value (en)']
        else:
            st.write(f"No data available for the selected date: {selected_date}")
            st.write("Available dates in calendar_df:")
            st.write(calendar_df['Date'].unique())
            return

        # Automatically select the book and parsha based on the selected_parsha
        selected_book = parsha_df[parsha_df['parsha'] == selected_parsha]['book'].iloc[0]
        st.session_state.selected_parsha = selected_parsha

        # Add dropdowns for selecting book and parsha
        books = parsha_df['book'].unique()
        selected_book = st.selectbox("Select a Book", books, index=list(books).index(selected_book))
        parshas = parsha_df[parsha_df['book'] == selected_book]['parsha'].unique()
        selected_parsha = st.selectbox("Select a Parsha", parshas, index=list(parshas).index(selected_parsha))

    # Filter DataFrame to match the selected parsha
    parsha_df = parsha_df[parsha_df['parsha'] == selected_parsha]

    # Preprocess DataFrame to ensure all elements are strings
    parsha_df = preprocess_df(parsha_df)

    # Clean DataFrame to remove unwanted formatting
    parsha_df = clean_values(parsha_df)

    # Add source column to the DataFrame
    parsha_df['source'] = 'Parsha'

    # Ensure the DataFrame has source ref column
    for column in ['source ref']:
        if column not in parsha_df.columns:
            parsha_df[column] = ""

    st.session_state.questions_df = parsha_df.copy()  # Preload the entire DataFrame

    # Filter questions based on source filters, including the current question
    if st.session_state.question:
        current_question_row = parsha_df[parsha_df['text'] == st.session_state.question]
        filtered_df = parsha_df[parsha_df['source'].apply(lambda x: st.session_state.source_filters.get(x, True))]
        filtered_df = pd.concat([filtered_df, current_question_row]).drop_duplicates().reset_index(drop=True)
    else:
        filtered_df = parsha_df[parsha_df['source'].apply(lambda x: st.session_state.source_filters.get(x, True))]

    st.session_state.questions_df = filtered_df.copy()  # Update the session state with the filtered DataFrame

    if st.session_state.selected_parsha != selected_parsha:
        st.session_state.selected_parsha = selected_parsha
        st.session_state.question = None
        st.session_state.options = None
        st.session_state.correct_answer = None
        st.session_state.answered = False
        st.session_state.selected_option = None

    if st.session_state.question is None:
        result = generate_combined_question()
        if result[0]:
            st.session_state.question, st.session_state.options, st.session_state.correct_answer, st.session_state.question_source, some_value, parsha, text, incorrect_answers, option_details = result

    if st.session_state.question:
        st.write(st.session_state.question)
        st.session_state.selected_option = st.radio("Choose an option:", st.session_state.options, key="radio_option")

        # Display the "Submit Answer" button
        if st.button("Submit Answer"):
            st.session_state.answered = True
            st.session_state.total_questions += 1
            if st.session_state.selected_option == st.session_state.correct_answer:
                st.session_state.correct_answers += 1
                st.success("Correct!")
                save_score(st.session_state.username, "Parsha", 1)
            else:
                st.error(f"Incorrect! The correct answer is: {st.session_state.correct_answer}")
                save_score(st.session_state.username, "Parsha", 0)

        # Display the "Next Question" button if the answer was submitted
        if st.session_state.answered and st.button("Next Question", key="next"):
            st.session_state.question = None
            st.session_state.options = None
            st.session_state.correct_answer = None
            st.session_state.answered = False
            st.session_state.selected_option = None
            st.rerun()
    else:
        st.write("No more questions available.")

    # Display expanders for each option if the question comes from Rashi or Kitzur
    if st.session_state.options and st.session_state.question_source in ["Rashi", "Halachot"]:
        choice_labels = ["Option A", "Option B", "Option C", "Option D"]
        for i, option in enumerate(st.session_state.options):
            with st.expander(f"{choice_labels[i]}"):
                st.write(option)