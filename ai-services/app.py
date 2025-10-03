# ai-services/app.py

import streamlit as st
import json
import os
from resume_parser.parsers.pdf_parser import parse_resume_with_llm, validate_parsed_resume

st.set_page_config(page_title="AI Resume Parser", layout="wide")
st.title("AI Resume Parser (PDF Only)")

# API Key is now hardcoded in the parser
with st.sidebar:
    st.markdown("### API Configuration")
    st.success("API Key: Hardcoded for testing")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

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
            st.subheader("Extracted Information")
            st.json(validated_result)

            st.download_button(
                label="Download JSON",
                data=json.dumps(validated_result, indent=2, ensure_ascii=False),
                file_name="parsed_resume.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"Unexpected error: {e}")
