"""
Question Generator for Interview AI
Generates interview questions based on parsed resume data
"""

import json
from typing import Dict, Any, List


class InterviewQuestionGenerator:
    """Generate interview questions based on parsed resume data."""
    
    def __init__(self):
        self.questions = []
        self.current_question_number = 1
    
    def generate_questions(self, parsed_resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on parsed resume data.
        
        Args:
            parsed_resume: Dictionary containing parsed resume data
            
        Returns:
            List of question dictionaries with question text, type, and metadata
        """
        self.questions = []
        self.current_question_number = 1
        
        # Extract data from resume
        name = parsed_resume.get('name', 'Candidate')
        projects = parsed_resume.get('projects', [])
        experience = parsed_resume.get('experience', [])
        skills = parsed_resume.get('skills', [])
        
        # Clean and validate data
        if not isinstance(projects, list):
            projects = []
        if not isinstance(experience, list):
            experience = []
        if not isinstance(skills, list):
            skills = []
        
        # Filter out None values from skills
        skills = [skill for skill in skills if skill is not None and isinstance(skill, str) and skill.strip()]
        
        # 1. Introduction question
        self._add_introduction_question(name)
        
        # 2. Hobbies question
        self._add_hobbies_question()
        
        # 3. Project-based questions
        if projects:
            self._add_project_questions(projects)
        
        # 4. Experience/Internship questions or Skills questions
        if experience:
            self._add_experience_questions(experience)
        else:
            # If no experience, ask 3-4 skills questions
            self._add_skills_questions(skills)
        
        return self.questions
    
    def _add_question(self, question_text: str, question_type: str, metadata: Dict = None):
        """Add a question to the list."""
        question = {
            "id": self.current_question_number,
            "question": question_text,
            "type": question_type,
            "metadata": metadata or {}
        }
        self.questions.append(question)
        self.current_question_number += 1
    
    def _add_introduction_question(self, name: str):
        """Add introduction question."""
        intro_question = f"Hello {name}! Please introduce yourself. Tell us about your background, education, and what interests you about this field."
        self._add_question(intro_question, "introduction", {"name": name})
    
    def _add_hobbies_question(self):
        """Add hobbies question."""
        hobbies_question = "Can you tell us about your hobbies and interests? How do they relate to your current course of study or career goals?"
        self._add_question(hobbies_question, "hobbies")
    
    def _add_project_questions(self, projects: List[Dict]):
        """Add project-based questions."""
        for i, project in enumerate(projects[:3], 1):  # Limit to first 3 projects
            if not isinstance(project, dict):
                continue
                
            project_name = project.get('title', f'Project {i}')
            project_tech = project.get('tech', [])
            
            # Ensure project_name is a string
            if not isinstance(project_name, str):
                project_name = f'Project {i}'
            
            # Ensure project_tech is a list
            if not isinstance(project_tech, list):
                project_tech = []
            
            if i == 1:
                question_text = f"Let's talk about your projects. Can you explain your first project '{project_name}'? Please cover the following: What was the project about? What difficulties did you face during development? What tech stack did you use? What was the overall outcome and what did you learn from it?"
            else:
                question_text = f"Tell me about your {self._ordinal(i)} project '{project_name}'. What challenges did you encounter? What technologies did you use? How did this project contribute to your learning and what was the final result?"
            
            self._add_question(
                question_text, 
                "project", 
                {
                    "project_name": project_name,
                    "project_number": i,
                    "technologies": project_tech,
                    "project_data": project
                }
            )
    
    def _add_experience_questions(self, experience: List[Dict]):
        """Add experience/internship questions."""
        for i, exp in enumerate(experience[:2], 1):  # Limit to first 2 experiences
            if not isinstance(exp, dict):
                continue
                
            company = exp.get('company', 'the company')
            title = exp.get('title', 'your role')
            duration = exp.get('duration', '')
            
            # Ensure strings
            if not isinstance(company, str):
                company = 'the company'
            if not isinstance(title, str):
                title = 'your role'
            if not isinstance(duration, str):
                duration = ''
            
            if 'intern' in title.lower() or 'intern' in exp.get('description', '').lower():
                question_text = f"I see you had an internship as {title} at {company}. Can you tell me about your internship experience? What were your main responsibilities? What challenges did you face and how did you overcome them? What skills did you develop during this internship?"
            else:
                question_text = f"Tell me about your experience as {title} at {company}. What were your key responsibilities? What projects did you work on? How did this experience contribute to your professional growth?"
            
            self._add_question(
                question_text,
                "experience",
                {
                    "company": company,
                    "title": title,
                    "duration": duration,
                    "experience_data": exp
                }
            )
    
    def _add_skills_questions(self, skills: List[str]):
        """Add skills-based questions when no experience is available."""
        if not skills:
            # Default skills questions if no skills are parsed
            default_questions = [
                "What programming languages are you most comfortable with and why?",
                "Can you describe a challenging problem you solved using your technical skills?",
                "How do you stay updated with the latest technologies in your field?",
                "Tell me about a time when you had to learn a new technology quickly. How did you approach it?"
            ]
            for question in default_questions:
                self._add_question(question, "skills")
        else:
            # Generate questions based on parsed skills
            skill_groups = self._group_skills(skills)
            
            if 'programming' in skill_groups:
                prog_skills = ", ".join(skill_groups['programming'][:3])
                self._add_question(
                    f"I see you have experience with {prog_skills}. Can you explain which of these you're most proficient in and describe a project where you used it effectively?",
                    "skills",
                    {"skill_type": "programming", "skills": skill_groups['programming']}
                )
            
            if 'web' in skill_groups:
                web_skills = ", ".join(skill_groups['web'][:3])
                self._add_question(
                    f"You've mentioned {web_skills} in your skills. Can you walk me through how you would build a web application using these technologies?",
                    "skills",
                    {"skill_type": "web", "skills": skill_groups['web']}
                )
            
            if 'database' in skill_groups:
                db_skills = ", ".join(skill_groups['database'])
                self._add_question(
                    f"Regarding your database skills ({db_skills}), can you explain how you would design a database for a simple e-commerce application?",
                    "skills",
                    {"skill_type": "database", "skills": skill_groups['database']}
                )
            
            # General skills question
            self._add_question(
                "How do you approach learning new technologies? Can you give me an example of a recent skill you've acquired?",
                "skills",
                {"skill_type": "learning"}
            )
    
    def _group_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group skills by category."""
        skill_groups = {
            'programming': [],
            'web': [],
            'database': [],
            'other': []
        }
        
        programming_keywords = ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift']
        web_keywords = ['html', 'css', 'react', 'vue', 'angular', 'node', 'express', 'django', 'flask', 'bootstrap']
        database_keywords = ['mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'firebase', 'sql']
        
        for skill in skills:
            if skill is None or not isinstance(skill, str):
                continue
            skill_lower = skill.lower()
            categorized = False
            
            for keyword in programming_keywords:
                if keyword in skill_lower:
                    skill_groups['programming'].append(skill)
                    categorized = True
                    break
            
            if not categorized:
                for keyword in web_keywords:
                    if keyword in skill_lower:
                        skill_groups['web'].append(skill)
                        categorized = True
                        break
            
            if not categorized:
                for keyword in database_keywords:
                    if keyword in skill_lower:
                        skill_groups['database'].append(skill)
                        categorized = True
                        break
            
            if not categorized:
                skill_groups['other'].append(skill)
        
        # Remove empty groups
        return {k: v for k, v in skill_groups.items() if v}
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)."""
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return f"{n}{suffix}"
    
    def get_questions_summary(self) -> Dict[str, Any]:
        """Get a summary of generated questions."""
        summary = {
            "total_questions": len(self.questions),
            "question_types": {},
            "questions": self.questions
        }
        
        for question in self.questions:
            q_type = question['type']
            summary['question_types'][q_type] = summary['question_types'].get(q_type, 0) + 1
        
        return summary


def generate_interview_questions(parsed_resume: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convenience function to generate interview questions.
    
    Args:
        parsed_resume: Dictionary containing parsed resume data
        
    Returns:
        List of question dictionaries
    """
    try:
        generator = InterviewQuestionGenerator()
        return generator.generate_questions(parsed_resume)
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Return basic questions if generation fails
        basic_questions = [
            {
                "id": 1,
                "question": "Hello! Please introduce yourself and tell us about your background.",
                "type": "introduction",
                "metadata": {}
            },
            {
                "id": 2,
                "question": "Can you tell us about your hobbies and interests?",
                "type": "hobbies",
                "metadata": {}
            },
            {
                "id": 3,
                "question": "What programming languages are you most comfortable with?",
                "type": "skills",
                "metadata": {}
            },
            {
                "id": 4,
                "question": "Can you describe a challenging project you worked on?",
                "type": "skills",
                "metadata": {}
            }
        ]
        return basic_questions