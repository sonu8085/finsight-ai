"""Parses uploaded bank-statement CSVs, previews rows, and detects duplicates.

Supports a flexible column-mapping approach so statements from different
banks (which use different header names) can all be imported. The caller
sends a `column_map` telling us which CSV column maps to which field.
"""
import io
import uuid

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository

REQUIRED_FIELDS = {"date", "description", "amount"}


class CSVImportService:
    def __init__(self, db: AsyncSession):
        self.repo = TransactionRepository(db)

    @staticmethod
    def preview(file_bytes: bytes) -> dict:
        """Return detected headers and the first 10 rows for the user to map/confirm."""
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not parse CSV: {exc}")

        if df.empty:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty")

        preview_rows = df.head(10).fillna("").to_dict(orient="records")
        return {"columns": list(df.columns), "preview_rows": preview_rows, "total_rows": len(df)}

    async def import_transactions(
        self,
        user_id: uuid.UUID,
        file_bytes: bytes,
        column_map: dict[str, str],
        default_type: TransactionType = TransactionType.EXPENSE,
    ) -> dict:
        """Parse full CSV using column_map (field -> csv_column) and bulk-insert transactions,
        skipping rows that look like duplicates of transactions already imported."""
        missing = REQUIRED_FIELDS - set(column_map.keys())
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"column_map missing required fields: {missing}",
            )

        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not parse CSV: {exc}")

        existing = await self.repo.get_all_for_user(user_id, limit=5000)
        existing_signatures = {
            (t.transaction_date.isoformat(), round(float(t.amount), 2), t.description.strip().lower())
            for t in existing
        }

        created, skipped_duplicates, skipped_invalid = 0, 0, 0
        to_insert: list[Transaction] = []

        for _, row in df.iterrows():
            try:
                raw_date = row[column_map["date"]]
                txn_date = pd.to_datetime(raw_date).date()
                amount = abs(float(row[column_map["amount"]]))
                description = str(row[column_map["description"]]).strip()

                if not description or amount <= 0:
                    skipped_invalid += 1
                    continue

                signature = (txn_date.isoformat(), round(amount, 2), description.lower())
                if signature in existing_signatures:
                    skipped_duplicates += 1
                    continue

                txn_type = default_type
                if "type" in column_map and column_map["type"] in row:
                    raw_type = str(row[column_map["type"]]).strip().lower()
                    if raw_type in ("credit", "income", "deposit"):
                        txn_type = TransactionType.INCOME
                    elif raw_type in ("debit", "expense", "withdrawal"):
                        txn_type = TransactionType.EXPENSE

                merchant = None
                if "merchant" in column_map and column_map["merchant"] in row:
                    merchant = str(row[column_map["merchant"]]).strip() or None

                transaction = Transaction(
                    user_id=user_id,
                    type=txn_type,
                    amount=amount,
                    description=description,
                    merchant=merchant,
                    transaction_date=txn_date,
                )
                to_insert.append(transaction)
                existing_signatures.add(signature)
                created += 1
            except (ValueError, KeyError, TypeError):
                skipped_invalid += 1
                continue

        if to_insert:
            await self.repo.bulk_create(to_insert)

        return {
            "imported": created,
            "skipped_duplicates": skipped_duplicates,
            "skipped_invalid": skipped_invalid,
            "total_rows": len(df),
        }
