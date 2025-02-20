import google.generativeai as genai
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
import pymongo
from config import ConfigData

# Initialize Gemini API
genai.configure(api_key=ConfigData.GEMINI_API_KEY)

# Create Gemini model instance using LangChain's wrapper
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.1,
    google_api_key=ConfigData.GEMINI_API_KEY
)

# Convert the table schema and schema description to JSON strings to prevent misinterpretation of {}
table_schema_json = json.dumps(ConfigData.TABLE_SCHEMA)
schema_description_json = json.dumps(ConfigData.SCHEMA_DESCRIPTION)
json_ex_string = json.dumps(ConfigData.FEW_SHOT_EXAMPLE_1)

# Create a LangChain prompt template
query_creation_prompt = PromptTemplate(
    template="""
    You are an expert in crafting NoSQL queries for MongoDB with 10 years of experience, particularly in MongoDB. 
    I will provide you with the table_schema and schema_description in a specified format. 
    Your task is to read the user_question, which will adhere to certain guidelines or formats, and create a NoSQL MongoDb pipeline accordingly.

    Table schema: {table_schema}
    Schema Description: {schema_description}

    Here are some examples:
    Input: name of departments where number of employees is greater than 1000
    Output: {json_ex_string}

    Note: You have to just return the query, nothing else. Don't return any additional text with the query.
    Input: {user_question}
    """,
    input_variables=["user_question"],
    partial_variables={
        "table_schema": table_schema_json,
        "schema_description": schema_description_json,
        "json_ex_string": json_ex_string
    }
)

# Initialize LLMChain with the prompt template
llmchain = LLMChain(llm=llm_gemini, prompt=query_creation_prompt, verbose=True)

# Function to generate MongoDB query using LLM
def get_query(user_question):
    response = llmchain.invoke({"user_question": user_question})

    # Extract the query part from the response
    response_text = response['text'].replace("Output: ", "")
    
    # Ensure we only extract the JSON query part
    pattern = r'db\.collectionName\.aggregate\(\s*\['  # Adjust based on expected response
    output_string = re.sub(pattern, '[', response_text)

    return json.loads(output_string)  # Convert JSON string to dictionary

# MongoDB connection setup
client = pymongo.MongoClient(ConfigData.MONGO_DB_URI)
db = client[ConfigData.DB_NAME]
collection = db[ConfigData.COLLECTION_NAME]

# Example usage
query_1 = get_query(user_question="how many unique SKUs are there?")
pipeline = query_1
result = collection.aggregate(pipeline)

# Print results
for doc in result:
    print(doc)

