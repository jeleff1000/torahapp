import random

def get_surrounding_parshas(parsha, n=3, torah_dict=None):
    keys = list(torah_dict.keys())
    index = keys.index(parsha)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

def parsha_tab(st, calendar_df, torah_dict, torah_df, date_option):
    st.header("Parsha Quiz")

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

    if date_option == "Specific Date":
        # Filter calendar data for the selected date and title "Parashat Hashavua"
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == st.session_state.selected_date) & (calendar_df['Title (en)'] == 'Parashat Hashavua')]
        # Get the parsha for the selected date
        if not filtered_calendar_df.empty:
            selected_parsha = filtered_calendar_df.iloc[0]['Display Value (en)']
            parsha_list = [selected_parsha]
            selected_book = torah_df[torah_df['Parsha'] == selected_parsha]['Book'].values[0]
            book_list = [selected_book]
        else:
            parsha_list = []
            book_list = []
    else:
        # Filter calendar data for all dates and title "Parashat Hashavua"
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Parashat Hashavua'].drop_duplicates(subset=['Display Value (en)'])
        parsha_list = filtered_calendar_df['Display Value (en)'].tolist()
        book_list = list(torah_df['Book'].unique())

    # Dropdowns for selecting Book and Parsha in one row
    col1, col2 = st.columns(2)
    with col1:
        selected_book = st.selectbox("Select a Book", book_list, index=0, key="book_torah")
    with col2:
        if date_option == "Specific Date":
            parsha_list = [selected_parsha] if selected_book else []
        else:
            parsha_list = torah_df[torah_df['Book'] == selected_book]['Parsha'].tolist() if selected_book else []
        selected_parsha = st.selectbox("Select a Parsha", parsha_list, index=0, key="parsha_torah")

    def generate_torah_question(parsha):
        correct_topics = torah_dict[parsha]
        correct_topic = random.choice(correct_topics)
        surrounding_parshas = get_surrounding_parshas(parsha, torah_dict=torah_dict)
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
        st.session_state.total_questions += 1
        if st.session_state.selected_option_torah == st.session_state.correct_topic_torah:
            st.session_state.correct_answers += 1
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct answer is: {st.session_state.correct_topic_torah}")

    # Next question button
    if st.session_state.answered_torah and st.button("Next Question", key="next_torah"):
        st.session_state.question_torah, st.session_state.options_torah, st.session_state.correct_topic_torah = generate_torah_question(selected_parsha)
        st.session_state.answered_torah = False
        st.session_state.selected_option_torah = None
        st.rerun()