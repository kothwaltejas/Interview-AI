# GitHub Copilot Instructions for IntervuAI

## Project Overview
IntervuAI is a comprehensive AI-powered mock interview platform that helps users practice interviews with real-time feedback. The platform includes resume parsing, audio analysis, mood detection, confidence scoring, and interactive AI avatars.

## Project Structure & Architecture

### Frontend (React + TypeScript)
- **Location**: `/frontend/`
- **Framework**: React 18 with TypeScript
- **Styling**: Material-UI (MUI) and custom CSS with glass-morphism effects
- **State Management**: React hooks and context (Redux if needed later)
- **Key Components**:
  - Dashboard with analytics and progress tracking
  - Interview interface with real-time feedback
  - Audio recorder with WebRTC
  - Resume upload and parser integration
  - User profile and settings

### Backend (Node.js + Express)
- **Location**: `/backend/`
- **Runtime**: Node.js with Express.js
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: JWT-based auth system
- **Real-time**: Socket.io for live interview features
- **File Upload**: Multer for resume and audio files
- **API Structure**: RESTful APIs with proper error handling

### AI Services (Python)
- **Location**: `/ai-services/`
- **Framework**: Python with Flask/FastAPI
- **ML Libraries**: TensorFlow, PyTorch, spaCy, NLTK, librosa
- **Services**:
  - Resume parser using NLP
  - Audio analysis for speech quality
  - Mood detection from facial expressions
  - Confidence scoring algorithms

### Shared Code
- **Location**: `/shared/`
- **Purpose**: Common TypeScript types, constants, and utilities
- **Usage**: Shared between frontend, backend, and type definitions

## Development Guidelines

### Code Style & Patterns
- Use **TypeScript** throughout the project for type safety
- Follow **functional programming** patterns where possible
- Implement **proper error handling** with try-catch blocks
- Use **async/await** instead of Promises
- Follow **React best practices** with hooks and functional components
- Implement **proper loading states** and error boundaries

### Naming Conventions
- **Files**: Use kebab-case for files (`user-dashboard.tsx`)
- **Components**: Use PascalCase (`UserDashboard`)
- **Functions**: Use camelCase (`getUserProfile`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_ENDPOINTS`)
- **Interfaces**: Prefix with 'I' or use descriptive names (`User`, `InterviewSession`)

### API Design
- Use RESTful conventions (`GET /api/users`, `POST /api/interviews`)
- Implement proper HTTP status codes
- Return consistent JSON responses with `success`, `data`, `message` structure
- Use middleware for authentication, validation, and error handling
- Implement rate limiting and security headers

### Database Schema
- Design MongoDB collections for:
  - Users (authentication, profile, preferences)
  - Interviews (sessions, questions, responses, results)
  - Resumes (parsed data, skills, experience)
  - Analytics (performance metrics, progress tracking)

## Feature Implementation Guidelines

### Resume Parsing
- Accept PDF, DOC, DOCX formats
- Extract: personal info, skills, experience, education, projects
- Use NLP libraries like spaCy for text processing
- Store parsed data in structured format
- Provide skill recommendations and gap analysis

### Audio Recording & Analysis
- Use WebRTC for browser-based recording
- Implement real-time audio streaming
- Analyze: clarity, pace, volume, filler words, pauses
- Provide instant feedback during interviews
- Store audio files securely with proper compression

### Mood Detection
- Use facial recognition during video interviews
- Detect emotions: confident, nervous, excited, calm, stressed
- Track mood changes throughout the interview
- Provide mood-based recommendations
- Respect privacy with local processing when possible

### Confidence Scoring
- Analyze multiple factors: voice quality, response time, body language
- Provide real-time confidence metrics
- Track improvement over time
- Generate personalized recommendations
- Use machine learning for accuracy improvement

### AI Avatar Integration
- Create interactive virtual interviewer
- Implement natural conversation flow
- Adapt questions based on user responses
- Provide realistic facial expressions and gestures
- Support multiple interview types (technical, behavioral, mixed)

## Security & Privacy Considerations
- Implement proper authentication and authorization
- Encrypt sensitive data (personal info, audio files)
- Use HTTPS for all communications
- Implement file upload validation and sanitization
- Follow GDPR/privacy regulations for data handling
- Use environment variables for sensitive configuration

## Testing Strategy
- **Unit Tests**: Jest for React components and Node.js functions
- **Integration Tests**: API endpoint testing with Supertest
- **E2E Tests**: Playwright or Cypress for user workflows
- **AI Model Tests**: Python testing for ML accuracy and performance

## Performance Optimization
- Implement lazy loading for React components
- Use React.memo for expensive components
- Optimize bundle size with code splitting
- Implement caching strategies for API responses
- Use CDN for static assets
- Optimize database queries with proper indexing

## Deployment & DevOps
- Use Docker containers for consistent environments
- Implement CI/CD pipelines for automated testing and deployment
- Use environment-specific configurations
- Implement proper logging and monitoring
- Use cloud services (AWS, GCP) for scalability

## Current Development Status
- ✅ Project structure established
- ✅ Basic HTML/CSS dashboard created
- 🔄 Backend API development in progress
- 🔄 React frontend implementation planned
- 🔄 AI services development planned
- 🔄 Database integration planned

## Code Generation Preferences
When generating code, please:
1. **Use TypeScript** for all frontend and shared code
2. **Include proper error handling** and loading states
3. **Add JSDoc comments** for complex functions
4. **Implement responsive design** for UI components
5. **Use modern ES6+ features** and React hooks
6. **Include proper validation** for user inputs
7. **Follow security best practices** for authentication and data handling
8. **Implement proper testing** structure when generating test files
9. **Use semantic HTML** and accessibility features
10. **Optimize for performance** with lazy loading and memoization

## Dependencies to Prefer
- **Frontend**: React, TypeScript, Material-UI, Axios, Socket.io-client
- **Backend**: Express, Mongoose, JWT, Multer, Socket.io, Joi
- **AI/ML**: TensorFlow, PyTorch, spaCy, NLTK, librosa, OpenCV
- **Testing**: Jest, Supertest, Playwright, pytest
- **Development**: ESLint, Prettier, Nodemon, Concurrently

## Avoid
- Avoid using class components in React (use functional components)
- Avoid inline styles (use Material-UI or CSS modules)
- Avoid hardcoded values (use environment variables and constants)
- Avoid synchronous operations (use async/await)
- Avoid storing sensitive data in local storage
- Avoid overly complex state management (keep it simple initially)
