import re
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
from typing import Optional, Literal
from enum import Enum


class BusinessModel(str, Enum):
    MANUFACTURING = "Manufacturing"
    TRADING_WHOLESALE = "Trading (Wholesale)"
    TRADING_RETAIL = "Trading (Retail)"


class SizingMode(str, Enum):
    CAPACITY_DRIVEN = "capacity_driven"
    BUDGET_DRIVEN = "budget_driven"


INDIA_STATE_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat", "Tawang"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar", "Bhavnagar"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Karnal"],
    "Himachal Pradesh": ["Shimla", "Dharamshala", "Solan", "Mandi", "Baddi"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi", "Shivamogga"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kannur"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Kolhapur"],
    "Manipur": ["Imphal", "Churachandpur", "Thoubal"],
    "Meghalaya": ["Shillong", "Tura", "Jowai"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Sambalpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Mohali"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Sikkim": ["Gangtok", "Namchi", "Gyalshing"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruppur", "Salem", "Trichy"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Noida", "Ghaziabad", "Agra", "Varanasi", "Prayagraj"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Haldwani"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Andaman and Nicobar Islands": ["Port Blair"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Diu", "Silvassa"],
    "Delhi": ["New Delhi", "Delhi"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag"],
    "Ladakh": ["Leh", "Kargil"],
    "Lakshadweep": ["Kavaratti"],
    "Puducherry": ["Puducherry", "Karaikal"]
}


INDIA_CITY_ALIASES = {
    "Maharashtra": {"bombay": "Mumbai", "poona": "Pune"},
    "Karnataka": {"bangalore": "Bengaluru", "hubli": "Hubballi"},
    "West Bengal": {"calcutta": "Kolkata"},
    "Tamil Nadu": {"madras": "Chennai", "trichinopoly": "Trichy"},
    "Kerala": {"cochin": "Kochi", "calicut": "Kozhikode", "trivandrum": "Thiruvananthapuram"},
    "Haryana": {"gurgaon": "Gurugram"},
    "Gujarat": {"baroda": "Vadodara"},
    "Uttar Pradesh": {"allahabad": "Prayagraj", "benaras": "Varanasi", "benares": "Varanasi"},
    "Himachal Pradesh": {"simla": "Shimla"},
    "Puducherry": {"pondicherry": "Puducherry"}
}


class SubmissionCreate(BaseModel):
    # Project Identity (Critical)
    client_name: str = Field(..., min_length=1, description="Client/organization name")
    project_title: str = Field(..., min_length=1, description="Project title")
    product_service: str = Field(..., min_length=1, description="Product or service description")
    hsn_family_code: str = Field(..., pattern=r'^\d{4}$', description="HSN family code (4-digit)")
    hsn_family_name: Optional[str] = Field(None, description="HSN family description")
    hsn_code: str = Field(..., description="HSN code (4, 6, or 8 digits)")
    hsn_description: str = Field(..., min_length=1, description="HSN code description")
    project_city: str = Field(..., min_length=1, description="Project city")
    project_state: str = Field(..., min_length=1, description="Project state")
    project_country: str = Field(default="India", min_length=1, description="Project country")
    project_pin_code: Optional[str] = Field(None, description="Project pin code")
    project_location: Optional[str] = Field(None, min_length=1, description="Project location details")
    target_customer: str = Field(..., min_length=1, description="Target customer segment")
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

    @model_validator(mode='before')
    @classmethod
    def populate_derived_fields(cls, data):
        if not isinstance(data, dict):
            return data

        city = data.get('project_city')
        state = data.get('project_state')
        pin_code = data.get('project_pin_code')
        country = data.get('project_country') or 'India'
        data['project_country'] = country

        if isinstance(state, str):
            data['project_state'] = state.strip()
        if isinstance(city, str):
            city = city.strip()
            data['project_city'] = city
        if isinstance(pin_code, str):
            pin_code = pin_code.strip() or None
            data['project_pin_code'] = pin_code
        if isinstance(country, str):
            data['project_country'] = country.strip() or 'India'

        location_parts = [data.get('project_country'), data.get('project_state'), city, pin_code]
        derived_location = ', '.join(str(part).strip() for part in location_parts if part)

        if derived_location and not data.get('project_location'):
            data['project_location'] = derived_location

        if derived_location and not data.get('location_land'):
            data['location_land'] = derived_location

        if data.get('target_customer') and not data.get('target_market'):
            data['target_market'] = data['target_customer']

        return data

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

    @field_validator('client_name', 'project_title', 'product_service', 'hsn_description', 'project_city', 'project_state', 'target_customer')
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError('This field cannot be blank')
        return normalized

    @field_validator('hsn_code')
    @classmethod
    def validate_hsn_code(cls, value: str) -> str:
        normalized = value.strip()
        if not re.fullmatch(r'\d{4}|\d{6}|\d{8}', normalized):
            raise ValueError('hsn_code must be 4, 6, or 8 digits')
        return normalized

    @field_validator('project_country')
    @classmethod
    def validate_project_country(cls, value: str) -> str:
        normalized = value.strip()
        return normalized or 'India'

    @model_validator(mode='after')
    def validate_location_rules(self):
        # India-specific validation lives here so future country rules are easy to find.
        if self.project_country.strip().lower() == 'india' and self.project_pin_code:
            if not re.fullmatch(r'\d{6}', self.project_pin_code):
                raise ValueError('project_pin_code must be exactly 6 digits for India')
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "client_name": "ABC Manufacturing Ltd",
                "project_title": "Eco-Friendly Packaging Plant",
                "product_service": "Biodegradable packaging materials for food industry",
                "hsn_family_code": "3923",
                "hsn_family_name": "Articles for the conveyance or packing of goods",
                "hsn_code": "392390",
                "hsn_description": "Other articles for conveyance or packing of goods",
                "project_city": "Ahmedabad",
                "project_state": "Gujarat",
                "project_country": "India",
                "project_pin_code": "382445",
                "project_location": "India, Gujarat, Ahmedabad, 382445",
                "target_customer": "Food packaging manufacturers and FMCG brands",
                "business_model": "Manufacturing",
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
    hsn_family_code: Optional[str] = None
    hsn_family_name: Optional[str] = None
    hsn_code: Optional[str] = None
    hsn_description: Optional[str] = None
    project_location: str
    project_city: Optional[str] = None
    project_state: Optional[str] = None
    project_country: Optional[str] = None
    project_pin_code: Optional[str] = None
    target_customer: Optional[str] = None
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

