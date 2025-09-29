#!/bin/bash
# Production Deployment Script

set -e

echo "🚀 Starting Radicalization Research System Deployment..."


# Configuration
PROJECT_NAME="radicalization-research"
DEPLOY_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="research"
PYTHON_VERSION="3.12"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

# System updates
log_info "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install system dependencies
log_info "Installing system dependencies..."
apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev \
    postgresql-client \
    redis-tools \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev

# Create service user
log_info "Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -m -s /bin/bash $SERVICE_USER
    log_info "Created user: $SERVICE_USER"
else
    log_warn "User $SERVICE_USER already exists"
fi

# Create deployment directory
log_info "Setting up deployment directory..."
mkdir -p $DEPLOY_DIR
chown $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR

# Copy application files
log_info "Copying application files..."
cp -r . $DEPLOY_DIR/
chown -R $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR

# Create Python virtual environment
log_info "Creating Python virtual environment..."
sudo -u $SERVICE_USER python${PYTHON_VERSION} -m venv $DEPLOY_DIR/venv

# Install Python dependencies
log_info "Installing Python dependencies..."
sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/pip install --upgrade pip
sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/pip install -r $DEPLOY_DIR/requirements-production.txt

# Create necessary directories
log_info "Creating application directories..."
sudo -u $SERVICE_USER mkdir -p $DEPLOY_DIR/{data/raw,data/processed,output,logs,config}

# Set up configuration
log_info "Setting up configuration..."
if [ ! -f "$DEPLOY_DIR/config/api_keys.env" ]; then
    sudo -u $SERVICE_USER cp $DEPLOY_DIR/config/api_keys.env.template $DEPLOY_DIR/config/api_keys.env
    log_warn "Please edit $DEPLOY_DIR/config/api_keys.env with your API keys"
fi

# Install systemd service
log_info "Installing systemd service..."
cp $DEPLOY_DIR/systemd/radicalization-research.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable radicalization-research.service

# Set up log rotation
log_info "Setting up log rotation..."
cat > /etc/logrotate.d/radicalization-research << EOF
$DEPLOY_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $SERVICE_USER $SERVICE_USER
}
EOF

# Set up nginx (optional - for API endpoint)
log_info "Configuring nginx..."
cat > /etc/nginx/sites-available/radicalization-research << EOF
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8080/health;
    }
}
EOF

ln -sf /etc/nginx/sites-available/radicalization-research /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Set up monitoring with supervisor (alternative to systemd)
log_info "Setting up supervisor configuration..."
cat > /etc/supervisor/conf.d/radicalization-research.conf << EOF
[program:radicalization-research]
command=$DEPLOY_DIR/venv/bin/python src/scheduler.py --daemon
directory=$DEPLOY_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
startsecs=10
startretries=3
redirect_stderr=true
stdout_logfile=$DEPLOY_DIR/logs/supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
EOF

supervisorctl reread
supervisorctl update

# Database setup (if using PostgreSQL)
log_info "Database setup instructions:"
log_warn "Please run the following commands to set up PostgreSQL:"
echo "sudo -u postgres createuser -P $SERVICE_USER"
echo "sudo -u postgres createdb -O $SERVICE_USER radicalization_research"
echo "sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/alembic upgrade head"

# Final checks
log_info "Running final checks..."

# Check if virtual environment is working
if sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/python --version; then
    log_info "✅ Python virtual environment is working"
else
    log_error "❌ Python virtual environment setup failed"
    exit 1
fi

# Check if dependencies are installed
if sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/python -c "import requests, yaml"; then
    log_info "✅ Core dependencies are installed"
else
    log_error "❌ Dependencies installation failed"
    exit 1
fi

# Security hardening
log_info "Applying security hardening..."
chmod 600 $DEPLOY_DIR/config/api_keys.env
chmod -R 755 $DEPLOY_DIR
chmod -R 644 $DEPLOY_DIR/src/*.py
chmod +x $DEPLOY_DIR/src/scheduler.py

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit API keys: sudo nano $DEPLOY_DIR/config/api_keys.env"
echo "2. Set up database: Follow the database setup instructions above"
echo "3. Start the service: sudo systemctl start radicalization-research"
echo "4. Check service status: sudo systemctl status radicalization-research"
echo "5. View logs: sudo journalctl -u radicalization-research -f"
echo ""
echo "Configuration files:"
echo "- Main config: $DEPLOY_DIR/config/config.yaml"
echo "- API keys: $DEPLOY_DIR/config/api_keys.env"
echo "- Service file: /etc/systemd/system/radicalization-research.service"
echo ""
echo "Useful commands:"
echo "- Restart service: sudo systemctl restart radicalization-research"
echo "- Stop service: sudo systemctl stop radicalization-research"
echo "- Check logs: sudo tail -f $DEPLOY_DIR/logs/*.log"
echo "- Test collection: sudo -u $SERVICE_USER $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/main.py --demo"

import json
from datetime import datetime
from src.scraper import WebScraper
from src.classifier import KeywordClassifier
from src.aggregator import EnhancedAggregator

def main():
    # Load keywords (only Turkish/English, only Turkey-relevant categories)
    classifier = KeywordClassifier("keywords.json")
    aggregator = EnhancedAggregator()

    # Collect data (web scraping, Turkey only)
    scraper = WebScraper()
    demo_data = scraper.collect_data(region="Turkey")

    # Classify texts
    classified = []
    for item in demo_data:
        matches = classifier.classify_text(item["text"], target_language=item.get("language", "TR"))
        for category, keywords in matches.items():
            classified.append({
                "text": item["text"],
                "platform": item["platform"],
                "timestamp": item["timestamp"],
                "location": item["location"],
                "category": category,
                "matched_keywords": keywords,
                "language": classifier.detect_language(item["text"])
            })

    # Aggregate results
    aggregated = aggregator.aggregate_hierarchical(classified)

    # Export results (JSON format)
    with open("output/aggregated_results.json", "w", encoding="utf-8") as f:
        json.dump(aggregated, f, ensure_ascii=False, indent=2)

    print("✅ Aggregation complete. See output/aggregated_results.json")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WebScraper:
    def collect_data(self, region="Turkey"):
        # Example: scrape headlines from hurriyet.com.tr
        url = "https://www.hurriyet.com.tr/"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        headlines = [h.get_text() for h in soup.select("h3")][:10]
        data = []
        for headline in headlines:
            data.append({
                "text": headline,
                "platform": "news",
                "timestamp": datetime.now().isoformat(),
                "location": "Turkey",
                "language": "TR"
            })
        return data

{
  "PKK_Related": {
    "TR": ["PKK", "hendek savaşı", "direniş"],
    "EN": ["PKK", "ditch war", "resistance"]
  },
  "Religious_Radical": {
    "TR": ["hilafet", "şeriat", "cihad"],
    "EN": ["caliphate", "sharia", "jihad"]
  }
}

from collections import Counter, defaultdict
from datetime import datetime

class EnhancedAggregator:
    def aggregate_hierarchical(self, classified_data):
        results = defaultdict(list)
        counter = Counter()
        for item in classified_data:
            week = datetime.fromisoformat(item["timestamp"]).isocalendar()[1]
            key = (item["location"], f"{datetime.now().year}-W{week:02d}", item["platform"], item["category"])
            counter[key] += 1
        for (region, week, platform, category), count in counter.items():
            results["by_region"].append({
                "region": region,
                "week": week,
                "platform": platform,
                "category": category,
                "count": count
            })
        return results