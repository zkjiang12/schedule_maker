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
            contents = "The request will be made by a student that is going to UPenn next year as a freshman. They currently have not spent much time on the course catalog and are looking to see what courses are best for next year. Do your best to provide the most comprehensive response possible by providing information on graduation requirements, freshman year requirements for the major they are taking, and for each course mentioned, search for the teacher that teaches the course and also their reputation." + user_query,
            config = config
        )
        # For now, just echo back the query - you can add AI logic here later
        print(response.text)
        return jsonify({'message': f"""{response.text}""", 'query': user_query})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug = True)