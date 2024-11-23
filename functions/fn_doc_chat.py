from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')

# Define chunk parameters
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP'))

INDEX_PATH = os.getenv("INDEX_PATH")
FILES_PATH = os.getenv("FILES_PATH")

async def fn_doc_chat(request: Request):
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
            api_key=OPENAI_API_KEY
        )

        # messages = [{"role": "system", "content": systemPrompt}]
        # if message is not None:
        #     messages.append({"role": "user", "content": message})

        chat_completion = client.chat.completions.create(
            model=LLM_MODEL,
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