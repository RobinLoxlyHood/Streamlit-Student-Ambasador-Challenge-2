import streamlit as st
import pandas as pd

st.header('Editable Dataframes ✎')


file = st.file_uploader("upload file a CSV file here", type = ['csv'])
if file is not None:
    df = pd.read_csv(file)
    edited_df = st.experimental_data_editor(pd.DataFrame(df), num_rows = "dynamic")


    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')


    csv = convert_df(edited_df)

    st.download_button(
        label="Download edited data as CSV",
        data=csv,
        file_name='edited_df.csv',
        mime='text/csv',
    )