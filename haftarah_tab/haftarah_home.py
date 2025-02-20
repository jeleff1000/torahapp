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
    if 'selected_shabbat' not in st.session_state:
        st.session_state.selected_shabbat = None
    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = None
    if 'source_filters' not in st.session_state:
        st.session_state.source_filters = {}

    # Initialize selected_parsha and holiday to None
    selected_parsha = None
    holiday = None
    option = None  # Initialize option to None

    # Get the selected date from session state
    selected_date = st.session_state.selected_date

    if date_option != "All Dates":
        # Filter the calendar dataframe to get the Haftarah for the selected date and where Title (en) is Haftarah
        haftarah_for_date = calendar_df[
            (calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Haftarah')]

        if not haftarah_for_date.empty:
            haftarah_value = haftarah_for_date.iloc[0]['Display Value (en)']
            st.write(f"**Haftarah for {selected_date}:** {haftarah_value}")

            # Filter the haftarah_path DataFrame to match the haftarah value
            filtered_haftarah_path = haftarah_path[haftarah_path['haftarah'] == haftarah_value]

            if not filtered_haftarah_path.empty:
                selected_shabbat = filtered_haftarah_path.iloc[0]['shabbat']
                selected_event = filtered_haftarah_path.iloc[0]['event']

                st.write(f"**Selected Shabbat:** {selected_shabbat}")
                st.write(f"**Selected Event:** {selected_event}")

                # Add an expander with checkboxes to filter based on the source file column
                with st.expander("Source Files"):
                    source_files = filtered_haftarah_path['source file'].unique()
                    cols = st.columns(len(source_files) + 1)
                    for i, source in enumerate(source_files):
                        if source not in st.session_state.source_filters:
                            st.session_state.source_filters[source] = True
                        st.session_state.source_filters[source] = cols[i].checkbox(f"Include {source}", st.session_state.source_filters[source])
                    if cols[-1].button("Apply", key="apply_button"):
                        st.session_state.question_bank = []
                        st.session_state.current_question_index = 0
                        st.session_state.correct_answers = 0
                        st.session_state.total_questions = 0
                        st.session_state.current_question = None
                        st.session_state.options = []
                        st.session_state.correct_answer = None

                        # Apply source filters to the filtered DataFrame
                        filtered_haftarah_path = filtered_haftarah_path[filtered_haftarah_path['source file'].isin([k for k, v in st.session_state.source_filters.items() if v])]

                        # Generate the question bank based on the filtered DataFrame
                        for _, row in filtered_haftarah_path.iterrows():
                            correct_answer = row['text']
                            incorrect_answers = row['incorrect answers'].split('\n- ')
                            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
                            options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
                            random.shuffle(options)
                            if row['source file'] == "Haftarah Topics":
                                question = f"What topic applies to the Haftarah for {selected_event}?"
                            elif row['source file'] == "Rashi":
                                question = f"What does Rashi say about the Haftarah for {selected_event}?"
                            elif row['source file'] == "Pasukim":
                                question = f"What verse comes from the Haftarah for {selected_event}?"
                            else:
                                question = f"What is the content of Haftarah {row['haftarah']}?"
                            st.session_state.question_bank.append((question, options, correct_answer))

                        st.session_state.total_questions = len(st.session_state.question_bank)
                        random.shuffle(st.session_state.question_bank)  # Shuffle the question bank
                        st.rerun()

                # Reset and generate the question bank when a new selection is made
                if (st.session_state.selected_date != selected_date or
                        st.session_state.selected_option != option or
                        st.session_state.selected_shabbat != selected_shabbat or
                        st.session_state.selected_event != selected_event):

                    st.session_state.selected_date = selected_date
                    st.session_state.selected_option = option
                    st.session_state.selected_shabbat = selected_shabbat
                    st.session_state.selected_event = selected_event
                    st.session_state.question_bank = []
                    st.session_state.current_question_index = 0
                    st.session_state.correct_answers = 0
                    st.session_state.total_questions = 0

                    for _, row in filtered_haftarah_path.iterrows():
                        correct_answer = row['text']
                        incorrect_answers = row['incorrect answers'].split('\n- ')
                        incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
                        options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
                        random.shuffle(options)
                        if row['source file'] == "Haftarah Topics":
                            question = f"What topic applies to the Haftarah for {selected_event}?"
                        elif row['source file'] == "Rashi":
                            question = f"What does Rashi say about the Haftarah for {selected_event}?"
                        elif row['source file'] == "Pasukim":
                            question = f"What verse comes from the Haftarah for {selected_event}?"
                        else:
                            question = f"What is the content of Haftarah {row['haftarah']}?"
                        st.session_state.question_bank.append((question, options, correct_answer))

                    st.session_state.total_questions = len(st.session_state.question_bank)
                    random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

                # Check if all questions are answered
                if st.session_state.current_question_index >= st.session_state.total_questions:
                    st.write(f"Congratulations! You have answered all the questions.")
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
                    if st.button("Submit Answer", key=f"submit_button_{st.session_state.current_question_index}"):
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
                        if st.button("Next Question", key=f"next_button_{st.session_state.current_question_index}"):
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

                # Display the filtered DataFrame at the bottom
                st.write("Haftarah Data:")
                st.dataframe(filtered_haftarah_path)

            else:
                st.write("No matching Haftarah found in the haftarah_path DataFrame.")

        else:
            st.write("No specific Haftarah found for the selected date.")

    # Ensure haftarah_path is a DataFrame
    if isinstance(haftarah_path, pd.DataFrame):
        # Drop duplicate rows based on 'text' and 'haftarah' columns
        haftarah_path = haftarah_path.drop_duplicates(subset=['text', 'haftarah'])

        if date_option == "All Dates":
            # Add a selectbox to filter the shabbat column
            cols = st.columns(2)
            shabbat_options = haftarah_path['shabbat'].unique()
            selected_shabbat = cols[0].selectbox("Select Reading Type", shabbat_options)

            # Filter the DataFrame based on the selected shabbat
            filtered_haftarah_path = haftarah_path[haftarah_path['shabbat'] == selected_shabbat]

            # Add a selectbox to filter the event column based on the filtered DataFrame
            event_options = filtered_haftarah_path['event'].unique()
            selected_event = cols[1].selectbox("Select Event", event_options)

            # Further filter the DataFrame based on the selected event
            filtered_haftarah_path = haftarah_path[
                (haftarah_path['shabbat'] == selected_shabbat) & (haftarah_path['event'] == selected_event)]

            # Add an expander with checkboxes to filter based on the source file column
            with st.expander("Source Files"):
                source_files = filtered_haftarah_path['source file'].unique()
                cols = st.columns(len(source_files) + 1)
                for i, source in enumerate(source_files):
                    if source not in st.session_state.source_filters:
                        st.session_state.source_filters[source] = True
                    st.session_state.source_filters[source] = cols[i].checkbox(f"Include {source}", st.session_state.source_filters[source])
                if cols[-1].button("Apply", key="apply_button_2"):
                    st.session_state.question_bank = []
                    st.session_state.current_question_index = 0
                    st.session_state.correct_answers = 0
                    st.session_state.total_questions = 0
                    st.session_state.current_question = None
                    st.session_state.options = []
                    st.session_state.correct_answer = None

                    # Apply source filters to the filtered DataFrame
                    filtered_haftarah_path = filtered_haftarah_path[filtered_haftarah_path['source file'].isin([k for k, v in st.session_state.source_filters.items() if v])]

                    # Generate the question bank based on the filtered DataFrame
                    for _, row in filtered_haftarah_path.iterrows():
                        correct_answer = row['text']
                        incorrect_answers = row['incorrect answers'].split('\n- ')
                        incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
                        options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
                        random.shuffle(options)
                        if row['source file'] == "Haftarah Topics":
                            question = f"What topic applies to the Haftarah for {selected_event}?"
                        elif row['source file'] == "Rashi":
                            question = f"What does Rashi say about the Haftarah for {selected_event}?"
                        elif row['source file'] == "Pasukim":
                            question = f"What verse comes from the Haftarah for {selected_event}?"
                        else:
                            question = f"What is the content of Haftarah {row['haftarah']}?"
                        st.session_state.question_bank.append((question, options, correct_answer))

                    st.session_state.total_questions = len(st.session_state.question_bank)
                    random.shuffle(st.session_state.question_bank)  # Shuffle the question bank
                    st.rerun()

            # Reset and generate the question bank when a new selection is made
            if (st.session_state.selected_date != selected_date or
                    st.session_state.selected_option != option or
                    st.session_state.selected_shabbat != selected_shabbat or
                    st.session_state.selected_event != selected_event):

                st.session_state.selected_date = selected_date
                st.session_state.selected_option = option
                st.session_state.selected_shabbat = selected_shabbat
                st.session_state.selected_event = selected_event
                st.session_state.question_bank = []
                st.session_state.current_question_index = 0
                st.session_state.correct_answers = 0
                st.session_state.total_questions = 0

                for _, row in filtered_haftarah_path.iterrows():
                    correct_answer = row['text']
                    incorrect_answers = row['incorrect answers'].split('\n- ')
                    incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
                    options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
                    random.shuffle(options)
                    if row['source file'] == "Haftarah Topics":
                        question = f"What topic applies to the Haftarah for {selected_event}?"
                    elif row['source file'] == "Rashi":
                        question = f"What does Rashi say about the Haftarah for {selected_event}?"
                    elif row['source file'] == "Pasukim":
                        question = f"What verse comes from the Haftarah for {selected_event}?"
                    else:
                        question = f"What is the content of Haftarah {row['haftarah']}?"
                    st.session_state.question_bank.append((question, options, correct_answer))

                st.session_state.total_questions = len(st.session_state.question_bank)
                random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

            # Check if all questions are answered
            if st.session_state.current_question_index >= st.session_state.total_questions:
                st.write(f"Congratulations! You have answered all the questions.")
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
                if st.button("Submit Answer", key=f"submit_button_{st.session_state.current_question_index}"):
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
                        st.session_state.current_question, st.session_state.options, st.session_state.correct_answer = st.session_state.question_bank.pop(0)
                        st.rerun()  # Rerun the app to update the state immediately
                    else:
                        st.write("No more questions available.")
        # Update the progress bar based on questions correct out of questions answered
        progress = st.session_state.correct_answers / st.session_state.current_question_index if st.session_state.current_question_index > 0 else 0
        st.progress(progress)

        # Display the score at the bottom
        st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.current_question_index}")

        # Display the filtered DataFrame at the bottom
        st.write("Haftarah Data:")
        st.dataframe(filtered_haftarah_path)

    else:
        st.write("Error: haftarah_path is not a DataFrame")