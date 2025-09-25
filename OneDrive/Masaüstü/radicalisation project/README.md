# Digital Radicalization Research Project

A comprehensive web scraping and text analysis system for monitoring digital radicalization patterns across social media and web platforms.

## 🎯 Project Overview

This project implements a data pipeline for detecting and analyzing radicalization content across digital platforms:

1. **Data Collection** - Web scraping from social media and news sites
2. **Keyword Classification** - Text categorization using predefined keyword sets
3. **Aggregation** - Weekly grouping by region/language/country
4. **Analysis** - Statistical analysis and visualization

## 📁 Project Structure

```
radicalisation project/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── keywords.json          # Keyword categories and terms
├── README.md              # This file
├── src/                   # Source code modules
│   ├── config.py          # Configuration management
│   ├── scraper.py         # Web scraping functionality
│   ├── classifier.py      # Text classification
│   ├── aggregator.py      # Data aggregation
│   └── utils.py           # Utility functions
├── config/                # Configuration files
├── data/                  # Raw and processed data
├── output/                # Generated reports
└── logs/                  # Application logs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Demo

To test the system with demo data:

```bash
python main.py --demo
```

### 3. Run Full Analysis

For a complete analysis (requires API keys for social media platforms):

```bash
python main.py --platform twitter --region TR --weeks 4
```

## 📊 Features

### Data Collection
- **Multi-platform support**: Twitter, Reddit, forums, news sites
- **Geographic filtering**: Region/country-based collection
- **Time-based collection**: Configurable date ranges
- **Rate limiting**: Respects platform API limits

### Text Classification
- **Multi-language support**: Turkish, English, Greek
- **8 Category classification**:
  - Violence/Call to Action
  - Group Identity
  - Delegitimization/Dehumanization
  - Conspiracy/Polarizing
  - Propaganda/Recruitment
  - Religious Radical
  - PKK-Related
  - Conversion/Identity
- **Language detection**: Automatic language identification
- **Sentiment analysis**: Optional sentiment scoring

### Data Aggregation
- **Temporal aggregation**: Weekly grouping
- **Geographic aggregation**: By NUTS-2 regions or countries
- **Language-based aggregation**: When regional data unavailable
- **Statistical summaries**: Comprehensive reporting

## 🔧 Configuration

The system uses YAML configuration files for customization:

### Keywords Configuration
Keywords are defined in `keywords.json` with the structure:
```json
{
  "Category_Name": {
    "EN": ["keyword1", "keyword2"],
    "TR": ["anahtar1", "anahtar2"]
  }
}
```

### System Configuration
Main configuration in `config/config.yaml`:
```yaml
scraping:
  delay_between_requests: 2
  max_retries: 3
  timeout: 30

classification:
  case_sensitive: false
  language_detection_threshold: 0.8

platforms:
  twitter:
    enabled: true
    rate_limit: 100
```

## 📈 Output Format

Results are provided in the format:
```json
{
  "region": "TR",
  "week": "2024-W01",
  "platform": "twitter",
  "category": "Violence_CallToAction",
  "count": 15
}
```

## 🛠️ Development

### Adding New Platforms
1. Extend the `WebScraper` class in `src/scraper.py`
2. Add platform configuration in config file
3. Update keyword matching if needed

### Adding New Categories
1. Update `keywords.json` with new category
2. Add category weights in `classifier.py`
3. Update visualization colors in `utils.py`

### Extending Language Support
1. Add language mappings in `classifier.py`
2. Include new language keywords in `keywords.json`
3. Update character detection methods

## 📋 Requirements

- Python 3.8+
- Internet connection for web scraping
- API keys for social media platforms (for production use)

## ⚠️ Important Notes

### Ethical Considerations
- This tool is for research purposes only
- Respect platform terms of service
- Ensure compliance with data protection regulations
- Consider ethical implications of data collection

### Legal Compliance
- Obtain necessary permissions for data collection
- Follow local data protection laws
- Respect user privacy and content rights
- Use collected data responsibly

### Technical Limitations
- Demo mode uses simulated data
- Real implementation requires API access
- Rate limiting may affect collection speed
- Geographic detection may be limited

## 📞 Support

For questions, issues, or contributions:
1. Check the logs in the `logs/` directory
2. Review configuration settings
3. Ensure all dependencies are installed
4. Verify API credentials (if applicable)

## 🔄 Future Enhancements

- Real-time data streaming
- Machine learning classification
- Advanced sentiment analysis
- Interactive dashboard
- Automated reporting
- Multi-modal content analysis

---

**Disclaimer**: This tool is designed for academic research and monitoring purposes. Users are responsible for ensuring ethical and legal compliance in their use of this system.