"""CSV bank-statement import endpoints: preview then confirm import."""
import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.transaction import TransactionType
from app.models.user import User
from app.services.csv_import_service import CSVImportService

router = APIRouter(prefix="/api/v1/import", tags=["CSV Import"])


@router.post("/preview")
async def preview_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    return CSVImportService.preview(content)


@router.post("/confirm")
async def confirm_import(
    file: UploadFile = File(...),
    column_map: str = Form(..., description='JSON string, e.g. {"date":"Date","description":"Narration","amount":"Amount"}'),
    default_type: TransactionType = Form(TransactionType.EXPENSE),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    mapping = json.loads(column_map)
    service = CSVImportService(db)
    return await service.import_transactions(current_user.id, content, mapping, default_type)
