# supa/supabase.py
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import UploadFile
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("No están configuradas las credenciales de Supabase")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


async def upload_to_bucket(file: UploadFile) -> str:
    """
    Sube un archivo al bucket de Supabase y devuelve la URL pública.
    """
    client = get_supabase_client()

    file_content = await file.read()
    file_path = f"public/{file.filename}"

    client.storage.from_(SUPABASE_BUCKET).upload(
        path=file_path,
        file=file_content,
        file_options={
            "content-type": file.content_type
        }
    )

    public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
    return public_url
