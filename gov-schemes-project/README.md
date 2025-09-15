# 🏛️ Disability Schemes Discovery System

A comprehensive AI-powered system that helps disabled people easily discover welfare schemes tailored to their needs. Using vector similarity search with ChromaDB, users can search in plain language and instantly get relevant schemes with details like eligibility, state, disability type, and application links.

## ✨ Features

- **🔍 AI-Powered Search**: Natural language search using vector similarity
- **🎯 Smart Filtering**: Filter by state, disability type, and support type
- **📱 Modern Web Interface**: Responsive, accessible web interface
- **🚀 Fast API**: RESTful API with comprehensive documentation
- **📊 Analytics**: Statistics and insights about available schemes
- **🔧 Easy Setup**: Simple installation and configuration

## 🏗️ Architecture

```
src/
├── api/                    # FastAPI routes and endpoints
│   └── routes.py          # API route definitions
├── models/                # Pydantic data models
│   └── scheme_models.py   # Request/response models
├── rag/                   # RAG (Retrieval Augmented Generation) components
│   ├── chroma_config.py   # ChromaDB configuration
│   ├── retriever.py       # Search and retrieval logic
│   └── vector_store.py    # Vector database operations
├── utils/                 # Utility functions
│   ├── config.py          # Application settings
│   └── data_processor.py  # Data cleaning and validation
└── main.py               # FastAPI application entry point

static/
└── index.html            # Web interface

data/
├── disability_schemes.json  # Scheme data (JSON format)
└── chroma_db/              # ChromaDB vector database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gov-schemes-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the data**
   - Place your disability schemes JSON file in `data/disability_schemes.json`
   - The JSON should have the following structure:
   ```json
   {
     "schemes": [
       {
         "name": "Scheme Name",
         "description": "Detailed description",
         "state": "State Name",
         "disability_type": "visual_impairment",
         "support_type": "financial",
         "apply_link": "https://example.com/apply",
         "eligibility": "Eligibility criteria",
         "benefits": "Benefits provided",
         "contact_info": "Contact information",
         "validity_period": "Valid until date"
       }
     ]
   }
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Access the system**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## 📚 API Documentation

### Search Endpoints

#### POST /api/v1/schemes/search
Search for schemes using natural language queries.

**Request Body:**
```json
{
  "query": "education support for visually impaired in Karnataka",
  "top_k": 5,
  "state": "Karnataka",
  "disability_type": "visual_impairment",
  "support_type": "educational",
  "min_score": 0.7
}
```

**Response:**
```json
{
  "query": "education support for visually impaired in Karnataka",
  "results": [
    {
      "name_and_desc": "Scheme Name - Description",
      "state": "Karnataka",
      "disability_type": "visual_impairment",
      "support_type": "educational",
      "apply_link": "https://example.com/apply",
      "similarity_score": 0.85
    }
  ],
  "total_results": 1,
  "search_time_ms": 45.2,
  "filters_applied": {
    "state": "Karnataka",
    "disability_type": "visual_impairment",
    "support_type": "educational",
    "min_score": 0.7
  }
}
```

#### GET /api/v1/schemes/search
Simple search using query parameters.

**Parameters:**
- `query` (required): Search query
- `top_k` (optional): Number of results (default: 5)
- `state` (optional): Filter by state
- `disability_type` (optional): Filter by disability type
- `support_type` (optional): Filter by support type
- `min_score` (optional): Minimum similarity score

### Utility Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/schemes/stats` - Database statistics
- `GET /api/v1/schemes/states` - Available states
- `GET /api/v1/schemes/disability-types` - Disability types
- `GET /api/v1/schemes/support-types` - Support types
- `GET /api/v1/schemes/suggestions` - Search suggestions
- `POST /api/v1/schemes/populate` - Populate database

## 🔧 Configuration

The system can be configured using environment variables or by modifying `src/utils/config.py`:

```python
class Settings(BaseSettings):
    # Data paths
    data_path: str = "data/disability_schemes.json"
    db_dir: str = "data/chroma_db"
    
    # API settings
    api_title: str = "Disability Schemes Discovery System"
    api_version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ChromaDB settings
    collection_name: str = "disability_schemes"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Search settings
    default_top_k: int = 5
    max_top_k: int = 50
    min_similarity_score: float = 0.0
```

## 🗄️ Data Format

### Scheme Data Structure

Each scheme in the JSON file should have the following structure:

```json
{
  "name": "Scheme Name",
  "description": "Detailed description of the scheme",
  "state": "State where the scheme is available",
  "disability_type": "visual_impairment|hearing_impairment|mobility_impairment|intellectual_disability|autism|cerebral_palsy|multiple_disabilities|other",
  "support_type": "financial|educational|medical|employment|assistive_devices|transportation|housing|other",
  "apply_link": "URL to apply for the scheme",
  "eligibility": "Eligibility criteria (optional)",
  "benefits": "Benefits provided (optional)",
  "contact_info": "Contact information (optional)",
  "validity_period": "Validity period (optional)"
}
```

### Supported Disability Types

- `visual_impairment` - Visual disabilities
- `hearing_impairment` - Hearing disabilities
- `mobility_impairment` - Mobility/physical disabilities
- `intellectual_disability` - Intellectual disabilities
- `autism` - Autism spectrum disorders
- `cerebral_palsy` - Cerebral palsy
- `multiple_disabilities` - Multiple disabilities
- `other` - Other types

### Supported Support Types

- `financial` - Financial assistance
- `educational` - Educational support
- `medical` - Medical support
- `employment` - Employment opportunities
- `assistive_devices` - Assistive devices
- `transportation` - Transportation support
- `housing` - Housing support
- `other` - Other support types

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 🚀 Deployment

### Using Docker

1. **Create a Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8000
   
   CMD ["python", "src/main.py"]
   ```

2. **Build and run**
   ```bash
   docker build -t disability-schemes .
   docker run -p 8000:8000 disability-schemes
   ```

### Using Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DEBUG=False
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ChromaDB](https://www.trychroma.com/) for vector database
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Sentence Transformers](https://www.sbert.net/) for embeddings
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation

## 📞 Support

For support, email support@example.com or create an issue in the repository.

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Integration with government databases
- [ ] AI-powered eligibility checking
- [ ] Notification system for new schemes
- [ ] User accounts and favorites
- [ ] Scheme comparison features

---

**Made with ❤️ for the disability community**
