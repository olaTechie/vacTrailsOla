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
    table_exists = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studies'").fetchone()
    
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
    study = cur.execute('SELECT * FROM studies WHERE Decision IS NULL LIMIT 1').fetchone()

    if study:
        # (The rest of the code remains the same)

    # If all studies have been screened
    else:
        st.write('All studies have been screened.')

    # Export data button - moved outside the 'if study' block to make it always available
    if st.button('Export Data'):
        export_data = pd.read_sql('SELECT * FROM studies', conn)
        export_data.to_csv('./screening_results.csv', index=False)
        st.markdown('Download the screened data [here](./screening_results.csv).')

    conn.close()

# Run the app
if __name__ == '__main__':
    app()
