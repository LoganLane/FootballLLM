import time

from fastapi import FastAPI, Header, Depends, HTTPException
from LLMConnector import respond_to_api
from auth import verify_api_key
from database import get_schema
from pydantic import BaseModel

from request_logger import add_log_to_db

app = FastAPI()

@app.get("/")

async def root():
    return {"message": "Hello World!"}

@app.get("/v1/health", status_code=200, dependencies=[])
def check_health():
    return {"status": "ok"}

@app.get("/v1/schema", dependencies=[Depends(verify_api_key)])
def schema():
    return get_schema()


class QuestionResponse(BaseModel):
    question_text: str
    answer: str
    sql: str
    question_sql_token_usage: int
    answer_token_usage: int
    latency_ms: float
    model_used: str


class QuestionRequest(BaseModel):
    question_text: str

@app.post("/v1/query", dependencies=[Depends(verify_api_key)])
def ask_question(question: QuestionRequest):
    timestamp = time.time()
    try:
        question_text, question_answer, question_sql, question_token, answer_token, latency_ms, model_used = respond_to_api(
            question.question_text)
        success = True
        error_message = None
        return QuestionResponse(question_text=question_text, answer=question_answer, sql=question_sql, question_sql_token_usage=question_token,
                                answer_token_usage=answer_token, latency_ms=latency_ms, model_used=model_used)
    except Exception as e:
        question_text = question.question_text
        question_answer = question_sql = question_token = answer_token = latency_ms = model_used = None
        success = False
        error_message = str(e)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        add_log_to_db(timestamp=timestamp, question_text=question_text, answer=question_answer, sql=question_sql, question_sql_token_usage=question_token,
                                answer_token_usage=answer_token, latency_ms=latency_ms, model_used=model_used, success=success, error_message = error_message)


