# 📊 **Monitoring Systems Guide - Homescreen Project**

## 🎯 **Overview**

The Homescreen project includes comprehensive monitoring and analytics systems to ensure optimal performance, quality, and user experience. This guide covers the ProductionMonitor and FeedbackAnalyzer systems.

---

## 🔍 **ProductionMonitor System**

### **Purpose**
Real-time monitoring of system health, performance metrics, and automated alerting for production environments.

### **Key Features**
- **Real-time Metrics Collection**: Request performance, quality scores, costs
- **Automated Alerting**: Configurable thresholds with severity levels
- **System Health Assessment**: Overall system status and diagnostics
- **Performance Analytics**: Comprehensive metrics dashboard
- **Historical Data**: Trend analysis and performance tracking

---

## 📈 **Using ProductionMonitor**

### **Basic Usage**

```python
from api.monitoring.production_monitor import production_monitor

# Record request metrics
metrics = {
    'success': True,
    'processing_time': 15.2,
    'quality_score': 0.85,
    'cost': 0.08,
    'cache_hit': False,
    'model_used': 'gpt-image-1',
    'error_type': None
}

production_monitor.record_request_metrics(metrics)
```

### **System Health Check**

```python
# Get current system health
health = production_monitor.get_system_health()

print(f"Status: {health['status']}")
print(f"Message: {health['message']}")
print(f"Metrics: {health['metrics']}")

# Example output:
# Status: healthy
# Message: All systems operational
# Metrics: {
#     'total_requests': 150,
#     'error_rate': 0.02,
#     'avg_response_time': 18.5,
#     'avg_quality_score': 0.82,
#     'cache_hit_rate': 0.35,
#     'total_cost_per_hour': 2.40
# }
```

### **Quality Metrics Dashboard**

```python
# Get dashboard metrics
dashboard = production_monitor.get_quality_metrics_dashboard()

print(f"Total requests: {dashboard['total_requests']}")
print(f"Average quality: {dashboard['average_quality']:.3f}")
print(f"Quality distribution: {dashboard['quality_distribution']}")

# Example output:
# Total requests: 150
# Average quality: 0.823
# Quality distribution: {
#     'excellent': 85,  # ≥0.85
#     'good': 45,       # 0.75-0.85
#     'fair': 15,       # 0.65-0.75
#     'poor': 5         # <0.65
# }
```

### **Alert Management**

```python
# Get recent alerts
alerts = production_monitor.get_recent_alerts(hours=24)

for alert in alerts:
    print(f"{alert['severity']}: {alert['message']} ({alert['timestamp']})")

# Example output:
# high: Request failed: Connection timeout (2024-01-15 14:30:22)
# medium: Low quality score: 0.65 (2024-01-15 14:25:10)
# low: High request cost: $0.12 (2024-01-15 14:20:05)
```

### **Metrics Export**

```python
# Export metrics to file
export_file = production_monitor.export_metrics()
print(f"Metrics exported to: {export_file}")

# Custom export path
export_file = production_monitor.export_metrics("custom_metrics_2024.json")
```

---

## 🚨 **Alert Configuration**

### **Default Alert Thresholds**

```python
alert_thresholds = {
    'error_rate': 0.05,        # 5% error rate threshold
    'response_time': 60.0,     # 60 second response time threshold
    'quality_score': 0.70,     # Minimum quality score threshold
    'cache_hit_rate': 0.30,    # Minimum cache hit rate threshold
    'cost_per_hour': 10.0      # Maximum cost per hour threshold
}
```

### **Alert Severity Levels**

- **High**: Critical system failures, high error rates
- **Medium**: Performance degradation, quality issues
- **Low**: Cost warnings, cache efficiency issues

### **Customizing Alert Thresholds**

```python
# Modify alert thresholds
production_monitor.alert_thresholds['quality_score'] = 0.80
production_monitor.alert_thresholds['response_time'] = 45.0

# More strict quality requirements
production_monitor.alert_thresholds['error_rate'] = 0.02  # 2% instead of 5%
```

---

## 📝 **FeedbackAnalyzer System**

### **Purpose**
Collect, analyze, and derive insights from user feedback to continuously improve system performance and user experience.

