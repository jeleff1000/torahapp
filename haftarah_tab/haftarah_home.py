import random
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from .haftarah_mapping import shabbat_readings, sorted_holiday_readings, parshiyot

# Define the correct order of Torah books
torah_books_order = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

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

def haftarah_tab(st, calendar_df, date_option, haftarah_path):
    st.title("Haftarah Tab")

    # Initialize session state variables
    if 'question_bank' not in st.session_state:
        st.session_state.question_bank = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 0
    if 'show_next' not in st.session_state:
        st.session_state.show_next = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'options' not in st.session_state:
        st.session_state.options = []
    if 'correct_answer' not in st.session_state:
        st.session_state.correct_answer = None
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'selected_book' not in st.session_state:
        st.session_state.selected_book = None
    if 'selected_parsha' not in st.session_state:
        st.session_state.selected_parsha = None
    if 'source_filters' not in st.session_state:
        st.session_state.source_filters = {
            "Haftarah Topics": True,
            "Rashi": True,
            "Pasukim": True,
            "Kitzur": True
        }

    # Checkbox filters for each source category
    with st.expander("Filter by Source"):
        cols = st.columns(len(st.session_state.source_filters))
        for i, (source, value) in enumerate(st.session_state.source_filters.items()):
            st.session_state.source_filters[source] = cols[i].checkbox(source, value)
        if st.button("Apply Filters"):
            st.rerun()

    # Get the selected date from session state
    selected_date = st.session_state.selected_date

    # Filter the calendar dataframe to get the Haftarah for the selected date and where Title (en) is Haftarah
    haftarah_for_date = calendar_df[
        (calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Haftarah')]

    if not haftarah_for_date.empty:
        haftarah_value = haftarah_for_date.iloc[0]['Display Value (en)']
        st.write(f"**Haftarah for {selected_date}:** {haftarah_value}")

        # Determine if the Haftarah is for a Holiday or Shabbat
        if haftarah_value in sorted_holiday_readings.values():
            option = "Holiday"
        else:
            option = "Shabbat"

        # Set the reading type
        st.selectbox("Select Reading Type", ["Holiday", "Shabbat"], index=["Holiday", "Shabbat"].index(option))

        if option == "Holiday":
            holiday = next((key for key, value in sorted_holiday_readings.items() if value == haftarah_value), None)
            if holiday:
                st.selectbox("Select a Holiday", list(sorted_holiday_readings.keys()),
                             index=list(sorted_holiday_readings.keys()).index(holiday))
                st.write(f"**Selected Holiday:** {holiday}")
                st.write(f"**Haftarah Reading:** {haftarah_value}")

        else:  # Shabbat readings
            selected_book = None
            selected_parsha = None
            for book, parshas in shabbat_readings.items():
                if haftarah_value in [haftarah for haftarah_list in parshas.values() for haftarah in haftarah_list]:
                    selected_book = book
                    selected_parsha = next((key for key, value in parshas.items() if haftarah_value in value), None)
                    break

            if selected_book and selected_parsha:
                col1, col2 = st.columns(2)
                with col1:
                    selected_book = st.selectbox("Select a Torah Book", torah_books_order,
                                                 index=torah_books_order.index(selected_book))
                with col2:
                    selected_parsha = st.selectbox("Select a Parsha", parshiyot[selected_book],
                                                   index=parshiyot[selected_book].index(selected_parsha))
                st.write(f"**Selected Parsha:** {selected_parsha}")
                st.write(f"**Haftarah Reading:** {haftarah_value}")
            else:
                st.write("No matching Shabbat reading found.")

    else:
        # Allow user to select Haftarah manually if not specific to a date
        st.write("No specific Haftarah found for the selected date. Please select manually.")

        option = st.selectbox("Select Reading Type", ["Holiday", "Shabbat"])

        if option == "Holiday":
            holiday = st.selectbox("Select a Holiday", list(sorted_holiday_readings.keys()))
            haftarah_value = sorted_holiday_readings.get(holiday, "No Haftarah Found")
            st.write(f"**Selected Holiday:** {holiday}")
            st.write(f"**Haftarah Reading:** {haftarah_value}")

        else:  # Shabbat readings
            col1, col2 = st.columns(2)
            with col1:
                selected_book = st.selectbox("Select a Torah Book", torah_books_order)
            with col2:
                selected_parsha = st.selectbox("Select a Parsha", parshiyot[selected_book])
            haftarah_value = shabbat_readings[selected_book].get(selected_parsha, "No Haftarah Found")

            st.write(f"**Selected Parsha:** {selected_parsha}")
            st.write(f"**Haftarah Reading:** {haftarah_value}")

    # Ensure haftarah_path is a DataFrame
    if isinstance(haftarah_path, pd.DataFrame):
        # Drop duplicate rows based on 'text' and 'haftarah' columns
        haftarah_path = haftarah_path.drop_duplicates(subset=['text', 'haftarah'])

        # Filter the haftarah_path DataFrame for the selected Haftarah
        filtered_haftarah_df = haftarah_path[haftarah_path['haftarah'] == haftarah_value]

        # Apply source filters to the filtered DataFrame
        filtered_haftarah_df = filtered_haftarah_df[filtered_haftarah_df['source file'].isin([k for k, v in st.session_state.source_filters.items() if v])]

        # Reset and generate the question bank when a new selection is made
        if st.session_state.selected_date != selected_date or st.session_state.selected_option != option or st.session_state.selected_book != selected_book or st.session_state.selected_parsha != selected_parsha:
            st.session_state.selected_date = selected_date
            st.session_state.selected_option = option
            st.session_state.selected_book = selected_book
            st.session_state.selected_parsha = selected_parsha
            st.session_state.question_bank = []
            st.session_state.current_question_index = 0
            st.session_state.correct_answers = 0
            st.session_state.total_questions = 0

            for _, row in filtered_haftarah_df.iterrows():
                correct_answer = row['text']
                incorrect_answers = row['incorrect answers'].split('\n- ')
                incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
                options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
                random.shuffle(options)
                source_file = row['source file']
                if source_file == "Haftarah Topics":
                    question = f"What topic applies to Haftarah {haftarah_value}?"
                elif source_file == "Rashi":
                    question = f"What does Rashi say about Haftarah {haftarah_value}?"
                elif source_file == "Pasukim":
                    question = f"What verse is from Haftarah {haftarah_value}?"
                elif source_file == "Kitzur":
                    question = f"What Halacha comes from Haftarah {haftarah_value}?"
                else:
                    question = f"What is the content of Haftarah {haftarah_value}?"
                st.session_state.question_bank.append((question, options, correct_answer))

            st.session_state.total_questions = len(st.session_state.question_bank)
            random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

        # Check if all questions are answered
        if st.session_state.current_question_index >= st.session_state.total_questions:
            st.write(f"Congratulations! You have answered all the questions for Haftarah {haftarah_value}.")
            st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.total_questions}")
            percentage_correct = (
                st.session_state.correct_answers / st.session_state.total_questions) * 100 if st.session_state.total_questions > 0 else 0
            st.write(f"Percentage Correct: {percentage_correct:.2f}%")
            return

        # Display the first question from the question bank
        if st.session_state.question_bank and st.session_state.current_question is None:
            st.session_state.current_question_index += 1
            st.session_state.current_question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(
                0)

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
                    save_score(st.session_state.username, "Haftarah", 1)
                else:
                    st.write(f"Incorrect. The correct answer is: {st.session_state.correct_answer}")
                    save_score(st.session_state.username, "Haftarah", 0)

            # Display the "Next Question" button if the answer was submitted
            if st.session_state.show_next:
                if st.button("Next Question"):
                    st.session_state.show_next = False
                    st.session_state.current_question = None
                    if st.session_state.question_bank:
                        st.session_state.current_question_index += 1
                        st.session_state.current_question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(
                            0)
                        st.rerun()  # Rerun the app to update the state immediately
                    else:
                        st.write("No more questions available.")

        # Update the progress bar based on questions correct out of questions answered
        progress = st.session_state.correct_answers / st.session_state.current_question_index if st.session_state.current_question_index > 0 else 0
        st.progress(progress)

        # Display the score at the bottom
        st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.current_question_index}")

        # Display the filtered DataFrame at the bottom
        st.write("Filtered Haftarah Data:")
        st.dataframe(filtered_haftarah_df)

    else:
        st.write("Error: haftarah_path is not a DataFrame")