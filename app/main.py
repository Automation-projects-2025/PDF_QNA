import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from app.embeddings import extract_text_from_pdf, store_embeddings, search
from app.models import UploadResponse, QuestionRequest, AnswerResponse
from app.groq_api import generate_answer  # Import generate_answer
from dotenv import load_dotenv
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# CRUCIAL: Mount static files *BEFORE* defining routes
app.mount("/static", StaticFiles(directory="templates"), name="static")  # Correct placement

@app.get("/", response_class=HTMLResponse)  # Now this will work correctly
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_path = f"uploads/{file.filename}"  # Save the uploaded file
        with open(pdf_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # 1. Delete old index files (if any)
        index_dir = "index_files"
        for filename in os.listdir(index_dir):
            if filename.endswith((".index", ".json")):  # Delete .index and .json
                file_path = os.path.join(index_dir, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted old index file: {file_path}")
                except Exception as e:
                    print(f"Error deleting old index file {file_path}: {e}")

        # 2. Process the new PDF and store embeddings
        text_chunks = extract_text_from_pdf(pdf_path)
        store_embeddings(text_chunks, pdf_path)  # Pass the actual pdf_path

        return UploadResponse(message=f"'{file.filename}' processed successfully.")

    except Exception as e:
        print(f"Upload Error: {e}")  # Print the full error to the console
        raise HTTPException(status_code=500, detail=str(e))  # Re-raise to send to frontend

    finally:
        try:
            os.remove(pdf_path)  # Delete the uploaded PDF file
            print(f"Deleted uploaded PDF: {pdf_path}")
        except Exception as e:
            print(f"Error deleting uploaded PDF {pdf_path}: {e}")

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        print(request.pdf_name,request.question)
        pdf_name = os.path.splitext(os.path.basename(request.pdf_name))[0]
        print(f"Searching for PDF: {pdf_name}")  # Print the PDF name
        relevant_chunks = search(request.question, pdf_name)
        
        context = "\n".join(relevant_chunks)
      
        prompt = f"Based on the following context, answer the question:\n{context}\n\nQuestion: {request.question}"
        answer = generate_answer(prompt, GROQ_API_KEY) # Pass the API key
        return AnswerResponse(answer=answer)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

#Create uploads directory if not exist
os.makedirs("uploads", exist_ok=True)