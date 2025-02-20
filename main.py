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

import json

table_schema_json = json.dumps(ConfigData.TABLE_SCHEMA, indent=2)  # ✅ Convert to a JSON string
schema_description_json = json.dumps(ConfigData.SCHEMA_DESCRIPTION, indent=2)  # ✅ Convert to a JSON string

json_ex_1 = ConfigData.FEW_SHOT_EXAMPLE_1

json_ex_string = json.dumps(json_ex_1)


query_creation_prompt = PromptTemplate(
    template="""
    You are an expert in crafting NoSQL queries for MongoDB with 10 years of experience, particularly in MongoDB. 
    I will provide you with the table_schema and schema_description in a specified format. 
    Your task is to read the user_question, which will adhere to certain guidelines or formats, and create a NoSQL MongoDb pipeline accordingly.

    Table schema: {table_schema_json}
    Schema Description: {schema_description_json}

    Here are some examples:
    Input: Retrieve all products where mrp > 400 and calculate profit_margin as mrp - purchase_cost using a MongoDB aggregation pipeline.
    Output: {json_ex_string}

    Note: You have to just return the query, nothing else. Don't return any additional text with the query.
    Input: {user_question}
    """,
    input_variables=["user_question"],
    partial_variables={
        "table_schema_json": table_schema_json,
        "schema_description_json": schema_description_json,
        "json_ex_string": json.dumps(ConfigData.FEW_SHOT_EXAMPLE_1, indent=2)  # ✅ Convert example to JSON string
    }
)


llmchain = LLMChain(llm=llm_gemini, prompt=query_creation_prompt, verbose=True)

def get_query(user_question):
    response = llmchain.invoke({
        "user_question": user_question,
        "json_ex_string_1": json_ex_string
    })

    response_text = response['text'].replace("Output: ", "")
    pattern = r'db\.collectionName\.aggregate\(\s*\['
    
    output_string = re.sub(pattern, '', response_text)
    
    return json.loads(output_string)

# MongoDB connection setup
client = pymongo.MongoClient(ConfigData.MONGO_DB_URI)
db = client[ConfigData.DB_NAME]
collection_name = db[ConfigData.COLLECTION_NAME]

# Example usage
query_1 = get_query(user_question="give me the sum of mrp of all product?")
pipeline = query_1
result = collection_name.aggregate(pipeline)
for doc in result:
    print(doc)