from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class BusinessType(str, Enum):
    RETAIL = "retail"
    SERVICES = "services"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"

class TaxType(str, Enum):
    SERVICE_TAX = "service_tax"
    PRODUCT_TAX = "product_tax"

class RevenueData(BaseModel):
    month: str
    revenue: float
    expenses: float
    business_type: BusinessType
    tax_type: TaxType
    service_revenue: float = 0.0
    product_revenue: float = 0.0
    timestamp: datetime = datetime.now()

class TaxRule(BaseModel):
    business_type: BusinessType
    tax_type: TaxType
    income_bracket_min: float
    income_bracket_max: float
    tax_rate: float
    description: str

class CompetitorBenchmark(BaseModel):
    business_type: BusinessType
    avg_monthly_revenue: float
    avg_profit_margin: float
    avg_tax_rate: float
    market_segment: str
    data_source: str

class FinancialInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    impact: str
    recommendation: str
    confidence: float
    timestamp: datetime = datetime.now()

class DocumentData(BaseModel):
    filename: str
    content: str
    document_type: str
    extracted_data: Dict = {}