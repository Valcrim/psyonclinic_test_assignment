from pydantic import BaseModel
from typing import Optional

class Doctor(BaseModel):
    id: Optional[int] = None
    name: str
    slug: Optional[str] = None
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    clinic: Optional[str] = None
    price_from: Optional[int] = None
    photo_url: Optional[str] = None
    profile_url: Optional[str] = None
