from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, LoginDetail
from rag_query import ask_database
from export_data import export_to_excel, export_to_pdf, export_to_csv
from datetime import datetime
import re

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    role_id: int  # Role ID (1 for admin)


class ExportRequest(BaseModel):
    role_id: int  # Role ID (1 for admin)
    question: str  # Question to generate data for export
    format: str  # "excel", "pdf", or "csv"


def verify_admin(role_id: int) -> bool:
    """Check if role_id is admin (role_id = 1)"""
    print(f"DEBUG: Checking role_id={role_id}")
    is_admin = role_id == 1
    print(f"DEBUG: Is admin? {is_admin}")
    return is_admin


def detect_download_intent(question: str) -> tuple[bool, str]:
    """
    Detect if user wants to download and in what format
    Returns: (should_download, format)
    """
    question_lower = question.lower()
    
    # Keywords that indicate download intent
    download_keywords = ['download', 'export', 'save', 'get file', 'generate file']
    
    # Check for download intent
    wants_download = any(keyword in question_lower for keyword in download_keywords)
    
    # Detect format
    if 'excel' in question_lower or 'xlsx' in question_lower:
        return wants_download, 'excel'
    elif 'pdf' in question_lower:
        return wants_download, 'pdf'
    elif 'csv' in question_lower:
        return wants_download, 'csv'
    else:
        # Default to CSV if download is requested but no format specified
        return wants_download, 'csv'


def clean_question(question: str) -> str:
    """Remove download-related keywords from question for SQL generation"""
    # Remove common download phrases
    patterns = [
        r'\b(download|export|save|get file|generate file)\b',
        r'\b(in|as|to)\s+(excel|pdf|csv|xlsx)\b',
        r'\bfile\b'
    ]
    
    cleaned = question
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


@router.post("/ask")
def ask_question(data: QuestionRequest, db: Session = Depends(get_db)):
    """
    Ask a natural language question about the database.
    Only accessible to admin users (role_id = 1).
    
    The system automatically detects download requests:
    - "Show all visitors" -> Returns JSON
    - "Download all visitors" -> Returns CSV file
    - "Export visitors in excel" -> Returns Excel file
    - "Get visitors as pdf" -> Returns PDF file
    
    Supported formats: CSV (default), Excel, PDF
    """
    if not data.question or len(data.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Check if user is admin
    if not verify_admin(data.role_id):
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only administrators can access this feature."
        )
    
    # Detect download intent and format
    wants_download, file_format = detect_download_intent(data.question)
    
    # Clean question for SQL generation
    clean_q = clean_question(data.question) if wants_download else data.question
    
    # Get data from database
    result = ask_database(clean_q)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    # If download is requested, return file
    if wants_download:
        query_results = result["results"]
        
        if file_format == "csv":
            file_data = export_to_csv(query_results, title="Query Results")
            filename = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            media_type = "text/csv"
        elif file_format == "excel":
            file_data = export_to_excel(query_results, title="Query Results")
            filename = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_format == "pdf":
            file_data = export_to_pdf(
                query_results, 
                title="Query Results",
                question=data.question
            )
            filename = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid format. Use 'csv', 'excel' or 'pdf'"
            )
        
        return StreamingResponse(
            file_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    # Otherwise return JSON response
    return {
        "question": result["question"],
        "answer": result["answer"],
        "sql_query": result["sql_query"],
        "results_count": len(result["results"]),
        "data": result["results"]
    }


@router.get("/check-admin/{role_id}")
def check_admin_status(role_id: int):
    """
    Debug endpoint to check if a role_id is admin
    """
    is_admin = role_id == 1
    
    return {
        "role_id": role_id,
        "is_admin": is_admin,
        "message": "Admin access granted" if is_admin else "Not an admin role"
    }


@router.post("/export")
def export_data(data: ExportRequest, db: Session = Depends(get_db)):
    """
    Export query results to CSV, Excel or PDF format.
    Only accessible to admin users (role_id = 1).
    
    This endpoint works with ANY question/query:
    - "Show all visitors"
    - "List users from last month"
    - "Get all admin users"
    - Any future tables and queries
    
    Request body:
    {
        "role_id": 1,
        "question": "Show all visitors",
        "format": "csv"  // or "excel" or "pdf"
    }
    """
    # Check if user is admin
    if not verify_admin(data.role_id):
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Only administrators can export data."
        )
    
    if not data.question or len(data.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Get data using RAG query
    result = ask_database(data.question)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500, 
            detail=f"Query failed: {result.get('error', 'Unknown error')}"
        )
    
    query_results = result["results"]
    format_lower = data.format.lower()
    
    # Generate appropriate file
    if format_lower == "csv":
        file_data = export_to_csv(query_results, title="Query Results")
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        media_type = "text/csv"
    elif format_lower == "excel":
        file_data = export_to_excel(query_results, title="Query Results")
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format_lower == "pdf":
        file_data = export_to_pdf(
            query_results, 
            title="Query Results",
            question=data.question
        )
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        media_type = "application/pdf"
    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid format. Use 'csv', 'excel' or 'pdf'"
        )
    
    return StreamingResponse(
        file_data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
