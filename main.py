from typing import List
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile

from functions.fn_authenticate_user import fn_authenticate_user
from functions.fn_create_chat_session import fn_create_chat_session
from functions.fn_create_chatbot import fn_create_chatbot
from functions.fn_create_conversation import fn_create_conversation
from functions.fn_create_user import fn_create_user
from fastapi.requests import Request

from functions.fn_delete_chat_session import fn_delete_chat_session
from functions.fn_delete_chatbot import fn_delete_chatbot
from functions.fn_delete_conversation import fn_delete_conversation
from functions.fn_delete_user import fn_delete_user
from functions.fn_get_chat_sessions_by_user import fn_get_chat_sessions_by_user
from functions.fn_get_chatbots_by_user import fn_get_chatbots_by_user
from functions.fn_get_conversations_by_chat_session import fn_get_conversations_by_chat_session
from functions.fn_update_chat_session import fn_update_chat_session
from functions.fn_update_chatbot import fn_update_chatbot
from functions.fn_update_user import fn_update_user
from functions.fn_chat import fn_chat
from functions.fn_upload_files import fn_upload_files
from functions.fn_get_files import fn_get_files

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/user")
async def create_user(request: Request):
    return await fn_create_user(request)


@app.post("/authenticate")
async def authenticate_user(request: Request):
    return await fn_authenticate_user(request)


@app.put("/user")
async def update_user(request: Request):
    return await fn_update_user(request)


@app.delete("/user/{username}")
async def delete_user(username: str):
    return await fn_delete_user(username)


@app.post("/chatbot/")
async def create_chatbot(request: Request):
    return await fn_create_chatbot(request)


@app.get("/chatbots/{username}")
async def get_chatbots_by_user(username: str):
    return await fn_get_chatbots_by_user(username)


@app.put("/chatbot")
async def update_chatbot(request: Request):
    return await fn_update_chatbot(request)


@app.delete("/chatbot/{chatbot_id}")
async def delete_chatbot(chatbot_id: int):
    return await fn_delete_chatbot(chatbot_id)


@app.post("/chat-session")
async def create_chat_session(request: Request):
    return await fn_create_chat_session(request)


@app.get("/chat-sessions/{username}")
async def get_chat_sessions_by_chatbot(username: str):
    return await fn_get_chat_sessions_by_user(username)


@app.put("/chat-session")
async def update_chat_session(request: Request):
    return await fn_update_chat_session(request)


@app.delete("/chat-session/{session_id}")
async def delete_chat_session(session_id: int):
    return await fn_delete_chat_session(session_id)


@app.post("/conversation/")
async def create_conversation(request: Request):
    return await fn_create_conversation(request)


@app.get("/conversations/{session_id}")
async def get_conversations_by_chat_session(session_id: int):
    return await fn_get_conversations_by_chat_session(session_id)


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: int):
    return await fn_delete_conversation(conversation_id)

@app.post("/chat/")
async def chat(request: Request):
    return await fn_chat(request)

@app.post("/upload/{chat_id}")
async def upload_files(chat_id: int, files: List[UploadFile] = File(...)):
    return await fn_upload_files(chat_id, files)

@app.get("/files/{chat_id}")
async def get_files(chat_id: int):
    return await fn_get_files(chat_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)