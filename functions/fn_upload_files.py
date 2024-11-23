import os
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from functions.fn_rag_utils import index_files

FILES_PATH = os.getenv("FILES_PATH")

async def fn_upload_files(chat_id: int, files: List[UploadFile] = File(...)):
    # try:
        # Create the directory for the given chat_id if it doesn't exist
        FILES_DIR = os.path.join(FILES_PATH, str(chat_id))
        os.makedirs(FILES_DIR, exist_ok=True)

        uploaded_files = []
        for file in files:
            # Save each uploaded file
            file_location = os.path.join(FILES_DIR, file.filename)
            with open(file_location, "wb") as f:
                f.write(await file.read())
            uploaded_files.append({
                "fileName": file.filename,  # Add file name
                "filePath": file_location   # Add file path if needed for retrieval
            })
        
        index = await index_files(chat_id)

        return JSONResponse(content={
            "message": f"Files uploaded successfully to chat session {chat_id}",
            "uploadedFiles": uploaded_files  # Return file metadata for the frontend
        }, status_code=201)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))