from fastapi.requests import Request
from fastapi.responses import JSONResponse
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")

async def fn_create_chat_session(request: Request):
    request_data = await request.json()
    username = request_data.get("username")
    title = request_data.get("title")
    systemPrompt = request_data.get("systemPrompt")
    temperature = request_data.get("temperature")
    chatType = request_data.get("chatType")

    if not all([username, title, systemPrompt, temperature, chatType]):
        return JSONResponse(content="All fields are required.", status_code=400)

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ChatSession (username, title, systemPrompt, temperature, chatType)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, title, systemPrompt, temperature, chatType))
            conn.commit()
            chat_id = cursor.lastrowid
            cursor.execute('''
                SELECT * FROM ChatSession WHERE id = ?
            ''', (chat_id,))
            chat_session = cursor.fetchone()
            return JSONResponse(content=json.dumps(chat_session), status_code=201)
        
    except sqlite3.IntegrityError:
        return JSONResponse(content="Database integrity error.", status_code=409)

    except sqlite3.OperationalError:
        return JSONResponse(content="Database operation failed. Please try again later.", status_code=500)

    except Exception:
        return JSONResponse(content="An unexpected error occurred. Please try again.", status_code=500)
