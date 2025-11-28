from django.db import models
from api.models import VisualizationRequest

class AuditReport(models.Model):
    """
    Stores the security audit results for a visualization request.
    """
    request = models.OneToOneField(
        VisualizationRequest,
        on_delete=models.CASCADE,
        related_name='audit_report',
        help_text="Associated visualization request"
    )
    
    # Vulnerability Flags (Boolean for easy querying)
    has_ground_level_access = models.BooleanField(default=False, help_text="Windows within 6ft of ground")
    has_concealment = models.BooleanField(default=False, help_text="Windows hidden by landscaping")
    has_glass_proximity = models.BooleanField(default=False, help_text="Glass within 40 inches of door lock")
    has_hardware_weakness = models.BooleanField(default=False, help_text="Visible standard fly screens")
    
    # Detailed Analysis (JSON)
    vulnerabilities = models.JSONField(
        default=list,
        help_text="List of detected vulnerabilities with coordinates and descriptions"
    )
    
    # AI Reasoning
    analysis_summary = models.TextField(help_text="AI generated summary of security risks")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Audit for Request {self.request.id}"
