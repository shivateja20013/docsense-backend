from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_create_chat_session(request: Request):
    request_data = await request.json()
    username = request_data["username"]
    # title = request_data["title"]
    # system_prompt = request_data.get("systemPrompt", "")
    # temperature = request_data.get("temperature", 0.7)

    try:
        chat_id = request_data["chatId"]
    except KeyError:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ChatSession (username, title, systemPrompt, temperature)
                VALUES (?, ?, ?, ?)
            ''', (username, "New Chat", "system_prompt", 0.7))
            conn.commit()
            chat_id = cursor.lastrowid
            return Response(content=json.dumps(chat_id), status_code=201)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
