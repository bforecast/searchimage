import os
import json
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
# This is the line that fixes things
import PIL.PngImagePlugin

load_dotenv()
cwd = os.getcwd()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

from anthropic import Anthropic
claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

#extract json from image and return the json
# def extract2json_gemini(img):
#     model = genai.GenerativeModel('gemini-1.5-flash',
#                 generation_config={"response_mime_type": "application/json"})
#     prompt = "return all contents of image. you should use the original text, turn all date to the date format. Remember, Create a complete json format output."
#     response = model.generate_content([prompt, img],
#                   safety_settings={
#                             HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#                         },
#                   stream=True)
#     response.resolve()
#     print(f"Finish Reason: {response.candidates[0].finish_reason}")
#     return response.candidates[0].content.parts[0].text

#extract json from image and return the json
def extract2json_gemini(img):
    model = genai.GenerativeModel('gemini-1.5-pro',
                generation_config={"response_mime_type": "application/json"})
    # prompt = "Extract all visible texts. Turn all date to the date format 'YYYY-MM-DD'. Create a json format output. At the end, return the category which the whole texts is as a 'sheet', 'email', or 'essay' based on content."
    prompt = '''Extract all visible texts and provide the information in a complete JSON format with the following structure:
                {
                "category": "...",
                "content": {
                    ...
                    }
                }
                Use code with caution.
                Json
                Where:
                "category": classify the content as a 'sheet', 'email', or 'essay'.
                "content": Extract all the text from the image. Turn the date to the date format "YYY-MM-DD'.Represent the information in key-value pairs, where the keys are meaningful descriptions of the content and the values are the extracted text.
                Pay close attention to the structure and meaning of the content, especially any tables and checkboxes.
                Tables: Tables might represent different information, so accurately capturing their structure is important.
                Checkboxes: When you encounter a group of checkboxes, create a single key that describes the category or purpose of those checkboxes. The value of this key should be an array of strings, where each string represents the text of a checked checkbox.
                '''
    response = model.generate_content(
                    contents = [prompt, img],
                    safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                    stream=True)
    response.resolve()
    json_str = response.candidates[0].content.parts[0].text
    return json_str

#extract text from image and return the data focused in type: dict
def extract_with_gemini(img):
    model = genai.GenerativeModel('gemini-1.5-flash',
                generation_config={"response_mime_type": "application/json"})
    prompt = "find the product number, issue date. Turn issue date to the date format.Return as the json format."
    response = model.generate_content([prompt, img],
                  safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                  stream=True)
    response.resolve()
    result_dict = json.loads(response.candidates[0].content.parts[0].text)
    return result_dict

#extract text from image and return the data focused in type: dict
def extract2dict_gemini(img):
    model = genai.GenerativeModel('gemini-1.5-pro',
                generation_config={"response_mime_type": "application/json"})
    # prompt = "Extract all visible texts. Turn all date to the date format 'YYYY-MM-DD'. Create a json format output. At the end, return the category which the whole texts is as a 'sheet', 'email', or 'essay' based on content."
    prompt = '''Extract all visible texts and provide the information in a complete JSON format with the following structure:
                {
                "category": "...",
                "content": {
                    ...
                    }
                }
                Use code with caution.
                Json
                Where:
                "category": classify the content as a 'sheet', 'email', or 'essay'.
                "content": Extract all the text from the image. Turn the date to the date format "YYY-MM-DD'.Represent the information in key-value pairs, where the keys are meaningful descriptions of the content and the values are the extracted text.
                Pay close attention to the structure and meaning of the content, especially any tables and checkboxes.
                Tables: Tables might represent different information, so accurately capturing their structure is important.
                Checkboxes: When you encounter a group of checkboxes, create a single key that describes the category or purpose of those checkboxes. The value of this key should be an array of strings, where each string represents the text of a checked checkbox.
                '''
    response = model.generate_content(
                    contents = [prompt, img],
                    safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                    stream=True)
    response.resolve()
    json_str = response.candidates[0].content.parts[0].text
    print(response) 
    print(f"Json String is {json_str}")
    result_dict = json2dict(json_str)
    return result_dict

def json2dict(json_str:str):
    """
    Attempts to fix a truncated JSON string by progressively adding closing 
    brackets and quotes until a valid JSON object is formed.

    Args:
        json_str (str): The truncated or potentially malformed JSON string.

    Returns:
        dict
    """
    if not json_str:
        return {}

    try:
        return json.loads(json_str, strict=False)  # Check if already valid
    except json.JSONDecodeError:
        pass

    # Potential fixes to try
    fixes = [
        ('"',), # Missing closing quote
        ('}',), # Missing closing brace
        ('"', '}'), # Missing quote and brace 
        ('}', '"'), # Missing brace and quote (for cases where quote is in a key)
    ]

    for fix in fixes:
        test_json = json_str
        for char in fix:
            test_json += char
        try:
            return json.loads(test_json, strict=False)
        except json.JSONDecodeError:
            continue 

    return {} # Return empty dict

def extract2json_claude(img):
    prompt = '''Extract all visible texts and provide the information in a complete JSON format with the following structure:
                {
                "category": "...",
                "content": {
                    ...
                    }
                }
                Use code with caution.
                Json
                Where:
                "category": classify the content as a 'sheet', 'email', or 'essay'.
                "content": Extract all the text from the image. Turn the date to the date format "YYY-MM-DD'.Represent the information in key-value pairs, where the keys are meaningful descriptions of the content and the values are the extracted text.
                Pay close attention to the structure and meaning of the content, especially any tables and checkboxes.
                Tables: Tables might represent different information, so accurately capturing their structure is important.
                Checkboxes: When you encounter a group of checkboxes, create a single key that describes the category or purpose of those checkboxes. The value of this key should be an array of strings, where each string represents the text of a checked checkbox.
                '''
    message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": pil_image_to_base64(img),
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "Describe this image."
                                }
                            ],
                        }
                    ],
                )
    json_str = message
    return json_str

import base64
from io import BytesIO
def pil_image_to_base64(image):
  """Converts a PIL Image object to a base64 string.

  Args:
    image: A PIL Image object.

  Returns:
    A string containing the base64 encoded image data.
  """

  buffered = BytesIO()
  image.save(buffered, format="PNG")  # You can adjust the format if needed
  img_str = base64.b64encode(buffered.getvalue()).decode()
  return img_str

def extract2json_openai(img):
    prompt = '''Extract all visible texts and provide the information in a complete JSON format with the following structure:
                {
                "category": "...",
                "content": {
                    ...
                    }
                }
                Use code with caution.
                Json
                Where:
                "category": classify the content as a 'sheet', 'email', or 'essay'.
                "content": Extract all the text from the image. Turn the date to the date format "YYY-MM-DD'.Represent the information in key-value pairs, where the keys are meaningful descriptions of the content and the values are the extracted text.
                Pay close attention to the structure and meaning of the content, especially any tables and checkboxes.
                Tables: Tables might represent different information, so accurately capturing their structure is important.
                Checkboxes: When you encounter a group of checkboxes, create a single key that describes the category or purpose of those checkboxes. The value of this key should be an array of strings, where each string represents the text of a checked checkbox.
                '''
    message = claude_client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=4096,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": pil_image_to_base64(img),
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "Describe this image."
                                }
                            ],
                        }
                    ],
                )
    json_str = message
    return json_str
