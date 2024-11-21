from tempfile import NamedTemporaryFile
import os

import streamlit as st
from PIL import Image
from utils.llamaindex import iPdfRAG
from dotenv import load_dotenv

load_dotenv()
cwd = os.getcwd()

# Streamlit app
def run():
    st.title("SearchImage, Image to Data 👨‍💻 ")
    st.subheader('Made with ❤️ by Ruan')
    temp_path = os.path.join(cwd, "temp")


    uploaded_file = st.file_uploader("Choose a pdf file", type=["pdf"])

    if uploaded_file is not None:
        with NamedTemporaryFile(dir=temp_path, suffix='.pdf') as f:
            f.write(uploaded_file.getbuffer())


        # get file type
        file_type = uploaded_file.type
        st.write(file_type)
        # get image from different file formats
        if file_type == "application/pdf":
            iPdf = iPdfRAG()
            st.write(temp_path)
            progress_text = st.empty()
                
            for progress in iPdf.load(temp_path):
                progress_text.text(progress)
                
                st.success("Processing completed!")

run()