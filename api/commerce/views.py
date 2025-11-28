from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import CommerceService, CommerceServiceError

class CommerceViewSet(viewsets.ViewSet):
    """
    ViewSet for Commerce operations (Payments, CRM).
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        """
        Create a payment intent for the deposit.
        """
        try:
            service = CommerceService()
            # Fixed $500 deposit
            amount = 50000 # cents
            
            # Add metadata
            metadata = {
                "user_id": request.user.id,
                "email": request.user.email,
                "request_id": request.data.get("request_id")
            }
            
            result = service.create_payment_intent(amount, metadata=metadata)
            return Response(result)
            
        except CommerceServiceError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm_deposit(self, request):
        """
        Called after successful payment to trigger CRM update.
        """
        try:
            service = CommerceService()
            lead_data = {
                "name": request.user.username, # Or profile name
                "email": request.user.email,
                "request_id": request.data.get("request_id")
            }
            
            crm_result = service.create_monday_lead(lead_data)
            return Response({"status": "success", "crm_result": crm_result})
            
        except Exception as e:
            # Even if CRM fails, payment was likely success, so return 200 with warning
            return Response({"status": "partial_success", "warning": str(e)})
