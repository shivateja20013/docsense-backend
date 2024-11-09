import json
import os
import sqlite3
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


async def fn_create_user(request: Request):
    request_data = await request.json()
    username = request_data.get("username")
    password = request_data.get("password")
    firstname = request_data.get("firstname")
    lastname = request_data.get("lastname")
    email = request_data.get("email")

    if not all([username, password, firstname, lastname, email]):
        return JSONResponse(content="All fields are required.", status_code=400)

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO User (username, password, firstname, lastname, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password, firstname, lastname, email))
            conn.commit()
            return JSONResponse(content="User registration successful.", status_code=201)

    except sqlite3.IntegrityError as e:
        error_message = str(e)
        if "email" in error_message:
            return JSONResponse(content="An account with this email already exists.", status_code=409)
        elif "username" in error_message:
            return JSONResponse(content="Username is already taken. Please choose another.", status_code=409)

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return JSONResponse(content="Database operation failed. Please try again later.", status_code=500)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content="An unexpected error occurred. Please try again.", status_code=500)
