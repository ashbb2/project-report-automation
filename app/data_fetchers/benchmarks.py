"""
Static industry benchmark database for common Indian project types.
Used to ground financial assumptions and regulatory context in prompts.
Extend _BENCHMARKS to add new industries.
"""
import re
from typing import Optional

# ---------------------------------------------------------------------------
# Industry keyword classifier
# ---------------------------------------------------------------------------

_KEYWORDS: dict = {
    "agro_processing": [
        "dal", "dhal", "lentil", "rice mill", "flour mill", "oil mill", "groundnut",
        "mustard oil", "edible oil", "sugar mill", "sugarcane", "jaggery", "spice",
        "grain processing", "wheat", "paddy", "maize", "soybean", "pulses",
        "agro processing", "food grain", "milling",
    ],
    "food_beverage": [
        "dairy", "milk", "paneer", "ghee", "curd", "cheese", "bakery", "bread",
        "biscuit", "snack", "namkeen", "juice", "beverage", "soft drink", "water",
        "mineral water", "packaged food", "ready to eat", "frozen food", "chocolate",
        "confectionery", "ice cream", "noodles", "pasta",
    ],
    "textile": [
        "textile", "garment", "fabric", "yarn", "spinning", "weaving", "knitting",
        "dyeing", "printing", "apparel", "clothing", "readymade", "denim", "saree",
        "dhoti", "silk", "cotton mill", "polyester", "fibre",
    ],
    "clean_energy": [
        "solar", "photovoltaic", "pv panel", "wind energy", "ev charging",
        "electric vehicle", "biogas", "biomass", "biofuel", "ethanol", "renewable",
        "green hydrogen", "battery storage", "energy storage",
    ],
    "pharma_healthcare": [
        "pharma", "pharmaceutical", "medicine", "drug", "hospital", "clinic",
        "diagnostic", "medical device", "healthcare", "ayurveda", "herbal",
        "nutraceutical", "wellness centre", "nursing home",
    ],
    "auto_components": [
        "auto component", "automobile", "vehicle parts", "two wheeler", "car",
        "truck", "commercial vehicle", "tyre", "brake", "clutch", "engine part",
        "casting", "forging", "stamping", "auto ancillary",
    ],
    "chemical": [
        "chemical", "specialty chemical", "dye", "pigment", "adhesive",
        "paint", "coating", "resin", "polymer", "plastic", "rubber",
        "fertiliser", "pesticide", "agrochemical",
    ],
    "logistics": [
        "logistics", "warehouse", "warehousing", "cold storage", "cold chain",
        "transport", "freight", "supply chain", "3pl", "distribution",
        "e-commerce logistics",
    ],
    "education": [
        "school", "college", "university", "coaching", "training institute",
        "skill development", "vocational", "education", "edtech", "preschool",
        "nursery",
    ],
    "hospitality": [
        "hotel", "resort", "motel", "restaurant", "cafe", "food court",
        "catering", "banquet", "tourism", "hospitality", "guest house",
        "homestay",
    ],
    "it_services": [
        "software", "it services", "saas", "mobile app", "web development",
        "digital", "technology", "data analytics", "ai", "platform",
        "ecommerce", "fintech",
    ],
    "construction": [
        "construction", "real estate", "housing", "apartment", "villa",
        "commercial complex", "builder", "developer", "infrastructure",
        "road", "bridge",
    ],
    "manufacturing_general": [
        "manufacturing", "fabrication", "assembly", "production", "factory",
        "industrial", "plant", "unit", "workshop",
    ],
}


def classify_industry(business_idea: str) -> str:
    """Return the best-matching industry key for the given business idea text."""
    text = business_idea.lower()
    scores: dict[str, int] = {k: 0 for k in _KEYWORDS}
    for industry, kws in _KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                scores[industry] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "manufacturing_general"


# ---------------------------------------------------------------------------
# Industry benchmark database
# ---------------------------------------------------------------------------

