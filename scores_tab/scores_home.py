import streamlit as st
import pandas as pd
from datetime import datetime

# Path to the scores file
scores_file_path = 'scores_tab/scores.parquet'

def scores_tab():
    st.title("Scores")

    # Load scores data
    try:
        scores_df = pd.read_parquet(scores_file_path)
    except FileNotFoundError:
        scores_df = pd.DataFrame(columns=['username', 'category', 'score', 'date'])

    # Create tabs for each viewer
    tab1, tab2, tab3, tab4 = st.tabs(["Today's Top Scores", "All-Time Top Scores", "Cumulative Top Scores", "Personal Top Scores"])

    with tab1:
        # Filter scores for today
        today = datetime.today().strftime('%Y-%m-%d')
        today_scores = scores_df[scores_df['date'] == today]

        # Display today's top scores
        if not today_scores.empty:
            st.write("Today's Top Scores")
            st.dataframe(today_scores[['username', 'category', 'score', 'date']])
        else:
            st.write("No scores for today yet.")

    with tab2:
        # Display all-time top scores
        if not scores_df.empty:
            st.write("All-Time Top Scores")
            all_time_top_scores = scores_df.groupby(['username', 'category', 'date'])['score'].max().reset_index()
            st.dataframe(all_time_top_scores)
        else:
            st.write("No scores available.")

    with tab3:
        # Display cumulative top scores
        if not scores_df.empty:
            st.write("Cumulative Top Scores")
            cumulative_top_scores = scores_df.groupby(['username', 'category'])['score'].sum().reset_index()
            st.dataframe(cumulative_top_scores)
        else:
            st.write("No scores available.")

    with tab4:
        # Display personal top scores
        username = st.text_input("Enter your username to view your top scores:")
        if username:
            personal_top_scores = scores_df[scores_df['username'] == username].groupby(['category'])['score'].max().reset_index()
            if not personal_top_scores.empty:
                st.write(f"{username}'s Top Scores")
                st.dataframe(personal_top_scores)
            else:
                st.write(f"No scores available for {username}.")