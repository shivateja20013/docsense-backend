from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_create_chatbot(request: Request):
    request_data = await request.json()
    user = request_data["user"]
    title = request_data["title"]
    description = request_data.get("description", "")
    status = request_data.get("status", "active")

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ChatBot (user, title, description, status)
                VALUES (?, ?, ?, ?)
            ''', (user, title, description, status))
            conn.commit()
            return Response(content=json.dumps("ChatBot created successfully."), status_code=201)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
