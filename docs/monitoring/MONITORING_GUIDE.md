# Monitoring and Metrics Infrastructure

## Overview

This guide explains how to set up monitoring and metrics collection for MR.VERMA in production.

---

## Metrics Collection

### 1. System Metrics

CPU, Memory, and Disk usage tracking:

```python
from core.monitoring import SystemMonitor

monitor = SystemMonitor()

# Get current metrics
metrics = monitor.collect_metrics()
print(f"CPU: {metrics['cpu_percent']}%")
print(f"Memory: {metrics['memory_used']}/{metrics['memory_total']} MB")
print(f"Disk: {metrics['disk_used']}/{metrics['disk_total']} GB")
```

### 2. Agent Performance Metrics

Track agent execution performance:

```python
from core.monitoring import AgentMetrics

metrics = AgentMetrics()

# Record agent execution
metrics.record_execution(
    agent_id="DataScientist",
    task_type="ai_log_analysis",
    duration=1.23,
    success=True
)

# Get performance summary
summary = metrics.get_summary()
print(f"Total tasks: {summary['total_tasks']}")
print(f"Success rate: {summary['success_rate']}%")
print(f"Avg duration: {summary['avg_duration']}s")
```

### 3. API Metrics

Track API usage and performance:

```python
from core.monitoring import APIMetrics

metrics = APIMetrics()

# Record API call
metrics.record_call(
    endpoint="/v1/chat/completions",
    latency=0.5,
    status_code=200,
    tokens_used=150
)

# Get usage statistics
stats = metrics.get_stats()
print(f"Total calls: {stats['total_calls']}")
print(f"Avg latency: {stats['avg_latency']}s")
print(f"Error rate: {stats['error_rate']}%")
```

---

## Health Checks

### Health Check Endpoint

```python
from core.monitoring import HealthCheck

health = HealthCheck()

# Register component checks
health.add_check("database", check_database_connection)
health.add_check("api", check_api_availability)
health.add_check("agents", check_agent_status)

# Get overall health status
status = health.get_status()
if status["status"] == "healthy":
    print("All systems operational")
else:
    print(f"Issues detected: {status['failures']}")
```

### Custom Health Checks

```python
async def check_database_connection():
    try:
        # Your database check logic
        return {"status": "pass", "response_time": 0.1}
    except Exception as e:
        return {"status": "fail", "error": str(e)}
```

---

## Logging

### Structured Logging

```python
import logging
from core.monitoring import StructuredLogger

logger = StructuredLogger("my_service")

# Log with context
logger.info(
    "Task completed",
    extra={
        "task_id": "123",
        "agent": "DataScientist",
        "duration": 1.5,
        "success": True
    }
)
```

### Log Aggregation

Configure log shipping to centralized system:

```python
from core.monitoring import LogShipper

shipper = LogShipper(
    destination="elasticsearch",
    host="logs.mrverma.internal",
    port=9200
)

shipper.start()
```

---

## Alerting

### Alert Rules

```python
from core.monitoring import AlertManager

alerts = AlertManager()

# Define alert rules
alerts.add_rule(
    name="high_cpu",
    condition="cpu_percent > 80",
    duration="5m",
    severity="warning"
)

alerts.add_rule(
    name="api_errors",
    condition="error_rate > 5",
    duration="2m",
    severity="critical"
)

# Configure notifications
alerts.configure_notification(
    channel="slack",
    webhook="https://hooks.slack.com/..."
)
```

### Custom Alert Handlers

```python
async def on_high_cpu(alert):
    # Scale up resources
    await scale_up_workers()
    
    # Notify team
    await send_notification(
        channel="slack",
        message=f"High CPU detected: {alert['value']}%"
    )

alerts.on("high_cpu", on_high_cpu)
```

---

## Prometheus Integration

### Metrics Export

```python
from core.monitoring import PrometheusExporter

exporter = PrometheusExporter(port=9090)
exporter.start()

# Register custom metrics
exporter.gauge("mrverma_agents_active", "Number of active agents")
exporter.counter("mrverma_tasks_total", "Total tasks processed")
exporter.histogram("mrverma_task_duration", "Task execution duration")

# Update metrics
exporter.set("mrverma_agents_active", 5)
exporter.increment("mrverma_tasks_total", labels={"agent": "DataScientist"})
exporter.observe("mrverma_task_duration", 1.23, labels={"agent": "DataScientist"})
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mrverma'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

---

## Grafana Dashboards

### Dashboard Configuration

Create `grafana/dashboards/mrverma.json`:

```json
{
  "dashboard": {
    "title": "MR.VERMA Overview",
    "panels": [
      {
        "title": "Active Agents",
        "type": "stat",
        "targets": [
          {
            "expr": "mrverma_agents_active"
          }
        ]
      },
      {
        "title": "Task Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mrverma_tasks_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "heatmap",
        "targets": [
          {
            "expr": "mrverma_task_duration_bucket"
          }
        ]
      }
    ]
  }
}
```

---

## Monitoring Setup Script

### Quick Start

Run the monitoring setup:

```bash
python scripts/setup_monitoring.py
```

This will:
1. Install Prometheus
2. Install Grafana
3. Configure data sources
4. Import dashboards
5. Start monitoring stack

### Docker Compose

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  node-exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
    ports:
      - "9100:9100"

volumes:
  prometheus_data:
  grafana_data:
```

Start monitoring:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## Production Monitoring Checklist

### Metrics to Track
- [ ] System resources (CPU, Memory, Disk)
- [ ] Agent task queue depth
- [ ] API response times and error rates
- [ ] Token usage and costs
- [ ] Agent execution success rates
- [ ] Security events and audit logs

### Alerts to Configure
- [ ] High CPU/Memory usage (>80%)
- [ ] API error rate > 5%
- [ ] Agent failure rate > 10%
- [ ] Queue backlog > 100 tasks
- [ ] Security events (unauthorized access)
- [ ] Disk space < 20%

### Dashboards to Create
- [ ] System Overview
- [ ] Agent Performance
- [ ] API Usage
- [ ] Security Audit
- [ ] Cost Analysis
