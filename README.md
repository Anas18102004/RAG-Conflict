# Smart Scheduler with RAG and MCP

An intelligent scheduling system that uses Retrieval-Augmented Generation (RAG) and Multi-Constraint Programming (MCP) to handle natural language scheduling requests and resolve conflicts.

## Features

- Natural language scheduling requests
- Intelligent conflict resolution
- Dark/light mode UI
- Real-time suggestions
- Mock data support
- Responsive design

## Tech Stack

### Frontend
- React
- Tailwind CSS
- Framer Motion
- Heroicons

### Backend
- FastAPI (Python)
- MongoDB
- FAISS for vector search
- Sentence Transformers
- DeepSeek API

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-scheduler
```

2. Set up the frontend:
```bash
cd frontend
npm install
npm start
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```
MONGODB_URL=mongodb://localhost:27017
DEEPSEEK_API_KEY=your_api_key_here
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

## Usage

1. Open http://localhost:3000 in your browser
2. Enter a natural language scheduling request (e.g., "Schedule a meeting with Alice next Monday")
3. The system will:
   - Analyze your request
   - Check for conflicts
   - Suggest optimal time slots
   - Provide alternatives if needed

## API Endpoints

- `POST /analyze-query`: Process natural language scheduling requests
- `GET /conflicts`: Get all scheduling conflicts
- `POST /upload`: Upload schedule data (CSV/JSON)
- `GET /users`: Get all users
- `GET /events`: Get all events
- `GET /constraints`: Get all constraints

## Project Structure

```
.
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── InputBox.jsx
│   │   │   └── ResultCards.jsx
│   │   └── App.jsx
│   └── package.json
└── backend/
    ├── main.py
    ├── models.py
    ├── database.py
    ├── rag.py
    ├── mcp.py
    ├── faiss_index.py
    └── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 