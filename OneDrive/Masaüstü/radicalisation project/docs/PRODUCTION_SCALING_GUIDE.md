# Infrastructure Scaling Guide for Production

## 🏗️ Infrastructure Scaling Options

### **Option 1: Local/Small Scale Deployment**
**Good for**: Initial research, small datasets (<10K texts/day)

```bash
# System Requirements
- CPU: 4+ cores
- RAM: 8GB+ 
- Storage: 100GB+ SSD
- Network: Stable internet connection

# Setup
pip install -r requirements-production.txt
python src/scheduler.py --daemon
```

### **Option 2: Cloud Deployment (Recommended)**
**Good for**: Medium to large scale research (10K-1M texts/day)

#### **AWS Deployment**
```yaml
# docker-compose.yml
version: '3.8'
services:
  radicalization-app:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/radicalization
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: radicalization
      POSTGRES_USER: researcher
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    
  scheduler:
    build: .
    command: python src/scheduler.py --daemon
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

#### **Google Cloud Platform**
```bash
# Deploy to Cloud Run
gcloud run deploy radicalization-research \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

### **Option 3: High-Performance Cluster**
**Good for**: Large scale research (1M+ texts/day)

#### **Kubernetes Deployment**
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: radicalization-research
spec:
  replicas: 5
  selector:
    matchLabels:
      app: radicalization-research
  template:
    metadata:
      labels:
        app: radicalization-research
    spec:
      containers:
      - name: app
        image: radicalization-research:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi" 
            cpu: "2000m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## 💾 Database Scaling

### **SQLite → PostgreSQL Migration**

```python
# src/database.py
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CollectedText(Base):
    __tablename__ = 'collected_texts'
    
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Text, nullable=False)
    platform = sa.Column(sa.String(50), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    location = sa.Column(sa.String(100))
    region = sa.Column(sa.String(10))
    url = sa.Column(sa.Text)
    metadata = sa.Column(sa.JSON)
    
    # Indexing for performance
    __table_args__ = (
        sa.Index('ix_timestamp', 'timestamp'),
        sa.Index('ix_platform', 'platform'),
        sa.Index('ix_region', 'region'),
    )

class ClassifiedText(Base):
    __tablename__ = 'classified_texts'
    
    id = sa.Column(sa.Integer, primary_key=True)
    text_id = sa.Column(sa.Integer, sa.ForeignKey('collected_texts.id'))
    category = sa.Column(sa.String(100), nullable=False)
    matched_keywords = sa.Column(sa.JSON)
    confidence_score = sa.Column(sa.Float)
    language = sa.Column(sa.String(10))
    
class AggregatedResults(Base):
    __tablename__ = 'aggregated_results'
    
    id = sa.Column(sa.Integer, primary_key=True)
    week = sa.Column(sa.String(20), nullable=False)
    region = sa.Column(sa.String(10), nullable=False)
    platform = sa.Column(sa.String(50), nullable=False)
    category = sa.Column(sa.String(100), nullable=False)
    count = sa.Column(sa.Integer, nullable=False)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        sa.UniqueConstraint('week', 'region', 'platform', 'category'),
    )
```

### **Database Performance Optimization**

```sql
-- PostgreSQL optimization queries
CREATE INDEX CONCURRENTLY idx_texts_timestamp_region ON collected_texts(timestamp, region);
CREATE INDEX CONCURRENTLY idx_texts_platform_category ON classified_texts(platform, category);

-- Partitioning for large datasets
CREATE TABLE collected_texts_2025 PARTITION OF collected_texts 
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Automated cleanup (keep last 6 months)
DELETE FROM collected_texts WHERE timestamp < NOW() - INTERVAL '6 months';
```

## ⚡ Performance Optimization

### **1. Parallel Processing**

```python
# src/parallel_processor.py
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio

class ParallelClassifier:
    def __init__(self, classifier, max_workers=None):
        self.classifier = classifier
        self.max_workers = max_workers or mp.cpu_count()
    
    def classify_batch_parallel(self, texts: List[str]) -> List[Dict]:
        """Process texts in parallel"""
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Split texts into chunks
            chunk_size = len(texts) // self.max_workers
            chunks = [texts[i:i+chunk_size] for i in range(0, len(texts), chunk_size)]
            
            # Process chunks in parallel
            futures = [executor.submit(self._process_chunk, chunk) for chunk in chunks]
            
            results = []
            for future in futures:
                results.extend(future.result())
            
            return results
    
    def _process_chunk(self, texts: List[str]) -> List[Dict]:
        """Process a chunk of texts"""
        return [self.classifier.classify_text(text) for text in texts]

# Async data collection
class AsyncScraper:
    async def collect_multiple_platforms(self, platforms: List[str]):
        """Collect from multiple platforms simultaneously"""
        tasks = []
        for platform in platforms:
            if platform == 'twitter':
                tasks.append(self.collect_twitter_async())
            elif platform == 'reddit':
                tasks.append(self.collect_reddit_async())
            # ... add more platforms
        
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]
```

