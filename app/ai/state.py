from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for the AI Librarian Assistant workflow."""
    # Input from user
    messages: List[BaseMessage]
    query: str

    # Intent classification results
    intent: Optional[str]
    intent_confidence: Optional[float]
    entities: Optional[Dict[str, Any]]

    # Tool execution results
    search_results: Optional[List[Dict[str, Any]]]
    recommendation_results: Optional[List[Dict[str, Any]]]
    enriched_metadata: Optional[Dict[str, Any]]

    # Final response
    answer: Optional[str]
    formatted_response: Optional[Dict[str, Any]]

    # Control flow
    error: Optional[str]
    next_step: Optional[str]

    # Metadata
    metadata: Optional[Dict[str, Any]]

# Pydantic models for structured output
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    intent: str = Field(description="The classified intent from the user query")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    entities: Dict[str, Any] = Field(description="Extracted entities from the query")

class BookMetadataEnrichment(BaseModel):
    genre: str = Field(description="Suggested genre for the book")
    summary: str = Field(description="Brief summary of the book")
    suggested_tags: List[str] = Field(description="List of suggested tags or keywords")

class SearchResult(BaseModel):
    books: List[Dict[str, Any]] = Field(description="List of books found in search")
    total_count: int = Field(description="Total number of books matching the search criteria")

class RecommendationResult(BaseModel):
    recommendations: List[Dict[str, Any]] = Field(description="List of recommended books")
    explanation: str = Field(description="Explanation of why these books were recommended")