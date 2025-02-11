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
    if selected_row['Summary']:
        correct_answer = selected_row['Summary']
    else:
        correct_answer = selected_row['Text']

    if selected_row['Summary Incorrect Answers']:
        incorrect_answers = selected_row['Summary Incorrect Answers'].split('\n- ')
    else:
        incorrect_answers = selected_row['Incorrect Answers'].split('\n- ')

    # Ensure incorrect answers are stripped of any leading/trailing whitespace
    incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]

    # Select three incorrect answers
    options = random.sample(incorrect_answers, min(3, len(incorrect_answers))) + [correct_answer]
    random.shuffle(options)

    # Formulate the question based on the Source column
    source = selected_row['Source']
    parsha = selected_row['Parsha']
    if source == "Quotes":
        question = f"Which text is from {parsha}?"
    elif source == "Rashi":
        question = f"Which Rashi applies to Parshat {parsha}? (See below for full text)"
    elif source == "Topics":
        question = f"Which topic is applies to Parshat {parsha}?"
    elif source == "Mitzvot":
        question = f"Which commandment is from Parshat {parsha}?"
    elif source == "Halachot":
        question = f"Which Halacha comes from Parshat {parsha}? (See below for full text)"
    else:
        question = f"Which text is from {parsha} according to {source}?"

    # Mark the selected row as used
    st.session_state.used_questions.add(selected_row.name)

    # Create a dictionary to store the corresponding Text and Incorrect Answers for each option
    option_details = {}
    for option in options:
        if option == correct_answer:
            option_details[option] = (selected_row['Text'], selected_row['Incorrect Answers'])
        else:
            # Find the row that contains this incorrect answer in the Summary Incorrect Answers
            matching_row = combined_df[combined_df['Summary Incorrect Answers'].str.contains(option, na=False)]
            if not matching_row.empty:
                incorrect_bullet = next((ans for ans in matching_row.iloc[0]['Summary Incorrect Answers'].split('\n- ') if ans.strip() == option), "")
                if incorrect_bullet:
                    incorrect_index = matching_row.iloc[0]['Summary Incorrect Answers'].split('\n- ').index(incorrect_bullet)
                    incorrect_answer_bullet = matching_row.iloc[0]['Incorrect Answers'].split('\n- ')[incorrect_index]
                    option_details[option] = (incorrect_answer_bullet, matching_row.iloc[0]['Incorrect Answers'])
                else:
                    option_details[option] = ("", "")
            else:
                option_details[option] = ("", "")

    return question, options, correct_answer, selected_row['Source'], None, selected_row['Parsha'], selected_row['Text'], incorrect_answers, option_details