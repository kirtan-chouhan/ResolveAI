# ResolveAI

<img width="754" height="434" alt="image" src="https://github.com/user-attachments/assets/8cd13162-d4ba-4be6-bfd5-ac05127f6f27" />


> An AI-powered PDF Question Answering System built using Retrieval-Augmented Generation (RAG), Google Gemini, Pinecone, FastAPI, and Docker.

<p align="center">
  <img src="screenshots/resolveai.png" alt="ResolveAI Interface" width="900">
</p>

## 🚀 Overview

ResolveAI is an AI-powered document question-answering application that allows users to upload a PDF and ask questions about its content.

Instead of sending the entire document directly to the Large Language Model, ResolveAI uses a **Retrieval-Augmented Generation (RAG)** pipeline.

The document is first processed, divided into smaller chunks, converted into vector embeddings, and stored in a Pinecone vector database. When a user asks a question, the question is converted into an embedding and the most relevant document chunks are retrieved using semantic similarity search.

These retrieved chunks are then provided as context to Google Gemini, which generates the final answer.

The system is designed to answer questions using the uploaded document context and avoid generating unsupported answers when the required information is not available.

---

## 🌐 Live Demo

**ResolveAI is deployed as a Docker-based web service on Render.**

Live application:

https://resolveai-s9aj.onrender.com/

---

## 🎯 Problem Statement

Traditional document search relies heavily on keyword matching. This can make it difficult to find information when the user's question uses different words or phrasing from the document.

For example:

A document may contain:

> "Retrieval-Augmented Generation combines information retrieval with language generation."

A user may ask:

> "What is the combination of searching information and generating an AI response called?"

A traditional keyword search may struggle to identify the relationship.

ResolveAI uses **semantic vector search** so that questions and document content can be matched based on their meaning rather than exact keywords.

---

## 💡 Solution

ResolveAI implements the following pipeline:

```text
PDF Document
     ↓
Text Extraction
     ↓
Text Chunking
     ↓
Gemini Embeddings
     ↓
Pinecone Vector Database
```

For a user question:

```text
User Question
     ↓
Question Embedding
     ↓
Pinecone Similarity Search
     ↓
Top Relevant Chunks
     ↓
Context Construction
     ↓
Google Gemini
     ↓
Final Answer
```

This allows the application to retrieve relevant information from the document before asking the LLM to generate an answer.

---

# ✨ Features

- 📄 PDF document upload
- 🔍 Semantic document search
- ✂️ Automatic text chunking
- 🧠 Gemini-powered embeddings
- 🗄️ Pinecone vector database
- 🤖 Google Gemini-powered answer generation
- 📚 Context-aware question answering
- 🚫 Context-based "I don't know" handling
- ⚡ Batched embedding generation
- ⚡ Batched Pinecone vector uploads
- 🌐 FastAPI backend
- 🎨 Responsive HTML/CSS/JavaScript frontend
- 🐳 Dockerized application
- ☁️ Cloud deployment on Render
- 🔐 Environment-based API key management

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Web Frontend      │
                         │   HTML/CSS/JS       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
            ┌─────────────────┐           ┌─────────────────┐
            │   PDF Upload    │           │ User Question   │
            └────────┬────────┘           └────────┬────────┘
                     │                             │
                     ▼                             ▼
            ┌─────────────────┐           ┌─────────────────┐
            │ Text Extraction │           │ Query Embedding │
            └────────┬────────┘           └────────┬────────┘
                     │                             │
                     ▼                             ▼
            ┌─────────────────┐           ┌─────────────────┐
            │ Text Chunking   │           │    Pinecone     │
            └────────┬────────┘           │ Vector Search   │
                     │                   └────────┬────────┘
                     ▼                            │
            ┌─────────────────┐                    │
            │ Gemini Embedding│                    │
            └────────┬────────┘                    │
                     │                            │
                     ▼                            ▼
            ┌────────────────────────────────────────────┐
            │             Retrieved Context              │
            └──────────────────────┬─────────────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │    Google Gemini    │
                         │  Answer Generation  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Final Answer     │
                         └─────────────────────┘
