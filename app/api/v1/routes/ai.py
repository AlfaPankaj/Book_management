from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.ai.graph import agent_graph
from app.ai.state import AgentState

# Check if AI assistant is enabled
AI_ENABLED = getattr(settings, 'ENABLE_AI_ASSISTANT', False)

if not AI_ENABLED:
    # Create a dummy router that returns 503 when AI is disabled
    ai_router = APIRouter()

    @ai_router.post("/assistant", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    async def ai_assistant_disabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Assistant is disabled. Set ENABLE_AI_ASSISTANT=true in environment variables to enable."
        )
else:
    # Create the actual AI router
    ai_router = APIRouter()

    # Request and response models
    class AIAssistantRequest(BaseModel):
        query: str

    class BookInfo(BaseModel):
        id: int
        title: str
        author: str
        genre: Optional[str] = None
        published_year: Optional[int] = None
        isbn: Optional[str] = None
        available: bool

    class AIAssistantResponse(BaseModel):
        answer: str
        intent: str
        books: List[BookInfo] = []

    @ai_router.post("/assistant", response_model=AIAssistantResponse)
    async def ai_assistant(request: AIAssistantRequest):
        """
        AI Librarian Assistant endpoint.
        Processes natural language queries about books and returns helpful responses.
        """
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        try:
            # Initialize the state
            initial_state: AgentState = {
                "messages": [],
                "query": request.query,
                "intent": None,
                "intent_confidence": None,
                "entities": None,
                "search_results": None,
                "recommendation_results": None,
                "enriched_metadata": None,
                "answer": None,
                "formatted_response": None,
                "error": None,
                "next_step": None,
                "metadata": {}
            }

            # Run the agent graph
            final_state = await agent_graph.ainvoke(initial_state)

            # Extract the response
            formatted_response = final_state.get("formatted_response")
            if not formatted_response:
                # Fallback if something went wrong
                formatted_response = {
                    "answer": "I'm sorry, I encountered an issue processing your request. Please try again.",
                    "intent": "error",
                    "books": []
                }

            # Convert books to our response format
            books = []
            for book_dict in formatted_response.get("books", []):
                books.append(BookInfo(
                    id=book_dict.get("id", 0),
                    title=book_dict.get("title", ""),
                    author=book_dict.get("author", ""),
                    genre=book_dict.get("genre"),
                    published_year=book_dict.get("published_year"),
                    isbn=book_dict.get("isbn"),
                    available=book_dict.get("available", False)
                ))

            return AIAssistantResponse(
                answer=formatted_response.get("answer", "I'm sorry, I couldn't process your request."),
                intent=formatted_response.get("intent", "unknown"),
                books=books
            )

        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"Error in AI assistant: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your request"
            )