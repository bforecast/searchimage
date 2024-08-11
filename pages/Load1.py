import streamlit as st
from PIL import Image

import os
import mimetypes
import shutil
import re

from dotenv import load_dotenv
import json
import fitz  # PyMuPDF library

from utils.llamaindex import llamaindex_base

load_dotenv()
cwd = os.getcwd()
from utils.llm import extract2json_gemini


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


def copy_and_rename(source_file, destination_directory, new_filename):
    """
    Copies a file to a new directory, renaming it and replacing invalid characters.

    Args:
        source_file: The path to the original file.
        destination_directory: The path to the directory where you want to copy the file.
        new_filename: The new name you want to give the copied file.
    """
    try:
        # Handle escape sequences by replacing them with a single "!"
        # Exclude the escaped double quote (\\") from replacement
        new_filename = re.sub(r'\\(?!")', '!', new_filename)

        # Replace invalid characters (excluding parentheses) with "!"
        new_filename = re.sub(r'[^\w\s.\-()]', '!', new_filename)

        shutil.copy2(source_file, os.path.join(destination_directory, new_filename))
        print(f"File '{source_file}' copied to '{destination_directory}' as '{new_filename}' successfully.")
        return new_filename
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
    except OSError as e:
        print(f"Error: Unable to copy file. {e}")
    return False

def fix_filename(filename):
    # Handle escape sequences by replacing them with a single "!"
    # Exclude the escaped double quote (\\") from replacement
    filename = re.sub(r'\\(?!")', '!', filename)
    # Replace invalid characters (excluding parentheses) with "!"
    filename = re.sub(r'[^\w\s.\-()]', '!', filename)
    filename.replace(" ", "")
    return filename

# Streamlit app
def run():
    st.title("Load pdf to Storage.")
    st.subheader('Made with ❤️ by Ruan')
    
    # select Source/Destination paths of local machine
    in_path =  os.path.join(cwd, "income")
    storage_path = os.path.join(cwd, "storage/pdf")


    file_types = get_files_with_type(in_path)
    st.write(file_types)
    if st.button("Extract all"):
        for filename, file_type in file_types.items():
            filepath= os.path.join(in_path, filename)
            newFileName = ''
            # get image from different file formats
            if file_type == "application/pdf":
                doc = fitz.open(filepath)
                images = []
                ocr_results = []
                for i, page in enumerate(doc):  # iterate through the pages
                    pixmap = page.get_pixmap()  # render page to an image
                    images.append(pixmap)

                    pil_image =  Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                    st.write(f"Extracting file {filename}")
                    result = extract2json_gemini(pil_image)
                    ocr_results.append(result)
                    st.write(result)
                    try:
                        result_dict = json.loads(result)
                    except Exception as e:
                        st.error(e)
                        continue

                    st.write(result_dict)
                    if result:
                        st.success(f"Extract by LLM sucessfully")
                    else:
                        st.error(f"Fail to extranct by LLM.")
                        continue

                doc.close()
                # Create a new PDF document
                new_doc = fitz.open()

                # Add pages with OCR text
                for i in range(len(images)):
                    new_page = new_doc.new_page()
                    st.write(fitz.Rect(0, 0, images[i].width, images[i].height))
                    new_page.insert_image(fitz.Rect(0, 0, images[i].width, images[i].height), pixmap = images[i])

                    # Add OCR text (adjust formatting as needed)
                    ocr_text = ocr_results[i]
                    # new_page.insert_text(fitz.Point(10, 10), ocr_text, stroke_opacity=0, fill_opacity=0)
                    new_page.insert_textbox(fitz.Rect(0, 0, pixmap.width, pixmap.height), 
                                            ocr_text, stroke_opacity=0, fill_opacity=0)

                # Save the new PDF
                newfilepath = os.path.join(storage_path, filename)
                st.write(newFileName)
                new_doc.save(newfilepath)
    if st.button("Save to llamaindex_base"):
            lli_base = llamaindex_base()
            num_docs = lli_base.load(storage_path)
            if num_docs:
                st.success(f"Save {num_docs} pdfs to llamaindex base.")


run()