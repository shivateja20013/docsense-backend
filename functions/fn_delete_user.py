import json
import os
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")

app = FastAPI()


@app.delete("/user/{username}")
async def fn_delete_user(username: str):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Attempt to delete the user
            cursor.execute('''
                DELETE FROM user WHERE username = ?
            ''', (username,))
            conn.commit()

            if cursor.rowcount == 0:
                # If no rows were affected, the user was not found
                raise HTTPException(status_code=404, detail="User not found.")

            return Response(content=json.dumps(f"User {username} deleted successfully."), status_code=200)

    except sqlite3.OperationalError as e:
        print(f"Operational error: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed.")
