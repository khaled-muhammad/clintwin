"""
Pill Akinator API Routes
========================
Endpoints for MCQ-based medicine identification.

Endpoints:
- POST /start - Start new identification session
- POST /answer - Submit answer and get next question/result
- GET /session/{session_id} - Get session state
- DELETE /session/{session_id} - End session
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from app.services.pill_akinator import get_akinator_service

router = APIRouter()


# ==================
# Request/Response Models
# ==================

class StartSessionResponse(BaseModel):
    """Response when starting a new Akinator session."""
    session_id: str = Field(..., description="Unique session identifier")
    question: dict = Field(..., description="First MCQ question")
    remaining_candidates: int = Field(..., description="Number of possible medicines")
    confidence: float = Field(..., description="Current confidence (0-1)")
    questions_asked: int = Field(0, description="Number of questions asked so far")


class AnswerRequest(BaseModel):
    """Request to submit an MCQ answer."""
    session_id: str = Field(..., description="Session identifier")
    answer: str = Field(..., description="Selected answer option")


class QuestionResponse(BaseModel):
    """Response containing next MCQ question."""
    type: str = Field("question", description="Response type")
    question: dict = Field(..., description="MCQ question data")
    remaining_candidates: int = Field(..., description="Remaining possible medicines")
    confidence: float = Field(..., description="Current confidence")
    questions_asked: int = Field(..., description="Questions asked so far")


class ResultResponse(BaseModel):
    """Response containing identification result."""
    type: str = Field("result", description="Response type")
    success: bool = Field(..., description="Whether identification succeeded")
    top_match: Optional[dict] = Field(None, description="Best matching medicine")
    alternatives: List[dict] = Field(default_factory=list, description="Alternative matches")
    confidence: float = Field(..., description="Final confidence score")
    questions_asked: int = Field(..., description="Total questions asked")
    answers_given: List[dict] = Field(default_factory=list, description="Answer history")


# ==================
# API Endpoints
# ==================

@router.post("/start", response_model=StartSessionResponse)
async def start_akinator_session():
    """
    Start a new Pill Akinator identification session.
    
    Initializes a session and returns the first dynamically generated MCQ.
    The question targets the visual attribute that will most effectively
    narrow down the possible medicines.
    
    Returns:
        Session ID and first question
        
    Example Response:
    ```json
    {
        "session_id": "abc123",
        "question": {
            "question_id": "q1",
            "question_text": "What is the main color of the medicine box?",
            "options": ["Red", "Blue", "White", "Green", "Other"],
            "field_target": "box_primary_color"
        },
        "remaining_candidates": 16,
        "confidence": 0.0,
        "questions_asked": 0
    }
    ```
    """
    service = get_akinator_service()
    
    try:
        # Use async version if LLM is configured
        result = await service.start_session_async()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return StartSessionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/answer")
async def submit_answer(request: AnswerRequest):
    """
    Submit an answer to the current MCQ.
    
    Processes the user's answer, filters candidate medicines,
    updates confidence, and either:
    - Returns the next MCQ (if confidence < 90% and questions < 3)
    - Returns the identification result (if conditions met)
    
    Args:
        request: Session ID and selected answer
        
    Returns:
        Next question or final result
        
    Example Request:
    ```json
    {
        "session_id": "abc123",
        "answer": "Red"
    }
    ```
    
    Example Response (next question):
    ```json
    {
        "type": "question",
        "question": {...},
        "remaining_candidates": 5,
        "confidence": 0.65,
        "questions_asked": 1
    }
    ```
    
    Example Response (result):
    ```json
    {
        "type": "result",
        "success": true,
        "top_match": {
            "medicine": {...},
            "confidence": 0.92
        },
        "alternatives": [...],
        "questions_asked": 3
    }
    ```
    """
    service = get_akinator_service()
    
    # Verify session exists
    session = service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Process answer (async for LLM question generation)
        result = await service.submit_answer_async(request.session_id, request.answer)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")


@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """
    Get current status of an Akinator session.
    
    Returns the current state including remaining candidates,
    confidence, and questions asked so far.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session state information
    """
    service = get_akinator_service()
    session = service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "questions_asked": session.get("questions_asked", 0),
        "confidence": session.get("confidence", 0.0),
        "remaining_candidates": len(session.get("candidates", [])),
        "asked_attributes": session.get("asked_attributes", []),
        "current_question": session.get("current_question")
    }


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    End an Akinator session.
    
    Cleans up session data. Called when user finishes or cancels.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Confirmation of session end
    """
    service = get_akinator_service()
    
    if service.end_session(session_id):
        return {"message": "Session ended successfully", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/generate_mcq")
async def generate_mcq_direct(
    candidates: Optional[List[str]] = None,
    asked_attributes: Optional[List[str]] = None
):
    """
    Generate a single MCQ without session context.
    
    Useful for testing or custom flows.
    
    Args:
        candidates: Optional list of medicine IDs to consider
        asked_attributes: Optional list of already-asked attributes
        
    Returns:
        Generated MCQ question
    """
    service = get_akinator_service()
    
    # Get candidates
    if candidates:
        medicine_list = [
            m for m in service.medicines 
            if m["id"] in candidates
        ]
    else:
        medicine_list = service.medicines
    
    # Select best attribute
    result = service._select_best_attribute(
        medicine_list,
        asked_attributes or []
    )
    
    if not result:
        return {"error": "No suitable question available"}
    
    attribute, distribution = result
    question = service._generate_question_mock(attribute, medicine_list, distribution)
    
    return {
        "question": question,
        "candidates_count": len(medicine_list),
        "attribute_targeted": attribute
    }
