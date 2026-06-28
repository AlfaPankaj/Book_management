from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from app.ai.state import AgentState
from app.ai.tools import search_books_tool, recommend_books_tool, enrich_book_metadata_tool
from app.ai.prompts import (
    general_response_prompt,
    response_format_prompt,
    intent_parser,
    book_search_parser,
    book_recommendation_parser,
    metadata_enrichment_parser
)
from app.ai.chains import (
    intent_classification_chain,
    book_search_response_chain,
    book_recommendation_response_chain,
    metadata_enrichment_chain,
    general_response_chain,
    response_formatting_chain
)

import logging
import os

logger = logging.getLogger(__name__)

# Initialize LLM for direct use
from langchain_openai import ChatOpenAI
from app.core.config import settings
llm = ChatOpenAI(
    model=settings.AI_MODEL,
    temperature=0.1,
    api_key=settings.LLM_API_KEY or os.getenv("OPENAI_API_KEY", "dummy_key_for_testing")
)

async def classify_intent_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Classify the user's intent and extract entities from their query.
    """
    try:
        query = state.get("query", "")
        if not query:
            return {
                **state,
                "error": "No query provided",
                "next_step": "error"
            }

        # Use the LLM to classify intent
        # In a full implementation, we would use structured output
        # For now, we'll use a simpler approach

        prompt = f"""
        You are an AI assistant for a book management system. Classify the user's intent and extract entities.

        User Query: {query}

        Possible intents:
        1. search_books - User wants to search for books with specific criteria
        2. recommend_books - User wants book recommendations based on a topic or book they like
        3. enrich_metadata - User wants to get additional information about a book (genre, summary, etc.)
        4. general_help - User needs help with the system or has a general question

        Respond with JSON in this format:
        {{
          "intent": "one of the intents above",
          "confidence": float between 0.0 and 1.0,
          "entities": {{
            // extracted entities relevant to the intent
          }}
        }}

        Examples:
        Query: "Show me science books by John"
        Intent: search_books
        Entities: {{"genre": "Science", "author": "John"}}

        Query: "Recommend books similar to Python programming"
        Intent: recommend_books
        Entities: {{"topic": "Python programming"}}

        Query: "What genre is Clean Code?"
        Intent: enrich_metadata
        Entities: {{"title": "Clean Code"}}

        Query: "How do I use this system?"
        Intent: general_help
        Entities: {{}}
        """

        try:
            response = await llm.ainvoke(prompt)
        except Exception as llm_error:
            logger.warning(f"LLM classification failed (likely missing API key), falling back to keyword extraction: {str(llm_error)}")
        # In a real implementation, we would parse this properly
        # For now, we'll do a simple extraction

        # Simple intent detection based on keywords (fallback)
        query_lower = query.lower()
        intent = "general_help"  # default
        confidence = 0.5
        entities = {}

        if any(word in query_lower for word in ["show", "find", "search", "look for", "get"]):
            intent = "search_books"
            confidence = 0.8
        elif any(word in query_lower for word in ["recommend", "suggest", "similar", "like"]):
            intent = "recommend_books"
            confidence = 0.8
        elif any(word in query_lower for word in ["what is", "genre", "summary", "about", "tell me about"]):
            intent = "enrich_metadata"
            confidence = 0.8
        elif any(word in query_lower for word in ["help", "how", "what", "explain"]):
            intent = "general_help"
            confidence = 0.7

        # Simple entity extraction (very basic)
        if "by" in query_lower:
            parts = query_lower.split("by")
            if len(parts) > 1:
                potential_author = parts[1].strip()
                if potential_author:
                    entities["author"] = potential_author.title()

        if intent == "search_books":
            # Extract potential genre
            genres = ["science", "fiction", "programming", "technology", "history", "biography", "fantasy", "mystery"]
            for genre in genres:
                if genre in query_lower:
                    entities["genre"] = genre.title()
                    break

        return {
            **state,
            "intent": intent,
            "intent_confidence": confidence,
            "entities": entities,
            "next_step": "route_based_on_intent"
        }
    except Exception as e:
        logger.error(f"Error in intent classification: {str(e)}")
        return {
            **state,
            "error": f"Failed to classify intent: {str(e)}",
            "next_step": "error"
        }

async def route_based_on_intent(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Route to the appropriate processing node based on classified intent.
    """
    intent = state.get("intent")

    if not intent:
        return {
            **state,
            "error": "No intent classified",
            "next_step": "error"
        }

    # Route based on intent
    if intent == "search_books":
        return {
            **state,
            "next_step": "search_books"
        }
    elif intent == "recommend_books":
        return {
            **state,
            "next_step": "recommend_books"
        }
    elif intent == "enrich_metadata":
        return {
            **state,
            "next_step": "enrich_metadata"
        }
    elif intent == "general_help":
        return {
            **state,
            "next_step": "general_help"
        }
    else:
        return {
            **state,
            "error": f"Unknown intent: {intent}",
            "next_step": "error"
        }

