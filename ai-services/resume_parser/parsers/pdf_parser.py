import fitz  # PyMuPDF
import json
import re
import logging
from typing import Dict, Any, Optional, Union
from langchain_core.prompts import PromptTemplate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# -------- Extract text from PDF --------
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    text = ""
    try:
        pdf = fitz.open(stream=file_content, filetype="pdf")
        for page in pdf:
            text += page.get_text()
        pdf.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise Exception(f"PDF extraction failed: {str(e)}")


# -------- Clean JSON --------
def clean_json_response(response: str) -> str:
    """Clean and extract JSON from LLM response."""
    if not response:
        return "{}"
    
    # Remove common prefixes
    response = re.sub(r'```json\s*', '', response, flags=re.IGNORECASE)
    response = re.sub(r'```\s*', '', response)
    response = re.sub(r'json\s*', '', response, flags=re.IGNORECASE)
    
    # Try to find JSON object
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    # If no JSON found, try to construct basic structure
    return response.strip() or "{}"


# -------- Setup LLM --------
def setup_llm_chain():
    """Setup the LLM chain for resume parsing."""
    from .llm_groq_config import get_llm
    
    # Get LLM dynamically
    current_llm = get_llm()
    if current_llm is None:
        logger.error("LLM is not initialized. Check GROQ_API_KEY environment variable.")
        return None
        
    template = """
You are an intelligent resume parser. Extract information from the resume text and return ONLY valid JSON in this exact format:

{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "education": [
    {{
      "degree": "degree name",
      "institution": "school name",
      "year": "graduation year"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "duration": "time period",
      "description": "job description"
    }}
  ],
  "projects": [
    {{
      "title": "project name",
      "tech": ["technology1", "technology2"],
      "description": "project description"
    }}
  ]
}}

Important Guidelines:
- Return ONLY the JSON object, no additional text or explanation
- If information is not available, use empty string for text fields and empty array for lists
- Ensure all JSON is properly formatted and escaped
- Extract skills from both dedicated skills section and experience descriptions
- For experience, include both duration and description if available

Resume Text:
{text}
"""
    prompt = PromptTemplate(input_variables=["text"], template=template)
    chain = prompt | current_llm
    return chain


# -------- Parse Resume --------
def parse_resume_with_llm(file_content: bytes, max_retries: int = 3) -> Dict[str, Any]:
    """
    Parse resume from PDF file content using LLM.
    
    Args:
        file_content: PDF file content as bytes
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary containing parsed resume data or error information
    """
    try:
        resume_text = extract_text_from_pdf(file_content)
        if not resume_text:
            return {"error": "Could not extract text from PDF"}
        
        chain = setup_llm_chain()
        if not chain:
            return {"error": "Could not setup LLM chain"}

        for attempt in range(max_retries):
            try:
                # Limit text to avoid token limits
                response = chain.invoke({"text": resume_text[:4000]}).content
                cleaned_response = clean_json_response(response)
                parsed_data = json.loads(cleaned_response)
                
                logger.info("Resume parsed successfully")
                return parsed_data
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {
                        "error": "Failed to parse JSON after multiple attempts", 
                        "raw_response": response, 
                        "cleaned_response": cleaned_response
                    }
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return {"error": f"Failed to process resume: {str(e)}"}
                    
        return {"error": "Unexpected failure"}
        
    except Exception as e:
        logger.error(f"Critical error in parse_resume_with_llm: {e}")
        return {"error": f"Critical parsing error: {str(e)}"}


def parse_resume_from_file_path(file_path: str) -> Dict[str, Any]:
    """
    Parse resume from a file path.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing parsed resume data or error information
    """
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
        return parse_resume_with_llm(file_content)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {"error": f"Could not read file: {str(e)}"}


def validate_parsed_resume(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean parsed resume data.
    
    Args:
        parsed_data: Raw parsed data from LLM
        
    Returns:
        Validated and cleaned resume data
    """
    if "error" in parsed_data:
        return parsed_data
    
    # Ensure required fields exist
    required_fields = ["name", "email", "phone", "education", "skills", "experience", "projects"]
    
    for field in required_fields:
        if field not in parsed_data:
            parsed_data[field] = [] if field in ["education", "skills", "experience", "projects"] else ""
    
    # Ensure lists are actually lists
    list_fields = ["education", "skills", "experience", "projects"]
    for field in list_fields:
        if not isinstance(parsed_data[field], list):
            parsed_data[field] = []
    
    return parsed_data


# -------- Main function for testing --------
def main():
    """Main function for testing the parser."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_parser.py <path_to_pdf>")
        return
    
    file_path = sys.argv[1]
    result = parse_resume_from_file_path(file_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        validated_result = validate_parsed_resume(result)
        print("Successfully parsed resume:")
        print(json.dumps(validated_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
