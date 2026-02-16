# Deployment Guide

## Overview

This guide covers deploying MR.VERMA to production environments.

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS (12+), or Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **Docker**: 20.10+ (optional, for containerized deployment)

### Network Requirements

- Outbound HTTPS (443) access to:
  - `integrate.api.nvidia.com`
  - `api.openai.com` (if using OpenAI)
  - Docker Hub (for container images)

---

## Installation

### Option 1: Direct Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/mr-verma.git
cd mr-verma
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Option 2: Docker Deployment

1. **Build images**
```bash
docker-compose -f agent-lightning-local/docker-compose.yml build
```

2. **Start services**
```bash
docker-compose -f agent-lightning-local/docker-compose.yml up -d
```

3. **Verify services**
```bash
docker-compose ps
```

---

## Configuration

### Environment Variables

Create `.env` file:

```bash
# Required
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=z-ai/glm5

# Optional - Secondary AI
NVIDIA_API_KEY_SECONDARY=your_secondary_key

# Optional - Vision AI
NVIDIA_API_KEY_VISION=your_vision_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mrverma.log

# Performance
MAX_WORKERS=5
TASK_TIMEOUT=300
```

### Production Settings

Edit `config/production.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8550
  workers: 4

security:
  enable_auth: true
  jwt_secret: ${JWT_SECRET}
  token_expiry: 3600

logging:
  level: INFO
  format: json
  output: stdout

rate_limiting:
  requests_per_second: 10
  burst_size: 20
```

---

## Deployment Strategies

### Single Server Deployment

```bash
# Start the core system
python -m core.orchestrator

# Or use the startup script
./start.sh
```

### Multi-Server Deployment

**Server 1 - API Gateway**
```bash
python -m core.gateway
```

**Server 2 - Agent Workers**
```bash
python -m agents.worker --cluster=INTELLIGENCE
python -m agents.worker --cluster=PLATFORM
```

**Server 3 - Task Queue**
```bash
python -m core.task_queue_server
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mrverma-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mrverma
  template:
    metadata:
      labels:
        app: mrverma
    spec:
      containers:
      - name: mrverma
        image: mrverma:latest
        env:
        - name: NVIDIA_API_KEY
          valueFrom:
            secretKeyRef:
              name: mrverma-secrets
              key: nvidia-api-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

Deploy:
```bash
kubectl apply -f k8s/
```

---

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d mrverma.yourdomain.com

# Configure paths in .env
SSL_CERT=/etc/letsencrypt/live/mrverma.yourdomain.com/fullchain.pem
SSL_KEY=/etc/letsencrypt/live/mrverma.yourdomain.com/privkey.pem
```

### Using Self-Signed Certificates

```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure paths
SSL_CERT=cert.pem
SSL_KEY=key.pem
```

---

## Database Setup (Optional)

For persistent storage:

### PostgreSQL

```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres createdb mrverma

# Configure connection
DATABASE_URL=postgresql://user:pass@localhost/mrverma
```

### Redis

```bash
# For caching and session storage
REDIS_URL=redis://localhost:6379/0
```

---

## Monitoring Setup

### Prometheus + Grafana

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Import dashboards
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/dashboards/mrverma.json
```

### Health Checks

```bash
# System health
curl http://localhost:8550/health

# Detailed status
curl http://localhost:8550/health/detailed
```

---

## Backup and Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backups/mrverma
DATE=$(date +%Y%m%d_%H%M%S)

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env config/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Backup database (if using)
pg_dump $DATABASE_URL > $BACKUP_DIR/db_$DATE.sql

# Clean old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Procedure

```bash
# Stop services
docker-compose down

# Restore configuration
tar -xzf backups/config_20240101_120000.tar.gz

# Restore database
psql $DATABASE_URL < backups/db_20240101_120000.sql

# Restart services
docker-compose up -d
```

---

## Security Hardening

### 1. File Permissions

```bash
# Set proper permissions
chmod 600 .env
chmod 755 logs/
chmod 700 scripts/
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8550/tcp  # MR.VERMA API
sudo ufw enable
```

### 3. Fail2Ban

```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure for MR.VERMA
sudo tee /etc/fail2ban/jail.local <<EOF
[mrverma]
enabled = true
port = 8550
filter = mrverma
logpath = /var/log/mrverma/auth.log
maxretry = 5
bantime = 3600
EOF
```

---

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Update PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/mr-verma
```

**2. API Connection Failures**
```bash
# Test connectivity
curl -I https://integrate.api.nvidia.com

# Check API key
python -c "from core.env_manager import load_env_file; load_env_file()"
```

**3. High Memory Usage**
```bash
# Check memory usage
ps aux | grep python

# Adjust worker count
MAX_WORKERS=2
```

**4. Task Queue Backlog**
```bash
# Check queue status
curl http://localhost:8550/queue/status

# Clear stuck tasks
python scripts/clear_queue.py
```

### Log Analysis

```bash
# View recent errors
tail -f logs/mrverma.log | grep ERROR

# Search for specific issues
grep "TASK_FAIL" logs/audit.log
```

---

## Performance Tuning

### 1. CPU Optimization

```python
# core/processing_unit.py
# Adjust based on your hardware
HIGH_PRIORITY_WORKERS = 6  # P-cores
STANDARD_WORKERS = 4       # E-cores
```

### 2. Memory Management

```python
# Set memory limits
import resource
resource.setrlimit(resource.RLIMIT_AS, (8 * 1024 * 1024 * 1024, -1))  # 8GB
```

### 3. Rate Limiting

```python
# Adjust based on API limits
RATE_LIMIT_CAPACITY = 100
RATE_LIMIT_REFILL = 10.0  # per second
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Check error logs
- Monitor disk space
- Verify API connectivity

**Weekly:**
- Review performance metrics
- Update dependencies
- Backup configuration

**Monthly:**
- Security audit
- Dependency updates
- Disaster recovery test

### Automated Maintenance

```bash
# Add to crontab
0 2 * * * /path/to/mr-verma/scripts/backup.sh
0 */6 * * * /path/to/mr-verma/scripts/health_check.sh
0 0 * * 0 /path/to/mr-verma/scripts/cleanup.sh
```

---

## Support

For deployment issues:
- Check logs: `logs/`
- Review documentation: `docs/`
- Open issue: GitHub Issues
- Contact: support@mrverma.ai

---

**Last Updated:** 2026-02-16  
**Version:** 5.0.0