async def search_books_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Search for books based on the user's query and extracted entities.
    """
    try:
        query = state.get("query", "")
        entities = state.get("entities", {})

        # Enhance the search query with entities if available
        enhanced_query = query
        if entities:
            # Add entity information to the query for better search
            entity_parts = []
            for key, value in entities.items():
                if value and isinstance(value, str):
                    entity_parts.append(f"{key}:{value}")
            if entity_parts:
                enhanced_query = f"{query} {' '.join(entity_parts)}"

        # Use the search tool
        search_results = await search_books_tool.ainvoke({
            "query": enhanced_query,
            "limit": 10
        })

        return {
            **state,
            "search_results": search_results,
            "next_step": "format_response"
        }
    except Exception as e:
        logger.error(f"Error in book search: {str(e)}")
        return {
            **state,
            "error": f"Failed to search for books: {str(e)}",
            "next_step": "error"
        }

async def recommend_books_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Get book recommendations based on user preferences.
    """
    try:
        query = state.get("query", "")
        entities = state.get("entities", {})

        # Use the recommendation tool
        recommendation_results = await recommend_books_tool.ainvoke({
            "query": query,
            "limit": 5
        })

        return {
            **state,
            "recommendation_results": recommendation_results,
            "next_step": "format_response"
        }
    except Exception as e:
        logger.error(f"Error in book recommendations: {str(e)}")
        return {
            **state,
            "error": f"Failed to get book recommendations: {str(e)}",
            "next_step": "error"
        }

async def enrich_metadata_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Enrich book metadata with genre, summary, and tags.
    """
    try:
        entities = state.get("entities", {})
        title = entities.get("title", "")
        author = entities.get("author", "")

        if not title and not author:
            return {
                **state,
                "error": "No book title or author provided for metadata enrichment",
                "next_step": "error"
            }

        # Use the enrichment tool
        enriched_metadata = await enrich_book_metadata_tool.ainvoke({
            "title": title,
            "author": author
        })

        return {
            **state,
            "enriched_metadata": enriched_metadata,
            "next_step": "format_response"
        }
    except Exception as e:
        logger.error(f"Error in metadata enrichment: {str(e)}")
        return {
            **state,
            "error": f"Failed to enrich book metadata: {str(e)}",
            "next_step": "error"
        }

async def general_help_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Provide general help and information about the system.
    """
    try:
        query = state.get("query", "")

        # Generate a helpful response
        help_prompt = f"""
        You are a helpful AI librarian assistant for a book management system.
        The user is asking for help or information about how to use the system.

        User Query: {query}

        Provide a helpful, friendly response that explains:
        - How to search for books
        - How to get book recommendations
        - How to get book information
        - Any other relevant help information

        Keep your response concise and helpful.
        """

        response = await llm.ainvoke(help_prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        return {
            **state,
            "answer": answer,
            "next_step": "format_response"
        }
    except Exception as e:
        logger.error(f"Error in general help: {str(e)}")
        return {
            **state,
            "error": f"Failed to provide help: {str(e)}",
            "next_step": "error"
        }

async def format_response_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Format the final response based on the user's query and results from processing.
    """
    try:
        query = state.get("query", "")
        intent = state.get("intent", "")
        search_results = state.get("search_results", [])
        recommendation_results = state.get("recommendation_results", [])
        enriched_metadata = state.get("enriched_metadata", {})
        answer = state.get("answer", "")

        # If we already have an answer from general_help, use it
        if answer:
            formatted_response = {
                "answer": answer,
                "intent": intent,
                "books": search_results if intent == "search_books" else [],
                "recommendations": recommendation_results if intent == "recommend_books" else [],
                "metadata": enriched_metadata if intent == "enrich_metadata" else {}
            }
        else:
            # Generate a response based on the intent and results
            if intent == "search_books":
                if search_results:
                    answer = f"I found {len(search_results)} book(s) matching your query."
                    if len(search_results) <= 3:
                        for book in search_results:
                            answer += f" '{book.get('title', 'Unknown')}' by {book.get('author', 'Unknown')}."
                else:
                    answer = "I didn't find any books matching your query. Try different search terms."

            elif intent == "recommend_books":
                if recommendation_results:
                    answer = f"Based on your interest, I recommend {len(recommendation_results)} book(s):"
                    for book in recommendation_results[:3]:  # Show top 3
                        answer += f" '{book.get('title', 'Unknown')}' by {book.get('author', 'Unknown')} ({book.get('reason', 'recommended')})."
                else:
                    answer = "I couldn't generate recommendations based on your input. Try being more specific about what you like."

            elif intent == "enrich_metadata":
                if enriched_metadata:
                    answer = f"Here's information about '{enriched_metadata.get('title', 'the book')}':"
                    answer += f" Genre: {enriched_metadata.get('genre', 'Unknown')}. "
                    answer += f"Summary: {enriched_metadata.get('summary', 'No summary available.')}"
                else:
                    answer = "I couldn't find information about that book. Please check the title and author."

            else:
                answer = "I'm here to help you find books, get recommendations, or learn about books in the collection. What would you like to know?"

            formatted_response = {
                "answer": answer,
                "intent": intent,
                "books": search_results if intent == "search_books" else [],
                "recommendations": recommendation_results if intent == "recommend_books" else [],
                "metadata": enriched_metadata if intent == "enrich_metadata" else {}
            }

        return {
            **state,
            "answer": answer,
            "formatted_response": formatted_response,
            "next_step": "end"
        }
    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}")
        return {
            **state,
            "error": f"Failed to format response: {str(e)}",
            "next_step": "error"
        }

async def error_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Handle errors that occur during processing.
    """
    error_msg = state.get("error", "An unknown error occurred")
    logger.error(f"Error in AI agent: {error_msg}")

    error_response = {
        "answer": "I'm sorry, I encountered an error while processing your request. Please try again.",
        "intent": "error",
        "books": [],
        "recommendations": [],
        "metadata": {}
    }

    return {
        **state,
        "answer": error_response["answer"],
        "formatted_response": error_response,
        "next_step": "end"
    }

# For backward compatibility with the graph definition
general_help_node = general_help_node
format_response_node = format_response_node
error_node = error_node

# Export all nodes
__all__ = [
    "classify_intent_node",
    "route_based_on_intent",
    "search_books_node",
    "recommend_books_node",
    "enrich_metadata_node",
    "general_help_node",
    "format_response_node",
    "error_node"
]