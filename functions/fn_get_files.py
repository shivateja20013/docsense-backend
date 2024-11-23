import os
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Assuming FILES_PATH is set in the .env file
FILES_PATH = os.getenv("FILES_PATH")

async def fn_get_files(chat_id: int):
    try:
        chat_dir = os.path.join(FILES_PATH, str(chat_id))
        print(chat_dir)

        if not os.path.exists(chat_dir):
            raise HTTPException(status_code=404, detail="Chat session not found")

        files = os.listdir(chat_dir)
        print(files)
        if not files:
            raise HTTPException(status_code=404, detail="No files found for this chat session")

        # Construct a list of file metadata
        file_metadata = [{"fileName": file, "filePath": os.path.join(chat_dir, file)} for file in files]

        return JSONResponse(content={
            "message": f"Files retrieved successfully for chat session {chat_id}",
            "files": file_metadata
        }, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
