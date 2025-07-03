from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

#initialized this instance of the class of Flask apps
app = Flask(__name__)
CORS(app)#permits all sources

load_dotenv()
#initialized the Gemini Stuff
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
#set the tool.
grounding_tool = types.Tool(
    google_search=types.GoogleSearch
)
# Configure generation settings
config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

def retrievingFromPinecone():
    pass

#Workflow
#LLM recieves the query. 
#processes it and responds with either a tool call or a text based response (most, if not all the time, it will be a tool call)
#if a tool call, then respond with alert of a tool call and also the parameters that we'll be passing into the function that calls the tool.
#if a response, then just return to the frontend

#defining the tool



@app.route('/', methods = ['POST', 'OPTIONS'])
def mainFunction():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        user_query = data['query']
        
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = f"""
                
            """,
            config = config
        )
        # For now, just echo back the query - you can add AI logic here later
        print(response.text)
        return jsonify({'message': f"""{response.text}""", 'query': user_query})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug = True)
