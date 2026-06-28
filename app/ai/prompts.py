from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Intent Classification Prompt and Parser
class IntentClassification(BaseModel):
    intent: str = Field(description="The classified intent from the user query")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    entities: Dict[str, Any] = Field(description="Extracted entities from the query")

intent_parser = JsonOutputParser(pydantic_object=IntentClassification)

intent_classification_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at classifying user intents for a book library assistant.
    Analyze the user's query and classify it into one of these intents:

    1. search_books - User wants to search for books (e.g., "Find books about Python", "Show me science fiction books")
    2. recommend_books - User wants book recommendations (e.g., "Recommend books like Harry Potter", "What should I read next?")
    3. enrich_metadata - User wants information about a specific book (e.g., "Tell me about The Great Gatsby", "What genre is 1984?")
    4. general_help - User needs help or is asking about how to use the system

    Also extract relevant entities like book titles, authors, genres, publication years, etc.

    {format_instructions}
    """),
    ("human", "{query}")
]).partial(format_instructions=intent_parser.get_format_instructions())

# Book Search Prompt and Parser
class BookSearchResult(BaseModel):
    books: List[Dict[str, Any]] = Field(description="List of books found")
    total_count: int = Field(description="Total number of matching books")

book_search_parser = JsonOutputParser(pydantic_object=BookSearchResult)

book_search_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a book search assistant. Based on the user's query and search results, provide a helpful response.

    User Query: {query}
    Search Results: {search_results}

    Provide a natural language response summarizing what you found and offering to help further if needed.
    """),
    ("human", "Please provide a helpful response based on the search results.")
])

# Book Recommendation Prompt and Parser
class BookRecommendationResult(BaseModel):
    recommendations: List[Dict[str, Any]] = Field(description="List of recommended books")
    explanation: str = Field(description="Explanation of why these books were recommended")

book_recommendation_parser = JsonOutputParser(pydantic_object=BookRecommendationResult)

book_recommendation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a book recommendation assistant. Based on the user's preferences and recommendation results, provide helpful suggestions.

    User Query: {query}
    Recommendation Results: {recommendation_results}

    Explain why these books were recommended and how they match the user's interests.
    """),
    ("human", "Please explain these recommendations.")
])

# Metadata Enrichment Prompt and Parser
class MetadataEnrichmentResult(BaseModel):
    genre: str = Field(description="Suggested genre for the book")
    summary: str = Field(description="Brief summary of the book")
    suggested_tags: List[str] = Field(description="List of suggested tags or keywords")

metadata_enrichment_parser = JsonOutputParser(pydantic_object=MetadataEnrichmentResult)

metadata_enrichment_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a book metadata expert. Based on the book title and author, provide enriched metadata.

    Title: {title}
    Author: {author}

    Provide a likely genre, a brief summary, and suggested tags for categorization.
    """),
    ("human", "Please provide metadata information for this book.")
])

# General Help Prompt
general_response_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful library assistant. Provide guidance on how to use the book library system.

    User Query: {query}
    Intent: {intent}

    Help the user understand how to search for books, get recommendations, or learn about specific books.
    """),
    ("human", "Please provide helpful guidance.")
])

# Response Formatting Prompt
response_format_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful library assistant. Format a final response based on the user's query and the results obtained.

    User Query: {query}
    Intent: {intent}
    Search Results: {search_results}
    Recommendation Results: {recommendation_results}
    Enriched Metadata: {enriched_metadata}

    Provide a natural, helpful response that addresses the user's original question.
    """),
    ("human", "Please provide a helpful response.")
])

# Export prompts and parsers
__all__ = [
    "intent_classification_prompt",
    "intent_parser",
    "book_search_prompt",
    "book_search_parser",
    "book_recommendation_prompt",
    "book_recommendation_parser",
    "metadata_enrichment_prompt",
    "metadata_enrichment_parser",
    "general_response_prompt",
    "response_format_prompt"
]