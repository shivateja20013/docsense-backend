from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_delete_chat_session(session_id: int):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM ChatSession WHERE id = ?
            ''', (session_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return Response(content=json.dumps("Chat session not found."), status_code=404)

            return Response(content=json.dumps(f"Chat session {session_id} deleted successfully."), status_code=200)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
