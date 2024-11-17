import os
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List

# Assuming INDEX_PATH is set in the .env file
INDEX_PATH = os.getenv("INDEX_PATH")

async def fn_upload_files(chat_id: int, files: List[UploadFile] = File(...)):
    try:
        # Create the directory for the given chat_id if it doesn't exist
        chat_dir = os.path.join(INDEX_PATH, str(chat_id))
        os.makedirs(chat_dir, exist_ok=True)

        uploaded_files = []
        for file in files:
            # Save each uploaded file
            file_location = os.path.join(chat_dir, file.filename)
            with open(file_location, "wb") as f:
                f.write(await file.read())
            uploaded_files.append(file.filename)

        return JSONResponse(content={"message": f"Files {uploaded_files} uploaded successfully to chat session {chat_id}"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
