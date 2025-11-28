from rest_framework import serializers
from .models import AuditReport

class AuditReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditReport
        fields = [
            'id', 
            'request', 
            'has_ground_level_access', 
            'has_concealment', 
            'has_glass_proximity', 
            'has_hardware_weakness', 
            'vulnerabilities', 
            'analysis_summary', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'request']
