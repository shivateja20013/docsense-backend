import json
import os
import sqlite3

from fastapi.requests import Request
from fastapi.responses import Response
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_authenticate_user(request: Request):
    request_data = await request.json()
    username = request_data["username"]
    password = request_data["password"]

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, firstname, lastname, email FROM user
                WHERE username = ? AND password = ?
            ''', (username, password))
            result = cursor.fetchone()

            if result is not None:
                response_data = {
                    "username": result[0],
                    "firstname": result[1],
                    "lastname": result[2],
                    "email": result[3],
                }
                return Response(content=json.dumps(response_data), status_code=200)
            else:
                return Response(content=json.dumps({
                    "error": "Authentication failed. Invalid username or password."
                }), status_code=401)
    except sqlite3.OperationalError as e:
        print(f"Operational error: {e}")
        return Response(content=json.dumps("Database operation failed."), status_code=500)
