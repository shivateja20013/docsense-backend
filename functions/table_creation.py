import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
print(DATABASE_PATH)

# Connect to SQLite database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Create User table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        username TEXT PRIMARY KEY NOT NULL,
        email TEXT UNIQUE NOT NULL,
        firstname TEXT,
        lastname TEXT,
        password TEXT
    )
''')

# Create Chat Session table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ChatSession (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title TEXT,
        systemPrompt TEXT,
        isDocumentSession BOOLEAN,
        temperature REAL,
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        lastAccessedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create Conversations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chatSession INTEGER,
        message TEXT,
        source TEXT,
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
