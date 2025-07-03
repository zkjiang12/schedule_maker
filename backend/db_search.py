from pinecone import Pinecone
import os
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
import json

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("penn-scheduler-py")

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
search_tool = types.Tool(google_search=types.GoogleSearch)
config = types.GenerateContentConfig(
    tools=[search_tool]
)
query = input("ask the AI")

response = client.models.generate_content(
    model = 'gemini-2.5-flash',
    contents = f"""
        you are advising an incoming freshman at UPenn on course scheduling. 
        respond with a list of the names of the courses that might be relevant to them.
        return format is list of strings with NO ADDITIONAL TEXT (e.g ["Calculus I","Economics","Managment and Tech"]) 
        {query}
    """,
    config = config,
)

recommended_courses = json.loads(response.candidates[0].content.parts[0].text)
print(recommended_courses)
print(type(recommended_courses))
for course in recommended_courses:
    results = index.search(
        namespace = "penn",
        query = {
            "inputs": {"text": course}, 
            "top_k": 5
        },
        fields=["chunk_text"]
    )
    print(f"below are the relevant courses for {course}: ")
    print(results)
    print()