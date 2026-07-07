"""AI-powered chat assistant and insight generation.

Uses OpenAI's API when OPENAI_API_KEY is configured. When it's not
configured, falls back to the rule-based analysis engine so the feature
still works (just without free-form natural-language chat).
"""
import json
import uuid

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analysis import analyze_transactions, rule_based_insights
from app.core.config import settings
from app.repositories.transaction_repository import TransactionRepository

SYSTEM_PROMPT = """You are FinSight AI, a helpful and encouraging personal finance assistant.
You are given a JSON summary of the user's recent transactions and spending statistics.
Answer the user's question using ONLY this data. Be concise, specific, and use actual numbers
from the data. If the data doesn't contain the answer, say so honestly. Never invent transactions.
Keep replies under 150 words unless the user asks for a detailed report."""


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def _get_stats(self, user_id: uuid.UUID) -> dict:
        transactions = await self.transaction_repo.get_all_for_user(user_id, limit=1000)
        return analyze_transactions(transactions)

    async def get_insights(self, user_id: uuid.UUID) -> list[str]:
        stats = await self._get_stats(user_id)
        base_insights = rule_based_insights(stats)

        if not self.client:
            return base_insights

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Based on this spending data, give me 4-6 short, specific, actionable "
                            f"financial insights as a JSON array of strings only.\n\nData: {json.dumps(stats)}"
                        ),
                    },
                ],
                temperature=0.4,
                max_tokens=500,
            )
            content = response.choices[0].message.content or "[]"
            content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(content)
            if isinstance(parsed, list) and parsed:
                return parsed
        except Exception:
            pass  # fall back silently to rule-based insights

        return base_insights

    async def chat(self, user_id: uuid.UUID, message: str) -> str:
        stats = await self._get_stats(user_id)

        if not self.client:
            insights = rule_based_insights(stats)
            return (
                "AI chat requires an OPENAI_API_KEY to be configured on the server. "
                "Here's what I can tell you from your data instead:\n- " + "\n- ".join(insights)
            )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"My spending data: {json.dumps(stats)}\n\nQuestion: {message}"},
                ],
                temperature=0.5,
                max_tokens=400,
            )
            return response.choices[0].message.content or "I couldn't generate a response, please try again."
        except Exception as exc:
            return f"AI assistant is temporarily unavailable ({exc.__class__.__name__}). Please try again shortly."
