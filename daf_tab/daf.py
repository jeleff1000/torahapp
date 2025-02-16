import random
import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

def daf_yomi_tab(st, calendar_df, daf_yomi_df, seder_tractates, daf_ranges, date_option):
    st.header("Daf Yomi Quiz")

    # Initialize session state
    if 'selected_seder' not in st.session_state:
        st.session_state.selected_seder = None
    if 'selected_tractate' not in st.session_state:
        st.session_state.selected_tractate = None
    if 'selected_daf' not in st.session_state:
        st.session_state.selected_daf = None
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
    if 'source_filters' not in st.session_state:
        st.session_state.source_filters = {
            'Quotes': True,
            'Rashi': True,
            'Topics': True,
            'Mitzvot': True,
            'Halachot': True
        }

    # Checkbox filters for each source category
    with st.expander("Filter by Source"):
        cols = st.columns(len(st.session_state.source_filters))
        for i, (source, value) in enumerate(st.session_state.source_filters.items()):
            with cols[i]:
                st.session_state.source_filters[source] = st.checkbox(source, value=value)
        if st.button("Apply Filters"):
            st.session_state.question = None  # Reset the current question
            st.rerun()

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

    # Ensure daf_yomi_df is a DataFrame
    if not isinstance(daf_yomi_df, pd.DataFrame):
        st.error("daf_yomi_df is not a DataFrame.")
        return

    # Filter the Daf Yomi DataFrame to only include rows where daf matches the selected Daf
    if 'daf' in daf_yomi_df.columns:
        filtered_daf_yomi_df = daf_yomi_df[daf_yomi_df['daf'] == selected_daf]
    else:
        st.error("The 'daf' column is missing in daf_yomi_df.")
        return

    # Generate the question bank when a Daf is selected, if not already generated
    if not st.session_state.question_bank:
        for _, row in filtered_daf_yomi_df.iterrows():
            correct_answer = row['text']
            incorrect_answers = row['incorrect answers'].split('\n- ')
            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]
            options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
            random.shuffle(options)
            question = f"What is the content of Daf {selected_daf}?"
            st.session_state.question_bank.append((question, options, correct_answer))

        st.session_state.total_questions = len(st.session_state.question_bank)
        random.shuffle(st.session_state.question_bank)  # Shuffle the question bank

    # Check if all questions are answered
    if st.session_state.current_question_index >= st.session_state.total_questions:
        st.write(f"Congratulations! You have answered all the questions for {selected_tractate} {selected_daf}.")
        st.write(f"Score: {st.session_state.correct_answers}/{st.session_state.total_questions}")
        percentage_correct = (st.session_state.correct_answers / st.session_state.total_questions) * 100 if st.session_state.total_questions > 0 else 0
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
            selected_option = st.radio("Select the correct answer:", st.session_state.options, key=f"selected_option_{st.session_state.current_question_index}")

        # Display the "Submit Answer" button
        if st.button("Submit Answer"):
            st.session_state.show_next = True
            if selected_option == st.session_state.correct_answer:
                st.session_state.correct_answers += 1
                st.write("Correct!")
                save_score(st.session_state.username, "Daf Yomi", 1)
            else:
                st.write(f"Incorrect. The correct answer is: {st.session_state.correct_answer}")
                save_score(st.session_state.username, "Daf Yomi", 0)

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