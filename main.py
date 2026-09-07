import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag import index_document, ask_question


app = FastAPI(title="ResolveAI")


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# Request Model
# =====================================

class QuestionRequest(BaseModel):
    question: str
    document_name: str


# =====================================
# Home
# =====================================

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# =====================================
# Health Check
# =====================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ResolveAI"
    }


# =====================================
# Upload Document
# =====================================

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )


    os.makedirs("uploads", exist_ok=True)


    file_path = os.path.join(
        "uploads",
        file.filename
    )


    # Read uploaded file
    content = await file.read()


    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )


    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)


    print()
    print("=" * 50)
    print(f"Upload received: {file.filename}")
    print("=" * 50)


    # Index document
    try:

        chunk_count = index_document(
            file_path,
            file.filename
        )

    except Exception as error:

        print("Indexing error:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Document indexing failed: {str(error)}"
        )


    print()
    print(f"Document indexed successfully: {file.filename}")
    print(f"Total chunks: {chunk_count}")
    print("=" * 50)


    # Return JSON
    return {
        "message": "Document uploaded successfully",
        "document": file.filename,
        "chunks_indexed": chunk_count
    }


# =====================================
# Ask Question
# =====================================

@app.post("/ask")
def ask(request: QuestionRequest):

    if not request.document_name:
        raise HTTPException(
            status_code=400,
            detail="No document selected."
        )


    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    try:

        answer = ask_question(
            request.question,
            request.document_name
        )

    except Exception as error:

        print("Question error:", error)

        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate answer: {str(error)}"
        )


    return {
        "question": request.question,
        "document": request.document_name,
        "answer": answer
    }


# =====================================
# Frontend Files
# =====================================

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)