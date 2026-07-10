# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] API keys obtained (OpenAI, Anthropic)
- [ ] SMTP credentials configured
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Backups configured

## Docker Compose Deployment

### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Clone Repository
```bash
git clone <repo-url>
cd ai_research_intelligence
```

### 3. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Key settings to configure:
# - DATABASE_URL
# - REDIS_URL
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - SMTP credentials
# - ENVIRONMENT=production
# - DEBUG=false
```

### 4. Start Services
```bash
# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Check logs
docker-compose logs -f api
```

### 5. Initialize Database
```bash
# Run migrations
docker-compose exec api python -m alembic upgrade head

# Or if using direct init
docker-compose exec api python -c "from app.db import init_db; init_db()"
```

### 6. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Flower monitoring
open http://localhost:5555
```

## AWS Deployment (ECS)

### 1. Prepare AWS Account
```bash
# Configure AWS CLI
aws configure

# Create ECR repository
aws ecr create-repository --repository-name air-api
aws ecr create-repository --repository-name air-worker
aws ecr create-repository --repository-name air-beat
```

### 2. Build and Push Images
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t air-api:latest -f Dockerfile .
docker tag air-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/air-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/air-api:latest

# Repeat for worker and beat
```

### 3. Create RDS PostgreSQL
```bash
aws rds create-db-instance \
  --db-instance-identifier ai-research-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username airesearch \
  --master-user-password <strong-password> \
  --allocated-storage 100 \
  --backup-retention-period 30
```

### 4. Create ElastiCache Redis
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id ai-research-cache \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0
```

### 5. Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name air-cluster

# Create task definition from task-definition.json
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create services
aws ecs create-service \
  --cluster air-cluster \
  --service-name air-api \
  --task-definition air-api:1 \
  --desired-count 2 \
  --load-balancers targetGroupArn=<arn>,containerName=api,containerPort=8000
```

### 6. Configure Auto Scaling
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/air-cluster/air-api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name air-api-scaling \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/air-cluster/air-api \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## GCP Deployment (Cloud Run)

### 1. Prepare GCP
```bash
gcloud projects create air-project
gcloud config set project air-project

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sql.googleapis.com
gcloud services enable redis.googleapis.com
```

### 2. Create Cloud SQL PostgreSQL
```bash
gcloud sql instances create ai-research-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

### 3. Create Memorystore Redis
```bash
gcloud redis instances create ai-research-cache \
  --size=1 \
  --region=us-central1
```

### 4. Build and Deploy
```bash
# Build image
gcloud builds submit --tag gcr.io/air-project/air-api

# Deploy to Cloud Run
gcloud run deploy air-api \
  --image gcr.io/air-project/air-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...,REDIS_URL=redis://... \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: air-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: air-api
  template:
    metadata:
      labels:
        app: air-api
    spec:
      containers:
      - name: api
        image: registry.example.com/air-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: air-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 2. Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace air

# Create secrets
kubectl create secret generic air-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=redis-url=redis://... \
  -n air

# Deploy
kubectl apply -f k8s/ -n air

# Verify deployment
kubectl get pods -n air
kubectl logs -f deployment/air-api -n air
```

## Scaling Configuration

### Horizontal Scaling
- API: 2-10 replicas based on CPU/memory
- Worker: 2-5 replicas based on queue depth
- Beat: 1 replica (should not scale)

### Vertical Scaling
```yaml
# Recommended minimums
api:
  memory: 1Gi
  cpu: 500m
worker:
  memory: 2Gi
  cpu: 1000m
beat:
  memory: 512Mi
  cpu: 250m
```

## Monitoring Setup

### Prometheus Metrics
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'air-api'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboards
- Request rate and latency
- Database connection pool
- Celery task queue depth
- Worker utilization
- Error rates
- Email delivery success

## Backup Strategy

### Database Backups
```bash
# Daily automated backups (configure in RDS/Cloud SQL)
# Retention: 30 days
# Point-in-time recovery: 7 days

# Manual backup
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Redis Backups
```bash
# Redis snapshots enabled
# Backup frequency: hourly
# Retention: 7 days
```

## SSL/TLS Configuration

### Let's Encrypt with Nginx
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Configure Nginx
```nginx
upstream api {
    server api:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Health Checks

```bash
# Container health
curl http://localhost:8000/health

# Database connection
docker-compose exec api python -c \
  "from app.db import verify_db_connection; verify_db_connection()"

# Redis connection
docker-compose exec api redis-cli -u $REDIS_URL ping

# Worker status
docker-compose exec celery_worker celery -A app.workers.celery_app inspect active

# Beat status
docker-compose exec celery_beat celery -A app.workers.celery_app inspect scheduled
```

## Troubleshooting

### Common Issues

#### Database connection errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -h localhost -U airesearch -d ai_research_intelligence

# Check logs
docker-compose logs postgres
```

#### Redis connection errors
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost ping

# Check logs
docker-compose logs redis
```

#### Celery worker not processing tasks
```bash
# Check worker is running
docker-compose ps celery_worker

# Inspect active tasks
celery -A app.workers.celery_app inspect active

# Check task queue
celery -A app.workers.celery_app inspect reserved

# Restart worker
docker-compose restart celery_worker
```

## Monitoring and Alerts

### CloudWatch/Stackdriver Alarms
- API latency > 1s
- Error rate > 1%
- Worker queue depth > 1000
- Database connection failures
- Disk usage > 80%
- Memory usage > 90%

### Alert Actions
- Send to Slack
- Email notification
- PagerDuty escalation
- Auto-scaling trigger

---

Last Updated: 2024
