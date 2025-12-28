import json
import os
from models import RevenueData, BusinessType, TaxType

def load_sample_dataset(agent, dataset_type="comprehensive"):
    """Load sample datasets into the agent"""
    
    if dataset_type == "comprehensive":
        # Comprehensive dataset with mixed business types
        sample_data = [
            RevenueData(month="2023-08", revenue=38000, expenses=28000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=5000, product_revenue=33000),
            RevenueData(month="2023-09", revenue=42000, expenses=30000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=6000, product_revenue=36000),
            RevenueData(month="2023-10", revenue=45000, expenses=32000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=45000, product_revenue=0),
            RevenueData(month="2023-11", revenue=48000, expenses=33000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=48000, product_revenue=0),
            RevenueData(month="2023-12", revenue=52000, expenses=35000, business_type=BusinessType.TECHNOLOGY, tax_type=TaxType.SERVICE_TAX, service_revenue=52000, product_revenue=0),
            RevenueData(month="2024-01", revenue=55000, expenses=36000, business_type=BusinessType.TECHNOLOGY, tax_type=TaxType.SERVICE_TAX, service_revenue=55000, product_revenue=0),
            RevenueData(month="2024-02", revenue=58000, expenses=38000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=8000, product_revenue=50000),
            RevenueData(month="2024-03", revenue=62000, expenses=40000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=10000, product_revenue=52000),
        ]
    
    elif dataset_type == "growth_story":
        # Strong growth trajectory
        sample_data = [
            RevenueData(month="2024-01", revenue=25000, expenses=20000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=25000, product_revenue=0),
            RevenueData(month="2024-02", revenue=32000, expenses=22000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=32000, product_revenue=0),
            RevenueData(month="2024-03", revenue=45000, expenses=28000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=45000, product_revenue=0),
            RevenueData(month="2024-04", revenue=58000, expenses=35000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=58000, product_revenue=0),
        ]
    
    elif dataset_type == "struggling_business":
        # Business with some loss months
        sample_data = [
            RevenueData(month="2024-01", revenue=35000, expenses=32000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=5000, product_revenue=30000),
            RevenueData(month="2024-02", revenue=28000, expenses=35000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=3000, product_revenue=25000),  # Loss month
            RevenueData(month="2024-03", revenue=32000, expenses=30000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=4000, product_revenue=28000),
            RevenueData(month="2024-04", revenue=38000, expenses=33000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, service_revenue=6000, product_revenue=32000),
        ]
    
    # Load data into agent
    total_insights = 0
    for data in sample_data:
        insights = agent.ingest_revenue_data(data)
        total_insights += len(insights) if insights else 0
    
    return {
        "loaded_months": len(sample_data),
        "total_insights": total_insights,
        "dataset_type": dataset_type
    }