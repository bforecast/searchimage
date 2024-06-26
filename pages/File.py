import streamlit as st
from PIL import Image
import tkinter as tk
from tkinter import filedialog

import os
import io
from dotenv import load_dotenv
# from extract_thinker.llm import LLM
# from extract_thinker import DocumentLoaderTesseract
# from extract_thinker.extractor import Extractor

import json
import fitz  # PyMuPDF library

from utils.llm import extract_with_gemini

# Streamlit app
def run():
    st.title("SearchImage, Image to Data 👨‍💻 ")
    st.subheader('Made with ❤️ by Ruan')


    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
            # get file type
            file_type = uploaded_file.type
            st.write(file_type)
            # get image from different file formats
            if file_type in ["image/jpeg", "image/png"]:
                pil_image = Image.open(uploaded_file)

            elif file_type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in doc:  # iterate through the pages
                    pixmap = page.get_pixmap()  # render page to an image
                    pil_image =  Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                doc.close()
            # show the image
            st.image(pil_image, caption=f'Uploaded {file_type}.', use_column_width=True)

            # Generate UI description
            if st.button("Extract Images"):
                st.write("🧑‍💻 Looking at your Images...")
                result = extract_with_gemini(pil_image)
                st.write(result)

run()