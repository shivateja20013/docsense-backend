import json
import os
import sqlite3

from fastapi.requests import Request
from fastapi.responses import Response
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_update_user(request: Request):
    request_data = await request.json()
    username = request_data.get("username")
    new_firstname = request_data.get("firstname")
    new_lastname = request_data.get("lastname")
    new_password = request_data.get("password")

    if not username:
        return Response(content=json.dumps("Username is required."), status_code=400)

    updates = []
    params = []

    if new_firstname:
        updates.append("firstname = ?")
        params.append(new_firstname)
    if new_lastname:
        updates.append("lastname = ?")
        params.append(new_lastname)
    if new_password:
        updates.append("password = ?")
        params.append(new_password)

    if not updates:
        return Response(content=json.dumps("No update fields provided."), status_code=400)

    params.append(username)

    update_query = f'''
        UPDATE user
        SET {', '.join(updates)}
        WHERE username = ?
    '''

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, tuple(params))
            conn.commit()

            if cursor.rowcount > 0:
                return Response(content=json.dumps("User details updated successfully."), status_code=200)
            else:
                return Response(content=json.dumps("User not found."), status_code=404)

    except sqlite3.OperationalError as e:
        print(f"Operational error: {e}")
        return Response(content=json.dumps("Database operation failed."), status_code=500)
