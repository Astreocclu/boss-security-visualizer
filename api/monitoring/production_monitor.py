"""
Production Monitoring System
Comprehensive monitoring and alerting for the homescreen AI services
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class ProductionMonitor:
    """Production monitoring and alerting system."""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.monitoring_enabled = True
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% error rate threshold
            'response_time': 60.0,  # 60 second response time threshold
            'quality_score': 0.70,  # Minimum quality score threshold
            'cache_hit_rate': 0.30,  # Minimum cache hit rate threshold
            'cost_per_hour': 10.0  # Maximum cost per hour threshold
        }
        
    def record_request_metrics(self, metrics: Dict[str, Any]):
        """Record metrics for a single request."""
        try:
            timestamp = datetime.now()
            
            request_metrics = {
                'timestamp': timestamp.isoformat(),
                'success': metrics.get('success', False),
                'processing_time': metrics.get('processing_time', 0.0),
                'quality_score': metrics.get('quality_score', 0.0),
                'cost': metrics.get('cost', 0.0),
                'cache_hit': metrics.get('cache_hit', False),
                'model_used': metrics.get('model_used', 'unknown'),
                'error_type': metrics.get('error_type', None)
            }
            
            self.metrics_history.append(request_metrics)
            
            # Keep only last 1000 entries to prevent memory issues
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Check for alerts
            self._check_alerts(request_metrics)
            
        except Exception as e:
            logger.error(f"Failed to record request metrics: {str(e)}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            if not self.metrics_history:
                return {
                    'status': 'unknown',
                    'message': 'No metrics available',
                    'last_updated': datetime.now().isoformat()
                }
            
            # Analyze recent metrics (last hour)
            recent_cutoff = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.metrics_history 
                if datetime.fromisoformat(m['timestamp']) > recent_cutoff
            ]
            
            if not recent_metrics:
                return {
                    'status': 'stale',
                    'message': 'No recent activity',
                    'last_updated': self.metrics_history[-1]['timestamp']
                }
            
            # Calculate health metrics
            total_requests = len(recent_metrics)
            successful_requests = sum(1 for m in recent_metrics if m['success'])
            error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 0
            
            avg_response_time = sum(m['processing_time'] for m in recent_metrics) / total_requests if total_requests > 0 else 0
            avg_quality = sum(m['quality_score'] for m in recent_metrics if m['quality_score'] > 0) / max(1, sum(1 for m in recent_metrics if m['quality_score'] > 0))
            
            cache_hits = sum(1 for m in recent_metrics if m['cache_hit'])
            cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
            
            total_cost = sum(m['cost'] for m in recent_metrics)
            
            # Determine overall status
            status = 'healthy'
            issues = []
            
            if error_rate > self.alert_thresholds['error_rate']:
                status = 'degraded'
                issues.append(f"High error rate: {error_rate:.1%}")
            
            if avg_response_time > self.alert_thresholds['response_time']:
                status = 'degraded'
                issues.append(f"Slow response time: {avg_response_time:.1f}s")
            
            if avg_quality < self.alert_thresholds['quality_score']:
                status = 'degraded'
                issues.append(f"Low quality score: {avg_quality:.3f}")
            
            if cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
                status = 'warning'
                issues.append(f"Low cache hit rate: {cache_hit_rate:.1%}")
            
            if total_cost > self.alert_thresholds['cost_per_hour']:
                status = 'warning'
                issues.append(f"High cost: ${total_cost:.2f}/hour")
            
            return {
                'status': status,
                'message': '; '.join(issues) if issues else 'All systems operational',
                'metrics': {
                    'total_requests': total_requests,
                    'error_rate': error_rate,
                    'avg_response_time': avg_response_time,
                    'avg_quality_score': avg_quality,
                    'cache_hit_rate': cache_hit_rate,
                    'total_cost_per_hour': total_cost
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            return {
                'status': 'error',
                'message': f'Health check failed: {str(e)}',
                'last_updated': datetime.now().isoformat()
            }
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check if metrics trigger any alerts."""
        try:
            alerts_triggered = []
            
            # Error rate alert
            if not metrics['success']:
                alerts_triggered.append({
                    'type': 'error',
                    'message': f"Request failed: {metrics.get('error_type', 'Unknown error')}",
                    'severity': 'high',
                    'timestamp': metrics['timestamp']
                })
            
            # Response time alert
            if metrics['processing_time'] > self.alert_thresholds['response_time']:
                alerts_triggered.append({
                    'type': 'performance',
                    'message': f"Slow response time: {metrics['processing_time']:.1f}s",
                    'severity': 'medium',
                    'timestamp': metrics['timestamp']
                })
            
            # Quality alert
            if metrics['quality_score'] > 0 and metrics['quality_score'] < self.alert_thresholds['quality_score']:
                alerts_triggered.append({
                    'type': 'quality',
                    'message': f"Low quality score: {metrics['quality_score']:.3f}",
                    'severity': 'medium',
                    'timestamp': metrics['timestamp']
                })
            
            # Cost alert
            if metrics['cost'] > 1.0:  # Alert for unusually high single request cost
                alerts_triggered.append({
                    'type': 'cost',
                    'message': f"High request cost: ${metrics['cost']:.2f}",
                    'severity': 'low',
                    'timestamp': metrics['timestamp']
                })
            
            # Add alerts to history
            self.alerts.extend(alerts_triggered)
            
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
            # Log critical alerts
            for alert in alerts_triggered:
                if alert['severity'] == 'high':
                    logger.error(f"ALERT: {alert['message']}")
                elif alert['severity'] == 'medium':
                    logger.warning(f"ALERT: {alert['message']}")
                
        except Exception as e:
            logger.error(f"Alert checking failed: {str(e)}")
    
    def get_quality_metrics_dashboard(self) -> Dict[str, Any]:
        """Get quality metrics for dashboard display."""
        try:
            if not self.metrics_history:
                return {'error': 'No metrics available'}
            
            # Last 24 hours of data
            cutoff = datetime.now() - timedelta(hours=24)
            recent_metrics = [
                m for m in self.metrics_history 
                if datetime.fromisoformat(m['timestamp']) > cutoff
            ]
            
            if not recent_metrics:
                return {'error': 'No recent metrics available'}
            
            # Quality distribution
            quality_scores = [m['quality_score'] for m in recent_metrics if m['quality_score'] > 0]
            
            quality_distribution = {
                'excellent': sum(1 for q in quality_scores if q >= 0.85),
                'good': sum(1 for q in quality_scores if 0.75 <= q < 0.85),
                'fair': sum(1 for q in quality_scores if 0.65 <= q < 0.75),
                'poor': sum(1 for q in quality_scores if q < 0.65)
            }
            
            # Performance metrics
            processing_times = [m['processing_time'] for m in recent_metrics]
            costs = [m['cost'] for m in recent_metrics]
            
            return {
                'total_requests': len(recent_metrics),
                'successful_requests': sum(1 for m in recent_metrics if m['success']),
                'quality_distribution': quality_distribution,
                'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                'average_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
                'total_cost': sum(costs),
                'cache_hit_rate': sum(1 for m in recent_metrics if m['cache_hit']) / len(recent_metrics) if recent_metrics else 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Dashboard metrics failed: {str(e)}")
            return {'error': f'Dashboard metrics failed: {str(e)}'}
    
    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to JSON file."""
        try:
            if not filepath:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"metrics_export_{timestamp}.json"
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_metrics': len(self.metrics_history),
                'total_alerts': len(self.alerts),
                'metrics_history': self.metrics_history,
                'alerts': self.alerts,
                'alert_thresholds': self.alert_thresholds
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Metrics exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Metrics export failed: {str(e)}")
            raise
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified hours."""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            recent_alerts = [
                alert for alert in self.alerts
                if datetime.fromisoformat(alert['timestamp']) > cutoff
            ]
            
            # Sort by timestamp (newest first)
            recent_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return recent_alerts
            
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {str(e)}")
            return []

# Global monitor instance
production_monitor = ProductionMonitor()
