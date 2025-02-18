import streamlit as st
import pandas as pd
import random
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

    # Verify the file path and check if the file exists
    if not os.path.exists(parsha_path):
        st.error(f"Parsha file not found at path: {parsha_path}")
        return

    # Load the parsha DataFrame
    try:
        parsha_df = pd.read_parquet(parsha_path)
    except Exception as e:
        st.error(f"Error reading Parsha file: {e}")
        return

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
            'Hachinuch': True,
            'Kitzur': True,
            'Pasukim': True,
            'Rashi': True,
            'Shulchan Arukh': True,
            'Topics': True
        }
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'question_bank' not in st.session_state:
        st.session_state.question_bank = []
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = None
    if 'question_source' not in st.session_state:
        st.session_state.question_source = None

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
        st.session_state.current_question_index = 0
        st.session_state.question_bank = []
        st.session_state.selected_book = None

    if date_option == "All Dates":
        # Allow user to select any book and parsha
        books = parsha_df['book'].unique()
        parshas = parsha_df[parsha_df['book'] == books[0]]['parsha'].unique()
        cols = st.columns(2)
        with cols[0]:
            selected_book = st.selectbox("Select a Book", books)
        with cols[1]:
            selected_parsha = st.selectbox("Select a Parsha", parshas)

        # Reset question bank if a new book or parsha is selected
        if st.session_state.selected_book != selected_book or st.session_state.selected_parsha != selected_parsha:
            st.session_state.question_bank = []
            st.session_state.correct_answers = 0
            st.session_state.total_questions = 0
            st.session_state.current_question_index = 0
            st.session_state.selected_book = selected_book
            st.session_state.selected_parsha = selected_parsha
            st.session_state.question = None
            st.session_state.options = None
            st.session_state.correct_answer = None
            st.session_state.answered = False
            st.session_state.selected_option = None
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

        # Display the selected book and parsha in select boxes with only one option
        cols = st.columns(2)
        with cols[0]:
            st.selectbox("Select a Book", [selected_book], index=0)
        with cols[1]:
            st.selectbox("Select a Parsha", [selected_parsha], index=0)

    # Checkbox filters for each source category
    with st.expander("Filter by Source"):
        cols = st.columns(len(st.session_state.source_filters))
        for i, (source, value) in enumerate(st.session_state.source_filters.items()):
            with cols[i]:
                st.session_state.source_filters[source] = st.checkbox(source, value=value)
        if st.button("Apply Filters"):
            st.session_state.question_bank = []  # Reset the question bank
            st.session_state.correct_answers = 0
            st.session_state.total_questions = 0
            st.session_state.current_question_index = 0
            st.session_state.question = None
            st.session_state.options = None
            st.session_state.correct_answer = None
            st.session_state.answered = False
            st.session_state.selected_option = None
            st.rerun()

    # Filter DataFrame to match the selected parsha and source filters
    parsha_df = parsha_df[(parsha_df['parsha'] == selected_parsha) & (parsha_df['source file'].isin([k for k, v in st.session_state.source_filters.items() if v]))]

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

    # Generate the question bank if not already generated
    if not st.session_state.question_bank:
        for _, row in parsha_df.iterrows():
            correct_answer = row['text']
            incorrect_answers = row['incorrect answers'].split('\n- ')
            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
            options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
            random.shuffle(options)
            source = row['source file']
            if source == "Quotes":
                question = f"Which text is from {row['parsha']}?"
            elif source == "Rashi":
                question = f"What does Rashi say about {row['parsha']}?"
            elif source == "Topics":
                question = f"What topic applies to {row['parsha']}?"
            elif source == "Hachinuch":
                question = f"Which Mitzvah is from {row['parsha']}?"
            elif source == "Shulchan Arukh":
                question = f"Which Halacha comes from {row['parsha']}?"
            elif source == "Pasukim":
                question = f"What verse is from {row['parsha']}?"
            elif source == "Tanakh Topics":
                question = f"What topic applies to {row['parsha']}?"
            elif source == "Kitzur":
                question = f"What Halacha comes from {row['parsha']}?"
            else:
                question = f"Which text is from {row['parsha']} according to {source}?"
            st.session_state.question_bank.append((question, options, correct_answer))
            st.session_state.question_source = source

        st.session_state.total_questions = len(st.session_state.question_bank)
        random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

    # Check if all questions are answered
    if st.session_state.current_question_index >= st.session_state.total_questions:
        st.write(f"Congratulations! You have answered all the questions for {selected_parsha}.")
        st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.total_questions}")
        percentage_correct = (
            st.session_state.correct_answers / st.session_state.total_questions) * 100 if st.session_state.total_questions > 0 else 0
        st.write(f"Percentage Correct: {percentage_correct:.2f}%")
        return

    # Display the first question from the question bank
    if st.session_state.question_bank and st.session_state.question is None:
        st.session_state.current_question_index += 1
        st.session_state.question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(0)

    if st.session_state.question:
        st.write(f"Question {st.session_state.current_question_index}/{st.session_state.total_questions}")
        st.write(st.session_state.question)
        st.session_state.selected_option = st.radio("Choose an option:", st.session_state.options, key="radio_option")

        # Display the "Submit Answer" button
        if st.button("Submit Answer"):
            st.session_state.answered = True
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

    # Update the progress bar based on questions correct out of questions answered
    progress = st.session_state.correct_answers / st.session_state.current_question_index if st.session_state.current_question_index > 0 else 0
    st.progress(progress)

    # Display the score at the bottom
    st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.current_question_index}")

    # Display expanders for each option if the question comes from Rashi or Kitzur
    if st.session_state.options and st.session_state.question_source in ["Rashi", "Halachot"]:
        choice_labels = ["Option A", "Option B", "Option C", "Option D"]
        for i, option in enumerate(st.session_state.options):
            with st.expander(f"{choice_labels[i]}"):
                st.write(option)