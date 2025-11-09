from fastapi import FastAPI, Form, UploadFile
from supabase import create_client
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/posts")
async def create_post(
    user_id: str = Form(...),
    content: str = Form(...),
    is_private: bool = Form(False),
    image: UploadFile = None,
    audio: UploadFile = None
):
    image_url = None
    audio_url = None

    if image:
        image_path = f"{user_id}/{datetime.utcnow().isoformat()}_{image.filename}"
        supabase.storage.from_("media").upload(image_path, image.file, {"content-type": image.content_type})
        image_url = supabase.storage.from_("media").get_public_url(image_path)

    if audio:
        audio_path = f"{user_id}/{datetime.utcnow().isoformat()}_{audio.filename}"
        supabase.storage.from_("media").upload(audio_path, audio.file, {"content-type": audio.content_type})
        audio_url = supabase.storage.from_("media").get_public_url(audio_path)

    response = supabase.table("posts").insert({
        "user_id": user_id,
        "content": content,
        "is_private": is_private,
        "image_url": image_url,
        "audio_url": audio_url
    }).execute()

    return {"status": "success", "post": response.data}

@app.get("/posts")
def get_posts():
    response = supabase.table("posts").select("*").order("created_at", desc=True).execute()
    return response.data

@app.post("/tips")
def send_tip(
    sender_id: str = Form(...),
    receiver_id: str = Form(...),
    amount: float = Form(...)
):
    response = supabase.table("tips").insert({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount
    }).execute()
    return {"status": "success", "tip": response.data}
