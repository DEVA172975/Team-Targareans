import sqlite3
import json
from datetime import datetime
from models import RevenueData, FinancialInsight, BusinessType, TaxType

class FinancialDB:
    def __init__(self, db_path="financial_data.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Revenue data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                revenue REAL NOT NULL,
                expenses REAL NOT NULL,
                business_type TEXT NOT NULL,
                tax_type TEXT NOT NULL,
                service_revenue REAL DEFAULT 0,
                product_revenue REAL DEFAULT 0,
                source_file TEXT DEFAULT 'manual',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add source_file column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE revenue_data ADD COLUMN source_file TEXT DEFAULT "manual"')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                impact TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                records_count INTEGER NOT NULL,
                insights_generated INTEGER NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_revenue_data(self, revenue_data: RevenueData, source_file="manual"):
        """Save revenue data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO revenue_data 
            (month, revenue, expenses, business_type, tax_type, service_revenue, product_revenue, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            revenue_data.month,
            revenue_data.revenue,
            revenue_data.expenses,
            revenue_data.business_type.value,
            revenue_data.tax_type.value,
            revenue_data.service_revenue,
            revenue_data.product_revenue,
            source_file
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_revenue_data(self):
        """Get all revenue data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM revenue_data ORDER BY month')
        rows = cursor.fetchall()
        conn.close()
        
        revenue_list = []
        for row in rows:
            revenue_data = RevenueData(
                month=row[1],
                revenue=row[2],
                expenses=row[3],
                business_type=BusinessType(row[4]),
                tax_type=TaxType(row[5]),
                service_revenue=row[6],
                product_revenue=row[7]
            )
            revenue_list.append(revenue_data)
        
        return revenue_list
    
    def save_insight(self, insight: FinancialInsight):
        """Save insight to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO insights 
            (insight_type, title, description, impact, recommendation, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            insight.insight_type,
            insight.title,
            insight.description,
            insight.impact,
            insight.recommendation,
            insight.confidence
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_insights(self, limit=10):
        """Get recent insights from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM insights ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insight = FinancialInsight(
                insight_type=row[1],
                title=row[2],
                description=row[3],
                impact=row[4],
                recommendation=row[5],
                confidence=row[6]
            )
            insights.append(insight)
        
        return insights
    
    def clear_all_data(self):
        """Clear all data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM revenue_data')
        cursor.execute('DELETE FROM insights')
        
        conn.commit()
        conn.close()
    
    def save_file_upload(self, filename, file_type, records_count, insights_generated):
        """Save file upload record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_uploads 
            (filename, file_type, records_count, insights_generated)
            VALUES (?, ?, ?, ?)
        ''', (filename, file_type, records_count, insights_generated))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_all_file_uploads(self):
        """Get all uploaded files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM file_uploads ORDER BY upload_date DESC')
        rows = cursor.fetchall()
        conn.close()
        
        files = []
        for row in rows:
            files.append({
                'id': row[0],
                'filename': row[1],
                'file_type': row[2],
                'records_count': row[3],
                'insights_generated': row[4],
                'upload_date': row[5]
            })
        return files
    
    def get_records_by_file(self, filename):
        """Get all revenue records from a specific file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM revenue_data WHERE source_file = ? ORDER BY month', (filename,))
        rows = cursor.fetchall()
        conn.close()
        
        records = []
        for row in rows:
            records.append({
                'id': row[0],
                'month': row[1],
                'revenue': row[2],
                'expenses': row[3],
                'business_type': row[4],
                'tax_type': row[5],
                'service_revenue': row[6],
                'product_revenue': row[7],
                'source_file': row[8],
                'created_at': row[9]
            })
        return records