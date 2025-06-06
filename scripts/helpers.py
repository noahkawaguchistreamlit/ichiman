import datetime as dt

import streamlit as st
import pandas as pd

import scripts.data_insights as data
from scripts.i18n import get_translation as gt
from scripts.i18n import localize_df_data, date_to_localized_string
from config import Lang

def show_all_data_info(df: pd.DataFrame) -> None:
    """Display averages, goal progress, and a graph of the data."""

    df_copy = df.copy()

    # Ensure the 'date' column is of datetime type and the 'duration' 
    # column of timedelta type
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy['duration'] = pd.to_timedelta(df_copy['duration'])

    c1, c2 = st.columns([1, 2])
    with c1:
        data.daily_averages(df_copy)
        st.divider()
        data.goal_progress(df_copy)
        st.divider()
    with c2:
        data.graph_data(df_copy)
    st.divider()
    with st.expander(gt('misc.show_all', Lang.lang)):
        st.dataframe(localize_df_data(df_copy, Lang.lang),
                     use_container_width=True)

def update_data(df: pd.DataFrame, date_cursor: dt.date) -> pd.DataFrame:
    """Given the currently recorded dates and durations, prompt the 
    user to enter data for each day up to the present day. 
    Return the data with every rerun of the page because of Streamlit's 
    repeated top-down execution.
    """
    # Initialize new session_state variables for the parameters
    if 'update_data_df' not in st.session_state:
        st.session_state.update_data_df = df.copy()
    if 'date_cursor' not in st.session_state:
        st.session_state.date_cursor = date_cursor

    # Ensure the 'date' column is of datetime type and the 'duration' 
    # column of timedelta type
    st.session_state.update_data_df['date'] = pd.to_datetime(
        st.session_state.update_data_df['date']
        )
    st.session_state.update_data_df['duration'] = pd.to_timedelta(
        st.session_state.update_data_df['duration']
        )

    # Check if the data needs to be updated
    today = dt.datetime.today().date()
    if st.session_state.date_cursor > today:
        return st.session_state.update_data_df
    else:
        st.write(gt('update.not_up2date', Lang.lang))

        # Define the form container and write the date in question
        duration_form = st.form('duration_form')
        formatted_date = date_to_localized_string(st.session_state.date_cursor)
        duration_form.write(gt('update.enter', Lang.lang).format(formatted_date))

        # Collect the hours and minutes from the user
        c1, c2, c3, c4 = duration_form.columns([5,1,5,1])
        with c1:
            st.number_input(gt('misc.hours', Lang.lang), min_value=0,
                            max_value=23, value=0, step=1, format='%d',
                            key='new_duration_hours')
        with c3:
            st.number_input(gt('misc.minutes', Lang.lang), min_value=0,
                            max_value=59, value=0, step=1, format='%d',
                            key='new_duration_minutes')

        def record_and_advance():
            # Convert the user's input into a DataFrame
            new_duration = dt.timedelta(
                hours=st.session_state.new_duration_hours,
                minutes=st.session_state.new_duration_minutes
                )
            new_row = pd.DataFrame({'date': [st.session_state.date_cursor],
                                    'duration': [new_duration]})
            new_row['date'] = pd.to_datetime(new_row['date'])
            # Save the data to the session_state DataFrame
            st.session_state.update_data_df = pd.concat(
                [st.session_state.update_data_df, new_row],
                ignore_index=True,
                )
            # Increment the date cursor
            st.session_state.date_cursor += dt.timedelta(days=1)

        duration_form.form_submit_button(gt('update.save', Lang.lang),
                                         on_click=record_and_advance)

        # Show the latest data as it is being updated
        if len(st.session_state.update_data_df) > 0:
            st.divider()
            reversed_df = st.session_state.update_data_df.iloc[::-1]
            st.dataframe(localize_df_data(reversed_df, Lang.lang),
                         use_container_width=True)

        # Return a valid value to the caller function with every rerun 
        # of the page
        return st.session_state.update_data_df

def up_to_date_download(df: pd.DataFrame) -> None:
    """Display the updated status of the data.
    Format the DataFrame and create a CSV file.
    Display an interface to download the file.
    """
    # Copy the DataFrame and remove '0 days' from the 'duration' values
    remove_days = df.copy()
    def format_timedelta(td):
        return f'{td.components.hours:02}:{td.components.minutes:02}:{td.components.seconds:02}'
    remove_days['duration'] = (remove_days['duration']
                                .apply(format_timedelta))
    
    # Create a CSV file with the formatted data 
    csv = remove_days.to_csv(index=False)

    # Display the up-to-date status of the data
    c1, c2 = st.columns(2)
    with c1:
        earliest_date = date_to_localized_string(df['date'].iloc[0].date())
        latest_date = date_to_localized_string(df['date'].iloc[-1].date())
        st.write(gt('download.up2date', Lang.lang))
        if earliest_date == latest_date:
            st.write(latest_date)
        else:
            st.write(gt('download.range', Lang.lang).format(
                earliest_date, latest_date,
                ))

    # Display a basic interface to download the CSV file 
    with c2:
        c1, c2 = st.columns(2)
        with c1:
            download_filename = st.text_input(gt('download.name', Lang.lang),
                                              value='tracked_habit')
            download_filename = download_filename.replace(' ', '_') + '.csv'
            st.download_button(label=gt('download.download', Lang.lang),
                               data=csv, file_name=download_filename,
                               mime='text/csv')
        with c2:
            st.write(gt('download.unfortunately', Lang.lang))
