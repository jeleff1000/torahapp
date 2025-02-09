import pandas as pd
import random
import streamlit as st

def generate_topic_question(torah_df, book, parsha):
    filtered_df = torah_df[(torah_df['Book'] == book) & (torah_df['Parsha'] == parsha)]
    if not filtered_df.empty:
        topics = filtered_df.iloc[0]['Topics']
        neighboring_topics = filtered_df.iloc[0]['Neighboring Topics']
        if isinstance(topics, str):
            topics = topics.split(', ')
        if isinstance(neighboring_topics, str):
            neighboring_topics = neighboring_topics.split(', ')
        if topics:
            correct_topic = random.choice(topics)
            incorrect_topics = random.sample(neighboring_topics, min(3, len(neighboring_topics)))

            options = incorrect_topics + [correct_topic]
            random.shuffle(options)
            return f"Which topic is discussed in {parsha}?", options, correct_topic, 'topics'
    return None, None, None, None

def generate_rashi_question(top_rashis_df, parsha):
    filtered_df = top_rashis_df[top_rashis_df['Parsha'] == parsha]
    if not filtered_df.empty:
        correct_text_full = filtered_df.iloc[0]['Clean Text']
        correct_text_short = '. '.join(correct_text_full.split('. ')[:3]) + '.'  # Get the first three sentences
        incorrect_answers = filtered_df.iloc[0]['Incorrect Answers']

        if isinstance(incorrect_answers, str):
            incorrect_answers = incorrect_answers.split('\n- ')
            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]

        incorrect_texts_short = ['. '.join(ans.split('. ')[:3]) + '.' for ans in incorrect_answers]
        incorrect_texts_full = incorrect_answers
        incorrect_options = random.sample(incorrect_texts_short, min(3, len(incorrect_texts_short)))
        options_short = incorrect_options + [correct_text_short]
        options_full = incorrect_texts_full + [correct_text_full]
        combined_options = list(zip(options_short, options_full))
        random.shuffle(combined_options)
        options_short, options_full = zip(*combined_options)

        return f"What is the correct Rashi interpretation for {parsha}?", options_short, correct_text_short, options_full, 'rashi'
    return None, None, None, None, None

