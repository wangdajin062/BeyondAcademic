# BeyondAcademic (彼岸学术)

## AI-Powered Academic Writing System

BeyondAcademic is a comprehensive academic writing platform that combines powerful editing tools with AI-assisted features to enhance the quality and efficiency of scholarly writing.

## System Architecture

The system follows a **modular academic writing architecture**, structured into three primary components:

### 1. Article Management Module

The Article Management Module handles the complete lifecycle of academic articles:

- **Document Creation**: Create new articles with customizable templates (IEEE, Elsevier, ACM, Springer, Nature, Science)
- **Version Control**: Automatic version tracking for all content changes with detailed history
- **Document Organization**: Organize drafts, revisions, and final submissions
- **Status Tracking**: Track article status from draft to publication
- **Metadata Management**: Manage authors, keywords, references, and other metadata

**Key Features:**
- Automatic version creation on content updates
- Revert to previous versions
- Complete version history with change summaries
- Multiple article status states (draft, in_review, revised, submitted, published)

### 2. Central Academic Editor

The Academic Editor provides a rich editing environment specifically designed for academic writing:

- **Rich-Text Editing**: Intuitive interface for composing academic papers
- **LaTeX Support**: Convert plain text to LaTeX format for mathematical expressions
- **Real-time Grammar Correction**: Intelligent grammar and spelling suggestions
- **Formatting Guidance**: Template-specific formatting rules and validation
- **Citation Validation**: Check citation formatting and consistency
- **Academic Templates**: Pre-configured templates for major publishers

**Supported Templates:**
- IEEE
- Elsevier
- ACM
- Springer
- Nature
- Science
- Generic

### 3. AI-Assisted Knowledge Recommendation Module

This module leverages advanced AI to enhance the writing process:

- **Literature Search**: Smart search for relevant academic papers
- **High-Impact Papers**: Discover high-citation and influential research
- **Contextual Recommendations**: AI analyzes your content to suggest relevant literature
- **Language Optimization**: Real-time suggestions for more formal and clear academic writing
- **Sentence Improvement**: AI-powered sentence restructuring and enhancement
- **Citation Suggestions**: Automatically generate formatted citations

**Recommendation Types:**
- High-impact papers
- High-citation papers
- Recent publications
- Seminal works
- Context-relevant literature

### 4. Backend AI Capability Middleware

The backend infrastructure is powered by an **AI capability middleware**, which integrates various AI models and data sources:

- **Semantic Understanding**: Analyzes research intent, entities, topics, and complexity
- **Literature Retrieval Systems**: Advanced search algorithms across scholarly databases
- **SCI-Oriented Language Optimization**: Ensures content meets high academic standards
- **Keyword Extraction**: Automatic extraction of key terms and concepts
- **Abstract Generation**: AI-powered abstract summarization
- **Plagiarism Detection**: Check for similarity with existing literature
- **Structure Suggestion**: Recommend paper organization based on topic and template

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/NLP**: OpenAI, Transformers, spaCy, Sentence-Transformers
- **Database**: SQLAlchemy with PostgreSQL support
- **API**: RESTful API with automatic documentation

### Frontend
- **Framework**: React with TypeScript
- **Editor**: Monaco Editor for code/LaTeX, Rich text editor
- **State Management**: React Hooks
- **API Client**: Axios
- **UI Components**: Custom academic-focused components

## Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The backend API will be available at `http://localhost:8000`
API documentation available at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variable
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Quick Start

### Using the Backend API

```python
# Start the backend server
cd backend
python main.py

# The API will be available at:
# - Main API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Example API Usage

Create an article:
```bash
curl -X POST "http://localhost:8000/api/articles/?author=researcher" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deep Learning for Academic Writing",
    "abstract": "This paper explores...",
    "template": "IEEE",
    "authors": ["Dr. Smith"],
    "keywords": ["AI", "NLP", "Academic Writing"]
  }'
