from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import fitz  # PyMuPDF
from datetime import datetime, timezone
from app.nlp import initialize_query_engine
from app.database import SessionLocal, engine
from app import crud, models

# Initialize DB and NLP
models.Base.metadata.create_all(bind=engine)
query_engine = initialize_query_engine()

app = FastAPI()

# CORS for dev + production frontend
origins = [
    'http://localhost:3000',
    'https://pdf-insight-app-full.vercel.app/',
    'https://pdf-insight-app-full-maanit-aroras-projects.vercel.app/'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema for query
class QueryRequest(BaseModel):
    question: str

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'application/pdf':
        return JSONResponse({"error": "Unsupported file type. Please upload a PDF file."}, status_code=400)

    try:
        contents = await file.read()

        # 🧠 Open PDF directly from memory buffer
        document = fitz.open(stream=contents, filetype="pdf")
        pdf_metadata = document.metadata
        num_pages = document.page_count
        text = ""

        for page_num in range(num_pages):
            page = document.load_page(page_num)
            text += page.get_text()

        # 💾 Save to DB
        pdf_info = crud.create_pdf_info(
            db=db,
            filename=file.filename,
            pdf_metadata=str(pdf_metadata),
            num_pages=num_pages
        )

        # 🔁 Reinitialize NLP engine with updated docs
        global query_engine
        query_engine = initialize_query_engine()

        return JSONResponsappe({
            "message": f"File uploaded successfully: {file.filename}",
            "filename": file.filename
        })

    except Exception as e:
        print(f"Error uploading file: {e}")
        return JSONResponse({"error": "Error uploading file."}, status_code=500)

@app.post("/api/query")
async def ask(request: QueryRequest):
    print("Received query request")

    if query_engine is None:
        print("NLP model has not been initialized")
        return JSONResponse({"error": "The NLP model has not been initialized."}, status_code=500)

    try:
        print(f"Processing query: {request.question}")
        llama_type_answer = query_engine.query(request.question)
        answer = str(llama_type_answer)

        if answer == "Empty Response":
            return JSONResponse({
                "answer": "I am sorry I couldn't comprehend :( Could you please ask the whole question again?"
            })

        return JSONResponse({"answer": answer})

    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
