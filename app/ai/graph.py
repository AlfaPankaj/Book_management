from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.ai.state import AgentState
from app.ai.nodes import (
    classify_intent_node,
    route_based_on_intent,
    search_books_node,
    recommend_books_node,
    enrich_metadata_node,
    general_help_node,
    format_response_node,
    error_node
)

def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the AI Librarian Assistant.
    """
    # Initialize the graph with our state
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("route_based_on_intent", route_based_on_intent)
    workflow.add_node("search_books", search_books_node)
    workflow.add_node("recommend_books", recommend_books_node)
    workflow.add_node("enrich_metadata", enrich_metadata_node)
    workflow.add_node("general_help", general_help_node)
    workflow.add_node("format_response", format_response_node)
    workflow.add_node("error", error_node)

    # Set the entry point
    workflow.set_entry_point("classify_intent")

    # Add edges
    workflow.add_edge("classify_intent", "route_based_on_intent")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "route_based_on_intent",
        lambda state: state.get("next_step"),
        {
            "search_books": "search_books",
            "recommend_books": "recommend_books",
            "enrich_metadata": "enrich_metadata",
            "general_help": "general_help",
            "error": "error",
            "format_response": "format_response"
        }
    )

    # All processing nodes lead to response formatting
    workflow.add_edge("search_books", "format_response")
    workflow.add_edge("recommend_books", "format_response")
    workflow.add_edge("enrich_metadata", "format_response")
    workflow.add_edge("general_help", "format_response")

    # Response formatting leads to end
    workflow.add_edge("format_response", END)
    workflow.add_edge("error", END)

    # Compile the graph
    return workflow.compile()

# Create the agent graph instance
agent_graph = create_agent_graph()

# Export the graph
__all__ = ["agent_graph", "create_agent_graph"]