```

---

# 🔄 RAG Pipeline

ResolveAI follows a Retrieval-Augmented Generation architecture consisting of two main stages.

## 1. Document Indexing

When a PDF is uploaded:

```text
PDF
 ↓
Extract Text
 ↓
Split into Chunks
 ↓
Generate Embeddings
 ↓
Store in Pinecone
```

### Step 1 — PDF Text Extraction

The application extracts text from the uploaded PDF using **PyPDF**.

### Step 2 — Text Chunking

Large documents are divided into smaller overlapping chunks using the LangChain Recursive Character Text Splitter.

Current configuration:

```text
Chunk Size   : 1000 characters
Chunk Overlap: 200 characters
```

Chunk overlap helps preserve context between neighboring chunks.

### Step 3 — Generate Embeddings

Each document chunk is converted into a numerical vector using:

```text
Gemini Embedding Model:
gemini-embedding-2
```

Embedding dimension:

```text
768
```

### Step 4 — Store Vectors

The generated embeddings, along with their corresponding text metadata, are stored in **Pinecone**.

The application uses the document name as the Pinecone namespace.

---

# 🔎 Question Answering Pipeline

When a user asks a question:

```text
Question
   ↓
Gemini Embedding
   ↓
768-dimensional Vector
   ↓
Pinecone Similarity Search
   ↓
Top 3 Relevant Chunks
   ↓
Context Construction
   ↓
Gemini
   ↓
Answer
```

## Query Embedding

The user's question is converted into an embedding using the same Gemini embedding model.

This allows the question to be compared with the stored document vectors.

## Similarity Search

Pinecone performs vector similarity search and retrieves the most relevant chunks.

The current implementation retrieves:

```text
Top K = 3
```

relevant chunks.

## Context Construction

The retrieved chunks are combined into a context that is passed to the generation model.

## Answer Generation

Google Gemini receives:

```text
Retrieved Context
+
User Question
```

and generates the final response.

The model is instructed to use only the provided document context.

If the required information cannot be found, the application responds with:

```text
I don't know based on the provided documents.
```

---

# 🤖 AI Models

ResolveAI uses Google Gemini for both embedding generation and answer generation.

## Embedding Model

```text
gemini-embedding-2
```

Configuration:

```text
Embedding Dimension: 768
```

## Generation Model

```text
gemini-3.5-flash-lite
```

The generation model is configured with minimal thinking to reduce response latency for this document Q&A use case.

---

# 🧠 Why RAG?

A Large Language Model already has general knowledge, but it may not know the contents of a private or newly uploaded document.

RAG solves this problem by providing relevant information from the document at query time.

Instead of:

```text
Question → LLM → Answer
```

ResolveAI uses:

```text
Question
   ↓
Retrieve relevant information
   ↓
Provide retrieved information to LLM
   ↓
Generate answer
```

This helps ground the generated response in the uploaded document.

---

# 🛠️ Technology Stack

## Backend

- Python
- FastAPI
- Uvicorn

## AI / Generative AI

- Google Gemini
- Gemini Embeddings
- Retrieval-Augmented Generation (RAG)

## Vector Database

- Pinecone

## Document Processing

- PyPDF
- LangChain Text Splitters

## Frontend

- HTML5
- CSS3
- JavaScript

## DevOps

- Docker
- Git
- GitHub

## Deployment

- Render

---

# 📂 Project Structure

```text
ResolveAI/
│
├── data/
│   └── dsa.pdf
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── uploads/
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── main.py
├── rag.py
├── requirements.txt
└── README.md
```

### Important files

### `main.py`

Contains the FastAPI application and API endpoints.

Main responsibilities:

- Serve frontend
- Handle PDF uploads
- Validate uploaded files
- Trigger document indexing
- Handle user questions
- Return generated answers
- Provide health endpoint

### `rag.py`

Contains the core RAG implementation.

Responsibilities include:

- PDF processing
- Text extraction
- Text chunking
- Embedding generation
- Pinecone indexing
- Vector retrieval
- Prompt construction
- Gemini answer generation

### `frontend/index.html`

Contains the user interface structure.

### `frontend/style.css`

Contains the styling and responsive UI design.

### `frontend/script.js`

Handles:

- PDF selection
- File upload
- Upload status
- Question submission
- API communication
- Answer rendering
- UI state management

### `Dockerfile`

Defines how the application is packaged into a Docker image.

### `requirements.txt`

Contains the Python dependencies required to run the application.

---

# 🔌 API Endpoints

ResolveAI exposes the following FastAPI endpoints.

## `GET /`

Serves the main ResolveAI frontend.

---

## `POST /upload`

Uploads and indexes a PDF document.

High-level flow:

```text
PDF
 ↓
