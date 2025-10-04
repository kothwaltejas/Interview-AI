# ai-services/app.py

import streamlit as st
import json
import os
import sys
import time

# Add current directory to Python path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from resume_parser.parsers.pdf_parser import parse_resume_with_llm, validate_parsed_resume
from question_generator import generate_interview_questions
from interactive_interview import start_interview_session, continue_interview, InteractiveInterviewSystem
from role_based_questions import RoleBasedQuestions

st.set_page_config(page_title="AI Interview System", layout="wide")
st.title("🎯 AI-Powered Interactive Interview System")

# Initialize session state
if 'interview_system' not in st.session_state:
    st.session_state.interview_system = None
if 'interview_active' not in st.session_state:
    st.session_state.interview_active = False
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'last_positive_response' not in st.session_state:
    st.session_state.last_positive_response = None
if 'question_context' not in st.session_state:
    st.session_state.question_context = None
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None

# API Key is now hardcoded in the parser
with st.sidebar:
    st.markdown("### 🔧 System Status")
    st.success("API Key: Connected")
    
    if st.session_state.interview_active:
        st.info("✅ Interview in Progress")
        if st.button("🔄 Reset Interview"):
            st.session_state.interview_system = None
            st.session_state.interview_active = False
            st.session_state.conversation_history = []
            st.session_state.current_question = None
            st.rerun()
    else:
        st.warning("⏳ Upload resume to start")
    
    st.markdown("### 📊 Interview Progress")
    if st.session_state.interview_active and st.session_state.interview_system:
        # Get session info with question stats
        session_info = st.session_state.interview_system._get_session_info()
        question_stats = session_info.get('question_stats', {})
        
        st.metric("Total Questions", question_stats.get('total_questions', 0))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Asked", question_stats.get('questions_asked', 0))
            st.metric("Answered", question_stats.get('questions_answered', 0))
        with col2:
            st.metric("Skipped", question_stats.get('questions_skipped', 0))
            remaining = question_stats.get('total_questions', 0) - question_stats.get('questions_asked', 0)
            st.metric("Remaining", remaining)
        
        # Progress bar
        if question_stats.get('total_questions', 0) > 0:
            progress = question_stats.get('questions_asked', 0) / question_stats.get('total_questions', 1)
            st.progress(progress)
            st.caption(f"Progress: {progress:.1%}")
        
        # Question breakdown
        with st.expander("📋 Question Breakdown"):
            st.write(f"• Resume-based: {question_stats.get('resume_questions', 0)}")
            st.write(f"• Technical: {question_stats.get('role_questions', 0)}")
            if session_info.get('role'):
                role_name = RoleBasedQuestions.get_role_display_names().get(session_info['role'], session_info['role'])
                st.write(f"• Selected Role: {role_name}")
    else:
        st.write("Start an interview to see progress")

# Cache Management Section
with st.sidebar:
    st.markdown("---")
    st.subheader("🗄️ Cache Management")
    
    resume_cache_count = len(st.session_state.get('resume_cache', {}))
    question_cache_count = len(st.session_state.get('question_cache', {}))
    
    st.metric("Cached Resumes", resume_cache_count)
    st.metric("Cached Question Sets", question_cache_count)
    
    if resume_cache_count > 0 or question_cache_count > 0:
        st.caption("💡 Cached data prevents repeated API calls")
        
        if st.button("🗑️ Clear All Cache", type="secondary"):
            if 'resume_cache' in st.session_state:
                del st.session_state.resume_cache
            if 'question_cache' in st.session_state:
                del st.session_state.question_cache
            st.success("Cache cleared!")
            st.rerun()
    else:
        st.caption("No cached data yet")

# Main interface
tab1, tab2, tab3, tab4 = st.tabs(["📄 Resume Upload", "🎯 Interactive Interview", "📋 Static Questions", "🔍 Question Preview"])

