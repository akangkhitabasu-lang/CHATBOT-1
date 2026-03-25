import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Langchain tracking
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "simple QnA chatbot with OLLAMA"

app = FastAPI(title="QnA Chatbot API")

# Setup CORS to allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local dev; recommend locking down in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant. Please respond to the user queries appropriately."),
        ("user", "Question: {question}")
    ]
)

class ChatRequest(BaseModel):
    question: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    answer: str

def generate_response(question, engine="llama3", temperature=0.7):
    llm = Ollama(model=engine, temperature=temperature)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    answer = chain.invoke({'question': question})
    return answer

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = generate_response(request.question, engine="llama3", temperature=request.temperature)
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

