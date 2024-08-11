import streamlit as st
import os
import mimetypes
from dotenv import load_dotenv
from utils.llamaindex import iPdfRAG

load_dotenv()
cwd = os.getcwd()

def get_files_with_type(directory):
  """
  Returns a dictionary containing file names and their MIME types.

  Args:
    directory: The path to the directory to search.

  Returns:
    A dictionary where keys are file names and values are MIME types.
  """
  files_with_types = {}
  for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if os.path.isfile(filepath):
      mime_type = mimetypes.guess_type(filepath)[0]
      files_with_types[filename] = mime_type
  return files_with_types



# Streamlit app
def run():
    st.title("Extract Image pdfs to Document, Build Document Agent for each Document.")
    st.subheader('Made with ❤️ by Ruan')
    iPdf_path =  os.path.join(cwd, "image_pdf")
    file_types = get_files_with_type(iPdf_path)
    st.write(file_types)
    if st.button("Extract and Save"):
            iPdf = iPdfRAG()
            num_docs = iPdf.load(iPdf_path)
            if num_docs:
                st.success(f"Save {num_docs} pdfs to llamaindex base.")

run()