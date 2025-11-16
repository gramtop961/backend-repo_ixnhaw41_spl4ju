"""
Database Schemas for Slate LMS

Each Pydantic model represents a MongoDB collection.
The collection name is the lowercase of the class name
(e.g., Course -> "course").
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    role: str = Field("student", description="Role: student | instructor | admin")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    is_active: bool = Field(True, description="Active user")


class Course(BaseModel):
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Short description")
    instructor: str = Field(..., description="Instructor name")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    progress_percent: Optional[int] = Field(0, ge=0, le=100, description="Progress if enrolled")


class Lecture(BaseModel):
    course_id: str = Field(..., description="Parent course id as string")
    title: str = Field(..., description="Lecture title")
    order: int = Field(..., ge=1, description="Lecture order number")
    duration_minutes: Optional[int] = Field(10, ge=0, description="Duration in minutes")
    pdf_attached: bool = Field(False, description="Whether PDF is attached")
    pdf_url: Optional[str] = Field(None, description="PDF URL if attached")


class Summary(BaseModel):
    lecture_id: str = Field(..., description="Lecture id as string")
    model_name: str = Field("mock-gpt", description="Model used to generate summary")
    word_count: int = Field(..., ge=0)
    content: str = Field(..., description="Summary content")


# Optional helper response models used by API (not stored as collections)
class AIChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class AIChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = None
