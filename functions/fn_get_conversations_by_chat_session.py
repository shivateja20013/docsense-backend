from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_get_conversations_by_chat_session(session_id: int):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, message, source, createdAt
                FROM Conversations
                WHERE chatSession = ?
            ''', (session_id,))
            result = cursor.fetchall()

            if result:
                response_data = [{"id": row[0], "message": row[1], "source": row[2], "createdAt": row[3]}
                                 for row in result]
                return Response(content=json.dumps(response_data), status_code=200)
            else:
                return Response(content=json.dumps([]), status_code=200)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
