import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# Suppress the deprecation warning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Function to create SQLite connection


def create_connection():
    conn = sqlite3.connect('./screening_results.db')
    return conn

# Function to check if table exists and populate data if empty


def initialize_db():
    conn = create_connection()
    cur = conn.cursor()

    # Check if table exists
    table_exists = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='studies'").fetchone()

    if not table_exists:
        # Populate data if table doesn't exist
        df = pd.read_csv('./cleaned_african_studies.csv')
        df['Decision'] = None
        df['Label'] = None
        df.to_sql('studies', conn, index_label='id', if_exists='replace')

    conn.close()


# Initialize the database
initialize_db()

# Streamlit app


def app():
    conn = create_connection()
    cur = conn.cursor()

    # Fetch the first study with a missing Decision from the database
    study = cur.execute(
        'SELECT * FROM studies WHERE Decision IS NULL LIMIT 1').fetchone()

    if study:
        # Calculate the total number of studies, number screened, and number remaining
        total_studies = cur.execute(
            'SELECT COUNT(*) FROM studies').fetchone()[0]
        screened_studies = cur.execute(
            'SELECT COUNT(*) FROM studies WHERE Decision IS NOT NULL').fetchone()[0]
        remaining_studies = total_studies - screened_studies

        # Display the row number and study statistics in the same row as cards
        st.markdown(f"### Study {study[0] + 1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Total Studies**\n\n{total_studies}")
        with col2:
            st.markdown(f"**Screened Studies**\n\n{screened_studies}")
        with col3:
            st.markdown(f"**Remaining Studies**\n\n{remaining_studies}")

        # Display the specified eight columns with their respective column numbers
        st.write(f"NCT Number: {study[1]}")
        st.write(f"Study Title: {study[2]}")
        st.write(f"Brief Summary: {study[3]}")
        st.write(f"Conditions: {study[4]}")
        st.write(f"Interventions: {study[5]}")
        st.write(f"Locations: {study[6]}")
        st.write(f"Countries: {study[7]}")
        st.write(f"MCountries: {study[8]}")

        # Buttons to include, exclude, or move to the next study
        col1, col2, col3 = st.columns(3)
        if col1.button('Include'):
            cur.execute('UPDATE studies SET Decision = ? WHERE id = ?',
                        ('Include', study[0]))
            conn.commit()
        if col2.button('Exclude'):
            cur.execute('UPDATE studies SET Decision = ? WHERE id = ?',
                        ('Exclude', study[0]))
            conn.commit()
        if col3.button('Next'):
            # Just refresh the page to get the next study with missing Decision
            st.experimental_rerun()

        # Display decision summary
        included_count = cur.execute(
            'SELECT COUNT(*) FROM studies WHERE Decision = "Include"').fetchone()[0]
        excluded_count = cur.execute(
            'SELECT COUNT(*) FROM studies WHERE Decision = "Exclude"').fetchone()[0]
        undecided_count = cur.execute(
            'SELECT COUNT(*) FROM studies WHERE Decision IS NULL').fetchone()[0]

        # Plot pie chart and bar chart side by side
        col1, col2 = st.columns(2)
        with col1:
            labels = ['Included', 'Excluded', 'Undecided']
            sizes = [included_count, excluded_count, undecided_count]
            colors = ['green', 'red', 'grey']
            explode = (0.1, 0.1, 0.1)

            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=True, startangle=140)
            plt.axis('equal')
            st.pyplot()

        # Plot bar chart for study statistics
        with col2:
            labels = ['Total Studies', 'Screened Studies', 'Remaining Studies']
            values = [total_studies, screened_studies, remaining_studies]
            index = np.arange(len(labels))

            plt.bar(index, values, color=['blue', 'orange', 'green'])
            plt.xlabel('Categories', fontsize=12)
            plt.ylabel('Number of Studies', fontsize=12)
            plt.xticks(index, labels, fontsize=12, rotation=30)
            plt.title('Study Statistics')
            st.pyplot()

        # Export data button
        if st.button('Export Data'):
            export_data = pd.read_sql('SELECT * FROM studies', conn)
            export_data.to_csv('./screening_results.csv', index=False)
            st.markdown(
                'Download the screened data [here](./screening_results.csv).')

    # If all studies have been screened
    else:
        st.write('All studies have been screened.')

    conn.close()


# Run the app
if __name__ == '__main__':
    app()
