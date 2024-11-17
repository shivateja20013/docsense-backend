import os
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Assuming INDEX_PATH is set in the .env file
INDEX_PATH = os.getenv("INDEX_PATH")

async def fn_get_files(chat_id: int):
    chat_dir = os.path.join(INDEX_PATH, str(chat_id))

    if not os.path.exists(chat_dir):
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    files = os.listdir(chat_dir)
    if not files:
        raise HTTPException(status_code=404, detail="No files found for this chat session")

    return JSONResponse(content={"files": files}, status_code=200)