### **2. Caching and Rate Limiting**

```python
# src/cache_manager.py
import redis
from functools import wraps
import pickle
import hashlib

class CacheManager:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    def cached_classification(self, expire_time=3600):
        """Cache classification results"""
        def decorator(func):
            @wraps(func)
            def wrapper(text):
                # Create cache key from text hash
                cache_key = f"classification:{hashlib.md5(text.encode()).hexdigest()}"
                
                # Try to get from cache
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    return pickle.loads(cached_result)
                
                # Compute and cache result
                result = func(text)
                self.redis_client.setex(cache_key, expire_time, pickle.dumps(result))
                return result
            
            return wrapper
        return decorator

# Rate limiting
from time import sleep
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=100, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        now = datetime.now()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]).seconds
            if sleep_time > 0:
                sleep(sleep_time)
        
        self.requests.append(now)
```

### **3. Monitoring and Alerting**

```python
# src/monitoring.py
import psutil
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

class SystemMonitor:
    def __init__(self, alert_email=None):
        self.alert_email = alert_email
        self.logger = logging.getLogger(__name__)
    
    def check_system_health(self):
        """Check system health metrics"""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check thresholds
        if metrics['cpu_percent'] > 80:
            self.send_alert(f"High CPU usage: {metrics['cpu_percent']}%")
        
        if metrics['memory_percent'] > 85:
            self.send_alert(f"High memory usage: {metrics['memory_percent']}%")
        
        if metrics['disk_percent'] > 90:
            self.send_alert(f"High disk usage: {metrics['disk_percent']}%")
        
        return metrics
    
    def send_alert(self, message):
        """Send alert email"""
        if not self.alert_email:
            self.logger.warning(f"ALERT: {message}")
            return
        
        try:
            msg = MIMEText(f"Alert from Radicalization Research System:\n\n{message}")
            msg['Subject'] = 'System Alert'
            msg['From'] = 'system@research.local'
            msg['To'] = self.alert_email
            
            # Configure SMTP server
            # smtp_server.sendmail(msg['From'], [msg['To']], msg.as_string())
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
```

## 🔒 Security and Compliance

### **Data Protection**
```python
# src/security.py
from cryptography.fernet import Fernet
import hashlib

class DataProtection:
    def __init__(self, encryption_key=None):
        self.key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt sensitive text data"""
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text data"""
        return self.cipher.decrypt(encrypted_text.encode()).decode()
    
    def anonymize_user_id(self, user_id: str) -> str:
        """Create anonymous hash of user ID"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
```

### **GDPR Compliance**
```python
# Data retention policies
def cleanup_old_data(days=180):
    """Remove data older than specified days for GDPR compliance"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Remove old raw data
    for file_path in Path("data/raw").glob("*.json"):
        if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
            file_path.unlink()
    
    # Remove from database
    # db.execute("DELETE FROM collected_texts WHERE timestamp < %s", (cutoff_date,))
```

## 📊 Production Deployment Checklist

### **Pre-Production**
- [ ] API keys configured and tested
- [ ] Database schema created and migrated
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] Security measures in place
- [ ] Rate limiting configured
- [ ] Error handling and logging improved

### **Production Launch**
- [ ] Start with limited collection (1-2 platforms)
- [ ] Monitor system performance closely
- [ ] Gradually increase collection volume
- [ ] Set up automated reports
- [ ] Test failover and recovery procedures

### **Post-Production**
- [ ] Regular performance reviews
- [ ] Cost optimization
- [ ] Scale based on research needs
- [ ] Update keywords and categories as needed
- [ ] Maintain compliance with platform policies

## 💰 Cost Estimation

### **Monthly Costs (USD)**

**Small Scale (10K texts/day)**
- Server: $50-100
- Database: $25-50  
- APIs: $20-100
- Storage: $10-25
- **Total: $105-275/month**

**Medium Scale (100K texts/day)**
- Server: $200-500
- Database: $100-300
- APIs: $100-500
- Storage: $50-150
- **Total: $450-1,450/month**

**Large Scale (1M+ texts/day)**
- Server cluster: $1,000-3,000
- Database: $500-1,500
- APIs: $500-2,000
- Storage: $200-800
- **Total: $2,200-7,300/month**