"""AI assistant endpoints: chat and auto-generated insights."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.assistant import AIService
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse, InsightsResponse

router = APIRouter(prefix="/api/v1/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AIService(db)
    reply = await service.chat(current_user.id, data.message)
    return ChatResponse(reply=reply)


@router.get("/insights", response_model=InsightsResponse)
async def get_ai_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AIService(db)
    insights = await service.get_insights(current_user.id)
    return InsightsResponse(insights=insights)
