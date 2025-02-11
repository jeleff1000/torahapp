import streamlit as st
import pandas as pd
from .parsha_questions import generate_combined_question

def preprocess_df(df):
    for column in df.columns:
        df[column] = df[column].apply(lambda x: str(x) if not pd.isna(x) else x)
    return df

def clean_values(df):
    for column in df.columns:
        df[column] = df[column].apply(lambda x: x.replace("['", "").replace("']", "") if isinstance(x, str) else x)
    return df

def parsha_tab(st, calendar_df, torah_dict, torah_df, date_option, sefer_hachinuch_df, kitzur_related_df, top_rashis_df, top_verses_df):
    st.header("Parsha Quiz")

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
            'Top Verses': True,
            'Rashi': True,
            'Torah': True,
            'Sefer Hachinuch': True,
            'Kitzur': True
        }

    # Checkbox filters for each source category
    with st.expander("Filter by Source"):
        cols = st.columns(len(st.session_state.source_filters))
        for i, (source, value) in enumerate(st.session_state.source_filters.items()):
            with cols[i]:
                st.session_state.source_filters[source] = st.checkbox(source, value=value)
        if st.button("Apply Filters"):
            st.rerun()

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

    # Filter DataFrames to match the selected parsha
    top_verses_df = top_verses_df[top_verses_df['Parsha'] == selected_parsha]
    top_rashis_df = top_rashis_df[top_rashis_df['Parsha'] == selected_parsha]
    torah_df = torah_df[torah_df['Parsha'] == selected_parsha]
    sefer_hachinuch_df = sefer_hachinuch_df[sefer_hachinuch_df['Parsha'] == selected_parsha]
    kitzur_related_df = kitzur_related_df[kitzur_related_df['Parsha'] == selected_parsha]

    # Preprocess DataFrames to ensure all elements are strings
    top_verses_df = preprocess_df(top_verses_df)
    top_rashis_df = preprocess_df(top_rashis_df)
    torah_df = preprocess_df(torah_df)
    sefer_hachinuch_df = preprocess_df(sefer_hachinuch_df)
    kitzur_related_df = preprocess_df(kitzur_related_df)

    # Clean DataFrames to remove unwanted formatting
    top_verses_df = clean_values(top_verses_df)
    top_rashis_df = clean_values(top_rashis_df)
    torah_df = clean_values(torah_df)
    sefer_hachinuch_df = clean_values(sefer_hachinuch_df)
    kitzur_related_df = clean_values(kitzur_related_df)

    # Add source column to each DataFrame
    top_verses_df['Source'] = 'Top Verses'
    top_rashis_df['Source'] = 'Rashi'
    torah_df['Source'] = 'Torah'
    sefer_hachinuch_df['Source'] = 'Sefer Hachinuch'
    kitzur_related_df['Source'] = 'Kitzur'

    # Ensure each DataFrame has Summary, Summary Incorrect Answers, and Source Ref columns
    for df in [top_verses_df, top_rashis_df, torah_df, sefer_hachinuch_df, kitzur_related_df]:
        if 'Summary' not in df.columns:
            df['Summary'] = ""
        if 'Summary Incorrect Answers' not in df.columns:
            df['Summary Incorrect Answers'] = ""
        if 'Source Ref' not in df.columns:
            df['Source Ref'] = ""

    # Select relevant columns and concatenate DataFrames
    combined_df = pd.concat([
        top_verses_df[['Book', 'Parsha', 'Text', 'Incorrect Answers', 'Source', 'Summary', 'Summary Incorrect Answers', 'Source Ref']],
        top_rashis_df[['Book', 'Parsha', 'Text', 'Incorrect Answers', 'Source', 'Summary', 'Summary Incorrect Answers', 'Source Ref']],
        torah_df[['Book', 'Parsha', 'Text', 'Incorrect Answers', 'Source', 'Summary', 'Summary Incorrect Answers', 'Source Ref']],
        sefer_hachinuch_df[['Book', 'Parsha', 'Text', 'Incorrect Answers', 'Source', 'Summary', 'Summary Incorrect Answers', 'Source Ref']],
        kitzur_related_df[['Book', 'Parsha', 'Text', 'Incorrect Answers', 'Source', 'Summary', 'Summary Incorrect Answers', 'Source Ref']]
    ], ignore_index=True)

    st.session_state.questions_df = combined_df.copy()  # Preload the entire combined DataFrame

    # Filter questions based on source filters
    filtered_df = combined_df[combined_df['Source'].apply(lambda x: st.session_state.source_filters.get(x, True))]
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

        if st.button("Submit", key="submit"):
            st.session_state.answered = True
            st.session_state.total_questions += 1
            if st.session_state.selected_option == st.session_state.correct_answer:
                st.session_state.correct_answers += 1
                st.success("Correct!")
            else:
                st.error(f"Incorrect! The correct answer is: {st.session_state.correct_answer}")

        if st.session_state.answered and st.button("Next Question", key="next"):
            st.session_state.question = None
            st.session_state.options = None
            st.session_state.correct_answer = None
            st.session_state.answered = False
            st.session_state.selected_option = None
            st.rerun()
    else:
        st.write("No more questions available.")

    # Display the combined questions DataFrame at the bottom
    #st.write("### Combined Questions DataFrame")
    #st.dataframe(st.session_state.questions_df)

    # Display expanders for each option if the question comes from Rashi or Kitzur
    if st.session_state.options and st.session_state.question_source in ["Rashi", "Kitzur"]:
        choice_labels = ["Option A", "Option B", "Option C", "Option D"]
        for i, option in enumerate(st.session_state.options):
            with st.expander(f"{choice_labels[i]}"):
                st.write(option)