### **Key Features**
- **Feedback Collection**: Rating system with detailed comments
- **Correlation Analysis**: AI quality scores vs user ratings
- **Trend Analysis**: Performance trends over time
- **Improvement Recommendations**: Automated suggestions based on feedback
- **Category Analysis**: Feedback breakdown by type and screen category

---

## 🔄 **Using FeedbackAnalyzer**

### **Collecting Feedback**

```python
from api.feedback.user_feedback import feedback_analyzer

# Collect user feedback
feedback_data = {
    'feedback_type': 'quality',
    'rating': 4,  # 1-5 scale
    'comment': 'Good quality but screen alignment could be better',
    'screen_type': 'security',
    'image_quality_score': 0.78,
    'processing_time': 18.5,
    'user_session': 'anonymous_session_123',
    'metadata': {
        'image_size': '1024x1024',
        'prompt_length': 150
    }
}

result = feedback_analyzer.collect_feedback(feedback_data)
print(f"Feedback collected: {result['success']}")
```

### **Feedback Analysis**

```python
# Get feedback summary for last 30 days
summary = feedback_analyzer.get_feedback_summary(days=30)

print(f"Total feedback: {summary['total_feedback']}")
print(f"Average rating: {summary['average_rating']:.2f}")
print(f"Rating distribution: {summary['rating_distribution']}")

# Feedback by type
for feedback_type, data in summary['feedback_by_type'].items():
    print(f"{feedback_type}: {data['average_rating']:.2f} ({data['count']} responses)")

# Example output:
# Total feedback: 245
# Average rating: 4.1
# Rating distribution: {1: 5, 2: 12, 3: 38, 4: 125, 5: 65}
# quality: 4.2 (89 responses)
# accuracy: 3.9 (67 responses)
# performance: 4.3 (45 responses)
# usability: 4.0 (44 responses)
```

### **Quality Correlation Analysis**

```python
# Analyze correlation between AI scores and user ratings
summary = feedback_analyzer.get_feedback_summary(days=30)
correlation = summary['quality_correlation']

print(f"Correlation coefficient: {correlation['correlation_coefficient']}")
print(f"Sample size: {correlation['sample_size']}")

# Quality range analysis
for range_name, data in correlation['quality_range_analysis'].items():
    print(f"{range_name}: {data['average_user_rating']:.2f} "
          f"({data['count']} samples, AI range: {data['quality_range']})")

# Example output:
# Correlation coefficient: 0.72
# Sample size: 156
# excellent: 4.6 (45 samples, AI range: 0.85 - 1.00)
# good: 4.1 (67 samples, AI range: 0.75 - 0.85)
# fair: 3.4 (32 samples, AI range: 0.65 - 0.75)
# poor: 2.8 (12 samples, AI range: 0.00 - 0.65)
```

### **Improvement Recommendations**

```python
# Get automated improvement recommendations
recommendations = feedback_analyzer.get_improvement_recommendations()

for rec in recommendations:
    print(f"{rec['type']}: {rec['message']}")
    print(f"Category: {rec['category']}")
    print(f"Actions: {rec['suggested_actions']}")
    print("---")

# Example output:
# high: Quality feedback is poor (2.8/5)
# Category: quality
# Actions: ['Increase quality thresholds', 'Enable iterative quality improvement', 'Review prompt engineering']
# ---
# medium: Low correlation between AI quality scores and user ratings (0.45)
# Category: quality_assessment
# Actions: ['Review quality assessment algorithm', 'Collect more detailed user feedback']
```

---

## 📊 **Dashboard Integration**

### **Real-time Monitoring Dashboard**

```python
# Get comprehensive dashboard data
def get_dashboard_data():
    # System health
    health = production_monitor.get_system_health()
    
    # Performance metrics
    metrics = production_monitor.get_quality_metrics_dashboard()
    
    # Recent alerts
    alerts = production_monitor.get_recent_alerts(hours=24)
    
    # User feedback summary
    feedback = feedback_analyzer.get_feedback_summary(days=7)
    
    return {
        'system_health': health,
        'performance_metrics': metrics,
        'recent_alerts': alerts,
        'user_feedback': feedback,
        'last_updated': datetime.now().isoformat()
    }

dashboard_data = get_dashboard_data()
```

### **Performance Trends**

