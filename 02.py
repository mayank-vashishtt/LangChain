from dotenv import load_dotenv
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain




load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model through LangChain
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
prompt =  PromptTemplate.from_template("what is the capital of {country}?")
# Make a prediction


cities = [
    "India",
    "Phoenix",
    "Nevada",
    "Amsterdam",
]

chain = LLMChain(llm=llm, prompt=prompt)


for city in cities:
    output = chain.run(city)
    print(output)
