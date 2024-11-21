import pandas as pd
import streamlit as st
import os
import mimetypes
from dotenv import load_dotenv
from utils.llamaindex import iPdfRAG
from utils.global_functions import load_data

load_dotenv()
cwd = os.getcwd()

# Streamlit app
def run():
    st.title("View the Documents in the library")
    st.subheader("Please select a File_Path to display the content.")

    iPdf = load_data()
    filepaths = list(iPdf.get_filepaths())
    filepath_df = pd.DataFrame({
        "File_Path": filepaths
    })
    event = st.dataframe(filepath_df,
                         hide_index = True,
                         on_select = "rerun",
                         selection_mode="single-row")
    selected_df = filepath_df.iloc[event.selection.rows]
    selects = selected_df['File_Path'].tolist()
    if len(selects) > 0:
        documents = iPdf.get_documentsbyfilepath(selects[0])
        st.write(documents)

run()