_BENCHMARKS: dict = {
    "agro_processing": {
        "label": "Agro-Processing / Food Grain Milling",
        "ebitda_margin": "8–18%",
        "gross_margin": "15–28%",
        "capital_intensity": "Medium — plant, machinery, and storage silos are major capex items",
        "payback_years": "4–7 years",
        "market_context": "India's food processing sector contributes ~8% to GDP and is growing at ~7–8% CAGR. Government target: increase value-addition from ~10% to 25% of agricultural output by 2026.",
        "growth_drivers": [
            "Rising domestic consumption of processed foods",
            "Government PLI (Production-Linked Incentive) scheme for food processing",
            "Export demand for processed agri-products (APEDA target: USD 50B by 2025)",
            "Cold-chain infrastructure buildout reducing post-harvest losses",
        ],
        "key_risks": [
            "Raw material price volatility (monsoon dependency)",
            "High power and water costs in processing",
            "Competition from unorganised sector players",
            "Regulatory compliance under FSSAI",
        ],
        "government_schemes": [
            "PLI Scheme for Food Processing (MoFPI)",
            "PM FME — Pradhan Mantri Formalisation of Micro Food Enterprises",
            "APEDA export promotion for processed agricultural products",
            "SFAC (Small Farmers Agri-Business Consortium) loan support",
            "State-level food park schemes (varies by state)",
        ],
        "regulatory_highlights": [
            "FSSAI license mandatory for food processing units",
            "Pollution Control Board NOC for effluent and waste",
            "Factory Act registration for manufacturing units",
            "BIS certification for certain commodities (e.g. packaged atta, oil)",
        ],
    },
    "food_beverage": {
        "label": "Food & Beverage Processing",
        "ebitda_margin": "10–22%",
        "gross_margin": "25–45%",
        "capital_intensity": "Medium",
        "payback_years": "4–6 years",
        "market_context": "India's packaged food market is ~USD 55B and growing at 10%+ CAGR. Dairy alone is a USD 140B market. Rising urbanisation and nuclear families drive packaged food demand.",
        "growth_drivers": [
            "Urbanisation and changing consumption patterns",
            "Modern retail (organised retail, quick commerce) expanding distribution reach",
            "Export growth to Indian diaspora markets",
            "Health & wellness trend driving premium product demand",
        ],
        "key_risks": [
            "Shelf life and cold chain logistics challenges",
            "FSSAI regulatory changes (labelling, additives)",
            "Input cost volatility (dairy, sugar, edible oils)",
            "High advertising and distribution costs for brand building",
        ],
        "government_schemes": [
            "PLI Scheme for Food Processing",
            "PM FME scheme for micro enterprises",
            "NDDB / NHB support for dairy and horticulture",
            "AgriInfra Fund for cold chain and processing infrastructure",
        ],
        "regulatory_highlights": [
            "FSSAI central or state license based on turnover",
            "BIS/AGMARK for select food categories",
            "Packaging and Labelling Rules under FSS Act",
            "GST: most food items at 5–12%; processed snacks at 18%",
        ],
    },
    "textile": {
        "label": "Textile & Apparel",
        "ebitda_margin": "10–20%",
        "gross_margin": "25–40%",
        "capital_intensity": "High — looms, spindles, dyeing machines are capital-heavy",
        "payback_years": "5–8 years",
        "market_context": "India's textile industry is ~USD 140B, the 2nd largest employer after agriculture. Government target: USD 250B by 2030. India is the world's 2nd largest exporter of textiles.",
        "growth_drivers": [
            "PLI scheme for man-made fibre and technical textiles",
            "China+1 sourcing strategy by global apparel brands",
            "PM MITRA (Mega Integrated Textile Region and Apparel) parks",
            "Growing domestic organised apparel retail",
        ],
        "key_risks": [
            "Competition from Bangladesh, Vietnam on labour costs",
            "Input cost volatility (cotton, dyes)",
            "High water and power consumption inviting regulatory scrutiny",
            "Currency fluctuation impacting export margins",
        ],
        "government_schemes": [
            "PLI for Textiles (MMF and technical textiles)",
            "PM MITRA Textile Parks",
            "Amended Technology Upgradation Fund Scheme (ATUFS)",
            "RoSCTL (Rebate of State and Central Taxes and Levies) for exporters",
        ],
        "regulatory_highlights": [
            "BIS certification for many textile products",
            "REACH compliance for export to EU",
            "GPCB/State PCB consent for dyeing units (wet process)",
            "Factory Act, EPF/ESIC mandatory at scale",
        ],
    },
    "clean_energy": {
        "label": "Clean Energy (Solar, EV, Biogas, Biomass)",
        "ebitda_margin": "20–40% (solar); 12–20% (biogas/biomass)",
        "gross_margin": "35–60% (solar); 20–35% (biomass)",
        "capital_intensity": "High — capex-intensive, low opex once commissioned",
        "payback_years": "5–9 years (sector-dependent)",
        "market_context": "India targets 500 GW renewable capacity by 2030. Solar installations growing at 25%+ CAGR. EV market growing at 40%+ CAGR. PM KUSUM and MNRE schemes provide direct capex support.",
        "growth_drivers": [
            "Government renewable energy targets (500 GW by 2030)",
            "Falling solar module and battery storage costs",
            "FAME-II and PM E-DRIVE for EV ecosystem",
            "Carbon credit markets opening new revenue streams",
        ],
        "key_risks": [
            "Regulatory risk: tariff revision and PPA renegotiation",
            "Grid integration and curtailment risk",
            "Technology obsolescence risk (battery chemistry)",
            "Land acquisition and community resistance",
        ],
        "government_schemes": [
            "PM KUSUM (solar for farmers)",
            "MNRE rooftop solar scheme",
            "FAME-II / PM E-DRIVE for EV infrastructure",
            "National Green Hydrogen Mission",
            "REWA / state solar park schemes",
        ],
        "regulatory_highlights": [
            "CERC/SERC grid connectivity and tariff orders",
            "MoEF environment clearance for large plants (>25 MW)",
            "DISCOM Power Purchase Agreement (PPA) mandatory",
            "Bureau of Energy Efficiency (BEE) star labelling for equipment",
        ],
    },
    "pharma_healthcare": {
        "label": "Pharmaceuticals & Healthcare",
        "ebitda_margin": "15–30% (pharma); 8–18% (hospital)",
        "gross_margin": "40–70% (pharma); 30–50% (hospital)",
        "capital_intensity": "High (hospital); Medium (pharma mfg)",
        "payback_years": "6–10 years",
        "market_context": "India's pharma market is ~USD 50B domestically and the world's largest generic drug exporter (USD 25B+). Healthcare sector growing at 12–15% CAGR driven by rising insurance coverage.",
        "growth_drivers": [
            "Ayushman Bharat and state health insurance expanding demand",
            "API (Active Pharmaceutical Ingredient) import substitution push",
            "PLI scheme for critical bulk drugs and medical devices",
            "Medical tourism growing at 12%+ CAGR",
        ],
        "key_risks": [
            "CDSCO regulatory compliance is time-intensive and costly",
            "Price control orders (NPPA) compressing pharma margins",
            "Qualified technical staff availability in Tier 2/3 cities",
            "US FDA / WHO GMP compliance for export markets",
        ],
        "government_schemes": [
            "PLI for Pharmaceuticals and Medical Devices",
            "Bulk Drug Parks scheme",
            "Medical Device Parks scheme",
            "Ayushman Bharat PM-JAY empanelment (for hospitals)",
        ],
        "regulatory_highlights": [
            "CDSCO license mandatory for drug manufacturing",
            "GMP compliance (Schedule M of Drugs & Cosmetics Act)",
            "PCPNDT Act compliance for diagnostic centres",
            "Clinical Establishment Act registration (state-specific)",
        ],
    },
    "auto_components": {
        "label": "Auto Components & Ancillaries",
        "ebitda_margin": "10–18%",
        "gross_margin": "20–35%",
        "capital_intensity": "High — precision machinery, tooling, and quality systems",
        "payback_years": "5–8 years",
        "market_context": "India's auto component industry is ~USD 70B, targeting USD 100B by 2026. India is the 3rd largest auto market globally and a key export hub for components to EU and US OEMs.",
        "growth_drivers": [
            "EV transition driving demand for new component categories",
            "OEM vendor localisation push post supply chain disruptions",
            "PLI for Auto and Auto Components",
            "Export growth to global OEMs seeking China alternatives",
        ],
        "key_risks": [
            "OEM concentration risk — 2–3 customers can be 70%+ of revenue",
            "EV disruption making ICE-specific components obsolete",
            "High tooling and mould costs for new programme entry",
            "Quality rejection risk and warranty liability",
        ],
        "government_schemes": [
            "PLI for Auto and Auto Components",
            "FAME-II for EV supply chain development",
            "ACMA (Automotive Component Manufacturers Association) MSME support",
        ],
        "regulatory_highlights": [
            "AIS/IS standards for safety-critical components",
            "IATF 16949 quality system certification expected by OEMs",
            "BIS certification for electrical components",
            "CMVR (Central Motor Vehicles Rules) type approval for certain parts",
        ],
    },
    "chemical": {
        "label": "Specialty Chemicals & Paints",
        "ebitda_margin": "15–28%",
        "gross_margin": "30–50%",
        "capital_intensity": "Medium–High",
        "payback_years": "4–7 years",
        "market_context": "India's chemical industry is ~USD 220B and growing at 9–10% CAGR. Specialty chemicals growing faster at 12–13% CAGR. Import substitution opportunity is significant.",
        "growth_drivers": [
            "China+1 strategy creating global sourcing diversification",
            "Agri-chemicals demand tied to crop protection needs",
            "Paints and coatings tied to real estate and auto booms",
            "Pharmaceutical API and intermediates demand",
        ],
        "key_risks": [
            "Raw material (petrochemical) price volatility",
            "Stringent CPCB and state pollution norms for effluents",
            "Hazardous waste management compliance costs",
            "Export market compliance (REACH, RoHS)",
        ],
        "government_schemes": [
            "PLI for Specialty Chemicals (under consideration)",
            "Chemical Industrial Parks with common effluent treatment",
        ],
        "regulatory_highlights": [
            "Hazardous Chemicals Rules compliance under Environment Act",
            "CPCB/State PCB consent to establish and operate",
            "Factories Act and MSIHC (Major Accident Hazards) Rules",
            "BIS certification for certain chemical products",
        ],
    },
    "logistics": {
        "label": "Logistics & Warehousing",
        "ebitda_margin": "12–22%",
        "gross_margin": "25–40%",
        "capital_intensity": "Medium–High (cold chain is higher)",
        "payback_years": "5–8 years",
        "market_context": "India's logistics market is ~USD 250B, targeted at USD 320B by 2026. PM GatiShakti and National Logistics Policy aim to cut logistics costs from 14% to 8% of GDP.",
        "growth_drivers": [
            "E-commerce and quick commerce driving warehousing demand",
            "Cold chain growth driven by food processing and pharma",
            "PM GatiShakti infrastructure push",
            "GST unifying national market and enabling hub-and-spoke models",
        ],
        "key_risks": [
            "High real estate costs in logistics corridors",
            "Fuel price volatility in transport",
            "Labour-intensive operations with attrition challenges",
            "Compliance with fire safety and hazardous goods rules",
        ],
        "government_schemes": [
            "PM GatiShakti National Master Plan",
            "National Logistics Policy 2022",
            "LEADS (Logistics Ease Across Different States) ranking",
            "AgriInfra Fund for agri-logistics infrastructure",
        ],
        "regulatory_highlights": [
            "Warehouse Development and Regulatory Authority (WDRA) registration for negotiable warehousing",
            "Fire NOC mandatory for warehouses above threshold area",
            "Municipal building permits and zoning compliance",
            "GST registration and e-way bill compliance for freight",
        ],
    },
    "education": {
        "label": "Education & Training",
        "ebitda_margin": "20–35%",
        "gross_margin": "50–70%",
        "capital_intensity": "Low–Medium",
        "payback_years": "3–6 years",
        "market_context": "India's education market is ~USD 120B and one of the world's largest. Private school enrolment exceeds 50% in urban areas. Skill development sector growing at 15%+ CAGR.",
        "growth_drivers": [
            "National Education Policy 2020 driving curriculum reform",
            "Rising middle-class aspiration for quality private education",
            "Skill development and vocational training government push",
            "Edtech and blended learning opening new revenue streams",
        ],
        "key_risks": [
            "Regulatory changes to fee structures and affiliations",
            "Teacher attrition and qualified staff scarcity",
            "Competition from online/edtech platforms",
            "Affiliation compliance timelines (CBSE, state boards)",
        ],
        "government_schemes": [
            "PM YASASVI (scholarships for OBC/EBC students)",
            "PMKVY (Pradhan Mantri Kaushal Vikas Yojana) for skill centres",
            "Jan Shikshan Sansthan for vocational training",
            "NSDC (National Skill Development Corporation) partnerships",
        ],
        "regulatory_highlights": [
            "Societies / Trust / Section 8 Company registration required",
            "Affiliation from CBSE/ICSE/state board (school)",
            "AICTE/UGC recognition for technical/higher education",
            "Fire NOC and building safety compliance for physical campus",
        ],
    },
    "hospitality": {
        "label": "Hospitality (Hotels, Resorts, Restaurants)",
        "ebitda_margin": "15–30%",
        "gross_margin": "60–75% (food & beverage typically lower)",
        "capital_intensity": "High (hotel); Low–Medium (restaurant)",
        "payback_years": "6–12 years (hotel); 2–5 years (restaurant)",
        "market_context": "India's hospitality market is ~USD 32B and targeted to double by 2030. Domestic tourism is the primary growth driver. Mid-market hotels are the fastest-growing segment.",
        "growth_drivers": [
            "Domestic tourism growth post-pandemic",
            "UDAN scheme expanding air connectivity to Tier 2/3 cities",
            "Religious and heritage tourism growing strongly",
            "Business travel linked to industrial corridor development",
        ],
        "key_risks": [
            "High fixed costs create revenue sensitivity to occupancy",
            "Seasonality and event-dependence in leisure markets",
            "FSSAI, liquor license, and fire NOC compliance complexity",
            "Aggregator (Zomato, Swiggy) margin pressure for restaurants",
        ],
        "government_schemes": [
            "PRASAD (Pilgrimage Rejuvenation and Spiritual Augmentation Drive) for religious tourism",
            "SWADESH DARSHAN 2.0 for thematic tourism circuits",
            "MDA (Market Development Assistance) for tourism promotion",
        ],
        "regulatory_highlights": [
            "Hotel/restaurant classification and licensing (state tourism)",
            "FSSAI license for food service operations",
            "Liquor license (state excise department)",
            "Fire NOC and building occupation certificate",
            "PCB consent for effluent disposal (large hotels)",
        ],
    },
    "it_services": {
        "label": "IT Services & Software",
        "ebitda_margin": "18–35%",
        "gross_margin": "35–60%",
        "capital_intensity": "Low — primarily office space and human capital",
        "payback_years": "2–4 years",
        "market_context": "India's IT-BPM industry is ~USD 250B with 5M+ employees. Exports dominate at ~USD 194B. Domestic IT market growing at 12%+ CAGR driven by digital transformation.",
        "growth_drivers": [
            "Global digital transformation outsourcing demand",
            "AI and cloud services creating new service lines",
            "Startup ecosystem and SaaS market expanding",
            "GIFT City and emerging tech hubs enabling GCC setups",
        ],
        "key_risks": [
            "Visa restrictions and immigration policy changes affecting onsite delivery",
            "AI automation reducing certain service categories",
            "Talent attrition and rising employee costs",
            "Currency fluctuation for export-oriented units",
        ],
        "government_schemes": [
            "Software Technology Parks of India (STPI) export benefits",
            "SEZ benefits for export-oriented units",
            "MeitY startup and AI innovation grants",
            "GIFT City financial and technology hub incentives",
        ],
        "regulatory_highlights": [
            "STPI or SEZ registration for export benefits",
            "Data Protection compliance (DPDPA 2023)",
            "RBI guidelines for fintech or payment businesses",
            "Shops and Establishments Act (state-specific) for office",
        ],
    },
    "construction": {
        "label": "Construction & Real Estate",
        "ebitda_margin": "12–22%",
        "gross_margin": "20–35%",
        "capital_intensity": "High",
        "payback_years": "4–8 years",
        "market_context": "India's real estate market is ~USD 265B and growing at 10%+ CAGR. Residential demand is driven by urbanisation; commercial demand by IT parks and logistics. RERA has improved regulatory transparency.",
        "growth_drivers": [
            "PM Awas Yojana (housing for all) driving affordable housing",
            "Smart City Mission and AMRUT driving urban infrastructure",
            "Data centre and warehousing demand from IT and e-commerce",
            "Tourism infrastructure investment",
        ],
        "key_risks": [
            "RERA compliance and delivery delay penalties",
            "Land acquisition and title risk",
            "Commodity price risk (steel, cement)",
            "Interest rate sensitivity on home loan offtake",
        ],
        "government_schemes": [
            "PMAY (Pradhan Mantri Awas Yojana) subsidy",
            "CLSS (Credit Linked Subsidy Scheme) for affordable housing",
            "Smart Cities Mission grants",
            "AMRUT (Atal Mission for Rejuvenation and Urban Transformation)",
        ],
        "regulatory_highlights": [
            "RERA registration mandatory for projects >500 sq.m or 8 apartments",
            "Building plan approval from local authority / development authority",
            "Environmental clearance for large projects (>20,000 sq.m built-up)",
            "OC (Occupancy Certificate) before handover",
        ],
    },
    "manufacturing_general": {
        "label": "General Manufacturing",
        "ebitda_margin": "10–20%",
        "gross_margin": "20–40%",
        "capital_intensity": "Medium–High",
        "payback_years": "4–7 years",
        "market_context": "India's manufacturing sector contributes ~17% to GDP, targeting 25% under Make in India. FDI in manufacturing reached USD 21B in FY24. China+1 strategy is creating significant greenfield investment.",
        "growth_drivers": [
            "Make in India and PLI schemes across 14 sectors",
            "China+1 sourcing diversification by global buyers",
            "Infrastructure buildout driving domestic demand for inputs",
            "Defence indigenisation (Atmanirbhar Bharat)",
        ],
        "key_risks": [
            "Raw material import dependence and supply chain disruption",
            "Skilled labour shortage in specialised manufacturing",
            "Power reliability and cost in industrial zones",
            "Competition from established players and imports",
        ],
        "government_schemes": [
            "PLI (Production-Linked Incentive) — sector-specific",
            "MSME Udyam Registration for credit and scheme benefits",
            "NSIC (National Small Industries Corporation) support",
            "District Industries Centre (DIC) for state-level support",
        ],
        "regulatory_highlights": [
            "Factory Act registration and periodic inspections",
            "Pollution Control Board NOC (consent to establish + operate)",
            "BIS certification for applicable product categories",
            "Udyam (MSME) registration for MSME benefits",
            "Labour law compliance: EPF, ESIC, Gratuity",
        ],
    },
}


def get_industry_benchmark_context(industry_key: str) -> str:
    b = _BENCHMARKS.get(industry_key, _BENCHMARKS["manufacturing_general"])
    drivers = "\n".join(f"  - {d}" for d in b["growth_drivers"])
    risks = "\n".join(f"  - {r}" for r in b["key_risks"])
    schemes = "\n".join(f"  - {s}" for s in b["government_schemes"])
    regs = "\n".join(f"  - {r}" for r in b["regulatory_highlights"])

    return (
        f"INDUSTRY BENCHMARKS — {b['label'].upper()}:\n"
        f"• Typical EBITDA Margin: {b['ebitda_margin']}\n"
        f"• Typical Gross Margin: {b['gross_margin']}\n"
        f"• Capital Intensity: {b['capital_intensity']}\n"
        f"• Typical Payback Period: {b['payback_years']}\n"
        f"• India Market Context: {b['market_context']}\n\n"
        f"Key Growth Drivers:\n{drivers}\n\n"
        f"Key Risks:\n{risks}\n\n"
        f"Applicable Government Schemes (verify current eligibility):\n{schemes}\n\n"
        f"Regulatory Highlights:\n{regs}"
    )
