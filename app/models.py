from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, Literal
from enum import Enum


class BusinessModel(str, Enum):
    B2B = "B2B"
    B2C = "B2C"
    B2G = "B2G"
    HYBRID = "Hybrid"


class SizingMode(str, Enum):
    CAPACITY_DRIVEN = "capacity_driven"
    BUDGET_DRIVEN = "budget_driven"


class SubmissionCreate(BaseModel):
    # Project Identity (Critical)
    client_name: str = Field(..., min_length=1, description="Client/organization name")
    project_title: str = Field(..., min_length=1, description="Project title")
    product_service: str = Field(..., min_length=1, description="Product or service description")
    project_location: str = Field(..., min_length=1, description="Project location details")
    business_model: BusinessModel = Field(..., description="Business model type")
    
    # Project Sizing (Critical - conditional based on mode)
    sizing_mode: SizingMode = Field(..., description="Capacity-driven or budget-driven")
    target_capacity: Optional[str] = Field(None, description="Target production capacity (for capacity-driven)")
    total_investment: Optional[float] = Field(None, ge=0, description="Total investment budget (for budget-driven)")
    
    # Commercial Assumptions (Critical)
    selling_price: float = Field(..., gt=0, description="Selling price per unit")
    currency: str = Field(default="INR", description="Currency code")
    product_mix: Optional[str] = Field(None, description="Product mix and revenue contribution")
    production_rampup: str = Field(..., min_length=1, description="Production ramp-up plan")
    market_geography: str = Field(..., min_length=1, description="Target market geography")
    
    # Operating Assumptions (Critical)
    operating_days: int = Field(..., ge=1, le=365, description="Operating days per year")
    shifts_per_day: int = Field(..., ge=1, le=3, description="Number of shifts per day")
    hours_per_shift: int = Field(..., ge=1, le=12, description="Hours per shift")
    utilization_rate: float = Field(..., ge=0, le=100, description="Plant utilization rate percentage")
    utilities_consumption: Optional[str] = Field(None, description="Utilities consumption estimates")
    
    # Financing Inputs (Critical)
    debt_percentage: float = Field(..., ge=0, le=100, description="Debt percentage")
    equity_percentage: float = Field(..., ge=0, le=100, description="Equity percentage")
    loan_tenor: int = Field(..., ge=1, le=30, description="Loan tenor in years")
    interest_rate: float = Field(..., ge=0, le=30, description="Interest rate per annum")
    moratorium_period: Optional[int] = Field(None, ge=0, le=36, description="Moratorium period in months")
    
    # Equipment Preferences (Optional)
    preferred_manufacturer_geography: Optional[str] = Field(None, description="Preferred manufacturer geography")
    brand_preferences: Optional[str] = Field(None, description="Preferred brands or manufacturers")
    technology_exclusions: Optional[str] = Field(None, description="Technologies to exclude")
    
    # Legacy/Additional fields (Optional for backward compatibility)
    promoter_background: Optional[str] = Field(None, description="Promoter background and experience")
    start_date: Optional[date] = Field(None, description="Expected start date")
    target_launch_date: Optional[date] = Field(None, description="Target launch date")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # Backward compatibility mappings (auto-populated from new fields if not provided)
    business_idea: Optional[str] = Field(None, description="Legacy: business idea")
    location_land: Optional[str] = Field(None, description="Legacy: location and land")
    goals: Optional[str] = Field(None, description="Legacy: project goals")
    budget: Optional[float] = Field(None, description="Legacy: budget")
    target_market: Optional[str] = Field(None, description="Legacy: target market")

    @field_validator('debt_percentage', 'equity_percentage')
    @classmethod
    def validate_debt_equity_sum(cls, v, info):
        """Validate that debt + equity = 100% when both are provided"""
        if info.field_name == 'equity_percentage':
            debt = info.data.get('debt_percentage')
            if debt is not None and v is not None:
                if abs(debt + v - 100) > 0.01:  # Allow small floating point errors
                    raise ValueError(f'Debt ({debt}%) + Equity ({v}%) must equal 100%')
        return v

    @field_validator('target_capacity', 'total_investment')
    @classmethod
    def validate_sizing_mode_fields(cls, v, info):
        """Validate that appropriate field is provided based on sizing mode"""
        sizing_mode = info.data.get('sizing_mode')
        if sizing_mode == SizingMode.CAPACITY_DRIVEN and info.field_name == 'target_capacity' and not v:
            raise ValueError('target_capacity is required for capacity-driven mode')
        if sizing_mode == SizingMode.BUDGET_DRIVEN and info.field_name == 'total_investment' and not v:
            raise ValueError('total_investment is required for budget-driven mode')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "ABC Manufacturing Ltd",
                "project_title": "Eco-Friendly Packaging Plant",
                "product_service": "Biodegradable packaging materials for food industry",
                "project_location": "Industrial Zone, Sector 5, XYZ City",
                "business_model": "B2B",
                "sizing_mode": "capacity_driven",
                "target_capacity": "10000 MT per year",
                "selling_price": 50.0,
                "currency": "INR",
                "production_rampup": "Year 1: 50%, Year 2: 75%, Year 3: 100%",
                "market_geography": "Domestic market with focus on metropolitan areas",
                "operating_days": 300,
                "shifts_per_day": 2,
                "hours_per_shift": 8,
                "utilization_rate": 85.0,
                "debt_percentage": 70.0,
                "equity_percentage": 30.0,
                "loan_tenor": 10,
                "interest_rate": 9.5
            }
        }


class SubmissionResponse(BaseModel):
    id: str
    client_name: str
    project_title: str
    product_service: str
    project_location: str
    business_model: str
    sizing_mode: str
    target_capacity: Optional[str] = None
    total_investment: Optional[float] = None
    selling_price: float
    currency: str
    product_mix: Optional[str] = None
    production_rampup: str
    market_geography: str
    operating_days: int
    shifts_per_day: int
    hours_per_shift: int
    utilization_rate: float
    utilities_consumption: Optional[str] = None
    debt_percentage: float
    equity_percentage: float
    loan_tenor: int
    interest_rate: float
    moratorium_period: Optional[int] = None
    preferred_manufacturer_geography: Optional[str] = None
    brand_preferences: Optional[str] = None
    technology_exclusions: Optional[str] = None
    promoter_background: Optional[str] = None
    start_date: Optional[date] = None
    target_launch_date: Optional[date] = None
    notes: Optional[str] = None
    # Legacy fields
    business_idea: Optional[str] = None
    location_land: Optional[str] = None
    goals: Optional[str] = None
    budget: Optional[float] = None
    target_market: Optional[str] = None


class ValidationSummary(BaseModel):
    """Summary of input validation for Policy C compliance"""
    critical_missing: list[str] = Field(default_factory=list, description="Critical fields that are missing")
    optional_missing: list[str] = Field(default_factory=list, description="Optional fields that are missing")
    assumptions_used: list[str] = Field(default_factory=list, description="AI default assumptions applied")
    

class SubmissionResponseWithValidation(SubmissionResponse):
    """Extended response with validation summary"""
    validation_summary: Optional[ValidationSummary] = None

