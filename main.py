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

table_schema = ConfigData.TABLE_SCHEMA
schema_description = ConfigData.SCHEMA_DESCRIPTION
json_ex_1 = ConfigData.FEW_SHOT_EXAMPLE_1

json_ex_string = json.dumps(json_ex_1)

prompt_template_for_creating_query = """
    You are an expert in crafting NoSQL queries for MongoDB with 10 years of experience, particularly in MongoDB. 
    I will provide you with the table_schema and schema_description in a specified format. 
    Your task is to read the user_question, which will adhere to certain guidelines or formats, and create a NOSQL MongoDb pipeline accordingly.

    Table schema:""" + table_schema + """
    Schema Description: """ + schema_description + """

    Here are some example:
    Input: name of departments where number of employees is greater than 1000
    Output: {json_ex_string_1} 

    Note: You have to just return the query nothing else. Don't return any additional text with the query.
    Input: {user_question}
    """

query_creation_prompt = PromptTemplate(
    template=prompt_template_for_creating_query,
    input_variables=["user_question", "json_ex_string_1"],
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
query_1 = get_query(user_question="how many unique skus are there?")
pipeline = query_1
result = collection_name.aggregate(pipeline)
for doc in result:
    print(doc)