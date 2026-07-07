"""Pydantic schemas for AI assistant endpoints."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    reply: str


class InsightsResponse(BaseModel):
    insights: list[str]
