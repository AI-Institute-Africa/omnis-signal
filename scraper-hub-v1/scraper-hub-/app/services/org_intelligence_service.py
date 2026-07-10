import logging
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session
from app.config import settings
from app.db.models.organization import Organization
from app.db.models.product import Product
from app.db.models.service import Service
from app.db.models.price_entry import PriceEntry
from app.scraping.schemas import ProductSchema, ServiceSchema

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class OrgExtractionResponse(BaseModel):
    ai_summary: str = Field(description="A concise summary of the organization's business and market position.")
    sector_classification: str = Field(description="The primary industry sector.")
    risk_score: float = Field(description="0-100 score indicating operational or market risk (lower is better).")
    reputation_score: float = Field(description="0-100 score indicating public reputation.")
    innovation_score: float = Field(description="0-100 score indicating technological innovation.")
    market_influence_score: float = Field(description="0-100 score indicating market share and influence.")
    products: List[ProductSchema] = Field(default_factory=list, description="List of physical or digital products.")
    services: List[ServiceSchema] = Field(default_factory=list, description="List of services or plans offered.")

class OrgIntelligenceService:
    """Uses Gemini API to extract rich insights from organization raw data."""

    def __init__(self, db: Session):
        self.db = db

    def get_sector_prompt(self, org: Organization) -> str:
        """Returns specialized instructions based on the organization's sector."""
        category = (org.category or "").lower()
        
        if category in ["telecoms", "telecom", "internet"]:
            return """
            MASTER ARCHITECTURE: TELECOMS & INTERNET
            You MUST follow this exact structure for every extracted item:
            
            EXTRACT COLUMNS:
            - category: (VOICE, SMS, DATA, USSD, INTERNET, QUALITY, COVERAGE, BILLING, BUNDLES)
            - subcategory: (e.g., On-net Calls, Standard Bundles, Fibre Internet)
            - what_to_compare: (The specific metric or plan name)
            - normalized_unit: ($/sec, $/min, $/SMS, $/MB, $/GB, Mbps, ms, etc.)
            - availability_flags: {
                "per_second": bool, "per_minute": bool, "per_hour": bool,
                "daily": bool, "3_days": bool, "weekly": bool, 
                "bi_weekly": bool, "monthly": bool, "yearly": bool
            }
            - formula: (The logic used to calculate the normalized_value)
            - normalized_value: (The result of the formula)
            
            SPECIFIC CATEGORIES:
            1. VOICE: Compare On-net, Off-net, International. Calculate $/min and $/sec.
            2. SMS: Local, Bulk, International. Calculate $/SMS.
            3. DATA: Standard, Social, Night, Unlimited. Calculate $/MB or $/GB.
            4. INTERNET: Fibre, Wireless, Broadband. Track Speed (Mbps) and Install fees.
            5. QUALITY: Track Download/Upload Speed, Latency, Uptime.
            
            NORMALIZATION LOGIC:
            - If "50c for 200MB", formula: "0.50 / 200", normalized_value: 0.0025, normalized_unit: "$/MB"
            - If "$1 for 1GB", formula: "1 / 1024", normalized_value: 0.00097, normalized_unit: "$/MB"
            """
        
        if category in ["universities", "colleges"]:
            return """
            MASTER ARCHITECTURE: UNIVERSITIES
            Follow this structure:
            - category: (TUITION, ACCOMMODATION, ADMIN, OTHER)
            - what_to_compare: (Course name or Fee type)
            - normalized_unit: ($/semester, $/year, $/once)
            - normalized_value: (Price per unit)
            - duration: (Semester, Year, etc.)
            """
            
        if category in ["hospitals", "medical"]:
            return """
            MASTER ARCHITECTURE: HOSPITALS
            Follow this structure:
            - category: (CONSULTATION, ACCOMMODATION, PROCEDURES, OTHER)
            - what_to_compare: (Service name)
            - normalized_unit: ($/visit, $/night, $/procedure)
            - normalized_value: (Price per unit)
            """

        if category in ["hotels", "tourism"]:
            return """
            MASTER ARCHITECTURE: HOTELS
            Follow this structure:
            - category: (ACCOMMODATION, DINING, FACILITIES)
            - what_to_compare: (Room type or Service)
            - normalized_unit: ($/night, $/person, $/use)
            - normalized_value: (Price per unit)
            """
            
        return "Extract all products, services, and prices mentioned."

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def enrich_organization(self, org: Organization, raw_text: str) -> dict:
        """Analyze raw text and extract structured intelligence and catalog items."""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Skipping AI enrichment.")
            return {}

        if not raw_text or len(raw_text) < 100:
            logger.warning(f"Not enough text to enrich {org.name}")
            return {}

        sector_instructions = self.get_sector_prompt(org)
        logger.info(f"[OrgIntelligence] Running Gemini for {org.name} ({org.category})")
        
        try:
            model = genai.GenerativeModel("gemini-flash-latest")
            prompt = f"""
            You are an expert Business Intelligence Analyst specializing in the Zimbabwean market.
            Analyze the following website text for '{org.name}'.
            
            {sector_instructions}
            
            Output ONLY valid JSON. 
            Be extremely precise with math. Ensure the 'normalized_value' matches the 'formula'.
            
            JSON format:
            {{
                "ai_summary": "Concise market position summary.",
                "sector_classification": "Industry sector",
                "risk_score": 25.0,
                "reputation_score": 85.0,
                "innovation_score": 75.0,
                "market_influence_score": 90.0,
                "items": [
                    {{
                        "name": "Full Plan Name",
                        "category": "CATEGORY",
                        "subcategory": "SUBCATEGORY",
                        "what_to_compare": "Specific aspect",
                        "description": "Details",
                        "price": {{ 
                            "price_value": 10.0, 
                            "currency": "USD",
                            "normalized_value": 0.0025,
                            "normalized_unit": "$/MB",
                            "formula": "price / quantity",
                            "availability_flags": {{ "daily": true, "weekly": false, ... }},
                            "metrics": {{ "speed": "10Mbps" }}
                        }}
                    }}
                ]
            }}

            Text:
            {raw_text[:25000]}
            """

            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )

            data = json.loads(response.text)
            
            # Save products/services
            self._save_items(org, data)

            return {
                "ai_summary": data.get("ai_summary"),
                "sector_classification": data.get("sector_classification"),
                "risk_score": data.get("risk_score"),
                "reputation_score": data.get("reputation_score"),
                "innovation_score": data.get("innovation_score"),
                "market_influence_score": data.get("market_influence_score"),
            }
        except Exception as e:
            logger.error(f"[OrgIntelligence] Gemini extraction failed: {e}")
            return {}

    def _save_items(self, org: Organization, data: dict):
        """Populate Product/Service and PriceEntry models from AI output."""
        items = data.get("items", [])
        for item in items:
            # We treat items as either Products or Services based on category
            # For simplicity, if it has 'what_to_compare', we put it in Service/Product
            # Let's decide based on category
            cat = item.get("category", "").upper()
            
            is_service = cat in ["VOICE", "SMS", "DATA", "INTERNET", "QUALITY", "COVERAGE", "BUNDLES", "USSD"]
            
            if is_service:
                target_model = Service
                obj = self.db.query(Service).filter(
                    Service.organization_id == org.id,
                    Service.name == item.get("name")
                ).first()
            else:
                target_model = Product
                obj = self.db.query(Product).filter(
                    Product.organization_id == org.id,
                    Product.name == item.get("name")
                ).first()

            if not obj:
                obj = target_model(
                    organization_id=org.id,
                    name=item.get("name"),
                    category=item.get("subcategory") or item.get("category"),
                    description=item.get("description")
                )
                # Add specific field for Service if it exists
                if is_service and hasattr(obj, "features"):
                    obj.features = item.get("features", [])
                
                self.db.add(obj)
                self.db.flush()
            
            self._add_price(
                product_id=obj.id if not is_service else None,
                service_id=obj.id if is_service else None,
                org_id=org.id,
                price_info=item.get("price", {})
            )

        self.db.commit()
        logger.info(f"[OrgIntelligence] Saved {len(items)} items for {org.name}")

    def _add_price(self, product_id, service_id, org_id, price_info: dict):
        if not price_info:
            return

        latest_price = self.db.query(PriceEntry).filter(
            PriceEntry.product_id == product_id if product_id else PriceEntry.service_id == service_id
        ).order_by(PriceEntry.captured_at.desc()).first()

        new_val = price_info.get("price_value")
        if new_val is None:
            return

        currency = price_info.get("currency", "USD")

        if latest_price and latest_price.price_value == new_val and latest_price.currency == currency:
            return # No change

        flags = price_info.get("availability_flags", {})

        pe = PriceEntry(
            product_id=product_id,
            service_id=service_id,
            organization_id=org_id,
            price_value=new_val,
            currency=currency,
            normalized_value=price_info.get("normalized_value"),
            normalized_unit=price_info.get("normalized_unit"),
            comparable_metrics=price_info.get("metrics"),
            formula=price_info.get("formula"),
            per_second=flags.get("per_second", False),
            per_minute=flags.get("per_minute", False),
            per_hour=flags.get("per_hour", False),
            daily=flags.get("daily", False),
            three_days=flags.get("3_days", False),
            weekly=flags.get("weekly", False),
            bi_weekly=flags.get("bi_weekly", False),
            monthly=flags.get("monthly", False),
            yearly=flags.get("yearly", False),
            discount_price=price_info.get("discount_price"),
            previous_price=latest_price.price_value if latest_price else price_info.get("previous_price"),
            is_promotion=price_info.get("is_promotion", False),
            promotion_details=price_info.get("promotion_details")
        )
        self.db.add(pe)
