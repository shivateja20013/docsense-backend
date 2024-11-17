from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_update_chat_session(request: Request):
    request_data = await request.json()
    session_id = request_data.get("id")
    title = request_data.get("title")
    system_prompt = request_data.get("systemPrompt")
    temperature = request_data.get("temperature")
    lastAccessedAt = request_data.get("lastAccessedAt")

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if system_prompt:
        updates.append("systemPrompt = ?")
        params.append(system_prompt)
    if temperature is not None:
        updates.append("temperature = ?")
        params.append(temperature)
    if lastAccessedAt:
        updates.append("lastAccessedAt = ?")
        params.append(lastAccessedAt)

    if not updates:
        return Response(content=json.dumps("No update fields provided."), status_code=400)

    params.append(session_id)

    update_query = f'''
        UPDATE ChatSession
        SET {', '.join(updates)}, lastAccessedAt = CURRENT_TIMESTAMP
        WHERE id = ?
    '''

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, tuple(params))
            conn.commit()

            if cursor.rowcount > 0:
                return Response(content=json.dumps("Chat session updated successfully."), status_code=200)
            else:
                return Response(content=json.dumps("Chat session not found."), status_code=404)
    except sqlite3.OperationalError:
        return Response(content=json.dumps("Database operation failed."), status_code=500)
