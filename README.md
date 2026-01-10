# Ctrl-A: Accessible Welfare Schemes Platform

Ctrl-A is a comprehensive, accessibility-focused platform designed to connect persons with disabilities (PwD) to government welfare schemes. It features a "disability-first" design, robust personalization, and AI-driven tools.

## 🌟 Key Features

### 1. **Accessibility First Design**
- **High Contrast UI**: Dark mode interface designed for reduced eye strain and high visibility.
- **Voice Navigation**: Search for schemes using voice commands (Web Speech API).
- **Audio Readout**: Built-in text-to-speech reads out search results for visually impaired users.
- **Sign Language Support**: (Prototype) Input methods designed for sign language users.

### 2. **Personalized Recommendations**
- **Smart Filtering**: Matches users to schemes based on:
    - **Disability Type** (e.g., Mobility, Visual, Hearing). "Multiple" type users see all relevant schemes.
    - **Demographics**: Filters by **State**, **Age**, and **Income**.
    - **Logic**: Automatically hides schemes where the user is ineligible (e.g., income exceeds limit).
- **Dedicated Portal**: A personalized dashboard showing only high-confidence matches.

### 3. **Smart Notification System**
- **Proactive Alerts**: Notifies users when new schemes matching their specific profile are added.
- **Micro-Targeting**: Matches schemes to users based on State and Disability Type.

### 4. **Admin Management**
- **Scheme Control**: Full CRUD (Create, Read, Update, Delete) capabilities for government officials.
- **Deadline Management**: Automatically hides expired schemes.
- **Analytics**: Dashboard showing total active schemes, states covered, and user stats.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3 (Vanilla + Custom Variables), JavaScript (ES6+).
- **Auth Server**: Python (Flask) - Handles User Auth, Session Management, and Profile Data.
- **Scheme API**: Python (FastAPI) - Handles Vector Search (ChromaDB), Filtering, and Scheme Data.
- **Database**: 
    - **MongoDB**: User profiles, sessions, applications.
    - **ChromaDB**: Vector embeddings for semantic scheme search.
    - **JSON**: Fallback verification for scheme data.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB (Running locally or Atlas)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/ctrl-a.git
    cd ctrl-a
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Platform

You need to run two servers: the Auth Server (Ctrl-A) and the Scheme API (gov-schemes-project).

**Option 1: Quick Start (Windows)**
Run the two automated startup scripts in separate terminals:

1.  **Start Frontend/Auth Server**:
    ```bash
    cd Ctrl-A
    python run_server.py
    ```

2.  **Start Scheme API Server**:
    ```bash
    cd Ctrl-A
    python start_gov_schemes_server.py
    ```

**Option 2: Manual Start**

1.  **Start the Auth/Frontend Server (Flask)**
    ```bash
    cd Ctrl-A
    python auth_server.py
    ```
    *Runs on `http://localhost:5000`*

2.  **Start the Scheme API Server (FastAPI)**
    ```bash
    cd gov-schemes-project/src
    uvicorn api:app --reload --port 8002
    ```
    *Runs on `http://localhost:8002`*

---

## 📂 Project Structure

- **`Ctrl-A/`**: Core application logic.
    - `*.html`: Frontend pages (Login, Dashboard, Schemes).
    - `auth_server.py`: Main Flask application.
    - `database.py`: MongoDB interaction layer.
- **`gov-schemes-project/`**: AI & Search Logic.
    - `src/api/routes.py`: FastAPI endpoints for search and personalization.
    - `src/rag/`: Vector retrieval logic (ChromaDB).
    - `data/`: Scheme datasets.

---

## 🤝 Contributing
1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License
Distributed under the MIT License.
