"""
Simple test script for the RAG system
Run this after installing dependencies and setting up your OpenAI API key
"""
from rag_query import ask_database

def test_rag():
    print("Testing RAG Application\n")
    
    # Test questions
    questions = [
        "How many total visitors are in the database?",
        "Show me the most recent 5 visitors",
        "List all visitor names",
        "Who has a gmail email address?",
    ]
    
    for question in questions:
        print(f"\n{'='*70}")
        print(f"Q: {question}")
        print("-" * 70)
        
        result = ask_database(question)
        
        if result["success"]:
            print(f"SQL: {result['sql_query']}")
            print(f"\nA: {result['answer']}")
            print(f"\nResults: {len(result['results'])} rows")
        else:
            print(f"ERROR: {result['error']}")

if __name__ == "__main__":
    test_rag()
