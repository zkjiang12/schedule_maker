from pinecone import Pinecone
import os
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
from parse_json import *

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
    model='gemini-2.5-flash',
    contents=f"""
    ROLE: You are a UPenn course advisor for incoming freshmen.

    TASK: Generate a list of course names that would be relevant to the student's query.

    CRITICAL OUTPUT REQUIREMENTS:
    1. ONLY return a valid JSON array of strings
    2. NO explanatory text before or after the JSON array
    3. NO additional commentary within the course names
    4. Course names should be exact titles (e.g., "Calculus I", not "Calculus I (recommended)")

    REQUIRED FORMAT:
    ["Course Name 1", "Course Name 2", "Course Name 3"]

    EXAMPLES:
    CORRECT: ["Calculus I", "Introduction to Economics", "Computer Science Fundamentals"]
    INCORRECT: Here are some courses: ["Calculus I", "Economics"]
    INCORRECT: ["Calculus I (if you have strong math background)", "Economics - great for business"]

    VALIDATION CHECKLIST:
    - ✓ Starts with opening bracket [
    - ✓ Ends with closing bracket ]
    - ✓ Contains only course names in quotes
    - ✓ No explanatory text anywhere
    - ✓ Valid JSON format

    Student query: {query}

    Output (JSON array only):
    """,
    config=config
)

# Use the parsed response to get structured data
print(response.candidates[0].content.parts[0].text) 
print(type(response.candidates[0].content.parts[0].text))
recommended_courses = parse_course_response(response)
print(recommended_courses)
print(type(recommended_courses))


#getting the related courses from pinecone
all_relevant_courses = []
for course in recommended_courses:
    results = index.search(
        namespace = "penn",
        query = {
            "inputs": {"text": course}, 
            "top_k": 3
        }        
    )
    # print(f"below are the relevant courses for {course}: ")
    # print(results)
    # print()
    for result in results['result']['hits']:
        result['fields']['course_name'] = result['fields'].pop('chunk_text')
        all_relevant_courses.append(result['fields'])
 
print('ALL RELEVANT COURSES')
print(all_relevant_courses)

def format_course_data(all_relevant_courses):
    """Format course data for better prompt readability"""
    formatted_courses = []
    for course in all_relevant_courses:
        formatted_courses.append({
            'name': course['course_name'],
            'department': course['department'],
            'quality': f"{course['course_quality']:.2f}/4.0",
            'difficulty': f"{course['difficulty']:.2f}/4.0",
            'instructor_quality': f"{course['instructor_quality']:.2f}/4.0",
            'workload': f"{course['work_required']:.2f}/4.0"
        })
    return formatted_courses

# Format the data for the prompt
formatted_courses = format_course_data(all_relevant_courses)


response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents = f"""
        You are a friendly and knowledgeable course advisor at UPenn. A student has come to you with this question: {query}

        Based on your knowledge of the university's courses and the student's needs, you've identified these potentially relevant courses: {formatted_courses}

        This course data includes real student feedback and ratings on a scale (typically 1-4), covering:
        - course_quality: Overall student satisfaction with the course
        - difficulty: How challenging students found the course
        - instructor_quality: Student ratings of the instructor's teaching effectiveness
        - work_required: Amount of workload/time commitment required
        - department: The academic department offering the course
        - course_name: The specific course title

        Your role is to have a helpful conversation with the student, just like an in-person advising session. Use this student feedback data to:
        - Recommend courses that balance quality, difficulty, and workload appropriately for their needs
        - Point out courses with particularly strong instructors or high student satisfaction
        - Help them understand what to expect in terms of difficulty and time commitment
        - Consider how different courses might fit into their academic goals and schedule
        - Explain your reasoning so they understand why you're suggesting certain courses over others

        Provide personalized advice that helps them make informed decisions about their coursework, drawing on the actual experiences of past students.
    """
)

print('Final Response')
print(response.candidates[0].content.parts[0].text)


