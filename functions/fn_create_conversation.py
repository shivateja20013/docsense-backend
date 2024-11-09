from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_create_conversation(request: Request):
    request_data = await request.json()
    chat_session_id = request_data["chatSession"]
    message = request_data["message"]
    source = request_data.get("source", "")

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Conversations (chatSession, message, source)
                VALUES (?, ?, ?)
            ''', (chat_session_id, message, source))
            conn.commit()
            return Response(content=json.dumps("Conversation created successfully."), status_code=201)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
