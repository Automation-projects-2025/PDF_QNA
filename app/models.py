from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str

class QuestionRequest(BaseModel):
    pdf_name: str
    question: str

class AnswerResponse(BaseModel):
    answer: str