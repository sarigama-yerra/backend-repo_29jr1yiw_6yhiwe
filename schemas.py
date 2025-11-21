"""
Database Schemas for Mouqab Al Noor Real Estate System

Each Pydantic model represents a MongoDB collection. The collection name
is the lowercase of the class name (e.g., Property -> "property").
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Core domain models

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field("buyer", description="buyer | agent | admin")
    preferred_language: str = Field("en", description="en | ar")
    avatar_url: Optional[str] = None
    is_active: bool = True

class Agent(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    whatsapp: Optional[str] = None
    languages: List[str] = ["en"]

class Property(BaseModel):
    title_en: str
    title_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    price: float = Field(..., ge=0)
    currency: str = Field("AED")
    location: str
    city: Optional[str] = None
    country: Optional[str] = None
    property_type: str = Field(..., description="apartment | villa | townhouse | land | office | retail | warehouse")
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    area_sqft: Optional[float] = Field(None, ge=0)
    amenities: Optional[List[str]] = []
    images: Optional[List[str]] = []
    floor_plans: Optional[List[str]] = []
    coordinates: Optional[Dict[str, float]] = None
    featured: bool = False
    status: str = Field("available", description="available | sold | rented | pending")
    listed_by: Optional[str] = Field(None, description="agent user id")

class Lead(BaseModel):
    property_id: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    source: str = Field("website", description="website | whatsapp | phone | email")

class Viewing(BaseModel):
    property_id: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_datetime: Optional[str] = None
    notes: Optional[str] = None

class Favorite(BaseModel):
    user_id: str
    property_id: str

class MaintenanceRequest(BaseModel):
    building: str
    unit: Optional[str] = None
    category: str = Field(..., description="plumbing | electrical | hvac | cleaning | other")
    priority: str = Field("medium", description="low | medium | high | urgent")
    description: Optional[str] = None
    status: str = Field("open", description="open | in_progress | resolved | closed")
    requested_by: Optional[str] = None  # user id or name
    contact_phone: Optional[str] = None
    photos: Optional[List[str]] = []
