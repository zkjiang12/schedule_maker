import json
import re
from typing import List, Optional

def parse_course_response(response) -> Optional[List[str]]:
    """
    Robustly parse course recommendations from various response formats.
    
    Handles:
    - Plain JSON arrays
    - JSON arrays wrapped in code blocks
    - JSON arrays with extra text
    - Malformed responses
    """
    
    try:
        # Extract the raw text from the response
        raw_text = response.candidates[0].content.parts[0].text
        print(f"Raw response text: {raw_text}")
        print(f"Response type: {type(raw_text)}")
        
        # Clean and extract JSON
        cleaned_json = extract_json_array(raw_text)
        
        if cleaned_json:
            courses = json.loads(cleaned_json)
            
            # Validate that it's a list of strings
            if isinstance(courses, list) and all(isinstance(course, str) for course in courses):
                print(f"Successfully parsed {len(courses)} courses")
                return courses
            else:
                print("Error: Parsed JSON is not a list of strings")
                return None
        else:
            print("Error: Could not extract valid JSON array")
            return None
            
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None

def extract_json_array(text: str) -> Optional[str]:
    """
    Extract JSON array from text, handling various formats.
    """
    
    # Method 1: Remove code block markers
    text = remove_code_blocks(text)
    
    # Method 2: Find JSON array using regex
    json_match = find_json_array_regex(text)
    if json_match:
        return json_match
    
    # Method 3: Find array by brackets
    json_match = find_json_array_brackets(text)
    if json_match:
        return json_match
    
    # Method 4: Try to clean and parse the entire text
    cleaned_text = text.strip()
    if cleaned_text.startswith('[') and cleaned_text.endswith(']'):
        return cleaned_text
    
    return None

def remove_code_blocks(text: str) -> str:
    """
    Remove markdown code block markers (```json, ```, etc.)
    """
    # Remove ```json and ``` markers
    text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*', '', text)
    
    # Remove single backticks
    text = text.replace('`', '')
    
    return text.strip()

def find_json_array_regex(text: str) -> Optional[str]:
    """
    Use regex to find JSON array pattern.
    """
    # Pattern to match JSON arrays
    pattern = r'\[(?:[^[\]]*(?:\[[^\]]*\])*)*[^[\]]*\]'
    
    matches = re.findall(pattern, text)
    
    for match in matches:
        try:
            # Test if it's valid JSON
            json.loads(match)
            return match
        except json.JSONDecodeError:
            continue
    
    return None

def find_json_array_brackets(text: str) -> Optional[str]:
    """
    Find JSON array by locating matching brackets.
    """
    # Find first '[' and last ']'
    start = text.find('[')
    end = text.rfind(']')
    
    if start != -1 and end != -1 and end > start:
        potential_json = text[start:end+1]
        
        try:
            # Test if it's valid JSON
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass
    
    return None

def parse_with_fallbacks(response, max_retries: int = 3) -> Optional[List[str]]:
    """
    Parse response with multiple fallback strategies.
    """
    
    # Try main parsing first
    result = parse_course_response(response)
    if result:
        return result
    
    # Fallback strategies
    raw_text = response.candidates[0].content.parts[0].text
    
    # Strategy 1: Try to extract course names from text even if not JSON
    courses = extract_course_names_from_text(raw_text)
    if courses:
        print(f"Extracted courses using text parsing: {courses}")
        return courses
    
    # Strategy 2: If all else fails, return None and let the caller handle it
    print("All parsing strategies failed")
    return None

def extract_course_names_from_text(text: str) -> Optional[List[str]]:
    """
    Extract course names from text even if not in JSON format.
    """
    # Remove code blocks
    text = remove_code_blocks(text)
    
    # Look for patterns like "Course Name" or 'Course Name'
    patterns = [
        r'"([^"]+)"',  # Double quotes
        r"'([^']+)'",  # Single quotes
        r'(?:^|\n)[\s\-\*]*([A-Z][^,\n]+?)(?:,|$|\n)',  # Lines starting with capital letters
    ]
    
    courses = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        if matches:
            # Filter out obviously wrong matches
            filtered_matches = [
                match.strip() for match in matches 
                if len(match.strip()) > 3 and not match.strip().lower().startswith('here')
            ]
            if filtered_matches:
                courses.extend(filtered_matches)
                break
    
    return courses if courses else None