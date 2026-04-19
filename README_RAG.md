# RAG Application for Database Queries

A Retrieval-Augmented Generation (RAG) system that lets you ask natural language questions about your PostgreSQL database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get a free Groq API key from https://console.groq.com and add it to `.env`:
```
GROQ_API_KEY=your_actual_groq_api_key
```

3. Make sure your PostgreSQL database is running

## Usage

### Option 1: API Endpoint (Admin Only)

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

#### Ask Questions
Make a POST request to `/api/ask` with admin user_id:
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many visitors do we have?", "user_id": 1}'
```

#### Export Query Results
Download ANY query results in Excel or PDF format:

**Excel Export:**
```bash
curl -X POST "http://localhost:8000/api/export" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "question": "Show all visitors", "format": "excel"}' \
  --output results.xlsx
```

**PDF Export:**
```bash
curl -X POST "http://localhost:8000/api/export" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "question": "Show visitors from last week", "format": "pdf"}' \
  --output results.pdf
```

**Works with ANY question:**
- "Show all visitors"
- "List users with gmail addresses"
- "Get admin users only"
- Any future tables you add!

**Important:** Only users with `role_id = 1` (admin) can access these endpoints. Regular users (role_id = 2) will get a 403 Forbidden error.

### Option 2: Python Script

Run the test script directly:
```bash
python test_rag.py
```

Or use it in your code:
```python
from rag_query import ask_database

result = ask_database("Show me all visitors from today")
print(result["answer"])
```

## Example Questions

- "How many visitors do we have?"
- "Show me the most recent 10 visitors"
- "List all visitors with gmail addresses"
- "Who visited in the last 7 days?"
- "Show me all phone numbers"
- "Find visitors named John"
- "How many admins are there?"
- "Show me all users by role"

## Export Features

Admins can export ANY query results in two formats:

1. **Excel (.xlsx)** - Formatted spreadsheet with auto-adjusted columns
2. **PDF** - Professional report with table formatting

The export is completely dynamic and works with:
- Current tables (visitors, login_details, etc.)
- Future tables you add to your database
- Any SQL query results
- Filtered data (e.g., "visitors from last month")

Simply ask a question and specify the format - the system will:
1. Generate and execute the SQL query
2. Format the results
3. Return a downloadable file

## How It Works

1. **Question → SQL**: Uses Groq's Llama 3.3 70B model to convert your natural language question into a SQL query
2. **Execute Query**: Runs the SQL query against your PostgreSQL database
3. **Results → Answer**: Uses Groq to convert the query results into a natural language answer

**Why Groq?** Groq offers blazing fast inference speeds and free API access, making it perfect for RAG applications.

## API Response Format

**Success (Admin user):**
```json
{
  "question": "How many visitors do we have?",
  "answer": "You have 15 visitors in the database.",
  "sql_query": "SELECT COUNT(*) FROM login_details;",
  "results_count": 1,
  "data": [{"count": 15}]
}
```

**Error (Non-admin user):**
```json
{
  "detail": "Access denied. Only administrators can access this feature."
}
```

## Role-Based Access Control

- **role_id = 1**: Admin - Can ask questions via RAG API
- **role_id = 2**: Regular User (default) - Cannot access RAG API
- New users are automatically assigned role_id = 2 on registration
