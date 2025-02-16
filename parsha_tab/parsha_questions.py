import random
import streamlit as st
import numpy as np

def generate_combined_question():
    combined_df = st.session_state.questions_df
    if combined_df.empty:
        return None, None, None, None, None, None, None, None, None

    # Initialize used questions set if not already done
    if 'used_questions' not in st.session_state:
        st.session_state.used_questions = set()

    # Select a random row from the combined DataFrame that has not been used
    unused_rows = combined_df[~combined_df.index.isin(st.session_state.used_questions)]
    if unused_rows.empty:
        return None, None, None, None, None, None, None, None, None

    selected_row = unused_rows.sample(n=1).iloc[0]

    # Determine the correct answer and incorrect answers
    correct_answer = selected_row['text']
    incorrect_answers = selected_row['incorrect answers'].split('\n- ')

    # Ensure incorrect answers are stripped of any leading/trailing whitespace
    incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]

    # Select three incorrect answers
    options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
    random.shuffle(options)

    # Formulate the question based on the source column
    source = selected_row['source']
    parsha = selected_row['parsha']
    if source == "Quotes":
        question = f"Which text is from {parsha}?"
    elif source == "Rashi":
        question = f"Which Rashi applies to Parshat {parsha}? (See below for full text)"
    elif source == "Topics":
        question = f"Which topic applies to Parshat {parsha}?"
    elif source == "Mitzvot":
        question = f"Which commandment is from Parshat {parsha}?"
    elif source == "Halachot":
        question = f"Which Halacha comes from Parshat {parsha}? (See below for full text)"
    else:
        question = f"Which text is from {parsha} according to {source}?"

    # Mark the selected row as used
    st.session_state.used_questions.add(selected_row.name)

    # Create a dictionary to store the corresponding text and incorrect answers for each option
    option_details = {}
    for option in options:
        if option == correct_answer:
            option_details[option] = (selected_row['text'], selected_row['incorrect answers'])
        else:
            option_details[option] = ("", "")

    return question, options, correct_answer, selected_row['source'], None, selected_row['parsha'], selected_row['text'], incorrect_answers, option_details