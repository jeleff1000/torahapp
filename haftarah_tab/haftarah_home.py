import streamlit as st
from .haftarah_mapping import shabbat_readings, sorted_holiday_readings, parshiyot
import pandas as pd

# Define the correct order of Torah books
torah_books_order = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]

def haftarah_tab(st, calendar_df, date_option, haftarah_path):
    st.title("Haftarah Tab")

    # Get the selected date from session state
    selected_date = st.session_state.selected_date

    # Filter the calendar dataframe to get the Haftarah for the selected date and where Title (en) is Haftarah
    haftarah_for_date = calendar_df[(calendar_df['Date'] == selected_date) & (calendar_df['Title (en)'] == 'Haftarah')]

    if not haftarah_for_date.empty:
        haftarah_value = haftarah_for_date.iloc[0]['Display Value (en)']
        st.write(f"**Haftarah for {selected_date}:** {haftarah_value}")

        # Determine if the Haftarah is for a Holiday or Shabbat
        if haftarah_value in sorted_holiday_readings.values():
            option = "Holiday"
        else:
            option = "Shabbat"

        # Set the reading type
        st.selectbox("Select Reading Type", ["Holiday", "Shabbat"], index=["Holiday", "Shabbat"].index(option))

        if option == "Holiday":
            holiday = next(key for key, value in sorted_holiday_readings.items() if value == haftarah_value)
            st.selectbox("Select a Holiday", list(sorted_holiday_readings.keys()), index=list(sorted_holiday_readings.keys()).index(holiday))
            st.write(f"**Selected Holiday:** {holiday}")
            st.write(f"**Haftarah Reading:** {haftarah_value}")

        else:  # Shabbat readings
            for book, parshas in shabbat_readings.items():
                if haftarah_value in [haftarah for haftarah_list in parshas.values() for haftarah in haftarah_list]:
                    selected_book = book
                    selected_parsha = next(key for key, value in parshas.items() if haftarah_value in value)
                    break

            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Select a Torah Book", torah_books_order, index=torah_books_order.index(selected_book))
            with col2:
                st.selectbox("Select a Parsha", parshiyot[selected_book], index=parshiyot[selected_book].index(selected_parsha))
            st.write(f"**Selected Parsha:** {selected_parsha}")
            st.write(f"**Haftarah Reading:** {haftarah_value}")
    else:
        st.write("No Haftarah found for the selected date.")