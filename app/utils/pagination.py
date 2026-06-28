from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar('T')

class PageParams(BaseModel):
    page_size: int = 10
    page_number: int = 1

class Page(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    data: List[T]

def paginate(query, page_params: PageParams):
    # This is a placeholder; in reality, we would modify the query with offset and limit
    # and also get the total count.
    # For async, we need to run two queries: one for count, one for data.
    # We'll implement this in the service or repository.
    pass