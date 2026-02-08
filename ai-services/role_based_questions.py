"""
Role-based technical questions system for the interview platform.
These questions are predefined and don't require API calls.
"""

import random
from typing import List, Dict

class RoleBasedQuestions:
    """Manages role-specific technical questions for interviews."""
    
    ROLE_QUESTIONS = {
        "python_developer": [
            "Explain the difference between deep copy and shallow copy in Python.",
            "What are decorators and how do you use them?",
            "Explain the concept of list comprehension.",
            "What is the use of the 'with' statement in Python?",
            "How do you manage virtual environments?",
            "What is the difference between '==' and 'is' in Python?",
            "Explain the Global Interpreter Lock (GIL) in Python.",
            "What are lambda functions and when would you use them?",
            "How do you handle exceptions in Python?",
            "What is the difference between a list and a tuple?"
        ],
        "java_developer": [
            "What is the difference between JDK, JRE, and JVM?",
            "Explain the concept of inheritance in Java.",
            "What are checked and unchecked exceptions?",
            "How does garbage collection work in Java?",
            "Explain the use of the 'final' keyword.",
            "What is the difference between abstract class and interface?",
            "Explain method overloading vs method overriding.",
            "What are access modifiers in Java?",
            "How does multithreading work in Java?",
            "What is the difference between String, StringBuilder, and StringBuffer?"
        ],
        "mern_stack": [
            "What is the difference between state and props in React?",
            "How does MongoDB differ from SQL databases?",
            "Explain the lifecycle methods in React.",
            "What is Express.js and how does it work?",
            "How do you handle authentication in a MERN app?",
            "What are React Hooks and why are they useful?",
            "Explain the concept of middleware in Express.js.",
            "What is JSX and how does it work?",
            "How do you optimize MongoDB queries?",
            "What is the difference between server-side and client-side rendering?"
        ]
    }
    
    AVAILABLE_ROLES = list(ROLE_QUESTIONS.keys())
    
    @classmethod
    def get_available_roles(cls) -> List[str]:
        """Get list of available job roles."""
        return cls.AVAILABLE_ROLES.copy()
    
    @classmethod
    def get_role_display_names(cls) -> Dict[str, str]:
        """Get user-friendly display names for roles."""
        return {
            "python_developer": "Python Developer",
            "java_developer": "Java Developer", 
            "mern_stack": "MERN Stack Developer"
        }
    
    @classmethod
    def get_random_questions(cls, role: str, count: int = 4) -> List[str]:
        """
        Get random technical questions for a specific role.
        
        Args:
            role: The job role key (e.g., 'python_developer')
            count: Number of questions to return (default: 4)
            
        Returns:
            List of random questions for the role
        """
        if role not in cls.ROLE_QUESTIONS:
            raise ValueError(f"Role '{role}' not found. Available roles: {cls.AVAILABLE_ROLES}")
        
        questions = cls.ROLE_QUESTIONS[role]
        
        # If count is greater than available questions, return all
        if count >= len(questions):
            return questions.copy()
        
        # Return random sample
        return random.sample(questions, count)
    
    @classmethod
    def get_all_questions(cls, role: str) -> List[str]:
        """Get all questions for a specific role."""
        if role not in cls.ROLE_QUESTIONS:
            raise ValueError(f"Role '{role}' not found. Available roles: {cls.AVAILABLE_ROLES}")
        
        return cls.ROLE_QUESTIONS[role].copy()
    
    @classmethod
    def get_question_count(cls, role: str) -> int:
        """Get total number of questions available for a role."""
        if role not in cls.ROLE_QUESTIONS:
            return 0
        
        return len(cls.ROLE_QUESTIONS[role])


class RoleBasedInterviewPhase:
    """Manages the role-based technical interview phase."""
    
    def __init__(self, role: str, question_count: int = 4):
        """
        Initialize the role-based interview phase.
        
        Args:
            role: The selected job role
            question_count: Number of questions to ask (default: 4)
        """
        self.role = role
        self.question_count = question_count
        self.questions = RoleBasedQuestions.get_random_questions(role, question_count)
        self.current_question_index = 0
        self.answers = []
        self.completed = False
    
    def get_current_question(self) -> str:
        """Get the current technical question."""
        if self.current_question_index >= len(self.questions):
            return None
        
        return self.questions[self.current_question_index]
    
    def submit_answer(self, answer: str) -> bool:
        """
        Submit an answer for the current question.
        
        Args:
            answer: The candidate's answer
            
        Returns:
            True if there are more questions, False if completed
        """
        if self.current_question_index >= len(self.questions):
            return False
        
        # Store the answer
        self.answers.append({
            'question': self.questions[self.current_question_index],
            'answer': answer.strip(),
            'question_number': self.current_question_index + 1
        })
        
        # Move to next question
        self.current_question_index += 1
        
        # Check if completed
        if self.current_question_index >= len(self.questions):
            self.completed = True
            return False
        
        return True
    
    def get_progress(self) -> Dict:
        """Get current progress information."""
        return {
            'current_question': self.current_question_index + 1,
            'total_questions': len(self.questions),
            'completed': self.completed,
            'role': self.role,
            'role_display': RoleBasedQuestions.get_role_display_names().get(self.role, self.role)
        }
    
    def get_completion_message(self) -> str:
        """Get the final completion message."""
        role_display = RoleBasedQuestions.get_role_display_names().get(self.role, self.role)
        
        return f"""🎉 **Thank you for completing the interview!**

We've covered:
- Personal introduction and background questions
- Questions based on your resume and experience  
- {len(self.questions)} technical questions for {role_display}

Your responses have been recorded and will be reviewed by our team. We appreciate the time you've taken to participate in this interview process.

**Next Steps:**
- Our team will review your responses
- You'll hear back from us within 2-3 business days
- Feel free to reach out if you have any questions

Thank you once again, and we look forward to potentially working with you! 🚀"""