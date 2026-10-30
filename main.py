# main.py
from fastapi import FastAPI, Depends
from 登录.auth import get_current_user
from 登录.rag_agent import chat_with_rag

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(query: str, user_id: str = Depends(get_current_user)):
    # user_id 由 JWT 解析得出，保证了数据隔离的安全性
    ai_response = await chat_with_rag(query, user_id)
    return {"response": ai_response}