import random

def get_surrounding_parshas(parsha, n=3, torah_dict=None):
    keys = list(torah_dict.keys())
    index = keys.index(parsha)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

def parsha_tab(st, calendar_df, torah_dict, torah_df, date_option, sefer_hachinuch_df, kitzur_related_df):
    st.header("Parsha Quiz")

    # Shuffle data frames
    sefer_hachinuch_df = sefer_hachinuch_df.sample(frac=1).reset_index(drop=True)
    kitzur_related_df = kitzur_related_df.sample(frac=1).reset_index(drop=True)

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
    if 'used_commandments' not in st.session_state:
        st.session_state.used_commandments = set()
    if 'used_kitzur_texts' not in st.session_state:
        st.session_state.used_kitzur_texts = set()
    if 'question_generators' not in st.session_state:
        st.session_state.question_generators = []

    if date_option == "Specific Date":
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == st.session_state.selected_date) & (calendar_df['Title (en)'] == 'Parashat Hashavua')]
        if not filtered_calendar_df.empty:
            selected_parsha = filtered_calendar_df.iloc[0]['Display Value (en)']
            parsha_list = [selected_parsha]
            selected_book = torah_df[torah_df['Parsha'] == selected_parsha]['Book'].values[0]
            book_list = [selected_book]
        else:
            parsha_list = []
            book_list = []
    else:
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Parashat Hashavua'].drop_duplicates(subset=['Display Value (en)'])
        parsha_list = filtered_calendar_df['Display Value (en)'].tolist()
        book_list = list(torah_df['Book'].unique())

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

    def generate_sefer_hachinuch_question(book, parsha):
        filtered_df = sefer_hachinuch_df[(sefer_hachinuch_df['book'] == book) & (sefer_hachinuch_df['parsha'] == parsha)]
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                if row['text'] not in st.session_state.used_commandments:
                    correct_text = row['text']
                    st.session_state.used_commandments.add(correct_text)
                    surrounding_texts = sefer_hachinuch_df[sefer_hachinuch_df['parsha'] != parsha]['text'].tolist()
                    incorrect_texts = random.sample(surrounding_texts, 3)
                    options = incorrect_texts + [correct_text]
                    random.shuffle(options)
                    return f"Which commandment is discussed in {parsha}?", options, correct_text
        return None, None, None

    def generate_kitzur_question(book, parsha):
        filtered_df = kitzur_related_df[(kitzur_related_df['Book'] == book) & (kitzur_related_df['Parsha'] == parsha)]
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                if row['Text'] not in st.session_state.used_kitzur_texts:
                    correct_text = row['Text']
                    st.session_state.used_kitzur_texts.add(correct_text)
                    surrounding_texts = kitzur_related_df[kitzur_related_df['Parsha'] != parsha]['Text'].tolist()
                    incorrect_texts = random.sample(surrounding_texts, 3)
                    options = incorrect_texts + [correct_text]
                    random.shuffle(options)
                    options_with_expanders = [st.expander(f"Option {i+1}").write(option) for i, option in enumerate(options)]
                    return f"According to the Kitzur Shulchan Aruch, which Halacha comes from {parsha}?", options, correct_text
        return None, None, None

    def generate_combined_question(book, parsha):
        if not st.session_state.question_generators:
            st.session_state.question_generators = [
                lambda: generate_sefer_hachinuch_question(book, parsha),
                lambda: generate_kitzur_question(book, parsha),
                lambda: generate_torah_question(parsha)
            ]
            random.shuffle(st.session_state.question_generators)

        for generator in st.session_state.question_generators:
            question, options, correct_topic = generator()
            if question:
                st.session_state.question_generators.remove(generator)
                return question, options, correct_topic
        return None, None, None

    if st.session_state.question_torah is None or st.session_state.selected_parsha != selected_parsha:
        st.session_state.selected_parsha = selected_parsha
        st.session_state.question_torah, st.session_state.options_torah, st.session_state.correct_topic_torah = generate_combined_question(selected_book, selected_parsha)
        st.session_state.answered_torah = False

    st.write(st.session_state.question_torah)
    st.session_state.selected_option_torah = st.radio("Choose an option:", st.session_state.options_torah)

    if st.button("Submit", key="submit_torah"):
        st.session_state.answered_torah = True
        st.session_state.total_questions += 1
        if st.session_state.selected_option_torah == st.session_state.correct_topic_torah:
            st.session_state.correct_answers += 1
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct answer is: {st.session_state.correct_topic_torah}")

    if st.session_state.answered_torah and st.button("Next Question", key="next_torah"):
        st.session_state.question_torah, st.session_state.options_torah, st.session_state.correct_topic_torah = generate_combined_question(selected_book, selected_parsha)
        st.session_state.answered_torah = False
        st.session_state.selected_option_torah = None
        st.rerun()