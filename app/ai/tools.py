"""
Tools for the AI Librarian Assistant to interact with the book management system.
These tools wrap the existing service layer functions to provide a clean interface
for the LangGraph workflow.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool, StructuredTool, tool
from pydantic import BaseModel, Field
import logging
import json

from app.services.book_service import get_books, get_book, create_book, update_book, delete_book
from app.schemas.book import BookCreate, BookUpdate
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.book import Book

logger = logging.getLogger(__name__)

# Pydantic models for tool inputs
class BookSearchInput(BaseModel):
    query: str = Field(description="Natural language query about books to search for")
    limit: int = Field(default=10, description="Maximum number of results to return")

class BookRecommendationInput(BaseModel):
    query: str = Field(description="What the user liked or wants recommendations for")
    limit: int = Field(default=5, description="Maximum number of recommendations")

class BookMetadataInput(BaseModel):
    title: str = Field(description="Title of the book")
    author: str = Field(description="Author of the book")

# Tool implementations
@tool("search_books_tool", args_schema=BookSearchInput)
async def search_books_tool(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for books based on a natural language query.
    Uses the existing book service to search the database.
    """
    try:
        logger.info(f"Searching for books with query: {query}, limit: {limit}")

        # Parse the query to extract search parameters
        # This is a simplified version - in production, you'd use more sophisticated NLP
        search_params = _parse_search_query(query)

        # Search for books
        async with AsyncSessionLocal() as db:
            books_response = await get_books(
                db=db,
                page=1,
                limit=limit,
                title=search_params.get("title"),
                author=search_params.get("author"),
                is_available=search_params.get("available")
            )
            books = books_response.items

            # Convert to dictionary format
            result = []
            for book in books:
                result.append({
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre,
                    "published_year": book.published_year,
                    "isbn": book.isbn,
                    "available": book.available
                })

            return result
    except Exception as e:
        logger.error(f"Error searching for books: {str(e)}")
        return []

