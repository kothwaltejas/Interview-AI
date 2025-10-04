"""
Interactive Interview System with Groq API
Handles two-way communication for dynamic interview sessions with role-based technical questions
"""

import json
import os
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from role_based_questions import RoleBasedInterviewPhase


class InteractiveInterviewSystem:
    """Manages interactive interview sessions with dynamic question generation."""
    
    def __init__(self, selected_role: str = None):
        self.llm = self._get_llm()
        self.conversation_history = []
        self.current_question_index = 0
        self.planned_questions = []
        self.resume_data = {}
        self.interview_state = "not_started"  # not_started, in_progress, role_based, completed
        self.selected_role = selected_role
        self.role_phase = None  # Will be initialized when role questions start
        
        # Question counting system
        self.question_stats = {
            "total_questions": 0,
            "questions_asked": 0,
            "questions_answered": 0,
            "questions_skipped": 0,
            "resume_questions": 0,
            "role_questions": 0
        }
        
    def _get_llm(self):
        """Initialize Groq LLM."""
        api_key = os.getenv("GROQ_API_KEY", "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")
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=api_key,
            temperature=0.7
        )
    
    def initialize_interview(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize the interview session with resume data.
        
        Args:
            resume_data: Parsed resume information
            
        Returns:
            Dictionary with first question and session info
        """
        self.resume_data = resume_data
        self.conversation_history = []
        self.current_question_index = 0
        self.interview_state = "in_progress"
        
        # Generate initial question plan
        self.planned_questions = self._generate_question_plan(resume_data)
        
        # Initialize question statistics
        role_question_count = 4 if self.selected_role else 0
        self.question_stats = {
            "total_questions": len(self.planned_questions) + role_question_count,
            "questions_asked": 0,
            "questions_answered": 0,
            "questions_skipped": 0,
            "resume_questions": len(self.planned_questions),
            "role_questions": role_question_count
        }
        
        # Get the first question
        first_question = self._get_next_question()
        
        return {
            "status": "success",
            "question": first_question,
            "session_info": self._get_session_info()
        }
    
    def process_answer(self, answer: str) -> Dict[str, Any]:
        """
        Process candidate's answer and generate next question.
        
        Args:
            answer: Candidate's response to current question
            
        Returns:
            Dictionary with next question, feedback, and session info
        """
        if self.interview_state not in ["in_progress", "role_based"]:
            return {"status": "error", "message": "Interview session not active"}
        
        # Handle skip request
        if answer.lower().strip() in ['skip', 'skip to next', 'next question', 'skip this', 'move to next']:
            self.question_stats["questions_skipped"] += 1
            
            # Handle skip for role-based questions
            if self.interview_state == "role_based" and self.role_phase:
                has_more = self.role_phase.submit_answer("Skipped")
                if has_more:
                    next_question = self.role_phase.get_current_question()
                    return {
                        "status": "success",
                        "question": next_question,
                        "is_followup": False,
                        "positive_response": "No problem! Let's move on to the next question.",
                        "analysis": "",
                        "session_info": self._get_session_info()
                    }
                else:
                    # Role questions completed
                    return self._complete_interview()
            
            # Handle skip for resume-based questions
            else:
                current_question = self.planned_questions[self.current_question_index - 1] if self.current_question_index > 0 else {"question": "Unknown"}
                self.conversation_history.append({
                    "question": current_question.get("question", "Unknown"),
                    "answer": "Skipped",
                    "timestamp": self._get_timestamp()
                })
                
                next_question = self._get_next_question()
                if next_question:
                    return {
                        "status": "success",
                        "question": next_question,
                        "is_followup": False,
                        "positive_response": "No problem! Let's move on to the next question.",
                        "analysis": "",
                        "session_info": self._get_session_info()
                    }
                else:
                    return self._complete_interview()
        
        # Process normal answers (count as answered)
        self.question_stats["questions_answered"] += 1
        if self.interview_state == "role_based" and self.role_phase:
            # Handle role-based question answers
            has_more = self.role_phase.submit_answer(answer)
            
            if has_more:
                next_question = self.role_phase.get_current_question()
                return {
                    "status": "success",
                    "question": next_question,
                    "is_followup": False,
                    "positive_response": "Good answer! Let's continue with the technical questions.",
                    "analysis": "",
                    "session_info": self._get_session_info()
                }
            else:
                # Role questions completed
                return self._complete_interview()
        
        else:
            # Handle resume-based question answers
            current_question = self.planned_questions[self.current_question_index - 1] if self.current_question_index > 0 else {"question": "Unknown"}
            self.conversation_history.append({
                "question": current_question.get("question", "Unknown"),
                "answer": answer,
                "timestamp": self._get_timestamp()
            })
            
            # Generate positive response and analyze the answer
            positive_response = self._generate_positive_response(answer, current_question)
            analysis = self._analyze_answer(current_question, answer)
            
            # Check if we need a follow-up question
            if analysis.get("needs_followup", False):
                followup_question = self._generate_followup_question(current_question, answer, analysis)
                return {
                    "status": "success",
                    "question": followup_question,
                    "is_followup": True,
                    "positive_response": positive_response,
                    "analysis": analysis.get("feedback", ""),
                    "session_info": self._get_session_info()
                }
            
            # Move to next planned question
            next_question = self._get_next_question()
            
            if next_question:
                return {
                    "status": "success",
                    "question": next_question,
                    "is_followup": False,
                    "positive_response": positive_response,
                    "analysis": analysis.get("feedback", ""),
                    "session_info": self._get_session_info()
                }
            else:
                return self._complete_interview()
    
    def _complete_interview(self) -> Dict[str, Any]:
        """Complete the interview and return final message."""
        self.interview_state = "completed"
        
        if self.role_phase:
            completion_message = self.role_phase.get_completion_message()
        else:
            completion_message = """🎉 **Thank you for completing the interview!**

We've covered:
- Personal introduction and background questions
- Questions based on your resume and experience  

Your responses have been recorded and will be reviewed by our team. We appreciate the time you've taken to participate in this interview process.

**Next Steps:**
- Our team will review your responses
- You'll hear back from us within 2-3 business days
- Feel free to reach out if you have any questions

Thank you once again, and we look forward to potentially working with you! 🚀"""
        
        return {
            "status": "completed",
            "message": completion_message,
            "session_info": self._get_session_info()
        }
    
    def _generate_question_plan(self, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate initial question plan based on resume."""
        questions = []
        name = resume_data.get('name', 'Candidate')
        
        # 1. Introduction
        questions.append({
            "id": 1,
            "type": "introduction",
            "question": f"Hello {name}! Please introduce yourself. Tell us about your background, education, and what interests you about this field.",
            "expected_duration": "2-3 minutes",
            "key_points": ["background", "education", "interests"]
        })
        
        # 2. Hobbies
        questions.append({
            "id": 2,
            "type": "hobbies",
            "question": "Can you tell us about your hobbies and interests? How do they relate to your current course of study or career goals?",
            "expected_duration": "1-2 minutes",
            "key_points": ["hobbies", "relation to career"]
        })
        
        # 3. Projects
        projects = resume_data.get('projects', [])
        for i, project in enumerate(projects[:3], 3):
            project_name = project.get('title', f'Project {i-2}')
            question_text = f"Let's discuss your project '{project_name}'. Can you explain what it was about, the challenges you faced, the technologies you used, and the outcome?"
            
            questions.append({
                "id": i,
                "type": "project",
                "question": question_text,
                "expected_duration": "3-4 minutes",
                "key_points": ["project description", "challenges", "technologies", "outcome"],
                "project_data": project
            })
        
        # 4. Experience or Skills (only ask experience if there's actual professional experience)
        experience = resume_data.get('experience', [])
        
        # Filter to only include actual work experience/internships
        valid_experience = []
        for exp in experience:
            title = exp.get('title', '').lower()
            company = exp.get('company', '').strip()
            duration = exp.get('duration', '').strip()
            
            # Only consider it valid experience if:
            # 1. Has a company name that's not self-employed, academic, or extracurricular
            # 2. Has a job title that suggests actual employment (not leadership roles)
            # 3. Duration is specified (even if it's "3 months" or "summer")
            # 4. Company is not educational institution or club
            
            # Exclude self-employed, freelance, personal projects, academic institutions, clubs
            exclusion_indicators = [
                'self employed', 'self-employed', 'freelance', 'personal', 'own', 'individual',
                'college', 'university', 'school', 'institute', 'club', 'society', 'committee',
                'student', 'academic', 'campus', 'pes', 'mit', 'iit', 'nit', 'bits',
                'team', 'group', 'association', 'organization'
            ]
            is_excluded = any(indicator in company.lower() for indicator in exclusion_indicators)
            
            # Check for actual employment job titles (exclude leadership/academic roles)
            employment_keywords = ['intern', 'trainee', 'apprentice', 'employee', 'worker']
            professional_roles = ['analyst', 'consultant', 'specialist', 'engineer', 'developer', 'programmer']
            
            # Exclude leadership/academic titles that are typically extracurricular
            leadership_titles = ['head', 'co-head', 'leader', 'president', 'vice president', 'secretary', 'treasurer', 'coordinator', 'member']
            is_leadership_role = any(leadership in title for leadership in leadership_titles)
            
            has_employment_title = (
                any(keyword in title for keyword in employment_keywords) or
                any(role in title for role in professional_roles)
            )
            
            # Only include if it's actual employment at a real company
            if (company and 
                not is_excluded and
                has_employment_title and
                not is_leadership_role and
                duration and
                len(company) > 3 and
                'college' not in company.lower() and
                'university' not in company.lower()):
                valid_experience.append(exp)
        
        if valid_experience:
            for i, exp in enumerate(valid_experience[:2]):  # Limit to 2 experiences
                question_id = len(questions) + 1
                company = exp.get('company', 'the company')
                title = exp.get('title', 'your role')
                
                if 'intern' in title.lower():
                    question_text = f"Tell me about your internship experience as {title} at {company}. What were your main responsibilities and what did you learn?"
                else:
                    question_text = f"Describe your experience as {title} at {company}. What were your key accomplishments and responsibilities?"
                
                questions.append({
                    "id": question_id,
                    "type": "experience",
                    "question": question_text,
                    "expected_duration": "2-3 minutes",
                    "key_points": ["responsibilities", "accomplishments", "learning"],
                    "experience_data": exp
                })
        else:
            # Skills questions if no valid professional experience
            skills = resume_data.get('skills', [])
            skill_questions = [
                "What programming languages or technologies are you most comfortable with and why?",
                "Can you describe a challenging technical problem you've solved recently?",
                "How do you stay updated with new technologies in your field?",
                "Tell me about a time you had to learn something new quickly. How did you approach it?"
            ]
            
            for i, skill_q in enumerate(skill_questions[:2]):  # Limit to 2 skill questions
                questions.append({
                    "id": len(questions) + 1,
                    "type": "skills",
                    "question": skill_q,
                    "expected_duration": "2-3 minutes",
                    "key_points": ["technical skills", "problem solving", "learning ability"]
                })
        
        return questions
    
    def _get_next_question(self) -> Optional[str]:
        """Get the next question in the sequence, including role-based questions."""
        # First, check if we have more resume-based questions
        if self.current_question_index < len(self.planned_questions):
            question = self.planned_questions[self.current_question_index]["question"]
            self.current_question_index += 1
            self.question_stats["questions_asked"] += 1
            return question
        
        # If resume questions are done and we have a role selected, start role-based questions
        if self.selected_role and self.interview_state == "in_progress":
            self.interview_state = "role_based"
            if not self.role_phase:
                self.role_phase = RoleBasedInterviewPhase(self.selected_role, 4)
            
            # Get current question from role phase
            role_question = self.role_phase.get_current_question()
            if role_question:
                self.question_stats["questions_asked"] += 1
                return f"Now let's test your technical knowledge. {role_question}"
            
        # If we're in role_based state, continue with role questions
        if self.interview_state == "role_based" and self.role_phase:
            role_question = self.role_phase.get_current_question()
            if role_question:
                self.question_stats["questions_asked"] += 1
                return role_question
            else:
                # Role questions completed, move to final state
                self.interview_state = "completed"
                return None
        
        # No more questions
        return None
    
    def _analyze_answer(self, question: Dict[str, Any], answer: str) -> Dict[str, Any]:
        """Analyze candidate's answer using Groq API."""
        analysis_prompt = f"""
        You are an expert interviewer. Analyze the candidate's answer to determine if a follow-up question is needed.

        Question Type: {question.get('type', 'general')}
        Question: {question.get('question', '')}
        
        Candidate's Answer: {answer}
        
        Expected Key Points: {question.get('key_points', [])}
        Expected Duration: {question.get('expected_duration', 'N/A')}

        Analyze the answer and respond with JSON in this format:
        {{
            "needs_followup": true/false,
            "reason": "brief reason why followup is/isn't needed",
            "missing_points": ["list of key points not addressed"],
            "strength_areas": ["areas where candidate did well"],
            "feedback": "brief constructive feedback",
            "completeness_score": 1-10
        }}
        
        Guidelines:
        - needs_followup = true if answer is too brief, vague, or missing key technical details
        - needs_followup = true if candidate mentions something interesting that needs elaboration
        - needs_followup = false if answer comprehensively covers the key points
        - For technical questions, always check if enough technical detail was provided
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_text = response.content.strip()
            
            # Clean and parse JSON
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            print(f"Error in answer analysis: {e}")
            return {
                "needs_followup": False,
                "reason": "Analysis error",
                "missing_points": [],
                "strength_areas": [],
                "feedback": "Good response",
                "completeness_score": 7
            }
    
    def _generate_followup_question(self, original_question: Dict[str, Any], answer: str, analysis: Dict[str, Any]) -> str:
        """Generate a follow-up question based on the answer analysis."""
        followup_prompt = f"""
        Generate a natural follow-up question based on the candidate's answer.

        Original Question: {original_question.get('question', '')}
        Question Type: {original_question.get('type', 'general')}
        
        Candidate's Answer: {answer}
        
        Analysis:
        - Missing Points: {analysis.get('missing_points', [])}
        - Reason for Follow-up: {analysis.get('reason', '')}
        
        Generate a specific, natural follow-up question that:
        1. Addresses the missing information
        2. Feels conversational, not repetitive
        3. Helps the candidate elaborate on important points
        4. Is appropriate for the question type
        
        For technical questions, ask for specific implementation details.
        For experience questions, ask for concrete examples or outcomes.
        For project questions, dig deeper into challenges or learning.
        
        Return only the follow-up question, nothing else.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=followup_prompt)])
            return response.content.strip().strip('"')
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return "Could you elaborate on that a bit more?"
    
    def _generate_final_assessment(self) -> Dict[str, Any]:
        """Generate final interview assessment."""
        assessment_prompt = f"""
        Based on the complete interview conversation, provide a comprehensive assessment.

        Resume Data: {json.dumps(self.resume_data, indent=2)}
        
        Conversation History:
        {json.dumps(self.conversation_history, indent=2)}

        Provide assessment in JSON format:
        {{
            "overall_score": 1-10,
            "strengths": ["list of key strengths"],
            "areas_for_improvement": ["areas that need work"],
            "technical_competency": 1-10,
            "communication_skills": 1-10,
            "problem_solving": 1-10,
            "enthusiasm": 1-10,
            "detailed_feedback": "comprehensive feedback paragraph",
            "recommendation": "hire/consider/not_recommended",
            "key_takeaways": ["main points from interview"]
        }}
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=assessment_prompt)])
            assessment_text = response.content.strip()
            
            # Clean and parse JSON
            if "```json" in assessment_text:
                assessment_text = assessment_text.split("```json")[1].split("```")[0]
            elif "```" in assessment_text:
                assessment_text = assessment_text.split("```")[1].split("```")[0]
            
            return json.loads(assessment_text)
            
        except Exception as e:
            print(f"Error generating assessment: {e}")
            return {
                "overall_score": 7,
                "strengths": ["Participated in complete interview"],
                "areas_for_improvement": ["Assessment could not be generated"],
                "technical_competency": 7,
                "communication_skills": 7,
                "problem_solving": 7,
                "enthusiasm": 7,
                "detailed_feedback": "Interview completed successfully.",
                "recommendation": "consider",
                "key_takeaways": ["Complete interview session"]
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation."""
        return {
            "total_questions_asked": len(self.conversation_history),
            "planned_questions": self.planned_questions,
            "conversation_history": self.conversation_history,
            "current_state": self.interview_state,
            "resume_data": self.resume_data
        }
    
    def reset_interview(self):
        """Reset the interview session."""
        self.conversation_history = []
        self.current_question_index = 0
        self.planned_questions = []
        self.resume_data = {}
        self.interview_state = "not_started"
        self.role_phase = None
        self.question_stats = {
            "total_questions": 0,
            "questions_asked": 0,
            "questions_answered": 0,
            "questions_skipped": 0,
            "resume_questions": 0,
            "role_questions": 0
        }
    
    def _get_session_info(self) -> Dict[str, Any]:
        """Get current session information with question statistics."""
        total_questions = len(self.planned_questions)
        if self.role_phase:
            total_questions += self.role_phase.get_progress()["total_questions"]
        
        current_question = self.current_question_index
        if self.interview_state == "role_based" and self.role_phase:
            current_question = len(self.planned_questions) + self.role_phase.get_progress()["current_question"]
        
        return {
            "total_planned_questions": total_questions,
            "current_question": current_question,
            "interview_state": self.interview_state,
            "role": self.selected_role,
            "question_stats": self.question_stats.copy()
        }
    
    def _generate_positive_response(self, user_answer: str, current_question: Dict) -> str:
        """
        Generate an encouraging positive response to the user's answer.
        Designed to handle answers of any length.
        """
        # For role-based questions, use simple positive responses to avoid API calls
        if self.interview_state == "role_based":
            responses = [
                "Great answer! Your technical knowledge is showing.",
                "Excellent! That demonstrates good understanding.",
                "Perfect! I can see you have solid technical skills.",
                "Wonderful! That's a well-thought-out response.",
                "Outstanding! Your expertise is clear."
            ]
            import random
            return random.choice(responses)
        
        # For resume-based questions, use AI to generate contextual responses
        try:
            # Handle long answers by focusing on key aspects
            answer_preview = user_answer[:500] + "..." if len(user_answer) > 500 else user_answer
            
            prompt = f"""Generate a brief, encouraging response to this interview answer. 
            Be positive, specific, and natural. Keep it under 20 words.
            
            Question type: {current_question.get('type', 'general')}
            Answer preview: {answer_preview}
            
            Examples:
            - "That's wonderful! Your passion for the field really comes through."
            - "Excellent! I can see you have hands-on experience."
            - "Great answer! Your technical approach is impressive."
            - "Perfect! That shows strong problem-solving skills."
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return response.content.strip()
            
        except Exception as e:
            # Fallback to generic positive responses
            fallback_responses = [
                "That's a great answer! Thank you for sharing.",
                "Excellent! I appreciate the detailed response.",
                "Wonderful! Your experience really shows.",
                "Perfect! That's exactly what we wanted to hear."
            ]
            import random
            return random.choice(fallback_responses)
    
    def _analyze_answer(self, current_question: Dict, user_answer: str) -> Dict[str, Any]:
        """
        Analyze the user's answer to determine if follow-up is needed.
        Optimized to handle answers of any length.
        """
        # Simple analysis that doesn't always require follow-ups
        # This reduces API calls and makes the interview flow better
        
        answer_length = len(user_answer.split())
        
        # Basic analysis without AI for efficiency
        analysis = {
            "needs_followup": False,
            "feedback": "",
            "answer_quality": "good" if answer_length > 10 else "brief"
        }
        
        # Only generate follow-ups occasionally for specific question types
        question_type = current_question.get('type', 'general')
        
        if question_type == 'projects' and answer_length > 20 and "challenge" in user_answer.lower():
            analysis["needs_followup"] = True
            analysis["feedback"] = "Great detail about the challenges you faced!"
        elif question_type == 'experience' and answer_length > 15:
            analysis["needs_followup"] = True
            analysis["feedback"] = "Interesting experience! I'd like to know more."
        
        return analysis
    
    def _generate_followup_question(self, current_question: Dict, user_answer: str, analysis: Dict) -> str:
        """
        Generate a follow-up question based on the user's answer.
        Handles long answers by focusing on key themes.
        """
        try:
            # Extract key themes from the answer for better follow-up generation
            answer_preview = user_answer[:300] + "..." if len(user_answer) > 300 else user_answer
            question_type = current_question.get('type', 'general')
            
            prompt = f"""Based on this interview answer, generate a relevant follow-up question.
            Keep it natural and specific to what they mentioned.
            
            Question type: {question_type}
            Original question: {current_question.get('question', 'Unknown')}
            Answer preview: {answer_preview}
            
            Generate a follow-up that digs deeper into their experience or asks for more specific details.
            Keep the follow-up question under 25 words.
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            return response.content.strip()
            
        except Exception as e:
            # Fallback follow-up questions based on question type
            fallbacks = {
                'projects': "Can you tell me more about the most challenging part of that project?",
                'experience': "What was the most valuable thing you learned from that experience?",
                'skills': "How do you stay updated with the latest developments in this area?",
                'general': "That's interesting! Can you give me a specific example?"
            }
            
            return fallbacks.get(question_type, "Can you elaborate on that a bit more?")


# Convenience functions for Streamlit integration
def start_interview_session(resume_data: Dict[str, Any], selected_role: str = None) -> tuple:
    """
    Start a new interview session with resume data and optional role selection.
    
    Args:
        resume_data: Parsed resume information
        selected_role: Selected job role for technical questions (python_developer, java_developer, mern_stack)
        
    Returns:
        Tuple of (InteractiveInterviewSystem, first_question_response)
    """
    interview_system = InteractiveInterviewSystem(selected_role)
    first_response = interview_system.initialize_interview(resume_data)
    return interview_system, first_response


def continue_interview(interview_system: InteractiveInterviewSystem, answer: str) -> Dict[str, Any]:
    """
    Continue the interview with candidate's answer.
    
    Args:
        interview_system: Active interview system
        answer: Candidate's response
        
    Returns:
        Response with next question or completion status
    """
    return interview_system.process_answer(answer)