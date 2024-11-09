from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")


async def fn_chat(request: Request):
    request_data = await request.json()
    username = request_data["username"]
    messages = request_data["messages"]
    chat_id = request_data["chatId"]
    
    print(messages[-1])
    
    if chat_id:
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Conversations (chatSession, message, source)
                    VALUES (?, ?, ?)
                ''', (chat_id, messages[-1]['content'], "user"))
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Adding user message - Database operation failed.")
            
        systemPrompt = """You are an AI assistant."""

        client = OpenAI(
            api_key=OPEN_AI_TOKEN
        )

        # messages = [{"role": "system", "content": systemPrompt}]
        # if message is not None:
        #     messages.append({"role": "user", "content": message})

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages
        )

        content = chat_completion.choices[0].message.content
        
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Conversations (chatSession, message, source)
                    VALUES (?, ?, ?)
                ''', (chat_id, content, "assistant"))
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Adding assistant message - Database operation failed.")
    
        return Response(content=json.dumps(content), status_code=200)
    
    else:
        return Response(content=json.dumps("Something went wrong."), status_code=500)

    # try:
    #     with sqlite3.connect(DATABASE_PATH) as conn:
    #         cursor = conn.cursor()
    #         cursor.execute('''
    #             INSERT INTO ChatSession (username, title, systemPrompt, temperature)
    #             VALUES (?, ?, ?, ?)
    #         ''', (username, title, system_prompt, temperature))
    #         conn.commit()
    #         return Response(content=json.dumps("Chat session created successfully."), status_code=201)
    # except sqlite3.OperationalError as e:
    #     return Response(content=json.dumps("Database operation failed."), status_code=500)