@tool("recommend_books_tool", args_schema=BookRecommendationInput)
async def recommend_books_tool(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get book recommendations based on what the user likes.
    Uses simple genre/author matching for recommendations.
    """
    try:
        logger.info(f"Getting recommendations for: {query}, limit: {limit}")

        # Parse query to understand what user likes
        preferences = _parse_preference_query(query)

        # Get books that match the preferences
        async with AsyncSessionLocal() as db:
            books_response = await get_books(
                db=db,
                page=1,
                limit=limit * 3,  # Get more to filter for recommendations
                author=preferences.get("author")
            )
            books = books_response.items

            # Simple recommendation logic: score books based on similarity
            recommendations = []
            for book in books:
                score = _calculate_similarity_score(book, preferences)
                if score > 0.3:  # Threshold for recommendation
                    recommendations.append({
                        "id": book.id,
                        "title": book.title,
                        "author": book.author,
                        "genre": book.genre,
                        "published_year": book.published_year,
                        "isbn": book.isbn,
                        "available": book.available,
                        "similarity_score": score,
                        "reason": _generate_recommendation_reason(book, preferences)
                    })

            # Sort by score and limit results
            recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            return recommendations[:limit]
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return []

@tool("enrich_book_metadata_tool")
async def enrich_book_metadata_tool(title: str, author: str) -> Dict[str, Any]:
    """
    Enrich book metadata with genre, summary, and tags.
    For now, returns placeholder information since we don't have
    an external knowledge base connected.
    """
    try:
        logger.info(f"Enriching metadata for: {title} by {author}")

        # Get database session
        db = await get_db_session()

        # Try to find the exact book first
        book = None
        if title and author:
            # Search for exact match
            stmt = select(Book).where(
                and_(
                    Book.title.ilike(f"%{title}%"),
                    Book.author.ilike(f"%{author}%")
                )
            )
            result = await db.execute(stmt)
            book = result.scalar_one_or_none()

        # If found, return actual data
        if book:
            return {
                "title": book.title,
                "author": book.author,
                "genre": book.genre or "Unknown",
                "summary": f"This book titled '{book.title}' by {book.author} is available in our library.",
                "suggested_tags": [book.genre or "unknown", "book", "literature"],
                "published_year": book.published_year,
                "isbn": book.isbn,
                "available": book.available
            }

        # If not found, provide generic information based on title/author analysis
        # In a real implementation, this would call an external API or knowledge base
        genre = _guess_genre_from_title(title)
        summary = f"A book titled '{title}' written by {author}."
        if genre != "Unknown":
            summary += f" It falls under the {genre} genre."

        return {
            "title": title,
            "author": author,
            "genre": genre,
            "summary": summary,
            "suggested_tags": [genre.lower(), "book", "literature"] if genre != "Unknown" else ["book", "literature", "unknown"],
            "published_year": None,
            "isbn": None,
            "available": None
        }
    except Exception as e:
        logger.error(f"Error enriching book metadata: {str(e)}")
        return {
            "title": title,
            "author": author,
            "genre": "Error",
            "summary": "Unable to retrieve book information.",
            "suggested_tags": ["error"],
            "published_year": None,
            "isbn": None,
            "available": None
        }

# Helper functions
def _parse_search_query(query: str) -> Dict[str, Any]:
    """
    Parse a natural language search query into search parameters.
    Simple implementation - in production would use NLP.
    """
    params = {}
    query_lower = query.lower()

    # First check for structured entity additions like "author:John"
    import re
    
    author_match = re.search(r'author:(\w+)', query)
    if author_match:
        params["author"] = author_match.group(1)
        
    genre_match = re.search(r'genre:(\w+)', query)
    if genre_match:
        params["genre"] = genre_match.group(1)
        
    # Extract potential author (look for "by" pattern) if not already found
    if "author" not in params and " by " in query:
        parts = query.split(" by ")
        if len(parts) > 1:
            potential_author = parts[-1].strip()
            # If there are appended entities, strip them off
            potential_author = potential_author.split(" author:")[0].split(" genre:")[0].strip()
            if potential_author:
                params["author"] = potential_author

    # Extract potential genre
    genres = ["science", "fiction", "programming", "technology", "history",
              "biography", "fantasy", "mystery", "romance", "thriller", "science fiction"]
    for genre in genres:
        if genre in query_lower:
            params["genre"] = genre.title()
            break

    # Extract potential year (look for 4-digit numbers)
    import re
    year_matches = re.findall(r'\b(19|20)\d{2}\b', query)
    if year_matches:
        try:
            params["published_year"] = int(year_matches[0])
        except ValueError:
            pass

    # Check for availability keywords
    if any(word in query_lower for word in ["available", "in stock", "can borrow"]):
        params["available"] = True
    elif any(word in query_lower for word in ["checked out", "unavailable", "borrowed"]):
        params["available"] = False

    # If no specific parameters found but query has content, treat as title search
    if not params and query.strip():
        # Remove common words and use as title search
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [word for word in query.lower().split() if word not in stop_words and len(word) > 2]
        if words:
            params["title"] = " ".join(words)

    return params

def _parse_preference_query(query: str) -> Dict[str, Any]:
    """
    Parse a query about user preferences for recommendations.
    """
    prefs = {}
    query_lower = query.lower()

    # Extract genre preferences
    genres = ["science", "fiction", "programming", "technology", "history",
              "biography", "fantasy", "mystery", "romance", "thriller"]
    for genre in genres:
        if genre in query_lower:
            prefs["genre"] = genre.title()
            break

    # Extract author preferences
    if " by " in query:
        parts = query.split(" by ")
        if len(parts) > 1:
            potential_author = parts[-1].strip()
            if potential_author:
                prefs["author"] = potential_author

    # Extract topic/subject preferences
    # Remove common words and extract meaningful terms
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
                  "like", "similar", "about", "on", "topic", "subject"}
    words = [word for word in query.lower().split() if word not in stop_words and len(word) > 2]
    if words and not prefs.get("genre") and not prefs.get("author"):
        # If we don't have specific genre/author, treat as topic
        prefs["topic"] = " ".join(words[:3])  # Take first 3 meaningful words

    return prefs

def _calculate_similarity_score(book: Book, preferences: Dict[str, Any]) -> float:
    """
    Calculate a similarity score between a book and user preferences.
    """
    score = 0.0
    max_score = 0.0

    # Genre match
    if preferences.get("genre"):
        max_score += 0.4
        if book.genre and book.genre.lower() == preferences["genre"].lower():
            score += 0.4

    # Author match
    if preferences.get("author"):
        max_score += 0.4
        if book.author and book.author.lower() == preferences["author"].lower():
            score += 0.4

    # Topic match (simplified - would use embeddings in production)
    if preferences.get("topic") and not preferences.get("genre") and not preferences.get("author"):
        max_score += 0.3
        # Simple keyword matching in title/author
        topic_words = preferences["topic"].lower().split()
        text_to_search = f"{book.title} {book.author}".lower()
        matches = sum(1 for word in topic_words if word in text_to_search)
        if topic_words:
            score += 0.3 * (min(len(topic_words), max(1, matches)) / len(topic_words))

    return score / max_score if max_score > 0 else 0.0

def _generate_recommendation_reason(book: Book, preferences: Dict[str, Any]) -> str:
    """
    Generate a human-readable reason for the recommendation.
    """
    reasons = []

    if preferences.get("genre") and book.genre and book.genre.lower() == preferences["genre"].lower():
        reasons.append(f"matches your interest in {preferences['genre']} books")

    if preferences.get("author") and book.author and book.author.lower() == preferences["author"].lower():
        reasons.append(f"by your favorite author {book.author}")

    if not reasons:
        reasons.append("has similar themes or topics")

    return "; ".join(reasons) if reasons else "may be of interest to you"

def _guess_genre_from_title(title: str) -> str:
    """
    Guess the genre based on book title keywords.
    Very simple implementation - in production would use ML or external APIs.
    """
    if not title:
        return "Unknown"

    title_lower = title.lower()

    # Science/Technology keywords
    tech_words = ["programming", "software", "computer", "algorithm", "data", "science",
                  "technology", "engineering", "math", "physics", "chemistry", "biology"]
    if any(word in title_lower for word in tech_words):
        return "Technology"

    # Fiction keywords
    fiction_words = ["novel", "story", "tale", "fiction", "mystery", "thriller", "romance"]
    if any(word in title_lower for word in fiction_words):
        return "Fiction"

    # History/Biography
    history_words = ["history", "historical", "biography", "memoir", "life of", "world war"]
    if any(word in title_lower for word in history_words):
        return "History"

    # Default
    return "General"

# Export tools for easy importing
search_books_tool = search_books_tool
recommend_books_tool = recommend_books_tool
enrich_book_metadata_tool = enrich_book_metadata_tool

__all__ = [
    "search_books_tool",
    "recommend_books_tool",
    "enrich_book_metadata_tool",
    "BookSearchInput",
    "BookRecommendationInput",
    "BookMetadataInput"
]