```python
# Analyze performance trends
def analyze_trends():
    summary = feedback_analyzer.get_feedback_summary(days=30)
    trends = summary['recent_trends']
    
    print(f"Trend direction: {trends['trend_direction']}")
    
    for segment in trends['segments']:
        print(f"{segment['period']}: {segment['average_rating']:.2f} "
              f"({segment['count']} responses)")

# Example output:
# Trend direction: improving
# 01/08 - 01/15: 4.3 (45 responses)
# 01/01 - 01/08: 4.1 (52 responses)
# 12/25 - 01/01: 3.9 (38 responses)
```

---

## 🔧 **Configuration and Customization**

### **ProductionMonitor Configuration**

```python
# Customize monitoring settings
production_monitor.monitoring_enabled = True
production_monitor.alert_thresholds = {
    'error_rate': 0.03,        # More strict error rate
    'response_time': 45.0,     # Faster response requirement
    'quality_score': 0.80,     # Higher quality standard
    'cache_hit_rate': 0.40,    # Better cache efficiency
    'cost_per_hour': 8.0       # Lower cost threshold
}
```

### **FeedbackAnalyzer Configuration**

```python
# Customize feedback analysis
feedback_analyzer.analysis_cache = {}
feedback_analyzer.cache_timeout = 600  # 10 minutes cache

# Custom feedback categories
CUSTOM_FEEDBACK_TYPES = [
    ('screen_alignment', 'Screen Alignment'),
    ('material_realism', 'Material Realism'),
    ('lighting_quality', 'Lighting Quality'),
    ('overall_satisfaction', 'Overall Satisfaction')
]
```

---

## 📈 **Best Practices**

### **Monitoring Best Practices**

1. **Regular Health Checks**: Monitor system health every 5 minutes
2. **Alert Response**: Respond to high-severity alerts within 15 minutes
3. **Performance Baselines**: Establish baseline metrics for comparison
4. **Trend Analysis**: Review weekly trends for proactive optimization
5. **Cost Monitoring**: Track costs daily to prevent budget overruns

### **Feedback Collection Best Practices**

1. **Prompt for Feedback**: Request feedback after each generation
2. **Contextual Information**: Include generation parameters with feedback
3. **Response Incentives**: Encourage detailed feedback with benefits
4. **Regular Analysis**: Review feedback weekly for improvement opportunities
5. **Action on Insights**: Implement changes based on feedback analysis

### **Data Retention**

- **Metrics History**: Keep 1000 most recent entries in memory
- **Alert History**: Retain 100 most recent alerts
- **Feedback Data**: Permanent storage in database
- **Export Frequency**: Weekly exports for long-term analysis

---

## 🚨 **Troubleshooting**

### **Common Monitoring Issues**

**No Metrics Being Recorded:**
```python
# Check if monitoring is enabled
print(f"Monitoring enabled: {production_monitor.monitoring_enabled}")

# Verify metrics recording
test_metrics = {'success': True, 'processing_time': 10.0, 'quality_score': 0.8, 'cost': 0.05}
production_monitor.record_request_metrics(test_metrics)
```

**Alerts Not Triggering:**
```python
# Check alert thresholds
print(f"Alert thresholds: {production_monitor.alert_thresholds}")

# Test alert system
test_metrics = {'success': False, 'error_type': 'Test error'}
production_monitor.record_request_metrics(test_metrics)
```

**Feedback Analysis Errors:**
```python
# Check database connection
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("Database connection: OK")
except Exception as e:
    print(f"Database error: {e}")
```

---

## 📞 **Support and Maintenance**

### **Regular Maintenance Tasks**

1. **Daily**: Check system health and recent alerts
2. **Weekly**: Review performance trends and user feedback
3. **Monthly**: Export metrics and analyze long-term trends
4. **Quarterly**: Review and adjust alert thresholds

### **Performance Optimization**

- **Cache Efficiency**: Monitor cache hit rates and optimize cache TTL
- **Alert Tuning**: Adjust thresholds based on actual system performance
- **Feedback Analysis**: Use insights to improve AI model performance
- **Cost Optimization**: Monitor costs and optimize API usage

This monitoring system provides comprehensive visibility into system performance and user satisfaction, enabling proactive optimization and continuous improvement of the Homescreen application.
