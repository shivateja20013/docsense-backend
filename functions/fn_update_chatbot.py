from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_update_chatbot(request: Request):
    request_data = await request.json()
    chatbot_id = request_data.get("id")
    title = request_data.get("title")
    description = request_data.get("description")
    status = request_data.get("status")
    lastUpdatedAt = request_data.get("lastUpdatedAt")
    lastAccessedAt = request_data.get("lastAccessedAt")

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if description:
        updates.append("description = ?")
        params.append(description)
    if status:
        updates.append("status = ?")
        params.append(status)
    if lastUpdatedAt:
        updates.append("lastUpdatedAt = ?")
        params.append(lastUpdatedAt)
    if lastAccessedAt:
        updates.append("lastAccessedAt = ?")
        params.append(lastAccessedAt)

    if not updates:
        return Response(content=json.dumps("No update fields provided."), status_code=400)

    params.append(chatbot_id)

    update_query = f'''
        UPDATE ChatBot
        SET {', '.join(updates)}, lastModifiedAt = CURRENT_TIMESTAMP
        WHERE id = ?
    '''

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, tuple(params))
            conn.commit()

            if cursor.rowcount > 0:
                return Response(content=json.dumps("ChatBot updated successfully."), status_code=200)
            else:
                return Response(content=json.dumps("ChatBot not found."), status_code=404)
    except sqlite3.OperationalError as e:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
