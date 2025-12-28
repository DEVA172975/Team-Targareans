#!/usr/bin/env python3
"""
Live Financial Memory Agent Demo
Demonstrates real-time financial intelligence with adaptive insights
"""

from financial_agent import LiveFinancialAgent
from models import RevenueData, BusinessType
import time
import json

def demo_live_analysis():
    print("🧠 Live Financial Memory Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = LiveFinancialAgent()
    
    # Simulate live data ingestion
    demo_scenarios = [
        {
            "data": RevenueData(month="2024-01", revenue=35000, expenses=25000, business_type=BusinessType.RETAIL),
            "description": "Starting small retail business"
        },
        {
            "data": RevenueData(month="2024-02", revenue=42000, expenses=28000, business_type=BusinessType.RETAIL),
            "description": "Growth month - 20% revenue increase"
        },
        {
            "data": RevenueData(month="2024-03", revenue=48000, expenses=30000, business_type=BusinessType.RETAIL),
            "description": "Continued growth trajectory"
        },
        {
            "data": RevenueData(month="2024-04", revenue=52000, expenses=31000, business_type=BusinessType.RETAIL),
            "description": "Strong performance month"
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['description']}")
        print(f"Revenue: ${scenario['data'].revenue:,.2f} | Expenses: ${scenario['data'].expenses:,.2f}")
        
        # Ingest data and trigger live analysis
        insights = agent.ingest_revenue_data(scenario['data'])
        
        if insights:
            print(f"\n🔍 Generated {len(insights)} new insights:")
            for insight in insights:
                print(f"  • {insight.title}")
                print(f"    {insight.description}")
                print(f"    💡 {insight.recommendation}")
                print()
        else:
            print("  No new insights generated")
        
        time.sleep(1)  # Simulate real-time delay
    
    # Show final summary
    print("\n📈 Final Financial Summary:")
    summary = agent.get_financial_summary()
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            if 'revenue' in key.lower() or 'expense' in key.lower() or 'profit' in key.lower():
                print(f"  {key.replace('_', ' ').title()}: ${value:,.2f}")
            else:
                print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    demo_live_analysis()