```

## Features

### Article Management
- ✅ Create, read, update, delete articles
- ✅ Automatic version control
- ✅ Version history tracking
- ✅ Revert to previous versions
- ✅ Status management (draft → published)
- ✅ Multiple template support

### Academic Editor
- ✅ Grammar and spelling checking
- ✅ Formatting validation
- ✅ LaTeX conversion
- ✅ Citation validation
- ✅ Template-specific rules
- ✅ Real-time suggestions

### AI Recommendations
- ✅ Semantic paper search
- ✅ Context-aware recommendations
- ✅ Language optimization
- ✅ Sentence improvement
- ✅ Citation generation
- ✅ High-impact paper discovery

### AI Middleware
- ✅ Semantic analysis
- ✅ Keyword extraction
- ✅ Abstract generation
- ✅ Plagiarism checking
- ✅ Structure suggestions
- ✅ Literature retrieval

## API Endpoints

### Article Management
- `POST /api/articles/` - Create article
- `GET /api/articles/` - List articles
- `GET /api/articles/{id}` - Get article
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article
- `GET /api/articles/{id}/versions` - Get version history
- `POST /api/articles/{id}/revert/{version}` - Revert to version

### Academic Editor
- `POST /api/editor/check/grammar` - Check grammar
- `POST /api/editor/check/formatting` - Check formatting
- `POST /api/editor/convert/latex` - Convert to LaTeX
- `POST /api/editor/improve` - Get improvement suggestions
- `GET /api/editor/templates/{template}/rules` - Get formatting rules
- `POST /api/editor/validate/citations` - Validate citations

### AI Recommendations
- `POST /api/recommendations/search` - Search papers
- `POST /api/recommendations/recommend` - Get recommendations
- `POST /api/recommendations/optimize/sentence` - Optimize sentence
- `POST /api/recommendations/optimize/paragraph` - Optimize paragraph
- `POST /api/recommendations/citations` - Get citations
- `GET /api/recommendations/papers/high-impact` - Get high-impact papers
- `GET /api/recommendations/papers/recent` - Get recent papers

## Project Structure

```
BeyondAcademic/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── api/                    # API routers
│   │   ├── article_router.py
│   │   ├── editor_router.py
│   │   └── recommendation_router.py
│   ├── models/                 # Data models
│   │   └── article.py
│   ├── services/               # Business logic
│   │   ├── article_service.py
│   │   ├── editor_service.py
│   │   └── recommendation_service.py
│   └── middleware/             # AI middleware
│       └── ai_middleware.py
├── frontend/
│   ├── package.json            # Node dependencies
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API services
│   │   └── types/              # TypeScript types
└── docs/                       # Documentation
```

## Development Roadmap

- [x] Article Management Module
- [x] Central Academic Editor
- [x] AI-Assisted Knowledge Recommendation
- [x] Backend AI Capability Middleware
- [ ] Database integration (PostgreSQL)
- [ ] User authentication (JWT/OAuth2)
- [ ] Real-time collaboration
- [ ] Advanced AI model integration (GPT-4, specialized academic models)
- [ ] Mobile application

## Security Considerations

**Important**: The current implementation uses a simplified authentication approach for development purposes. For production deployment:

1. **Authentication**: Replace the `author` parameter with proper JWT or OAuth2 authentication
2. **Authorization**: Implement role-based access control for articles
3. **Input Validation**: Enhanced validation for all user inputs
4. **Rate Limiting**: Implement API rate limiting to prevent abuse
5. **HTTPS**: Ensure all API calls are over HTTPS
6. **Environment Variables**: Store sensitive data (API keys, secrets) in environment variables
7. **Database Security**: Use connection pooling and prepared statements
8. **Dependency Updates**: Regularly update dependencies to patch security vulnerabilities

### Dependency Security

All dependencies have been updated to patched versions to address known vulnerabilities:
- `aiohttp>=3.13.3` - Fixed zip bomb, DoS, and directory traversal vulnerabilities
- `fastapi>=0.109.1` - Fixed ReDoS vulnerability
- `python-multipart>=0.0.18` - Fixed DoS and ReDoS vulnerabilities
- `torch>=2.6.0` - Fixed buffer overflow, use-after-free, and RCE vulnerabilities
- `transformers>=4.48.0` - Fixed deserialization vulnerabilities

**Recommendation**: Regularly check for security updates using tools like:
```bash
pip install safety
safety check
```

See `config/.env.example` for configuration templates.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is for academic use and research purposes.

---

**BeyondAcademic** - Enhancing Academic Writing with AI
