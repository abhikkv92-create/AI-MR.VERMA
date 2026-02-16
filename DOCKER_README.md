# MR.VERMA Docker Setup

## Quick Start

```bash
# 1. Clone and navigate to the project
cd mr-verma

# 2. Configure environment
cp .env.example .env
# Edit .env with your NVIDIA API keys

# 3. Build and start all services
docker-compose up -d

# 4. Check service status
docker-compose ps

# 5. View logs
docker-compose logs -f collector
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| collector | 8550 | Main API Gateway & NVIDIA Proxy |
| trainer | - | Background SFT Training Engine |
| milvus-standalone | 19530 | Vector Database |
| etcd | 2379 | Milvus Metadata Store |
| minio | 9000/9001 | Object Storage |

## Environment Variables

Required in `.env`:
```bash
NVIDIA_API_KEY=your_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
NVIDIA_MODEL=moonshotai/kimi-k2.5
```

Optional:
```bash
LOG_LEVEL=INFO
TRAINING_INTERVAL_HOURS=6
COLLECTOR_PORT=8550
```

## Commands

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d collector

# View logs
docker-compose logs -f

# Scale collector (if needed)
docker-compose up -d --scale collector=2

# Stop all
docker-compose down

# Stop and remove volumes (WARNING: Data loss)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Execute command in container
docker-compose exec collector python -c "print('Hello')"
```

## Health Checks

All services include health checks:
- Collector: http://localhost:8550/health
- Milvus: http://localhost:9091/healthz
- MinIO: http://localhost:9000/minio/health/live

## Data Persistence

Data is persisted in Docker volumes:
- `etcd-data`: Milvus metadata
- `minio-data`: Object storage
- `milvus-data`: Vector data

Host-mounted directories:
- `./agent-lightning-local/data`: Interactions & logs
- `./agent-lightning-local/logs`: Application logs
- `./agent-lightning-local/checkpoints`: Training checkpoints

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Restart service
docker-compose restart service-name
```

### NVIDIA API Issues
```bash
# Test API connectivity
docker-compose exec collector curl -H "Authorization: Bearer $NVIDIA_API_KEY" \
  https://integrate.api.nvidia.com/v1/models
```

### Milvus Connection Issues
```bash
# Check Milvus status
docker-compose logs milvus-standalone

# Restart Milvus
docker-compose restart milvus-standalone
```

## Production Deployment

For production, use the production-specific configuration:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Or create a `.env` file with production settings.

## Monitoring

To enable Prometheus and Grafana monitoring:

1. Uncomment monitoring services in `docker-compose.yml`
2. Start services: `docker-compose up -d`
3. Access Grafana: http://localhost:3000 (admin/admin)
4. Access Prometheus: http://localhost:9090

## Security

- Never commit `.env` files
- Use Docker secrets for sensitive data in production
- Regularly update base images: `docker-compose pull`
- Run security scans: `docker-compose exec collector pip list`

## Support

For issues, check:
1. Service logs: `docker-compose logs`
2. System resources: `docker stats`
3. Network connectivity: `docker network ls`
