# ai-services/app.py

import streamlit as st
import json
import os
from resume_parser.parsers.pdf_parser import parse_resume_with_llm, validate_parsed_resume
from question_generator import generate_interview_questions

st.set_page_config(page_title="Resume Parser & Interview Question Generator", layout="wide")
st.title("🎯 Resume Parser & Interview Question Generator")

# API Key is now hardcoded in the parser
with st.sidebar:
    st.markdown("### API Configuration")
    st.success("API Key: Hardcoded for testing")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"], help="Upload a PDF resume to parse and generate interview questions")

if uploaded_file:
    st.info("Parsing resume... this may take a few seconds.")
    
    try:
        # Get file content as bytes
        file_content = uploaded_file.read()
        
        # Parse using the corrected function
        result = parse_resume_with_llm(file_content)
        
        if "error" in result:
            st.error(f"Failed to parse resume: {result['error']}")
            if "raw_response" in result:
                with st.expander("Debug Info"):
                    st.code(result["raw_response"])
        else:
            # Validate the result
            validated_result = validate_parsed_resume(result)
            
            st.success("Resume parsed successfully!")
            
            # Create two columns for resume data and questions
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📄 Extracted Resume Information")
                st.json(validated_result)

                st.download_button(
                    label="Download Resume JSON",
                    data=json.dumps(validated_result, indent=2, ensure_ascii=False),
                    file_name="parsed_resume.json",
                    mime="application/json"
                )
            
            with col2:
                st.subheader("🎯 Generated Interview Questions")
                
                # Generate interview questions
                try:
                    questions = generate_interview_questions(validated_result)
                    
                    if questions:
                        for i, question in enumerate(questions, 1):
                            with st.expander(f"Q{i}: {question['type'].title()} Question"):
                                st.write(f"**Question {i}:**")
                                st.write(question['question'])
                                
                                if question['metadata']:
                                    st.write("**Details:**")
                                    for key, value in question['metadata'].items():
                                        if key not in ['project_data', 'experience_data']:  # Skip large data
                                            st.write(f"- {key.replace('_', ' ').title()}: {value}")
                        
                        # Download questions as JSON
                        st.download_button(
                            label="Download Questions JSON",
                            data=json.dumps(questions, indent=2, ensure_ascii=False),
                            file_name="interview_questions.json",
                            mime="application/json"
                        )
                        
                        # Summary
                        st.write("**📊 Questions Summary:**")
                        question_types = {}
                        for q in questions:
                            q_type = q['type']
                            question_types[q_type] = question_types.get(q_type, 0) + 1
                        
                        for q_type, count in question_types.items():
                            st.write(f"- {q_type.title()}: {count} question(s)")
                    
                    else:
                        st.warning("No questions could be generated from this resume.")
                        
                except Exception as e:
                    st.error(f"Error generating questions: {e}")
                    st.write("Questions will be generated based on the parsed resume data.")

    except Exception as e:
        st.error(f"Unexpected error: {e}")
