import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Course, Lecture, Summary, AIChatRequest, AIChatResponse

app = FastAPI(title="Slate LMS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Slate LMS backend ready"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# Seed/demo endpoints
@app.get("/api/courses", response_model=List[Course])
async def list_courses() -> List[Course]:
    items = get_documents("course", {}, limit=20) if db else []
    if not items:
        # Provide demo data if DB empty/unavailable
        demo = [
            {
                "title": "Intro to Machine Learning",
                "description": "Foundations and practical ML projects",
                "instructor": "Dr. Rivera",
                "thumbnail_url": "https://images.unsplash.com/photo-1551033406-611cf9a28f67?w=800&q=80&auto=format&fit=crop",
                "progress_percent": 42,
            },
            {
                "title": "Modern Web Development",
                "description": "React, APIs, and cloud-native patterns",
                "instructor": "Alex Kim",
                "thumbnail_url": "https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=800&q=80&auto=format&fit=crop",
                "progress_percent": 75,
            },
            {
                "title": "Data Visualization",
                "description": "Tell stories with data using D3 and Tableau",
                "instructor": "Priya Natarajan",
                "thumbnail_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&q=80&auto=format&fit=crop",
                "progress_percent": 10,
            },
        ]
        return [Course(**c) for c in demo]
    return [Course(**{k: v for k, v in c.items() if k != "_id"}) for c in items]


class LectureListResponse(BaseModel):
    lectures: List[Lecture]
    summaries: List[Summary]


@app.get("/api/courses/{course_id}/lectures", response_model=LectureListResponse)
async def list_lectures(course_id: str):
    lectures = get_documents("lecture", {"course_id": course_id}, limit=100) if db else []
    summaries = get_documents("summary", {}, limit=100) if db else []

    if not lectures:
        # demo lectures
        demo_lectures = [
            {
                "course_id": course_id,
                "title": "Lecture 1: Introduction",
                "order": 1,
                "duration_minutes": 12,
                "pdf_attached": True,
                "pdf_url": "#",
            },
            {
                "course_id": course_id,
                "title": "Lecture 2: Core Concepts",
                "order": 2,
                "duration_minutes": 18,
                "pdf_attached": False,
                "pdf_url": None,
            },
        ]
        demo_summaries = [
            {
                "lecture_id": "1",
                "model_name": "mock-gpt-4o-mini",
                "word_count": 124,
                "content": "This lecture introduces the course structure and key outcomes...",
            }
        ]
        return LectureListResponse(
            lectures=[Lecture(**l) for l in demo_lectures],
            summaries=[Summary(**s) for s in demo_summaries],
        )

    normalized_lectures = [Lecture(**{k: v for k, v in l.items() if k != "_id"}) for l in lectures]
    normalized_summaries = [Summary(**{k: v for k, v in s.items() if k != "_id"}) for s in summaries]
    return LectureListResponse(lectures=normalized_lectures, summaries=normalized_summaries)


# Upload endpoint (mock processing)
@app.post("/api/instructor/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    generate_summary: bool = Form(True)
):
    # In a real system you'd store the file and trigger background processing
    info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": None,
        "summary_generated": generate_summary,
        "summary_preview": None,
    }
    content = await file.read()
    info["size"] = len(content)
    if generate_summary:
        info["summary_preview"] = "Auto-generated summary will appear here after processing."
    return info


# AI chat (mock)
@app.post("/api/ai/chat", response_model=AIChatResponse)
async def ai_chat(payload: AIChatRequest):
    reply = (
        "Here's a helpful explanation based on your course context. "
        "I'm a demo AI assistant in Slate LMS."
    )
    return AIChatResponse(reply=reply, sources=["Course materials", "Lecture notes"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
