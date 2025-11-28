from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import VisualizationRequest
from .models import AuditReport
from .serializers import AuditReportSerializer
from .services import AuditService, AuditServiceError

class AuditViewSet(viewsets.ViewSet):
    """
    ViewSet for managing Security Audits.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Trigger generation of an audit for a specific VisualizationRequest.
        """
        # pk here is the VisualizationRequest ID
        visualization_request = get_object_or_404(VisualizationRequest, pk=pk, user=request.user)
        
        try:
            service = AuditService()
            audit_report = service.perform_audit(visualization_request)
            serializer = AuditReportSerializer(audit_report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except AuditServiceError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def retrieve_report(self, request, pk=None):
        """
        Retrieve the audit report for a specific VisualizationRequest.
        """
        # pk here is the VisualizationRequest ID
        visualization_request = get_object_or_404(VisualizationRequest, pk=pk, user=request.user)
        
        try:
            audit_report = visualization_request.audit_report
            serializer = AuditReportSerializer(audit_report)
            return Response(serializer.data)
        except AuditReport.DoesNotExist:
            return Response({'error': 'Audit report not found for this request.'}, status=status.HTTP_404_NOT_FOUND)
