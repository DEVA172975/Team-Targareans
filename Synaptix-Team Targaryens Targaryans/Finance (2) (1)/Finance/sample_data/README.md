# Sample Financial Datasets

## 📁 Available Dataset Files

### JSON Files:
- **comprehensive_data.json** - 8 months of mixed business types (retail, services, technology)
- **growth_story.json** - 5 months showing strong growth from $25K to $72K revenue
- **struggling_business.json** - 5 months with loss periods and recovery

### CSV Files:
- **manufacturing_business.csv** - 5 months of manufacturing business data

## 🚀 How to Use

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Upload dataset**:
   - Go to http://localhost:8000
   - Click "Choose File" under "Upload Dataset File"
   - Select any file from this `sample_data` folder
   - Click "Load Dataset File"

3. **View analysis**:
   - Visit `/profit-analysis` for profit insights
   - Visit `/loss-analysis` for risk assessment
   - Visit `/tax-analysis` for tax optimization

## 💡 Dataset Scenarios

### Comprehensive Data
- **Best for**: Overall system demo
- **Shows**: Mixed business types, service vs product tax, growth trends
- **Insights**: Competitive analysis, tax optimization, profit trends

### Growth Story
- **Best for**: Success story demo
- **Shows**: 188% revenue growth over 5 months
- **Insights**: Strong growth recommendations, scaling opportunities

### Struggling Business
- **Best for**: Risk analysis demo
- **Shows**: Loss months, recovery patterns
- **Insights**: Loss prevention, risk mitigation strategies

### Manufacturing Business
- **Best for**: Product-focused business demo
- **Shows**: Steady manufacturing growth, product tax scenarios
- **Insights**: Manufacturing-specific tax benefits, industrial benchmarks

## 📊 File Formats Supported

**JSON Format:**
```json
[
  {
    "month": "2024-01",
    "revenue": 45000,
    "expenses": 32000,
    "business_type": "services",
    "tax_type": "service_tax",
    "service_revenue": 45000,
    "product_revenue": 0
  }
]
```

**CSV Format:**
```csv
month,revenue,expenses,business_type,tax_type,service_revenue,product_revenue
2024-01,45000,32000,services,service_tax,45000,0
```

Choose any file to see the Live Financial Memory Agent in action!