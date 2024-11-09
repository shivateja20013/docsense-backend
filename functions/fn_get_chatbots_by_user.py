from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_get_chatbots_by_user(username: str):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, description, status, createdAt, lastAccessedAt, lastUpdatedAt
                FROM ChatBot
                WHERE user = ?
            ''', (username,))
            result = cursor.fetchall()

            if result:
                response_data = [{"id": row[0], "title": row[1], "description": row[2], "status": row[3],
                                  "createdAt": row[4], "lastAccessedAt": row[5], "lastUpdatedAt": row[6]}
                                 for row in result]
                return Response(content=json.dumps(response_data), status_code=200)
            else:
                return Response(content=json.dumps("No chatbots found for this user."), status_code=404)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