with tab1:
    st.header("Step 1: Upload Your Resume")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"], help="Upload a PDF resume to parse and start interview")

    if uploaded_file:
        # Create cache key based on file content
        file_content = uploaded_file.read()
        file_hash = hash(file_content)
        
        # Initialize resume cache if not exists
        if 'resume_cache' not in st.session_state:
            st.session_state.resume_cache = {}
        
        # Check if we've already parsed this exact file
        if file_hash in st.session_state.resume_cache:
            st.info("🚀 Loading from cache - Resume already parsed!")
            validated_result = st.session_state.resume_cache[file_hash]
            st.session_state.resume_data = validated_result
        else:
            st.info("🔄 Parsing resume... this may take a few seconds.")
            
            try:
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
                    
                    # Cache the validated result
                    st.session_state.resume_cache[file_hash] = validated_result
                    st.session_state.resume_data = validated_result
                    
            except Exception as e:
                st.error(f"Unexpected error: {e}")
        
        # Show results if we have them
        if st.session_state.resume_data:
            st.success("✅ Resume parsed successfully!")
            
            # Show parsed resume data
            with st.expander("📄 View Parsed Resume Data"):
                st.json(st.session_state.resume_data)
            
            # Download option
            st.download_button(
                label="📥 Download Resume JSON",
                data=json.dumps(st.session_state.resume_data, indent=2, ensure_ascii=False),
                file_name="parsed_resume.json",
                mime="application/json"
            )
            
            # Role selection for technical questions
            st.subheader("📝 Select Job Role for Technical Questions")
            role_options = RoleBasedQuestions.get_role_display_names()
            
            selected_role = st.selectbox(
                "Choose the job role you're applying for:",
                options=list(role_options.keys()),
                format_func=lambda x: role_options[x],
                help="This will determine which technical questions you'll be asked"
            )
            
            st.info(f"You'll receive 3-4 technical questions for {role_options[selected_role]} after the resume-based questions.")
            
            # Start interview button
            if st.button("🚀 Start Interactive Interview", type="primary"):
                interview_system, first_response = start_interview_session(st.session_state.resume_data, selected_role)
                st.session_state.interview_system = interview_system
                st.session_state.interview_active = True
                st.session_state.current_question = first_response['question']
                st.session_state.conversation_history = []
                st.session_state.selected_role = selected_role
                st.success("Interview started! Go to the 'Interactive Interview' tab.")
                st.rerun()
            
            # Show cache status
            st.caption(f"🗄️ Cache Status: {len(st.session_state.resume_cache)} resumes cached, {len(st.session_state.get('question_cache', {}))} question sets cached")

