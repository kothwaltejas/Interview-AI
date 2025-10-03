#!/usr/bin/env python3
"""
Test script for the PDF parser functionality.
"""

import sys
import json
from pathlib import Path

# Add the parsers directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from pdf_parser import (
        extract_text_from_pdf, 
        clean_json_response, 
        setup_llm_chain,
        validate_parsed_resume
    )
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_clean_json_response():
    """Test JSON cleaning function."""
    print("\n🧪 Testing JSON cleaning function...")
    
    test_cases = [
        ('{"name": "John Doe"}', '{"name": "John Doe"}'),
        ('```json\n{"name": "John Doe"}\n```', '{"name": "John Doe"}'),
        ('Here is the JSON: {"name": "John Doe"} End.', '{"name": "John Doe"}'),
        ('', '{}'),
        ('No JSON here', 'No JSON here')
    ]
    
    for input_str, expected in test_cases:
        result = clean_json_response(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {repr(input_str)} -> Output: {repr(result)}")

def test_validate_parsed_resume():
    """Test resume validation function."""
    print("\n🧪 Testing resume validation function...")
    
    # Test with incomplete data
    incomplete_data = {"name": "John Doe", "email": "john@example.com"}
    validated = validate_parsed_resume(incomplete_data)
    
    required_fields = ["name", "email", "phone", "education", "skills", "experience", "projects"]
    all_present = all(field in validated for field in required_fields)
    
    print(f"{'✅' if all_present else '❌'} Validation adds missing fields: {all_present}")
    print(f"Validated data keys: {list(validated.keys())}")

def test_setup_llm_chain():
    """Test LLM chain setup."""
    print("\n🧪 Testing LLM chain setup...")
    
    chain = setup_llm_chain()
    if chain is None:
        print("⚠️  LLM chain is None (likely missing GROQ_API_KEY)")
    else:
        print("✅ LLM chain setup successful")

def main():
    """Run all tests."""
    print("🚀 Starting PDF Parser Tests")
    print("=" * 50)
    
    test_clean_json_response()
    test_validate_parsed_resume()
    test_setup_llm_chain()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\nTo test with an actual PDF file, set GROQ_API_KEY environment variable and run:")
    print("python pdf_parser.py <path_to_pdf_file>")

if __name__ == "__main__":
    main()