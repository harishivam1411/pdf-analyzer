import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers.chat_router import chat_router
from app.routers.pdf_router import pdf_router

from app.routers.health_router import health_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PDF Summarizer",
    description="Extract and summarize information from PDF documents using LLMs.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Server checkup"])
app.include_router(pdf_router, tags=["PDF Processing"])
app.include_router(chat_router, tags=["LLM chat"])

@app.get("/")
async def root():
    return {"message": "PDF Summarizer API",
            "version": "1.0.0",
            "purpose": "Summarizing PDF documents",
            "description": "A detailed PDF summarizer designed and implemented by Hari Shivam."}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=7000,
        reload=True
    )
