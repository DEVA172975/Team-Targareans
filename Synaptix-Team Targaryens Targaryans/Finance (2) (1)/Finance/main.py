from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from financial_agent import LiveFinancialAgent
from models import RevenueData, BusinessType, TaxType
from sample_datasets import load_sample_dataset
from auth import UserAuth, UserRegistration, UserLogin
from datetime import datetime
from typing import Optional

app = FastAPI(title="Live Financial Memory Agent", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Global instances
agent = LiveFinancialAgent()
auth = UserAuth()

def get_current_user(session_token: Optional[str] = Cookie(None)):
    """Get current user from session"""
    if not session_token:
        return None
    return auth.get_user_by_session(session_token)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_token: Optional[str] = Cookie(None)):
    """Home page - login or dashboard"""
    user = get_current_user(session_token)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/api/register")
async def register_user(user_data: UserRegistration):
    """Register new user"""
    result = auth.register_user(user_data)
    return result

@app.get("/verify/{token}")
async def verify_email(token: str):
    """Verify email with token"""
    result = auth.verify_email(token)
    if result["status"] == "success":
        return RedirectResponse(url="/?verified=true")
    return {"error": result["message"]}

@app.post("/api/login")
async def login_user(login_data: UserLogin):
    """Login user"""
    result = auth.login_user(login_data)
    return result

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session_token: Optional[str] = Cookie(None)):
    """Main dashboard - requires authentication"""
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/")
    
    summary = agent.get_financial_summary()
    insights = agent.get_latest_insights()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "summary": summary,
        "insights": insights
    })

