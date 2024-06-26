import os
import io
import json
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
load_dotenv()
cwd = os.getcwd()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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