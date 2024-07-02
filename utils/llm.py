import os
import io
import json
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
load_dotenv()
cwd = os.getcwd()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#extract json from image and return the json
def extract2json_gemini(img):
    model = genai.GenerativeModel('gemini-1.5-flash',
                generation_config={"response_mime_type": "application/json"})
    prompt = "return all contents of image. you should use the original text, turn issue date to the date format, keep the serial number of text, return as the json format."
    response = model.generate_content([prompt, img],
                  safety_settings={
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        },
                  stream=True)
    response.resolve()
    print(response)
    return response.candidates[0].content.parts[0].text

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

# 本地嵌入模型: bge-small-zh-v1.5

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# bge_embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
bge_embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")