@app.get("/user-dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, session_token: Optional[str] = Cookie(None)):
    """User's last data dashboard"""
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/")
    
    # Get user's latest data
    latest_data = None
    if agent.revenue_memory:
        latest_data = agent.revenue_memory[-1]
    
    return templates.TemplateResponse("user_dashboard.html", {
        "request": request,
        "user": user,
        "latest_data": latest_data
    })

@app.get("/revenue", response_class=HTMLResponse)
async def revenue_page(request: Request, session_token: Optional[str] = Cookie(None)):
    """Revenue data page"""
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("revenue.html", {"request": request, "user": user})

@app.get("/tax-rules", response_class=HTMLResponse)
async def tax_rules_page(request: Request, session_token: Optional[str] = Cookie(None)):
    """Tax rules page"""
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("tax_rules.html", {"request": request, "user": user})

@app.get("/competitors", response_class=HTMLResponse)
async def competitors_page(request: Request, session_token: Optional[str] = Cookie(None)):
    """Competitors page"""
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("competitors.html", {"request": request, "user": user})

@app.get("/profit-analysis", response_class=HTMLResponse)
async def profit_analysis(request: Request):
    """Dedicated profit analysis page"""
    analysis = agent.get_profit_analysis()
    return templates.TemplateResponse("profit_analysis.html", {
        "request": request,
        "analysis": analysis
    })

@app.get("/tax-analysis", response_class=HTMLResponse)
async def tax_analysis(request: Request):
    """Dedicated tax analysis page"""
    analysis = agent.get_tax_analysis()
    return templates.TemplateResponse("tax_analysis.html", {
        "request": request,
        "analysis": analysis
    })

@app.get("/loss-analysis", response_class=HTMLResponse)
async def loss_analysis(request: Request):
    """Dedicated loss analysis page"""
    analysis = agent.get_loss_analysis()
    return templates.TemplateResponse("loss_analysis.html", {
        "request": request,
        "analysis": analysis
    })

@app.get("/data-history", response_class=HTMLResponse)
async def data_history(request: Request):
    """Data history page showing all uploaded files"""
    files = agent.db.get_all_file_uploads()
    return templates.TemplateResponse("data_history.html", {
        "request": request,
        "files": files
    })

@app.get("/file-details/{filename}", response_class=HTMLResponse)
async def file_details(request: Request, filename: str):
    """Show details of a specific uploaded file"""
    records = agent.db.get_records_by_file(filename)
    return templates.TemplateResponse("file_details.html", {
        "request": request,
        "filename": filename,
        "records": records
    })

@app.post("/api/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload and process dataset files (JSON/CSV)"""
    try:
        content = await file.read()
        
        if file.filename.endswith('.json'):
            import json
            data = json.loads(content.decode('utf-8'))
        elif file.filename.endswith('.csv'):
            import csv
            import io
            csv_data = csv.DictReader(io.StringIO(content.decode('utf-8')))
            data = list(csv_data)
        else:
            raise HTTPException(status_code=400, detail="Only JSON and CSV files supported")
        
        # Process each record
        total_insights = 0
        for record in data:
            revenue_data = RevenueData(
                month=record['month'],
                revenue=float(record['revenue']),
                expenses=float(record['expenses']),
                business_type=BusinessType(record['business_type']),
                tax_type=TaxType(record['tax_type']),
                service_revenue=float(record.get('service_revenue', 0)),
                product_revenue=float(record.get('product_revenue', 0))
            )
            insights = agent.ingest_revenue_data(revenue_data, source_file=file.filename)
            total_insights += len(insights) if insights else 0
        
        # Save file upload record
        agent.db.save_file_upload(file.filename, file.filename.split('.')[-1], len(data), total_insights)
        
        return {
            "status": "success",
            "message": f"Loaded {len(data)} records from {file.filename}",
            "total_insights_generated": total_insights
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/revenue")
async def add_revenue_data(revenue_data: RevenueData):
    """Add new revenue data and trigger live analysis"""
    try:
        insights = agent.ingest_revenue_data(revenue_data)
        return {
            "status": "success",
            "message": f"Revenue data for {revenue_data.month} processed",
            "new_insights": len(insights) if insights else 0,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/chart-data")
async def get_chart_data():
    """Get chart data for revenue trends"""
    revenue_data = agent.revenue_memory
    if not revenue_data:
        return {"months": [], "revenue": [], "expenses": []}
    
    months = [data.month for data in revenue_data[-12:]]  # Last 12 months
    revenue = [data.revenue for data in revenue_data[-12:]]
    expenses = [data.expenses for data in revenue_data[-12:]]
    
    return {"months": months, "revenue": revenue, "expenses": expenses}

@app.get("/api/insights")
async def get_insights(limit: int = 10):
    """Get latest financial insights"""
    insights = agent.get_latest_insights(limit)
    return {"insights": insights}

@app.get("/api/summary")
async def get_summary():
    """Get financial summary"""
    return agent.get_financial_summary()

@app.post("/api/load-dataset/{dataset_type}")
async def load_dataset(dataset_type: str):
    """Load different types of sample datasets"""
    try:
        result = load_sample_dataset(agent, dataset_type)
        return {
            "status": "success",
            "message": f"Loaded {result['loaded_months']} months of {result['dataset_type']} data",
            "total_insights_generated": result['total_insights']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/demo-data")
async def load_demo_data():
    """Load sample data for demonstration"""
    demo_data = [
        RevenueData(month="2024-01", revenue=42000, expenses=28000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, product_revenue=42000),
        RevenueData(month="2024-02", revenue=45000, expenses=29000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=45000),
        RevenueData(month="2024-03", revenue=48000, expenses=30000, business_type=BusinessType.RETAIL, tax_type=TaxType.PRODUCT_TAX, product_revenue=48000),
        RevenueData(month="2024-04", revenue=52000, expenses=31000, business_type=BusinessType.SERVICES, tax_type=TaxType.SERVICE_TAX, service_revenue=52000),
    ]
    
    total_insights = 0
    for data in demo_data:
        insights = agent.ingest_revenue_data(data)
        total_insights += len(insights) if insights else 0
    
    return {
        "status": "success",
        "message": f"Loaded {len(demo_data)} months of demo data",
        "total_insights_generated": total_insights
    }

@app.get("/api/database-info")
async def get_database_info():
    """Get database information and record counts"""
    try:
        import os
        db_path = "financial_data.db"
        
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            revenue_count = len(agent.revenue_memory)
            insights_count = len(agent.insights_history)
            
            return {
                "database_exists": True,
                "database_path": os.path.abspath(db_path),
                "file_size_bytes": file_size,
                "revenue_records": revenue_count,
                "insights_records": insights_count
            }
        else:
            return {"database_exists": False, "message": "Database not created yet"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/clear-loss-data")
async def clear_loss_data():
    """Clear only loss-related data"""
    try:
        # Keep only profitable months in revenue memory
        agent.revenue_memory = [r for r in agent.revenue_memory if r.revenue >= r.expenses]
        return {"status": "success", "message": "Loss data cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/clear-profit-data")
async def clear_profit_data():
    """Clear only profit-related data"""
    try:
        # Clear only insights related to profit/competitive analysis
        agent.insights_history = [i for i in agent.insights_history if i.insight_type not in ['competitive_analysis', 'trend_analysis']]
        return {"status": "success", "message": "Profit data cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/clear-tax-data")
async def clear_tax_data():
    """Clear only tax-related data"""
    try:
        # Clear only insights related to tax
        agent.insights_history = [i for i in agent.insights_history if i.insight_type != 'tax_analysis']
        return {"status": "success", "message": "Tax data cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/clear-data")
async def clear_data():
    """Clear all data from database"""
    try:
        agent.db.clear_all_data()
        agent.revenue_memory = []
        agent.insights_history = []
        return {"status": "success", "message": "All data cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Clear all existing data on startup
agent.db.clear_all_data()
agent.revenue_memory = []
agent.insights_history = []

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)