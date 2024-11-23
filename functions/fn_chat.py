from fastapi.requests import Request
from fastapi.responses import Response
import json
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI
from llama_index.chat_engine.types import ChatMode
from llama_index.llms import ChatMessage, MessageRole

from functions.fn_rag_utils import getIndex

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')

INDEX_PATH = os.getenv("INDEX_PATH")
FILES_PATH = os.getenv("FILES_PATH")

CHAT_MODE = ChatMode.REACT

async def fn_chat(request: Request):
    requestData = await request.json()
    messages = requestData["messages"]
    chatId = requestData["chatId"]
    chatType = requestData["chatType"]
    systemPrompt = requestData["systemPrompt"]
    temperature = requestData["temperature"]
    
    if chatId:
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Conversations (chatSession, message, source)
                    VALUES (?, ?, ?)
                ''', (chatId, messages[-1]['content'], "user"))
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Adding user message - Database operation failed.")

        if not systemPrompt:
            systemPrompt = """You are an AI assistant."""
        response = ""
            
        if chatType=="model":
            messages.insert(0, {'role':'system', 'content':systemPrompt})
            client = OpenAI(
                api_key=OPENAI_API_KEY
            )

            chat_completion = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=temperature
            )

            response = chat_completion.choices[0].message.content
        else:
            chatHistory = []
            for message in messages:
                chatHistory.append(ChatMessage(content=message["content"], role=(MessageRole.USER if message["content"] == "user" else MessageRole.ASSISTANT)))
            data_index = await getIndex(chatId)
            chat_engine = data_index.as_chat_engine(chat_mode=CHAT_MODE, system_prompt=systemPrompt)
            response = chat_engine.chat(message=messages[-1]["content"], chat_history=chatHistory)

        print(response)
        response = str(response)
        
        try:
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Conversations (chatSession, message, source)
                    VALUES (?, ?, ?)
                ''', (chatId, response, "assistant"))
                conn.commit()
        except sqlite3.OperationalError as e:
            print("Adding assistant message - Database operation failed.", e)
    
        return Response(content=json.dumps(response), status_code=200)
    
    else:
        return Response(content=json.dumps("Something went wrong."), status_code=500)