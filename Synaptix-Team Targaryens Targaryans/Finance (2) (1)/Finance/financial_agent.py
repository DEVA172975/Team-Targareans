# import pathway as pw  # Not needed for this implementation
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from models import RevenueData, TaxRule, CompetitorBenchmark, FinancialInsight, BusinessType, TaxType
from database import FinancialDB
import PyPDF2
import io

class LiveFinancialAgent:
    def __init__(self):
        self.db = FinancialDB()
        self.revenue_memory = self.db.get_all_revenue_data()  # Load from DB
        self.tax_rules = self._load_default_tax_rules()
        self.competitor_benchmarks = self._load_default_benchmarks()
        self.insights_history = self.db.get_recent_insights(50)  # Load from DB
        self.documents = []
        
    def _load_default_tax_rules(self) -> List[TaxRule]:
        return [
            # Service Tax Rules
            TaxRule(business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, income_bracket_min=0, income_bracket_max=50000, tax_rate=0.18, description="Service tax - Small business"),
            TaxRule(business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, income_bracket_min=50000, income_bracket_max=200000, tax_rate=0.28, description="Service tax - Medium business"),
            TaxRule(business_type=BusinessType.TECHNOLOGY, tax_type=TaxType.SERVICE_TAX, income_bracket_min=0, income_bracket_max=100000, tax_rate=0.20, description="Tech service tax"),
            
            # Product Tax Rules
            TaxRule(business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, income_bracket_min=0, income_bracket_max=50000, tax_rate=0.12, description="Product tax - Small retail"),
            TaxRule(business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, income_bracket_min=50000, income_bracket_max=200000, tax_rate=0.18, description="Product tax - Medium retail"),
            TaxRule(business_type=BusinessType.MANUFACTURING, tax_type=TaxType.PRODUCT_TAX, income_bracket_min=0, income_bracket_max=100000, tax_rate=0.15, description="Manufacturing product tax"),
        ]
    
    def _load_default_benchmarks(self) -> List[CompetitorBenchmark]:
        return [
            CompetitorBenchmark(business_type=BusinessType.RETAIL, avg_monthly_revenue=45000, avg_profit_margin=0.12, avg_tax_rate=0.15, market_segment="local", data_source="industry_report"),
            CompetitorBenchmark(business_type=BusinessType.SERVICES, avg_monthly_revenue=65000, avg_profit_margin=0.25, avg_tax_rate=0.22, market_segment="regional", data_source="market_analysis"),
            CompetitorBenchmark(business_type=BusinessType.TECHNOLOGY, avg_monthly_revenue=120000, avg_profit_margin=0.35, avg_tax_rate=0.20, market_segment="startup", data_source="tech_survey"),
            CompetitorBenchmark(business_type=BusinessType.MANUFACTURING, avg_monthly_revenue=85000, avg_profit_margin=0.18, avg_tax_rate=0.15, market_segment="industrial", data_source="manufacturing_report"),
        ]
    
    def process_document(self, file_content: bytes, filename: str) -> Dict:
        """Extract financial data from PDF documents"""
        try:
            if filename.lower().endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Simple extraction logic - can be enhanced with ML
                extracted_data = self._extract_financial_data(text)
                return {"status": "success", "extracted_data": extracted_data, "text": text[:500]}
            else:
                return {"status": "error", "message": "Only PDF files supported"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _extract_financial_data(self, text: str) -> Dict:
        """Basic financial data extraction from text"""
        import re
        
        # Simple regex patterns for common financial terms
        revenue_pattern = r'revenue[:\s]*\$?([0-9,]+(?:\.[0-9]{2})?)'
        expense_pattern = r'expense[s]?[:\s]*\$?([0-9,]+(?:\.[0-9]{2})?)'
        
        revenue_match = re.search(revenue_pattern, text.lower())
        expense_match = re.search(expense_pattern, text.lower())
        
        extracted = {}
        if revenue_match:
            extracted['revenue'] = float(revenue_match.group(1).replace(',', ''))
        if expense_match:
            extracted['expenses'] = float(expense_match.group(1).replace(',', ''))
            
        return extracted
    
    def ingest_revenue_data(self, revenue_data: RevenueData, source_file="manual"):
        """Live ingestion of new revenue data with database persistence"""
        self.revenue_memory.append(revenue_data)
        self.db.save_revenue_data(revenue_data, source_file)  # Save to database with source
        return self._trigger_analysis()
    
    def _trigger_analysis(self):
        """Triggered whenever new data arrives"""
        if not self.revenue_memory:
            return
            
        latest_data = self.revenue_memory[-1]
        insights = []
        
        # Calculate tax impact
        tax_insight = self._analyze_tax_impact(latest_data)
        if tax_insight:
            insights.append(tax_insight)
        
        # Analyze trends if we have historical data
        if len(self.revenue_memory) > 1:
            trend_insight = self._analyze_trends()
            if trend_insight:
                insights.append(trend_insight)
        
        # Compare with competitors
        competitor_insight = self._compare_with_competitors(latest_data)
        if competitor_insight:
            insights.append(competitor_insight)
        
        self.insights_history.extend(insights)
        
        # Save insights to database
        for insight in insights:
            self.db.save_insight(insight)
            
        return insights
    
    def _analyze_tax_impact(self, revenue_data: RevenueData) -> FinancialInsight:
        """Calculate monthly tax burden with separate service/product tax"""
        net_income = revenue_data.revenue - revenue_data.expenses
        
        # Find applicable tax rule
        applicable_tax_rule = None
        for rule in self.tax_rules:
            if (rule.business_type == revenue_data.business_type and 
                rule.tax_type == revenue_data.tax_type and
                rule.income_bracket_min <= net_income <= rule.income_bracket_max):
                applicable_tax_rule = rule
                break
        
        if not applicable_tax_rule:
            return None
            
        # Calculate tax based on type
        if revenue_data.tax_type == "service_tax":
            taxable_amount = revenue_data.service_revenue or revenue_data.revenue
        else:
            taxable_amount = revenue_data.product_revenue or revenue_data.revenue
            
        monthly_tax = (taxable_amount - revenue_data.expenses) * applicable_tax_rule.tax_rate
        tax_percentage = (monthly_tax / revenue_data.revenue) * 100
        
        tax_type_label = "Service Tax" if revenue_data.tax_type == "service_tax" else "Product Tax"
        
        return FinancialInsight(
            insight_type="tax_analysis",
            title=f"{tax_type_label}: ₹{monthly_tax:,.2f}",
            description=f"Based on {tax_type_label.lower()} rate of {applicable_tax_rule.tax_rate*100:.1f}%, you'll pay ₹{monthly_tax:,.2f} ({tax_percentage:.1f}% of revenue)",
            impact=f"Tax burden represents {tax_percentage:.1f}% of total revenue",
            recommendation="Consider tax optimization if burden exceeds 20%" if tax_percentage > 20 else "Tax burden is within optimal range",
            confidence=0.9
        )
    
    def _analyze_trends(self) -> FinancialInsight:
        """Analyze revenue trends over time"""
        if len(self.revenue_memory) < 2:
            return None
            
        recent_revenues = [r.revenue for r in self.revenue_memory[-3:]]
        if len(recent_revenues) >= 2:
            growth_rate = ((recent_revenues[-1] - recent_revenues[0]) / recent_revenues[0]) * 100
            
            if growth_rate > 10:
                trend = "strong growth"
                recommendation = "Maintain current strategies and consider scaling operations"
            elif growth_rate > 0:
                trend = "moderate growth"
                recommendation = "Look for opportunities to accelerate growth"
            else:
                trend = "declining"
                recommendation = "Urgent: Review operations and market positioning"
            
            return FinancialInsight(
                insight_type="trend_analysis",
                title=f"Revenue Trend: {growth_rate:+.1f}%",
                description=f"Revenue shows {trend} with {growth_rate:+.1f}% change over recent periods",
                impact=f"Current trajectory suggests {trend} business performance",
                recommendation=recommendation,
                confidence=0.8
            )
    
    def _compare_with_competitors(self, revenue_data: RevenueData) -> FinancialInsight:
        """Compare performance against industry benchmarks"""
        benchmark = None
        for b in self.competitor_benchmarks:
            if b.business_type == revenue_data.business_type:
                benchmark = b
                break
        
        if not benchmark:
            return None
            
        revenue_vs_benchmark = ((revenue_data.revenue - benchmark.avg_monthly_revenue) / benchmark.avg_monthly_revenue) * 100
        
        if revenue_vs_benchmark > 20:
            performance = "significantly outperforming"
            recommendation = "Excellent performance! Consider expanding market share"
        elif revenue_vs_benchmark > 0:
            performance = "outperforming"
            recommendation = "Good performance, identify key success factors to amplify"
        elif revenue_vs_benchmark > -20:
            performance = "underperforming"
            recommendation = "Analyze competitor strategies and optimize operations"
        else:
            performance = "significantly underperforming"
            recommendation = "Critical: Immediate strategic review required"
        
        return FinancialInsight(
            insight_type="competitive_analysis",
            title=f"vs Competitors: {revenue_vs_benchmark:+.1f}%",
            description=f"Your revenue of ₹{revenue_data.revenue:,.2f} is {performance} compared to industry average of ₹{benchmark.avg_monthly_revenue:,.2f}",
            impact=f"Market position: {performance} by {abs(revenue_vs_benchmark):.1f}%",
            recommendation=recommendation,
            confidence=0.75
        )
    
    def get_latest_insights(self, limit: int = 5) -> List[FinancialInsight]:
        """Get most recent insights"""
        return sorted(self.insights_history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_profit_analysis(self) -> Dict:
        """Dedicated profit analysis"""
        if not self.revenue_memory:
            return {"status": "No data"}
            
        profits = [(r.revenue - r.expenses) for r in self.revenue_memory]
        avg_profit = sum(profits) / len(profits)
        profit_trend = ((profits[-1] - profits[0]) / profits[0] * 100) if len(profits) > 1 else 0
        
        # Compare with competitors
        latest = self.revenue_memory[-1]
        benchmark = next((b for b in self.competitor_benchmarks if b.business_type == latest.business_type), None)
        
        competitive_position = "Unknown"
        if benchmark:
            expected_profit = benchmark.avg_monthly_revenue * benchmark.avg_profit_margin
            vs_competitors = ((profits[-1] - expected_profit) / expected_profit * 100)
            competitive_position = f"{vs_competitors:+.1f}% vs industry average"
        
        return {
            "current_profit": profits[-1],
            "average_profit": avg_profit,
            "profit_trend": profit_trend,
            "competitive_position": competitive_position,
            "months_data": len(profits),
            "profit_margin": (profits[-1] / latest.revenue * 100) if latest.revenue > 0 else 0
        }
    
    def get_loss_analysis(self) -> Dict:
        """Dedicated loss analysis"""
        if not self.revenue_memory:
            return {"status": "No data"}
            
        losses = [max(0, r.expenses - r.revenue) for r in self.revenue_memory]
        loss_months = [i for i, loss in enumerate(losses) if loss > 0]
        
        return {
            "total_losses": sum(losses),
            "loss_months_count": len(loss_months),
            "biggest_loss": max(losses) if losses else 0,
            "loss_trend": "Improving" if len(losses) > 1 and losses[-1] < losses[0] else "Stable",
            "risk_level": "High" if len(loss_months) > len(self.revenue_memory) * 0.3 else "Low"
        }
    
    def get_tax_analysis(self) -> Dict:
        """Dedicated tax analysis with service/product breakdown"""
        if not self.revenue_memory:
            return {"status": "No data"}
            
        tax_data = []
        for revenue in self.revenue_memory:
            net_income = revenue.revenue - revenue.expenses
            
            # Find applicable tax rule
            tax_rule = None
            for rule in self.tax_rules:
                if (rule.business_type == revenue.business_type and 
                    rule.tax_type == revenue.tax_type and
                    rule.income_bracket_min <= net_income <= rule.income_bracket_max):
                    tax_rule = rule
                    break
            
            if tax_rule:
                if revenue.tax_type == "service_tax":
                    taxable = revenue.service_revenue or revenue.revenue
                else:
                    taxable = revenue.product_revenue or revenue.revenue
                    
                tax_amount = (taxable - revenue.expenses) * tax_rule.tax_rate
                tax_data.append({
                    "month": revenue.month,
                    "tax_amount": tax_amount,
                    "tax_rate": tax_rule.tax_rate * 100,
                    "tax_type": revenue.tax_type
                })
        
        total_tax = sum(t["tax_amount"] for t in tax_data)
        avg_tax_rate = sum(t["tax_rate"] for t in tax_data) / len(tax_data) if tax_data else 0
        
        # Compare with competitors
        latest = self.revenue_memory[-1]
        benchmark = next((b for b in self.competitor_benchmarks if b.business_type == latest.business_type), None)
        tax_efficiency = "Unknown"
        if benchmark and tax_data:
            competitor_tax_rate = benchmark.avg_tax_rate * 100
            current_rate = tax_data[-1]["tax_rate"]
            tax_efficiency = "Better" if current_rate < competitor_tax_rate else "Needs Improvement"
        
        return {
            "total_tax_paid": total_tax,
            "average_tax_rate": avg_tax_rate,
            "tax_efficiency": tax_efficiency,
            "monthly_breakdown": tax_data,
            "service_vs_product": {
                "service_months": len([t for t in tax_data if t["tax_type"] == "service_tax"]),
                "product_months": len([t for t in tax_data if t["tax_type"] == "product_tax"])
            }
        }
    def get_financial_summary(self) -> Dict:
        """Get comprehensive financial summary"""
        if not self.revenue_memory:
            return {"status": "No data available"}
        
        latest = self.revenue_memory[-1]
        total_revenue = sum(r.revenue for r in self.revenue_memory)
        total_expenses = sum(r.expenses for r in self.revenue_memory)
        
        return {
            "latest_month": latest.month,
            "latest_revenue": latest.revenue,
            "latest_expenses": latest.expenses,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": total_revenue - total_expenses,
            "months_tracked": len(self.revenue_memory),
            "recent_insights": len([i for i in self.insights_history if i.timestamp > datetime.now() - timedelta(days=30)])
        }