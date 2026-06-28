from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.ai.prompts import (
    intent_classification_prompt,
    book_search_prompt,
    book_recommendation_prompt,
    metadata_enrichment_prompt,
    general_response_prompt,
    response_format_prompt
)
from app.ai.state import AgentState

import logging
import os

logger = logging.getLogger(__name__)

from app.core.config import settings

# Initialize LLM
llm = ChatOpenAI(
    model=settings.AI_MODEL,
    temperature=0.1,
    api_key=settings.LLM_API_KEY or os.getenv("OPENAI_API_KEY", "dummy_key_for_testing")
)

# Intent Classification Chain
intent_classification_chain: Runnable = (
    intent_classification_prompt
    | llm
    | StrOutputParser()
)

# Book Search Response Chain
book_search_response_chain: Runnable = (
    book_search_prompt
    | llm
    | StrOutputParser()
)

# Book Recommendation Response Chain
book_recommendation_response_chain: Runnable = (
    book_recommendation_prompt
    | llm
    | StrOutputParser()
)

# Metadata Enrichment Chain
metadata_enrichment_chain: Runnable = (
    metadata_enrichment_prompt
    | llm
    | StrOutputParser()
)

# General Response Chain
general_response_chain: Runnable = (
    general_response_prompt
    | llm
    | StrOutputParser()
)

# Response Formatting Chain
response_formatting_chain: Runnable = (
    response_format_prompt
    | llm
    | StrOutputParser()
)

# Dictionary of all chains for easy access
CHAINS = {
    "intent_classification": intent_classification_chain,
    "book_search_response": book_search_response_chain,
    "book_recommendation_response": book_recommendation_response_chain,
    "metadata_enrichment": metadata_enrichment_chain,
    "general_response": general_response_chain,
    "response_formatting": response_formatting_chain
}

# Export chains
__all__ = [
    "intent_classification_chain",
    "book_search_response_chain",
    "book_recommendation_response_chain",
    "metadata_enrichment_chain",
    "general_response_chain",
    "response_formatting_chain",
    "CHAINS"
]