def generate_top_verses_question(top_verses_df, parsha):
    filtered_df = top_verses_df[top_verses_df['Parsha'] == parsha]
    if not filtered_df.empty:
        correct_text = filtered_df.iloc[0]['Text']
        incorrect_answers = filtered_df.iloc[0]['Incorrect Answers']

        if isinstance(incorrect_answers, str):
            incorrect_answers = incorrect_answers.split('\n- ')
            incorrect_answers = [ans.strip() for ans in incorrect_answers if ans.strip()]

        incorrect_texts = random.sample(incorrect_answers, min(3, len(incorrect_answers)))
        options = incorrect_texts + [correct_text]
        random.shuffle(options)
        return f"Which verse is from {parsha}?", options, correct_text, 'top_verses'
    return None, None, None, None

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
    if 'used_commandments' not in st.session_state:
        st.session_state.used_commandments = set()
    if 'used_kitzur_texts' not in st.session_state:
        st.session_state.used_kitzur_texts = set()
    if 'question_generators' not in st.session_state:
        st.session_state.question_generators = {}
    if 'used_questions' not in st.session_state:
        st.session_state.used_questions = set()
    if 'used_correct_answers' not in st.session_state:
        st.session_state.used_correct_answers = {
            'sefer_hachinuch': set(),
            'kitzur': set(),
            'topics': set(),
            'rashi': set(),
            'top_verses': set()
        }
    if 'allowed_dfs' not in st.session_state:
        st.session_state.allowed_dfs = {
            'sefer_hachinuch': True,
            'kitzur': True,
            'topics': True,
            'rashi': True,
            'top_verses': True
        }

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
        selected_book = st.selectbox("Select a Book", book_list, index=0, key="book")
    with col2:
        if date_option == "Specific Date":
            parsha_list = [selected_parsha] if selected_book else []
        else:
            parsha_list = torah_df[torah_df['Book'] == selected_book]['Parsha'].tolist() if selected_book else []
        selected_parsha = st.selectbox("Select a Parsha", parsha_list, index=0, key="parsha")

    with st.expander("Select DataFrames for Questions"):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.session_state.allowed_dfs['sefer_hachinuch'] = st.checkbox("Sefer Hachinuch", value=st.session_state.allowed_dfs['sefer_hachinuch'])
        with col2:
            st.session_state.allowed_dfs['kitzur'] = st.checkbox("Kitzur", value=st.session_state.allowed_dfs['kitzur'])
        with col3:
            st.session_state.allowed_dfs['topics'] = st.checkbox("Topics", value=st.session_state.allowed_dfs['topics'])
        with col4:
            st.session_state.allowed_dfs['rashi'] = st.checkbox("Rashi", value=st.session_state.allowed_dfs['rashi'])
        with col5:
            st.session_state.allowed_dfs['top_verses'] = st.checkbox("Top Verses", value=st.session_state.allowed_dfs['top_verses'])

    def generate_sefer_hachinuch_question(book, parsha):
        sefer_hachinuch_df_shuffled = sefer_hachinuch_df.sample(frac=1).reset_index(drop=True)
        filtered_df = sefer_hachinuch_df_shuffled[(sefer_hachinuch_df_shuffled['book'] == book) & (sefer_hachinuch_df_shuffled['parsha'] == parsha)]
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                if row['text'] not in st.session_state.used_commandments and row['text'] not in st.session_state.used_correct_answers['sefer_hachinuch']:
                    correct_text = row['text']
                    st.session_state.used_commandments.add(correct_text)
                    st.session_state.used_correct_answers['sefer_hachinuch'].add(correct_text)
                    incorrect_answers = row['Incorrect Answers'].split('\n')
                    incorrect_texts = random.sample(incorrect_answers, min(3, len(incorrect_answers)))
                    options = incorrect_texts + [correct_text]
                    random.shuffle(options)
                    return f"Which commandment is discussed in {parsha}?", options, correct_text, 'sefer_hachinuch'
        return None, None, None, None

    def generate_kitzur_question(book, parsha):
        kitzur_related_df_shuffled = kitzur_related_df.sample(frac=1).reset_index(drop=True)
        filtered_df = kitzur_related_df_shuffled[(kitzur_related_df_shuffled['Book'] == book) & (kitzur_related_df_shuffled['Parsha'] == parsha)]
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                if row['Text'] not in st.session_state.used_kitzur_texts and row['Text'] not in st.session_state.used_correct_answers['kitzur']:
                    correct_text_short = '. '.join(row['Text'].split('. ')[:2]) + '.'  # Get the first two sentences
                    correct_text_full = row['Text']  # Get the full text
                    reference = row['Source Ref']  # Get the reference
                    st.session_state.used_kitzur_texts.add(row['Text'])
                    st.session_state.used_correct_answers['kitzur'].add(row['Text'])
                    surrounding_texts_short = ['. '.join(text.split('. ')[:2]) + '.' for text in kitzur_related_df_shuffled[kitzur_related_df_shuffled['Parsha'] != parsha]['Text'].tolist()]
                    surrounding_texts_full = [text for text in kitzur_related_df_shuffled[kitzur_related_df_shuffled['Parsha'] != parsha]['Text'].tolist()]
                    references = [row['Source Ref'] for _, row in kitzur_related_df_shuffled[kitzur_related_df_shuffled['Parsha'] != parsha].iterrows()]
                    incorrect_texts_short = random.sample(surrounding_texts_short, min(3, len(surrounding_texts_short)))
                    incorrect_texts_full = random.sample(surrounding_texts_full, min(3, len(surrounding_texts_full)))
                    incorrect_references = random.sample(references, min(3, len(references)))
                    options_short = incorrect_texts_short + [correct_text_short]
                    options_full = incorrect_texts_full + [correct_text_full]
                    references = incorrect_references + [reference]
                    combined_options = list(zip(options_short, options_full, references))
                    random.shuffle(combined_options)
                    options_short, options_full, references = zip(*combined_options)
                    return f"According to the Kitzur Shulchan Aruch, which Halacha comes from {parsha}? (See expanders below for full text)", options_short, correct_text_short, options_full, references, 'kitzur'
        return None, None, None, None, None, None

    def generate_combined_question(book, parsha):
        if not st.session_state.question_generators:
            st.session_state.question_generators = {
                'sefer_hachinuch': lambda: generate_sefer_hachinuch_question(book, parsha),
                'kitzur': lambda: generate_kitzur_question(book, parsha),
                'topics': lambda: generate_topic_question(torah_df, book, parsha),
                'rashi': lambda: generate_rashi_question(top_rashis_df, parsha),
                'top_verses': lambda: generate_top_verses_question(top_verses_df, parsha)
            }

        available_generators = [key for key in st.session_state.question_generators.keys() if st.session_state.allowed_dfs[key]]
        while available_generators:
            generator_key = random.choice(available_generators)
            result = st.session_state.question_generators[generator_key]()
            if result[0] and result[2] not in st.session_state.used_correct_answers[generator_key]:  # Check if the question is not None and not used
                st.session_state.used_correct_answers[generator_key].add(result[2])
                return result
            else:
                available_generators.remove(generator_key)  # Remove exhausted generator
        return None, None, None, None, None, None

    if st.session_state.selected_parsha != selected_parsha:
        st.session_state.selected_parsha = selected_parsha
        st.session_state.question = None
        st.session_state.options = None
        st.session_state.correct_answer = None
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.session_state.question_generators = {}

    if st.session_state.question is None or not st.session_state.allowed_dfs.get(st.session_state.question_source, False):
        result = generate_combined_question(selected_book, selected_parsha)
        if result[0] is None:
            st.write("No more questions available.")
            return
        st.session_state.question = result[0]
        st.session_state.options = result[1]
        st.session_state.correct_answer = result[2]
        st.session_state.full_texts = result[3] if len(result) > 3 else None
        st.session_state.references = result[4] if len(result) > 4 else None
        st.session_state.question_source = result[5] if len(result) > 5 else None
        st.session_state.answered = False

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
        result = generate_combined_question(selected_book, selected_parsha)
        if result[0] is None:
            st.write("No more questions available.")
            return
        st.session_state.question = result[0]
        st.session_state.options = result[1]
        st.session_state.correct_answer = result[2]
        st.session_state.full_texts = result[3] if len(result) > 3 else None
        st.session_state.references = result[4] if len(result) > 4 else None
        st.session_state.question_source = result[5] if len(result) > 5 else None
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.rerun()

    if st.session_state.full_texts:
        for i, option in enumerate(st.session_state.options):
            first_10_words = ' '.join(option.split()[:10])
            full_text = next((row['Clean Text'] for _, row in top_rashis_df.iterrows() if first_10_words in ' '.join(row['Clean Text'].split()[:10])), None)
            if full_text:
                with st.expander(f"Option {chr(65 + i)}"):
                    st.write(full_text)
            else:
                full_text = next((row['Text'] for _, row in kitzur_related_df.iterrows() if option in row['Text']), None)
                reference = next((row['Source Ref'] for _, row in kitzur_related_df.iterrows() if option in row['Text']), None)
                if full_text and reference:
                    with st.expander(f"Option {chr(65 + i)}"):
                        st.write(f"**{reference}**: {full_text}")