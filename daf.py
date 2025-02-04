import random

def get_surrounding_dafs(daf, n=3, talmud_dict=None):
    keys = list(talmud_dict.keys())
    index = keys.index(daf)
    start = max(0, index - n)
    end = min(len(keys), index + n + 1)
    return keys[start:index] + keys[index + 1:end]

def daf_yomi_tab(st, calendar_df, talmud_dict, seder_tractates, daf_ranges, date_option):
    st.header("Daf Yomi Quiz")

    # Initialize session state
    if 'selected_seder' not in st.session_state:
        st.session_state.selected_seder = None
    if 'selected_tractate' not in st.session_state:
        st.session_state.selected_tractate = None
    if 'selected_daf' not in st.session_state:
        st.session_state.selected_daf = None
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'options' not in st.session_state:
        st.session_state.options = None
    if 'correct_topic' not in st.session_state:
        st.session_state.correct_topic = None
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None

    if date_option == "Specific Date":
        # Filter calendar data for the selected date and title "Daf Yomi"
        filtered_calendar_df = calendar_df[(calendar_df['Date'] == st.session_state.selected_date) & (calendar_df['Title (en)'] == 'Daf Yomi')]
        # Get the daf for the selected date
        if not filtered_calendar_df.empty:
            selected_daf = filtered_calendar_df.iloc[0]['Display Value (en)']
            daf_list = [selected_daf]
            selected_tractate = selected_daf.split()[0]
            tractate_list = [selected_tractate]
            selected_seder = next(seder for seder, tractates in seder_tractates.items() if selected_tractate in tractates)
            seder_list = [selected_seder]
        else:
            daf_list = []
            tractate_list = []
            seder_list = []
    else:
        # Filter calendar data for all dates and title "Daf Yomi"
        filtered_calendar_df = calendar_df[calendar_df['Title (en)'] == 'Daf Yomi'].drop_duplicates(subset=['Display Value (en)'])
        daf_list = filtered_calendar_df['Display Value (en)'].tolist()
        seder_list = list(seder_tractates.keys())

    # Dropdowns for selecting Seder, Tractate, and Daf in one row
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

    def generate_talmud_question(daf):
        base_daf = daf[:-1] if daf[-1] in ['a', 'b'] else daf
        correct_topics = talmud_dict[base_daf]
        correct_topic = random.choice(correct_topics)
        surrounding_dafs = get_surrounding_dafs(base_daf, talmud_dict=talmud_dict)
        surrounding_topics = {topic for daf in surrounding_dafs for topic in talmud_dict[daf] if topic not in correct_topics}

        # Ensure we do not sample more than available topics
        num_incorrect_topics = min(3, len(surrounding_topics))
        incorrect_topics = random.sample(list(surrounding_topics), num_incorrect_topics)

        options = incorrect_topics + [correct_topic]
        random.shuffle(options)
        return f"Which topic is discussed in {daf}?", options, correct_topic

    if st.session_state.question is None or st.session_state.selected_daf != selected_daf:
        st.session_state.selected_daf = selected_daf
        st.session_state.question, st.session_state.options, st.session_state.correct_topic = generate_talmud_question(selected_daf)
        st.session_state.answered = False

    # Display the question
    st.write(st.session_state.question)
    st.session_state.selected_option = st.radio("Choose an option:", st.session_state.options)

    # Check the answer
    if st.button("Submit"):
        st.session_state.answered = True
        st.session_state.total_questions += 1
        if st.session_state.selected_option == st.session_state.correct_topic:
            st.session_state.correct_answers += 1
            st.success("Correct!")
        else:
            st.error(f"Incorrect! The correct answer is: {st.session_state.correct_topic}")

    # Next question button
    if st.session_state.answered and st.button("Next Question"):
        st.session_state.question, st.session_state.options, st.session_state.correct_topic = generate_talmud_question(selected_daf)
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.rerun()