Save File
 ↓
Extract Text
 ↓
Create Chunks
 ↓
Generate Embeddings
 ↓
Store Vectors in Pinecone
```

Returns information about the indexed document and number of chunks.

---

## `POST /ask`

Accepts a user question and selected document.

High-level flow:

```text
Question
 ↓
Generate Query Embedding
 ↓
Search Pinecone
 ↓
Retrieve Relevant Context
 ↓
Generate Gemini Response
 ↓
Return Answer
```

---

## `GET /health`

Provides a simple health check for the application.

---

# ⚡ Performance Optimization

During development, the initial implementation generated embeddings for document chunks individually.

For larger documents, this could result in a large number of API requests.

The indexing pipeline was therefore optimized to process embeddings in batches.

```text
Before:

Chunk 1 → API request
Chunk 2 → API request
Chunk 3 → API request
...
```

Optimized approach:

```text
Batch of chunks
      ↓
Embedding API
      ↓
Multiple vectors
      ↓
Pinecone batch upload
```

This reduces the number of API requests made during indexing.

The application also uses a low-latency Gemini generation model with minimal thinking configuration to improve response speed.

---

# 🐳 Docker

ResolveAI is fully containerized using Docker.

## Docker Architecture

```text
ResolveAI Source Code
        ↓
    Dockerfile
        ↓
   Docker Build
        ↓
 Docker Image
        ↓
 Docker Container
        ↓
    FastAPI
```

## Build Docker Image

```bash
docker build -t resolveai .
```

## Run Docker Container

```bash
docker run --name resolveai-app --env-file .env -p 8000:8000 resolveai
```

The application will then be available locally at:

```text
http://127.0.0.1:8000
```

---

# 💾 Persistent Uploads with Docker

For local Docker development, the `uploads` directory can be mounted from the host machine.

```bash
docker run --name resolveai-app \
  --env-file .env \
  -p 8000:8000 \
  -v "%cd%\uploads:/app/uploads" \
  resolveai
```

This maps:

```text
Windows:
ResolveAI/uploads/

        ↕
        
Docker:
/app/uploads/
```

This allows uploaded files to remain available on the host machine when the container is recreated.

---

# 🔐 Environment Variables

ResolveAI requires API keys for Gemini and Pinecone.

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

### Security

The `.env` file is intentionally excluded from Git using `.gitignore`.

API keys should never be committed to a public GitHub repository.

For deployment, environment variables are configured through the hosting platform instead of storing secrets in the source code.

---

# 💻 Local Development

## Prerequisites

Make sure the following are installed:

- Python
- Git
- Docker (optional for containerized execution)

## 1. Clone the Repository

```bash
git clone https://github.com/kirtan-chouhan/ResolveAI.git
cd ResolveAI
```

## 2. Create Virtual Environment

Windows:

```bash
py -m venv .venv
```

## 3. Activate Virtual Environment

```bash
.venv\Scripts\activate
```

## 4. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create:

```text
.env
```

and add:

```env
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

## 6. Run the Application

