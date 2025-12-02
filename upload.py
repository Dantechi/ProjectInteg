# upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException

from supa.supabase import upload_to_bucket

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    try:
        url = await upload_to_bucket(file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
