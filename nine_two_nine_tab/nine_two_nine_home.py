import random
import streamlit as st
import pandas as pd
from datetime import datetime
import re
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

def nine_two_nine_tab(st, calendar_df, nine_two_nine_df, date_option):
    st.header("929 Quiz")

    # Initialize session state
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().strftime('%Y-%m-%d')
    if 'used_rows' not in st.session_state:
        st.session_state.used_rows = set()
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'show_next' not in st.session_state:
        st.session_state.show_next = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'options' not in st.session_state:
        st.session_state.options = []
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'question_bank' not in st.session_state:
        st.session_state.question_bank = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = None
    if 'selected_chapter' not in st.session_state:
        st.session_state.selected_chapter = None
    if 'source_filters' not in st.session_state:
        st.session_state.source_filters = {
            'Rashi': True,
            'Pasukim': True,
            'Tanakh Topics': True,
            'Kitzur': True
        }

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
            st.session_state.current_question = None
            st.session_state.options = []
            st.session_state.correct_answer = None
            st.session_state.show_next = False
            st.rerun()

    # Check if calendar_df is not empty and contains 'Date' column
    if calendar_df.empty or 'Date' not in calendar_df.columns:
        st.error("The 'Date' column is missing in the calendar DataFrame.")
        return

    # Extract the 929 for the given date
    selected_date_str = st.session_state.selected_date

    if date_option == "Specific Date":
        # Reset session state if the date has changed
        if st.session_state.selected_date != selected_date_str:
            st.session_state.selected_date = selected_date_str
            st.session_state.question_bank = []
            st.session_state.correct_answers = 0
            st.session_state.total_questions = 0
            st.session_state.current_question_index = 0
            st.session_state.selected_book = None
            st.session_state.selected_chapter = None
            st.session_state.current_question = None
            st.session_state.options = []
            st.session_state.correct_answer = None

        filtered_calendar_df = calendar_df[
            (calendar_df['Date'] == selected_date_str) & (calendar_df['Title (en)'] == '929')]
        if not filtered_calendar_df.empty:
            display_value = filtered_calendar_df.iloc[0]['Display Value (en)']
            parts = display_value.split()
            selected_book = ' '.join(parts[:-2])
            selected_chapter = re.sub(r'\(.*?\)', '', parts[-2]).strip()
        else:
            st.write(f"No data available for the selected date: {selected_date_str}")
            st.write("Available dates in calendar_df:")
            st.write(calendar_df['Date'].unique())
            return
    else:
        # Extract unique books and chapters from the entire calendar_df
        book_list = calendar_df[calendar_df['Title (en)'] == '929']['Display Value (en)'].apply(
            lambda x: ' '.join(x.split()[:-2])).unique()

        col1, col2 = st.columns(2)
        with col1:
            selected_book = st.selectbox("Select a Book", book_list, key="book_929")

        chapter_list = calendar_df[
            (calendar_df['Title (en)'] == '929') & (calendar_df['Display Value (en)'].str.startswith(selected_book))][
            'Display Value (en)'].apply(lambda x: re.sub(r'\(.*?\)', '', x.split()[-2]).strip()).unique()
        with col2:
            selected_chapter = st.selectbox("Select a Chapter", chapter_list, key="chapter_929")

    # Reset session state if a new book or chapter is selected
    if st.session_state.selected_book != selected_book or st.session_state.selected_chapter != selected_chapter:
        st.session_state.question_bank = []
        st.session_state.correct_answers = 0
        st.session_state.total_questions = 0
        st.session_state.current_question_index = 0
        st.session_state.selected_book = selected_book
        st.session_state.selected_chapter = selected_chapter
        st.session_state.current_question = None
        st.session_state.options = []
        st.session_state.correct_answer = None

    # Ensure nine_two_nine_df is a DataFrame
    if not isinstance(nine_two_nine_df, pd.DataFrame):
        st.error("nine_two_nine_df is not a DataFrame.")
        return

    # Check if 'chapter' column exists in nine_two_nine_df
    if 'chapter' not in nine_two_nine_df.columns:
        st.error("The 'chapter' column is missing in nine_two_nine_df.")
        return

    # Convert selected_chapter to integer if it is numeric
    try:
        selected_chapter_int = int(selected_chapter)
    except ValueError:
        st.error(f"Invalid chapter value: {selected_chapter}")
        return

    # Filter the 929 DataFrame to only include rows where book and chapter match
    filtered_nine_two_nine_df = nine_two_nine_df[
        (nine_two_nine_df['book'] == selected_book) & (nine_two_nine_df['chapter'] == selected_chapter_int)]

    # Apply source filters to the filtered DataFrame
    filtered_nine_two_nine_df = filtered_nine_two_nine_df[filtered_nine_two_nine_df['source file'].isin([k for k, v in st.session_state.source_filters.items() if v])]

    # Remove duplicate rows based on the 'text' column
    filtered_nine_two_nine_df = filtered_nine_two_nine_df.drop_duplicates(subset=['text'])

    # Generate the question bank when a 929 is selected, if not already generated
    if not st.session_state.question_bank:
        for _, row in filtered_nine_two_nine_df.iterrows():
            correct_answer = row['text']
            incorrect_answers = row['incorrect answers'].split('\n- ')
            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
            options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
            random.shuffle(options)
            source = row['source file']  # Assuming there is a 'source file' column in the DataFrame
            if source == "Rashi":
                question = f"What does Rashi say about {selected_book} {selected_chapter}?"
            elif source == "Pasukim":
                question = f"What verse is from {selected_book} {selected_chapter}?"
            elif source == "Tanakh Topics":
                question = f"What topic applies to {selected_book} {selected_chapter}?"
            elif source == "Kitzur":
                question = f"What Halacha comes from {selected_book} {selected_chapter}?"
            else:
                question = f"What is the content of {selected_book} {selected_chapter}?"
            st.session_state.question_bank.append((question, options, correct_answer))

        st.session_state.total_questions = len(st.session_state.question_bank)
        random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

    # Check if all questions are answered
    if st.session_state.current_question_index >= st.session_state.total_questions:
        st.write(f"Congratulations! You have answered all the questions for {selected_book} {selected_chapter}.")
        st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.total_questions}")
        percentage_correct = (
            st.session_state.correct_answers / st.session_state.total_questions) * 100 if st.session_state.total_questions > 0 else 0
        st.write(f"Percentage Correct: {percentage_correct:.2f}%")
        return

    # Display the first question from the question bank
    if st.session_state.question_bank and st.session_state.current_question is None:
        st.session_state.current_question_index += 1
        st.session_state.current_question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(0)

    if st.session_state.current_question:
        st.write(f"Question {st.session_state.current_question_index}/{st.session_state.total_questions}")
        st.write(f"Question: {st.session_state.current_question}")
        if st.session_state.options:
            selected_option = st.radio("Select the correct answer:", st.session_state.options,
                                       key=f"selected_option_{st.session_state.current_question_index}")

        # Display the "Submit Answer" button
        if st.button("Submit Answer"):
            st.session_state.show_next = True
            if selected_option == st.session_state.correct_answer:
                st.session_state.correct_answers += 1
                st.write("Correct!")
                save_score(st.session_state.username, "929", 1)
            else:
                st.write(f"Incorrect. The correct answer is: {st.session_state.correct_answer}")
                save_score(st.session_state.username, "929", 0)

        # Display the "Next Question" button if the answer was submitted
        if st.session_state.show_next:
            if st.button("Next Question"):
                st.session_state.show_next = False
                st.session_state.current_question = None
                if st.session_state.question_bank:
                    st.session_state.current_question_index += 1
                    st.session_state.current_question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(0)
                    st.rerun()  # Rerun the app to update the state immediately
                else:
                    st.write("No more questions available.")

    # Update the progress bar based on questions correct out of questions answered
    progress = st.session_state.correct_answers / st.session_state.current_question_index if st.session_state.current_question_index > 0 else 0
    st.progress(progress)

    # Display the score at the bottom
    st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.current_question_index}")

    # Display the filtered 929 DataFrame
    st.dataframe(filtered_nine_two_nine_df)