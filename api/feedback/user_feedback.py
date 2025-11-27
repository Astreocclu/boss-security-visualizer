"""
User Feedback Collection System
Collect and analyze user feedback for continuous improvement
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

logger = logging.getLogger(__name__)

class FeedbackEntry(models.Model):
    """Model for storing user feedback."""
    
    FEEDBACK_TYPES = [
        ('quality', 'Image Quality'),
        ('accuracy', 'Screen Accuracy'),
        ('performance', 'Performance'),
        ('usability', 'Usability'),
        ('general', 'General Feedback')
    ]
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Excellent')
    ]
    
    # Basic fields
    timestamp = models.DateTimeField(auto_now_add=True)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (Very Poor) to 5 (Excellent)"
    )
    
    # Detailed feedback
    comment = models.TextField(blank=True, help_text="Optional detailed feedback")
    
    # Context information
    screen_type = models.CharField(max_length=50, blank=True, help_text="Type of screen being visualized")
    image_quality_score = models.FloatField(null=True, blank=True, help_text="AI-assessed quality score")
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    
    # User information (optional, anonymous by default)
    user_session = models.CharField(max_length=100, blank=True, help_text="Anonymous session identifier")
    user_agent = models.CharField(max_length=500, blank=True, help_text="Browser user agent")
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional context data")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['feedback_type']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.feedback_type} - {self.rating}/5 - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class FeedbackAnalyzer:
    """Analyze user feedback for insights and improvements."""
    
    def __init__(self):
        self.analysis_cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def collect_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and store user feedback."""
        try:
            # Validate required fields
            required_fields = ['feedback_type', 'rating']
            for field in required_fields:
                if field not in feedback_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create feedback entry
            feedback = FeedbackEntry.objects.create(
                feedback_type=feedback_data['feedback_type'],
                rating=feedback_data['rating'],
                comment=feedback_data.get('comment', ''),
                screen_type=feedback_data.get('screen_type', ''),
                image_quality_score=feedback_data.get('image_quality_score'),
                processing_time=feedback_data.get('processing_time'),
                user_session=feedback_data.get('user_session', ''),
                user_agent=feedback_data.get('user_agent', ''),
                metadata=feedback_data.get('metadata', {})
            )
            
            logger.info(f"Feedback collected: {feedback.feedback_type} - {feedback.rating}/5")
            
            return {
                'success': True,
                'feedback_id': feedback.id,
                'message': 'Feedback collected successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to collect feedback'
            }
    
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of feedback over specified period."""
        try:
            # Check cache
            cache_key = f"feedback_summary_{days}"
            if cache_key in self.analysis_cache:
                cached_data, timestamp = self.analysis_cache[cache_key]
                if datetime.now().timestamp() - timestamp < self.cache_timeout:
                    return cached_data
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get feedback in date range
            feedback_queryset = FeedbackEntry.objects.filter(
                timestamp__gte=start_date,
                timestamp__lte=end_date
            )
            
            total_feedback = feedback_queryset.count()
            
            if total_feedback == 0:
                return {
                    'total_feedback': 0,
                    'message': 'No feedback available for the specified period'
                }
            
            # Calculate overall metrics
            ratings = list(feedback_queryset.values_list('rating', flat=True))
            average_rating = sum(ratings) / len(ratings)
            
            # Rating distribution
            rating_distribution = {}
            for i in range(1, 6):
                rating_distribution[i] = ratings.count(i)
            
            # Feedback by type
            feedback_by_type = {}
            for feedback_type, _ in FeedbackEntry.FEEDBACK_TYPES:
                type_feedback = feedback_queryset.filter(feedback_type=feedback_type)
                if type_feedback.exists():
                    type_ratings = list(type_feedback.values_list('rating', flat=True))
                    feedback_by_type[feedback_type] = {
                        'count': len(type_ratings),
                        'average_rating': sum(type_ratings) / len(type_ratings),
                        'rating_distribution': {i: type_ratings.count(i) for i in range(1, 6)}
                    }
            
            # Screen type analysis
            screen_type_feedback = {}
            screen_types = feedback_queryset.exclude(screen_type='').values_list('screen_type', flat=True).distinct()
            for screen_type in screen_types:
                type_feedback = feedback_queryset.filter(screen_type=screen_type)
                type_ratings = list(type_feedback.values_list('rating', flat=True))
                screen_type_feedback[screen_type] = {
                    'count': len(type_ratings),
                    'average_rating': sum(type_ratings) / len(type_ratings)
                }
            
            # Quality correlation analysis
            quality_correlation = self._analyze_quality_correlation(feedback_queryset)
            
            # Recent trends
            recent_trends = self._analyze_recent_trends(feedback_queryset, days)
            
            summary = {
                'period_days': days,
                'total_feedback': total_feedback,
                'average_rating': round(average_rating, 2),
                'rating_distribution': rating_distribution,
                'feedback_by_type': feedback_by_type,
                'screen_type_feedback': screen_type_feedback,
                'quality_correlation': quality_correlation,
                'recent_trends': recent_trends,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the result
            self.analysis_cache[cache_key] = (summary, datetime.now().timestamp())
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {str(e)}")
            return {
                'error': str(e),
                'message': 'Failed to analyze feedback'
            }
    
    def _analyze_quality_correlation(self, feedback_queryset) -> Dict[str, Any]:
        """Analyze correlation between AI quality scores and user ratings."""
        try:
            # Get feedback with quality scores
            quality_feedback = feedback_queryset.exclude(image_quality_score__isnull=True)
            
            if quality_feedback.count() < 5:
                return {'message': 'Insufficient data for quality correlation analysis'}
            
            # Calculate correlation
            quality_scores = list(quality_feedback.values_list('image_quality_score', flat=True))
            user_ratings = list(quality_feedback.values_list('rating', flat=True))
            
            # Simple correlation calculation
            n = len(quality_scores)
            sum_x = sum(quality_scores)
            sum_y = sum(user_ratings)
            sum_xy = sum(x * y for x, y in zip(quality_scores, user_ratings))
            sum_x2 = sum(x * x for x in quality_scores)
            sum_y2 = sum(y * y for y in user_ratings)
            
            correlation = (n * sum_xy - sum_x * sum_y) / ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
            
            # Quality score ranges vs user ratings
            quality_ranges = {
                'excellent': (0.85, 1.0),
                'good': (0.75, 0.85),
                'fair': (0.65, 0.75),
                'poor': (0.0, 0.65)
            }
            
            range_analysis = {}
            for range_name, (min_score, max_score) in quality_ranges.items():
                range_feedback = quality_feedback.filter(
                    image_quality_score__gte=min_score,
                    image_quality_score__lt=max_score
                )
                if range_feedback.exists():
                    range_ratings = list(range_feedback.values_list('rating', flat=True))
                    range_analysis[range_name] = {
                        'count': len(range_ratings),
                        'average_user_rating': sum(range_ratings) / len(range_ratings),
                        'quality_range': f"{min_score:.2f} - {max_score:.2f}"
                    }
            
            return {
                'correlation_coefficient': round(correlation, 3),
                'sample_size': n,
                'quality_range_analysis': range_analysis
            }
            
        except Exception as e:
            logger.error(f"Quality correlation analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_recent_trends(self, feedback_queryset, days: int) -> Dict[str, Any]:
        """Analyze recent trends in feedback."""
        try:
            # Split period into segments for trend analysis
            segments = min(7, days)  # Max 7 segments
            segment_days = days // segments
            
            trends = []
            end_date = datetime.now()
            
            for i in range(segments):
                segment_end = end_date - timedelta(days=i * segment_days)
                segment_start = segment_end - timedelta(days=segment_days)
                
                segment_feedback = feedback_queryset.filter(
                    timestamp__gte=segment_start,
                    timestamp__lt=segment_end
                )
                
                if segment_feedback.exists():
                    ratings = list(segment_feedback.values_list('rating', flat=True))
                    trends.append({
                        'period': f"{segment_start.strftime('%m/%d')} - {segment_end.strftime('%m/%d')}",
                        'count': len(ratings),
                        'average_rating': sum(ratings) / len(ratings)
                    })
            
            # Calculate trend direction
            if len(trends) >= 2:
                recent_avg = trends[0]['average_rating']
                older_avg = trends[-1]['average_rating']
                trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
            else:
                trend_direction = 'insufficient_data'
            
            return {
                'trend_direction': trend_direction,
                'segments': trends
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Generate improvement recommendations based on feedback analysis."""
        try:
            recommendations = []
            
            # Get recent feedback summary
            summary = self.get_feedback_summary(days=30)
            
            if 'error' in summary:
                return [{'type': 'error', 'message': 'Unable to analyze feedback for recommendations'}]
            
            # Low overall rating
            if summary.get('average_rating', 5) < 3.5:
                recommendations.append({
                    'type': 'critical',
                    'category': 'overall_quality',
                    'message': f"Overall rating is low ({summary['average_rating']:.1f}/5). Immediate attention needed.",
                    'suggested_actions': [
                        'Review recent quality issues',
                        'Analyze failed generations',
                        'Consider adjusting quality thresholds'
                    ]
                })
            
            # Quality-specific recommendations
            feedback_by_type = summary.get('feedback_by_type', {})
            
            for feedback_type, type_data in feedback_by_type.items():
                if type_data['average_rating'] < 3.0:
                    recommendations.append({
                        'type': 'high',
                        'category': feedback_type,
                        'message': f"{feedback_type.title()} feedback is poor ({type_data['average_rating']:.1f}/5)",
                        'suggested_actions': self._get_type_specific_actions(feedback_type)
                    })
            
            # Quality correlation recommendations
            quality_correlation = summary.get('quality_correlation', {})
            if 'correlation_coefficient' in quality_correlation:
                correlation = quality_correlation['correlation_coefficient']
                if correlation < 0.5:
                    recommendations.append({
                        'type': 'medium',
                        'category': 'quality_assessment',
                        'message': f"Low correlation between AI quality scores and user ratings ({correlation:.2f})",
                        'suggested_actions': [
                            'Review quality assessment algorithm',
                            'Collect more detailed user feedback',
                            'Adjust quality scoring criteria'
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return [{'type': 'error', 'message': f'Recommendation generation failed: {str(e)}'}]
    
    def _get_type_specific_actions(self, feedback_type: str) -> List[str]:
        """Get specific improvement actions for feedback type."""
        actions_map = {
            'quality': [
                'Increase quality thresholds',
                'Enable iterative quality improvement',
                'Review prompt engineering',
                'Analyze low-quality generations'
            ],
            'accuracy': [
                'Improve window detection algorithms',
                'Add more reference images',
                'Enhance screen alignment logic',
                'Review perspective correction'
            ],
            'performance': [
                'Optimize processing pipeline',
                'Improve caching efficiency',
                'Review API call optimization',
                'Consider infrastructure scaling'
            ],
            'usability': [
                'Improve user interface',
                'Add better progress indicators',
                'Enhance error messages',
                'Simplify user workflow'
            ],
            'general': [
                'Collect more specific feedback',
                'Review overall user experience',
                'Analyze user journey',
                'Consider feature improvements'
            ]
        }
        
        return actions_map.get(feedback_type, ['Review and analyze specific issues'])

# Global feedback analyzer instance
feedback_analyzer = FeedbackAnalyzer()
