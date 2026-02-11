from pydantic import BaseModel
from datetime import date
from typing import Optional


class SubmissionCreate(BaseModel):
    business_idea: str
    location_land: str
    promoter_background: str
    goals: str
    start_date: date
    target_launch_date: date
    budget: float
    target_market: str
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "business_idea": "An eco-friendly packaging company",
                "location_land": "Industrial area in XYZ city",
                "promoter_background": "10 years in manufacturing",
                "goals": "Scale to 5 locations within 2 years",
                "start_date": "2026-03-01",
                "target_launch_date": "2026-06-01",
                "budget": 500000,
                "target_market": "E-commerce companies",
                "notes": "Focus on sustainable practices"
            }
        }


class SubmissionResponse(BaseModel):
    id: str
    business_idea: str
    location_land: str
    promoter_background: str
    goals: str
    start_date: date
    target_launch_date: date
    budget: float
    target_market: str
    notes: Optional[str] = None
