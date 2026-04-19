import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from groq import Groq
from database import SessionLocal, LoginDetail
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_table_schema():
    """Get database schema information"""
    return """
    Table: login_details
    Columns:
    - id (Integer, Primary Key)
    - name (String) - Visitor's name
    - email (String) - Visitor's email address
    - phone (String) - Visitor's phone number
    - visited_at (DateTime) - Timestamp of visit
    - role_id (Integer) - User role (1=Admin, 2=Regular User)
    """


def generate_sql_query(question: str) -> str:
    """Use LLM to generate SQL query from natural language question"""
    schema = get_table_schema()
    
    prompt = f"""You are a SQL expert. Given the following database schema and a user question, 
generate a valid PostgreSQL SQL query to answer the question.

{schema}

User Question: {question}

Rules:
- Return ONLY the SQL query, no explanations
- Use proper PostgreSQL syntax with SELECT statements
- Table name is 'login_details'
- For date queries, use visited_at column
- Always limit results to 100 rows max
- DO NOT use COPY, COPY TO, or any file export commands
- Use only SELECT, WHERE, ORDER BY, LIMIT, JOIN, GROUP BY, HAVING
- Return data using SELECT statements only

SQL Query:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a SQL expert that generates PostgreSQL SELECT queries only. Never use COPY or file export commands."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    sql_query = response.choices[0].message.content.strip()
    # Remove markdown code blocks if present
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    # Safety check: reject COPY commands
    if "COPY" in sql_query.upper():
        # Fallback to simple SELECT
        sql_query = "SELECT * FROM login_details LIMIT 100"
    
    return sql_query


def execute_query(sql_query: str):
    """Execute SQL query and return results"""
    db = SessionLocal()
    try:
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return data
    except Exception as e:
        raise Exception(f"Query execution error: {str(e)}")
    finally:
        db.close()


def generate_answer(question: str, query_results: list) -> str:
    """Generate natural language answer from query results"""
    prompt = f"""Based on the following database query results, answer the user's question in a clear and concise way.

User Question: {question}

Query Results:
{query_results}

Provide a natural language answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that explains database results clearly."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()


def ask_database(question: str) -> dict:
    """Main RAG function - ask a question and get an answer"""
    try:
        # Step 1: Generate SQL query from question
        sql_query = generate_sql_query(question)
        print(f"Generated SQL: {sql_query}")
        
        # Step 2: Execute query
        results = execute_query(sql_query)
        print(f"Found {len(results)} results")
        
        # Step 3: Generate natural language answer
        answer = generate_answer(question, results)
        
        return {
            "question": question,
            "sql_query": sql_query,
            "results": results,
            "answer": answer,
            "success": True
        }
    except Exception as e:
        return {
            "question": question,
            "error": str(e),
            "success": False
        }


if __name__ == "__main__":
    # Test the RAG system
    questions = [
        "How many visitors do we have?",
        "Show me all visitors from today",
        "Who visited most recently?",
        "List all visitor names and emails"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        result = ask_database(q)
        if result["success"]:
            print(f"Answer: {result['answer']}")
        else:
            print(f"Error: {result['error']}")
