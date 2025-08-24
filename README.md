# 🧠 IntervuAI - Mock Interview Platform

A comprehensive AI-powered mock interview platform featuring resume parsing, real-time audio analysis, mood detection, confidence scoring, and interactive AI avatars.

## 🚀 Features

### Core Features (In Development)
- **🔍 Resume Parsing** - NLP-powered resume analysis and skill extraction
- **🎤 Audio Recording** - Real-time audio capture with speech analysis
- **😊 Mood Detection** - AI-based emotional state analysis during interviews
- **📊 Confidence Scoring** - Automated confidence level assessment
- **🤖 Interactive Avatar** - Virtual interviewer with adaptive questioning
- **📈 Analytics Dashboard** - Comprehensive performance tracking and insights

### Current Status
- ✅ Project structure created
- ✅ Basic HTML/CSS dashboard implemented
- 🔄 Backend API development (in progress)
- 🔄 Frontend React application (planned)
- 🔄 AI services implementation (planned)
- 🔄 Database integration (planned)

## 🏗️ Project Structure

```
IntervuAI/
├── 📁 frontend/                 # React.js frontend application
│   ├── 📁 src/
│   │   ├── 📁 components/      # Reusable UI components
│   │   │   ├── 📁 Dashboard/   # Dashboard components
│   │   │   ├── 📁 Avatar/      # Avatar-related components
│   │   │   ├── 📁 Interview/   # Interview interface components
│   │   │   ├── 📁 AudioRecorder/ # Audio recording components
│   │   │   └── 📁 ResumeUpload/  # Resume upload components
│   │   ├── 📁 pages/           # Page components
│   │   ├── 📁 services/        # API services
│   │   ├── 📁 hooks/           # Custom React hooks
│   │   ├── 📁 utils/           # Utility functions
│   │   └── 📁 types/           # TypeScript type definitions
│   └── 📁 public/              # Static assets & current HTML dashboard
│
├── 📁 backend/                 # Node.js backend API
│   ├── 📁 src/
│   │   ├── 📁 controllers/     # Route handlers
│   │   ├── 📁 models/          # Database models
│   │   ├── 📁 routes/          # API routes
│   │   ├── 📁 middleware/      # Custom middleware
│   │   ├── 📁 services/        # Business logic
│   │   ├── 📁 utils/           # Utility functions
│   │   └── 📁 config/          # Configuration files
│   └── 📁 uploads/             # File upload storage
│
├── 📁 ai-services/             # Python AI/ML services
│   ├── 📁 resume-parser/       # NLP resume parsing service
│   ├── 📁 audio-analysis/      # Audio processing service
│   ├── 📁 mood-detection/      # Mood detection service
│   ├── 📁 confidence-scoring/  # Confidence scoring service
│   └── 📁 shared/              # Shared AI utilities and models
│
├── 📁 shared/                  # Shared code across all services
│   ├── 📁 types/               # Common TypeScript type definitions
│   └── 📁 constants/           # Application constants and enums
│
├── 📁 docs/                    # Project documentation
├── 📁 tests/                   # Test files and test utilities
│   ├── 📁 unit/                # Unit tests
│   ├── 📁 integration/         # Integration tests
│   ├── 📁 e2e/                 # End-to-end tests
│   └── 📁 fixtures/            # Test data and mock files
│
└── 📄 README.md               # Project documentation
```

## 🛠️ Tech Stack

### Frontend
- **React.js** with TypeScript
- **Material-UI** / **Tailwind CSS** for styling
- **WebRTC** for audio/video capabilities
- **Socket.io-client** for real-time communication
- **Axios** for API requests

### Backend
- **Node.js** with Express.js
- **MongoDB** with Mongoose
- **Socket.io** for real-time features
- **Multer** for file uploads
- **JWT** for authentication
- **Joi** for input validation

### AI/ML Services
- **Python** with Flask/FastAPI
- **spaCy** / **NLTK** for NLP (resume parsing)
- **librosa** for audio analysis
- **OpenCV** for video processing
- **TensorFlow** / **PyTorch** for ML models

