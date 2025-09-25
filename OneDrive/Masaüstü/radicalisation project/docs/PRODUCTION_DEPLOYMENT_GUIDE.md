# Production Deployment Guide

## 🚀 **Complete Production Deployment Instructions**

### **Quick Start (Recommended)**

**For Ubuntu/Debian servers:**
```bash
# 1. Upload your project to the server
scp -r radicalization-project/ user@your-server:/tmp/

# 2. Run the automated deployment script
cd /tmp/radicalization-project
chmod +x deploy.sh
sudo ./deploy.sh
```

**The deployment script automatically:**
- ✅ Installs all system dependencies
- ✅ Creates dedicated service user
- ✅ Sets up Python virtual environment
- ✅ Installs all Python packages
- ✅ Configures systemd service
- ✅ Sets up log rotation
- ✅ Configures nginx reverse proxy
- ✅ Applies security hardening

### **Manual Deployment Steps**

#### **Step 1: Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.12 python3.12-venv python3-dev \
    postgresql-client redis-tools nginx git curl build-essential

# Create service user
sudo useradd -r -m -s /bin/bash research
```

#### **Step 2: Application Setup**
```bash
# Create deployment directory
sudo mkdir -p /opt/radicalization-research
sudo chown research:research /opt/radicalization-research

# Copy application (as research user)
sudo -u research cp -r . /opt/radicalization-research/
cd /opt/radicalization-research

# Create virtual environment
sudo -u research python3.12 -m venv venv
sudo -u research venv/bin/pip install -r requirements-production.txt
```

#### **Step 3: Configuration**
```bash
# Set up API keys
sudo -u research cp config/api_keys.env.template config/api_keys.env
sudo -u research nano config/api_keys.env  # Add your API keys

# Set up configuration
sudo -u research nano config/config.yaml   # Adjust settings if needed
```

#### **Step 4: Database Setup (PostgreSQL)**
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql << EOF
CREATE USER research WITH PASSWORD 'secure_password_here';
CREATE DATABASE radicalization_research OWNER research;
GRANT ALL PRIVILEGES ON DATABASE radicalization_research TO research;
\q
EOF

# Update database URL in config
DATABASE_URL="postgresql://research:secure_password_here@localhost/radicalization_research"
```

#### **Step 5: Service Installation**
```bash
# Install systemd service
sudo cp systemd/radicalization-research.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable radicalization-research

# Start the service
sudo systemctl start radicalization-research

# Check status
sudo systemctl status radicalization-research
```

### **Docker Deployment (Alternative)**

```bash
# Build Docker image
docker build -t radicalization-research .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### **Cloud Deployment Options**

#### **AWS EC2**
```bash
# Launch EC2 instance (t3.medium recommended)
# - Ubuntu 22.04 LTS
# - 4GB RAM, 2 vCPU
# - 20GB SSD storage
# - Security group: Allow SSH (22), HTTP (80), HTTPS (443)

# Connect and deploy
ssh -i your-key.pem ubuntu@ec2-instance-ip
# Follow manual deployment steps above
```

#### **Google Cloud Platform**
```bash
# Create VM instance
gcloud compute instances create radicalization-research \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --boot-disk-size=20GB

# Connect and deploy
gcloud compute ssh radicalization-research
# Follow manual deployment steps above
```

### **Production Monitoring**

#### **System Health Monitoring**
```bash
# Check service status
sudo systemctl status radicalization-research

# View real-time logs
sudo journalctl -u radicalization-research -f

# Check system resources
htop
df -h
free -h
```

#### **Application Logs**
```bash
# View application logs
sudo tail -f /opt/radicalization-research/logs/scheduler.log
sudo tail -f /opt/radicalization-research/logs/error.log

# Check collection statistics
sudo -u research /opt/radicalization-research/venv/bin/python \
    /opt/radicalization-research/main.py --status
```

### **Security Checklist**

- [ ] **API Keys**: Stored securely in environment file (600 permissions)
- [ ] **Service User**: Running as non-root user with minimal privileges
- [ ] **File Permissions**: Proper file ownership and permissions set
- [ ] **Firewall**: Only necessary ports open (22, 80, 443)
- [ ] **SSL/TLS**: HTTPS enabled for web interfaces
- [ ] **Updates**: Automatic security updates enabled
- [ ] **Monitoring**: System monitoring and alerting configured
- [ ] **Backups**: Regular backups of data and configuration

### **Maintenance Operations**

#### **Regular Tasks**
```bash
# Weekly: Check disk space and clean old logs
df -h
sudo find /opt/radicalization-research/logs -name "*.log" -mtime +30 -delete

# Monthly: Update system packages
sudo apt update && sudo apt upgrade -y
sudo systemctl restart radicalization-research

# Quarterly: Update Python dependencies
sudo -u research /opt/radicalization-research/venv/bin/pip list --outdated
sudo -u research /opt/radicalization-research/venv/bin/pip install --upgrade package_name
```

#### **Troubleshooting**
```bash
# Service won't start
sudo systemctl status radicalization-research
sudo journalctl -u radicalization-research --since "1 hour ago"

# High memory usage
free -h
ps aux --sort=-%mem | head -10

# Database connection issues
sudo -u research psql -d radicalization_research -c "SELECT version();"

# API rate limiting issues
grep "rate limit" /opt/radicalization-research/logs/*.log
```

### **Scaling for Production**

#### **Performance Optimization**
1. **Enable Redis caching** for classification results
2. **Use database connection pooling** for better performance
3. **Implement parallel processing** for large datasets
4. **Set up load balancing** for multiple instances

#### **High Availability Setup**
1. **Database replication** with PostgreSQL standby
2. **Redis clustering** for cache redundancy
3. **Application clustering** with multiple instances
4. **Health checks and automatic failover**

### **Cost Optimization**

#### **AWS Cost Estimates (Monthly)**
- **t3.small**: $15-20 (development/testing)
- **t3.medium**: $30-40 (small production)
- **t3.large**: $60-75 (medium production)
- **RDS PostgreSQL**: $15-50 (depending on size)
- **Data transfer**: $5-20 (depending on volume)

#### **Cost-Saving Tips**
1. Use **spot instances** for non-critical workloads
2. Implement **automatic scaling** to handle variable loads
3. Set up **data lifecycle policies** to archive old data
4. Monitor and optimize **API usage** to stay within free tiers

---

## 📞 **Support and Next Steps**

### **Immediate Actions After Deployment**
1. **Test the demo**: `sudo -u research python main.py --demo`
2. **Configure API keys**: Add your Twitter, Reddit, and other platform credentials
3. **Start small**: Begin with 1-2 platforms and limited collection
4. **Monitor closely**: Watch logs and system resources for the first 24-48 hours
5. **Set up alerts**: Configure email/SMS alerts for system issues

### **Production Readiness Checklist**
- [ ] All API keys configured and tested
- [ ] Database setup completed
- [ ] Service starts automatically on boot
- [ ] Logs are being written correctly
- [ ] System monitoring is active
- [ ] Backup strategy implemented
- [ ] Security measures in place
- [ ] Documentation updated with your specific setup

Your **Digital Radicalization Research System** is now ready for production deployment! 🎉

The system will automatically:
- ✅ Collect data from multiple platforms every 30 minutes to 2 hours
- ✅ Classify texts using your 59 Turkish/English keywords across 8 categories
- ✅ Aggregate results by region, week, platform, and category
- ✅ Generate weekly reports in both HTML and JSON formats
- ✅ Handle errors gracefully and resume collection automatically
- ✅ Scale from small research projects to large-scale monitoring