```bash
py -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# ☁️ Deployment

ResolveAI is deployed using a Docker-based deployment workflow.

```text
GitHub
   ↓
Render
   ↓
Dockerfile
   ↓
Docker Image
   ↓
Web Service
   ↓
ResolveAI
```

Deployment configuration:

```text
Platform : Render
Runtime  : Docker
Branch   : main
Plan     : Free
Port     : 8000
```

Environment variables are configured separately in the Render dashboard.

---

# 🔄 Development Workflow

The project follows a simple Git-based workflow:

```text
Local Development
       ↓
     Git
       ↓
   GitHub main
       ↓
    Render
       ↓
Automatic Deployment
```

Changes pushed to the GitHub repository can trigger a new deployment of the application.

---

# 🧪 Example Usage

### Step 1

Open ResolveAI.

### Step 2

Upload a PDF document.

### Step 3

Wait for document indexing to complete.

### Step 4

Ask a question related to the uploaded document.

For example:

```text
What is Retrieval-Augmented Generation?
```

### Step 5

ResolveAI retrieves relevant document chunks and generates an answer using the retrieved context.

---

# 📈 Key Technical Concepts Demonstrated

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation
- Large Language Models
- Text embeddings
- Vector databases
- Semantic similarity search
- Document chunking
- Context retrieval
- Prompt construction
- Hallucination control
- Batch processing
- REST APIs
- FastAPI
- Docker containerization
- Environment variable management
- Git/GitHub
- Cloud deployment

---

# 🎓 What I Learned

Through building ResolveAI, I gained practical understanding of:

### Generative AI

- LLM-based application development
- Gemini API integration
- Prompt construction
- Context-grounded generation

### RAG

- Document ingestion
- Chunking strategies
- Embeddings
- Vector similarity search
- Retrieval and context construction

### Backend Development

- FastAPI
- REST API design
- File upload handling
- Request validation
- API error handling

### Databases

- Vector database concepts
- Pinecone indexing
- Namespaces
- Metadata storage
- Similarity search

### DevOps

- Docker images
- Docker containers
- Port mapping
- Environment variables
- Containerized application deployment

### Cloud

- Git-based deployment
- Docker-based cloud deployment
- Environment-specific configuration

---

# 🚧 Current Limitations

The current version intentionally focuses on a simple and reliable document Q&A workflow.

Current limitations include:

- One selected document is used for the question-answering flow.
- Uploaded files are not permanently stored by the cloud deployment.
- Retrieval currently uses the top 3 Pinecone matches.
- The application does not currently maintain persistent chat history.
- No dedicated RAG evaluation framework is included.

---

# 🔮 Future Improvements

Possible future improvements include:

- Multi-document search
- Source citations and page references
- Persistent chat history
- Document summarization
- Suggested questions
- Retrieval reranking
- Hybrid keyword + vector search
- Automated RAG evaluation
- Agentic RAG
- Authentication and user accounts
- Persistent cloud storage

---

# 📌 Project Highlights

```text
✓ AI-powered PDF Question Answering
✓ Retrieval-Augmented Generation
✓ Gemini Embeddings
✓ Pinecone Vector Search
✓ Gemini LLM
✓ FastAPI Backend
✓ HTML/CSS/JavaScript Frontend
✓ Dockerized Application
✓ GitHub Repository
✓ Cloud Deployment
```

---

# 👨‍💻 Author

## Kirtan Kumar Chouhan

B.Tech Computer Science & Engineering

Interested in:

- Software Development
- Generative AI
- RAG Systems
- Agentic AI
- Backend Development

### Profiles

GitHub: https://github.com/kirtan-chouhan

LinkedIn: https://www.linkedin.com/in/kirtan-kumar-chouhan-64a021294/

---

# ⭐ Acknowledgements

ResolveAI was built as a hands-on project to understand how modern RAG-based AI applications are designed, developed, containerized, and deployed.

---

## 📄 License

This project is currently available for educational and portfolio purposes.
