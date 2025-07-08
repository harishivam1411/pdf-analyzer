# Universal PDF Analyzer

A powerful web application to analyze, summarize, and chat with any PDF document. Built with FastAPI (backend) and Streamlit (frontend), this tool supports research papers, business reports, technical manuals, policy documents, books, and more. This project leverages OpenAI's language models for summarization and interactive chat, with ChromaDB for vector storage. It provides a seamless user experience to extract insights from documents and engage in meaningful conversations about their content.

## 🚀 Features

- **Smart Summarization:**
  - Upload any PDF and get a comprehensive, auto-detected summary.
  - Extracts key insights, findings, and adapts to document type.
- **Interactive Chat:**
  - Ask questions about your document and get detailed, context-aware answers.
  - Explore specific sections or topics interactively.
- **Multiple Export Options:**
  - Download results as Text, Markdown, or JSON.
- **Robust Error Handling:**
  - Handles timeouts, connection errors, and invalid responses gracefully.

## 🏗️ Project Structure

```bash
main.py                # FastAPI backend entry point
streamlit_app.py       # Streamlit frontend app
requirements.txt       # Python dependencies
pyproject.toml         # Project metadata
.env                   # Environment variables
app/
  chroma_db/           # ChromaDB for vector storage
  routers/             # FastAPI routers (chat, pdf, health)
  services/            # Core logic for PDF, LLM, vector, chat
  pydantics/           # Pydantic models
  templates/           # Prompt templates
  utils/               # Utility files and sample data
```

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/harishivam1411/pdf-analyzer.git
cd pdf-analyzer
```

### 2. Install UV

```bash
pip install uv
```

### 2. Create a Virtual Environment

```bash
uv venv 
```

### 3. Install Dependencies

```bash
uv add -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_BASE_URL=http://127.0.0.1:7000
OPENAI_BASE_URL=https://api.openai.com/v1
VECTOR_PERSIST=True  # Set to True to enable persistent vector storage with ChromaDB, or False to use in-memory storage
```

### 5. Start the Backend (FastAPI)

```bash
uv run main.py
```

### 6. Start the Frontend (Streamlit)

```bash
uv run streamlit run streamlit_app.py
```

## 🖇️ API Endpoints

- `POST /upload-pdf`
  - Handles both summarization and chat setup (operation: 'summarize' or 'chat')
- `POST /chat`
  - Query the document in chat mode
- `GET /health`
  - Server health check

## 📄 Supported Document Types

- Research papers & academic articles
- Business reports & corporate documents
- Technical manuals & specifications
- Policy documents & legal texts
- Books, articles, presentations, and more

## 🛠️ Tips & Notes

- For best results, use high-quality PDF files
- Large documents may take longer to process
- Try specific questions in chat mode for detailed answers

## 🌟 Enhanced Experience

- Upload your PDF once and both summary and chat modes will be ready
- Switch between modes instantly without reprocessing
- Use specific questions in chat mode for detailed answers
- Export your results in multiple formats

## 📝 Notes

- The backend is built with FastAPI and exposes endpoints for PDF upload, summarization, and chat.
- The frontend is built with Streamlit and provides a seamless, interactive user experience.
- Both summary and chat modes are prepared simultaneously for instant switching.

## 🔧 Server Status & Troubleshooting

- The sidebar in the Streamlit app shows server status.
- If you see connection errors, ensure the FastAPI backend is running and the `API_BASE_URL` is set correctly in your `.env` file.
