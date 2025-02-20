from dotenv import load_dotenv
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model through LangChain
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

# Make a prediction
print(llm.predict("What is the meaning of life?"))