### Development Tools
- **TypeScript** for type safety
- **Jest** for testing
- **Prettier** for code formatting
- **ESLint** for code linting
- **Docker** for containerization (planned)

## 🚦 Getting Started

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **MongoDB** (or MongoDB Atlas)
- **npm** or **yarn**

### Quick Start (Current Demo)

1. **View the Dashboard**
   ```bash
   # Navigate to frontend folder
   cd frontend/public
   
   # Open index.html in your browser
   # Or use a local server:
   npx serve .
   ```

### Future Setup (Full Application)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IntervuAI
   ```

2. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Setup Backend**
   ```bash
   cd backend
   npm install
   cp .env.example .env
   # Configure your environment variables
   npm run dev
   ```

4. **Setup AI Services**
   ```bash
   cd ai-services
   pip install -r requirements.txt
   python main.py
   ```

## 📋 Development Roadmap

### Phase 1: Foundation (Current)
- [x] Project structure setup
- [x] Basic HTML/CSS dashboard
- [ ] Backend API skeleton
- [ ] Database schema design
- [ ] Authentication system

### Phase 2: Core Features
- [ ] React frontend implementation
- [ ] File upload system
- [ ] Basic resume parsing
- [ ] Audio recording functionality
- [ ] User management

### Phase 3: AI Integration
- [ ] Resume NLP analysis
- [ ] Audio analysis pipeline
- [ ] Mood detection system
- [ ] Confidence scoring algorithm
- [ ] Real-time analysis

### Phase 4: Advanced Features
- [ ] AI avatar integration
- [ ] Advanced analytics dashboard
- [ ] Performance tracking
- [ ] Recommendation system
- [ ] Interview simulation

### Phase 5: Production
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Deployment setup
- [ ] Monitoring and logging
- [ ] User testing and feedback

## 🎯 Current Demo Features

The current HTML/CSS dashboard includes:
- **Modern UI Design** with gradient backgrounds and glass-morphism effects
- **Feature Overview** showing all planned capabilities
- **Progress Indicators** for each feature development status
- **Responsive Design** that works on desktop and mobile
- **Interactive Elements** with hover effects and animations

## 🤝 Team Collaboration

This project is designed for team collaboration with clearly separated concerns:

- **Frontend Team**: React components, UI/UX, user interactions
- **Backend Team**: API development, database design, authentication
- **AI/ML Team**: Resume parsing, audio analysis, mood detection
- **DevOps Team**: Deployment, CI/CD, monitoring

## 🔧 Development Guidelines

### Code Structure
- Use **TypeScript** for type safety
- Follow **modular architecture**
- Implement **proper error handling**
- Write **comprehensive tests**
- Use **consistent naming conventions**

### Git Workflow
- Create **feature branches** for new development
- Use **descriptive commit messages**
- Submit **pull requests** for code review
- Maintain **clean commit history**

### Testing Strategy
- **Unit tests** for individual components/functions
- **Integration tests** for API endpoints
- **E2E tests** for user workflows
- **Performance tests** for AI services

## 📚 Documentation

- **API Documentation**: Will be generated using Swagger/OpenAPI
- **Component Documentation**: Using Storybook for React components
- **Architecture Docs**: Detailed system design in `/docs` folder
- **User Guide**: End-user documentation and tutorials

## 🔒 Security Considerations

- **JWT-based authentication**
- **Input validation and sanitization**
- **File upload security**
- **Rate limiting**
- **CORS configuration**
- **Environment variable protection**

## 🚀 Deployment

Future deployment will support:
- **Docker containerization**
- **AWS/GCP cloud deployment**
- **CI/CD pipelines**
- **Environment-specific configurations**
- **Monitoring and logging**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For questions and support:
- Create an issue in the repository
- Contact the development team
- Check the documentation in `/docs`

---

**Built with ❤️ by the IntervuAI Team**

*Current Status: Foundation Phase - Dashboard Demo Ready*
