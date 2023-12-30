"""
Models used in the API but not the DB
"""

from pydantic import BaseModel

class Search(BaseModel):
    query: str