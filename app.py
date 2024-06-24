import streamlit as st
import pathlib
from PIL import Image

import os
import io
from dotenv import load_dotenv
# from extract_thinker.llm import LLM
# from extract_thinker import DocumentLoaderTesseract

# from extract_thinker.extractor import Extractor
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import fitz  # PyMuPDF library


load_dotenv()
cwd = os.getcwd()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_with_gemini(img):
    model = genai.GenerativeModel('gemini-1.5-flash',
                generation_config={"response_mime_type": "application/json"})

    response = model.generate_content(["find the product number, issue date. Turn issue date to the date format.Return as the json format.", img],
                  safety_settings={
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                  stream=True)
    response.resolve()
    result_dict = json.loads(response.candidates[0].content.parts[0].text)
    return result_dict



import xml.etree.ElementTree as ET
    
# Streamlit app
def main():
    st.title("ExtractThinker, Image to Text 👨‍💻 ")
    st.subheader('Made with ❤️ by Ruan')

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
            # 获取文件类型
            file_type = uploaded_file.type
            st.write(file_type)
            # Load and display the image
            # 显示图片
            if file_type in ["image/jpeg", "image/png"]:
                pil_image = Image.open(uploaded_file)

            # 显示PDF文件并提取第一页图片
            elif file_type == "application/pdf":
                # 打开PDF文件
                doc = fitz.open(uploaded_file)
                for page in doc:  # iterate through the pages
                    pixmap = page.get_pixmap()  # render page to an image
                    pil_image =  Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                doc.close()

            st.image(pil_image, caption=f'Uploaded {file_type}.', use_column_width=True)

            # Generate UI description
            if st.button("Extract Images"):
                st.write("🧑‍💻 Looking at your Images...")
                result = extract_with_gemini(pil_image)
                st.write(result)


if __name__ == "__main__":
    main()