with tab2:
    st.header("Step 2: Interactive Interview Session")
    
    if not st.session_state.interview_active:
        st.warning("⏳ Please upload and parse a resume first, then start the interview.")
        st.info("💡 **How it works:** Upload your resume in Tab 1, then come back here to start your interactive interview!")
    else:
        st.success("🎯 Interview in progress - Let's have a conversation!")
        
        # Show helpful tips
        with st.expander("💡 Interview Tips"):
            st.markdown("""
            **How to interact naturally:**
            - Answer questions in your own words
            - Be specific with examples when possible
            - If you want to skip a question, just type 'skip' or click the Skip button
            - Take your time - there's no rush!
            - The AI will give you positive feedback and ask follow-up questions when needed
            - You can provide detailed answers of any length
            """)
        
        # Current question
        if st.session_state.current_question:
            # Show positive response from previous answer if available
            if hasattr(st.session_state, 'last_positive_response') and st.session_state.last_positive_response:
                st.success(f"🎉 {st.session_state.last_positive_response}")
                # Clear the response after showing it
                st.session_state.last_positive_response = None
            
            # Show question context if available
            if hasattr(st.session_state, 'question_context') and st.session_state.question_context:
                st.info(st.session_state.question_context)
                # Clear the context after showing it
                st.session_state.question_context = None
            
            # Show analysis feedback if available
            if hasattr(st.session_state, 'last_analysis') and st.session_state.last_analysis:
                with st.expander("💡 Feedback on your previous answer"):
                    st.write(st.session_state.last_analysis)
                # Clear the analysis after showing it
                st.session_state.last_analysis = None
            
            st.markdown("### 🎤 Current Question:")
            st.markdown(f"**{st.session_state.current_question}**")
            
            # Answer input
            answer = st.text_area(
                "Your Answer:",
                height=150,
                placeholder="Type your answer here... Be detailed and specific. There's no length limit - feel free to provide thorough explanations.\\n\\nType 'skip' if you want to move to the next question.",
                key=f"answer_input_{st.session_state.current_question.replace(' ', '_').replace('?', '').replace('.', '')[:50]}"
            )
            
            # Buttons for submit and skip
            col1, col2 = st.columns([3, 1])
            with col1:
                submit_answer = st.button("📤 Submit Answer", type="primary")
            with col2:
                skip_question = st.button("⏭️ Skip Question")
            
            # Process submission
            if submit_answer or skip_question:
                if skip_question:
                    answer_to_process = "skip"
                elif answer.strip():
                    answer_to_process = answer
                else:
                    st.warning("Please provide an answer before submitting.")
                    answer_to_process = None
                
                if answer_to_process:
                    # Process the answer
                    response = continue_interview(st.session_state.interview_system, answer_to_process)
                    
                    # Store conversation
                    st.session_state.conversation_history.append({
                        "question": st.session_state.current_question,
                        "answer": answer_to_process if answer_to_process != "skip" else "Skipped",
                        "timestamp": response.get("timestamp", "")
                    })
                    
                    if response['status'] == 'success':
                        # Store positive response to show before next question
                        if response.get('positive_response'):
                            st.session_state.last_positive_response = response['positive_response']
                        
                        st.session_state.current_question = response['question']
                        
                        if response.get('is_followup'):
                            st.session_state.question_context = "🔄 Follow-up question based on your previous answer."
                        else:
                            st.session_state.question_context = "➡️ Moving to the next question."
                        
                        if response.get('analysis'):
                            st.session_state.last_analysis = response['analysis']
                        
                        # Use rerun to refresh the interface
                        st.rerun()
                        
                    elif response['status'] == 'completed':
                        # Store final positive response
                        if response.get('positive_response'):
                            st.session_state.last_positive_response = response['positive_response']
                        
                        st.session_state.interview_active = False
                        st.session_state.current_question = None
                        st.success("🎉 Congratulations! Interview completed successfully!")
                        
                        # Show the thank you message
                        completion_message = response.get('message', 'Thank you for completing the interview!')
                        st.markdown(completion_message)
                        
                        # Add delay with visual countdown
                        st.info("⏳ Processing your interview results...")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # 12-second countdown
                        for i in range(12):
                            progress_bar.progress((i + 1) / 12)
                            status_text.text(f"Finalizing assessment... {12 - i} seconds remaining")
                            time.sleep(1)
                        
                        progress_bar.empty()
                        status_text.empty()
                        st.success("✅ Assessment ready!")
                        
                        # Show final assessment
                        st.markdown("### 📊 Final Interview Statistics")
                        
                        # Get question statistics
                        session_info = st.session_state.interview_system._get_session_info()
                        question_stats = session_info.get('question_stats', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Questions", question_stats.get('total_questions', 0))
                        with col2:
                            st.metric("Questions Asked", question_stats.get('questions_asked', 0))
                        with col3:
                            st.metric("Questions Answered", question_stats.get('questions_answered', 0))
                        with col4:
                            st.metric("Questions Skipped", question_stats.get('questions_skipped', 0))
                        
                        # Calculate percentages
                        total_asked = question_stats.get('questions_asked', 1)
                        answered_pct = (question_stats.get('questions_answered', 0) / total_asked) * 100 if total_asked > 0 else 0
                        skipped_pct = (question_stats.get('questions_skipped', 0) / total_asked) * 100 if total_asked > 0 else 0
                        
                        st.markdown("### 📊 Response Rate Analysis")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Response Rate", f"{answered_pct:.1f}%")
                        with col2:
                            st.metric("Skip Rate", f"{skipped_pct:.1f}%")
                        
                        # Interview breakdown
                        st.markdown("### 📋 Interview Breakdown")
                        role_name = RoleBasedQuestions.get_role_display_names().get(session_info.get('role', ''), 'Unknown')
                        
                        breakdown_info = f"""
                        **Interview Structure:**
                        - Resume-based questions: {question_stats.get('resume_questions', 0)}
                        - Technical questions: {question_stats.get('role_questions', 0)}
                        - Selected role: {role_name}
                        - Total duration: Approximately {total_asked * 2} minutes
                        """
                        st.markdown(breakdown_info)
                        
                        # Download interview summary
                        interview_summary = {
                            "interview_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "question_statistics": question_stats,
                            "role_selected": role_name,
                            "conversation_history": st.session_state.conversation_history,
                            "response_rate": f"{answered_pct:.1f}%",
                            "skip_rate": f"{skipped_pct:.1f}%"
                        }
                        
                        st.download_button(
                            label="📥 Download Interview Summary",
                            data=json.dumps(interview_summary, indent=2, ensure_ascii=False),
                            file_name=f"interview_summary_{time.strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                        
                        st.rerun()
                        
                    else:
                        st.error(f"Error: {response.get('message', 'Unknown error')}")
        
        # Show conversation history
        if st.session_state.conversation_history:
            st.markdown("### 💬 Conversation History")
            with st.expander("View Previous Q&A"):
                for i, conv in enumerate(st.session_state.conversation_history, 1):
                    st.markdown(f"**🎤 Q{i}:** {conv['question']}")
                    st.markdown(f"**💬 A{i}:** {conv['answer']}")
                    st.markdown("---")

with tab3:
    st.header("Step 3: Static Question Generation")
    
    if not st.session_state.resume_data:
        st.warning("⏳ Please upload and parse a resume first.")
    else:
        st.info("📋 Generate a static list of interview questions based on the resume")
        
        if st.button("🎯 Generate Static Questions"):
            try:
                questions = generate_interview_questions(st.session_state.resume_data)
                
                if questions:
                    st.success(f"✅ Generated {len(questions)} questions!")
                    
                    for i, question in enumerate(questions, 1):
                        with st.expander(f"Q{i}: {question['type'].title()} Question"):
                            st.write(f"**Question {i}:**")
                            st.write(question['question'])
                            
                            if question['metadata']:
                                st.write("**Context:**")
                                for key, value in question['metadata'].items():
                                    if key not in ['project_data', 'experience_data']:  # Skip large data
                                        st.write(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    # Download questions as JSON
                    st.download_button(
                        label="📥 Download Questions JSON",
                        data=json.dumps(questions, indent=2, ensure_ascii=False),
                        file_name="static_interview_questions.json",
                        mime="application/json"
                    )
                    
                    # Summary
                    st.markdown("### 📊 Questions Summary")
                    question_types = {}
                    for q in questions:
                        q_type = q['type']
                        question_types[q_type] = question_types.get(q_type, 0) + 1
                    
                    for q_type, count in question_types.items():
                        st.write(f"- **{q_type.title()}:** {count} question(s)")
                
                else:
                    st.warning("No questions could be generated from this resume.")
                    
            except Exception as e:
                st.error(f"Error generating questions: {e}")

with tab4:
    st.header("🔍 Interview Question Preview")
    st.info("This tab shows ALL questions that will be asked during the interview - perfect for preparation!")
    
    # Complete Interview Preview
    if st.session_state.resume_data:
        st.subheader("🎯 Complete Interview Flow Preview")
        
        # Role selection for preview
        preview_role_key = st.selectbox(
            "Select role to preview complete interview:",
            options=list(RoleBasedQuestions.get_role_display_names().keys()),
            format_func=lambda x: RoleBasedQuestions.get_role_display_names()[x],
            key="preview_role_selector"
        )
        
        # Create cache key based on resume data and role
        cache_key = f"preview_{hash(str(st.session_state.resume_data))}_{preview_role_key}"
        
        # Initialize cache if not exists
        if 'question_cache' not in st.session_state:
            st.session_state.question_cache = {}
        
        if st.button("🔍 Preview Complete Interview Questions", type="primary"):
            st.markdown("---")
            st.markdown("### 📋 Complete Interview Question List")
            
            # Check if we have cached results
            if cache_key in st.session_state.question_cache:
                st.info("🚀 Loading from cache - No API calls needed!")
                cached_data = st.session_state.question_cache[cache_key]
                resume_questions = cached_data['resume_questions']
                role_questions = cached_data['role_questions']
            else:
                st.info("🔄 Generating questions - First time for this resume+role combination")
                
                # Generate questions and cache them
                preview_system = InteractiveInterviewSystem(preview_role_key)
                preview_system.resume_data = st.session_state.resume_data
                
                # Generate question plan (no API calls in this method)
                resume_questions = preview_system._generate_question_plan(st.session_state.resume_data)
                
                # Get role-based questions (no API calls)
                role_questions = RoleBasedQuestions.get_random_questions(preview_role_key, 4)
                
                # Cache the results
                st.session_state.question_cache[cache_key] = {
                    'resume_questions': resume_questions,
                    'role_questions': role_questions
                }
            
            # Display all questions in order
            question_counter = 1
            
            st.markdown("#### 🌟 Personal & Resume-Based Questions")
            for q in resume_questions:
                st.write(f"**Q{question_counter}:** {q['question']}")
                st.caption(f"Type: {q['type'].title()} | Expected: {q.get('expected_duration', 'N/A')}")
                question_counter += 1
            
            st.markdown(f"#### ⚙️ Technical Questions ({RoleBasedQuestions.get_role_display_names()[preview_role_key]})")
            for q in role_questions:
                st.write(f"**Q{question_counter}:** {q}")
                st.caption("Type: Technical | No API calls required")
                question_counter += 1
            
            # Summary
            total_resume_questions = len(resume_questions)
            total_role_questions = len(role_questions)
            total_questions = total_resume_questions + total_role_questions
            
            st.markdown("---")
            st.success(f"""
            📊 **Interview Summary:**
            - Personal/Resume Questions: {total_resume_questions}
            - Technical Questions: {total_role_questions}
            - **Total Questions: {total_questions}**
            - Selected Role: {RoleBasedQuestions.get_role_display_names()[preview_role_key]}
            """)
            
            st.info("💡 This is exactly what the candidate will experience during the interview!")
            
            # Show cache status
            st.caption(f"🗄️ Cache Status: {len(st.session_state.question_cache)} question sets cached")
    
    else:
        st.warning("⏳ Upload and parse a resume first to see the complete interview preview")
    
    st.markdown("---")
    st.caption("� This preview helps you prepare by showing all interview questions in advance")