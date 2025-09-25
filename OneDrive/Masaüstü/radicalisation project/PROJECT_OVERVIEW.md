# Digital Radicalization Research Project Overview

## 🎯 Project Summary

This is a comprehensive web scraping and text analysis system for monitoring digital radicalization patterns across social media and web platforms. The system implements a complete data pipeline from collection to analysis and reporting.

## 📊 What This System Does

### 1. **Data Collection (Web Scraping)**
- Collects text content from social media platforms (Twitter, Reddit)
- Scrapes forums and news websites
- Supports multiple platforms simultaneously
- Handles rate limiting and ethical scraping practices

### 2. **Keyword Classification**
- Uses your provided keyword categories in JSON format
- Supports multiple languages (Turkish, English, Greek, etc.)
- Classifies text into 8 main categories:
  - Violence/Call to Action
  - Group Identity
  - Delegitimization/Dehumanization
  - Conspiracy/Polarizing
  - Propaganda/Recruitment
  - Religious Radical
  - PKK-Related
  - Conversion/Identity

### 3. **Data Aggregation**
- Groups results by week, region, platform, and category
- Supports three aggregation levels:
  - **Primary**: By NUTS-2 regions/provinces
  - **Secondary**: By language when region data unavailable
  - **Tertiary**: By country as fallback
- Generates output in format: `{region/language/country, week, platform, category, count}`

## 🚀 Quick Start

### Option 1: Use Batch Files (Windows)
1. Double-click `install.bat` to set up the system
2. Double-click `run_demo.bat` to run the full demo
3. Double-click `run_stats.bat` to see keyword statistics

### Option 2: Use Command Line
```bash
# Install and setup
python setup.py

# Run full demo
python demo.py --full

# Show keyword statistics
python demo.py --stats

# Test classifier only
python demo.py --classifier

# Run main system demo
python main.py --demo
```

## 📁 Key Files

- `keywords.json` - Your keyword definitions (already present)
- `main.py` - Main application entry point
- `demo.py` - Demo script with test data
- `setup.py` - Installation and setup script
- `README.md` - Detailed documentation

## 📈 Output Examples

The system generates results like:
```json
{
  "region": "TR",
  "week": "2025-W38", 
  "platform": "twitter",
  "category": "Violence_CallToAction",
  "count": 15
}
```

## 🎨 Generated Reports

The system creates:
- **JSON files** with raw aggregated data
- **CSV files** for spreadsheet analysis  
- **HTML reports** with visualizations and charts
- **Console summaries** with key statistics

## ⚡ Demo Results

When you run the demo, you'll see:
- Text classification in real-time
- Weekly aggregation by region and platform
- Summary statistics and top categories
- Generated HTML report for browser viewing

## 🔧 Technical Features

- **Fault Tolerant**: Works even without optional dependencies
- **Multi-language**: Automatic language detection
- **Configurable**: YAML configuration files
- **Logging**: Comprehensive logging system
- **Scalable**: Modular design for easy extension

## 📋 Demo Data Categories Found

Based on your keywords, the demo typically finds:
- Violence/Call to Action content
- Group Identity discussions
- PKK-Related material
- Propaganda/Recruitment text
- Religious Radical content
- Conspiracy theories

## 🌐 Next Steps for Production

For real-world deployment:
1. Obtain API keys for social media platforms
2. Configure target websites and platforms
3. Set up automated scheduling
4. Implement data storage solutions
5. Add real-time monitoring capabilities

## ⚠️ Important Notes

- **Research Purpose**: This tool is designed for academic research
- **Ethical Use**: Respect platform terms of service
- **Demo Mode**: Current setup uses simulated data for feasibility testing
- **Legal Compliance**: Ensure compliance with local data protection laws

---

**Ready to start?** Run `python demo.py --full` to see the system in action!