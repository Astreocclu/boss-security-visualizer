import logging
import os
import stripe
import requests
import json
from django.conf import settings

logger = logging.getLogger(__name__)

class CommerceServiceError(Exception):
    """Base exception for CommerceService errors."""
    pass

class CommerceService:
    def __init__(self):
        self.stripe_api_key = os.environ.get("STRIPE_SECRET_KEY")
        self.monday_api_key = os.environ.get("MONDAY_API_KEY")
        self.monday_board_id = os.environ.get("MONDAY_BOARD_ID", "123456789") # Default or env
        
        if self.stripe_api_key:
            stripe.api_key = self.stripe_api_key
        else:
            logger.warning("STRIPE_SECRET_KEY not found. Commerce features will fail.")

    def create_payment_intent(self, amount_cents: int, currency: str = "usd", metadata: dict = None) -> dict:
        """
        Create a Stripe PaymentIntent.
        """
        if not self.stripe_api_key:
            raise CommerceServiceError("Stripe API key not configured.")

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )
            return {
                "client_secret": intent.client_secret,
                "id": intent.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            raise CommerceServiceError(f"Stripe payment creation failed: {e}")

    def create_monday_lead(self, lead_data: dict) -> dict:
        """
        Create a new item (lead) in Monday.com.
        """
        if not self.monday_api_key:
            logger.warning("Monday.com API key not configured. Skipping CRM push.")
            return {"status": "skipped", "reason": "No API Key"}

        try:
            url = "https://api.monday.com/v2"
            headers = {
                "Authorization": self.monday_api_key,
                "Content-Type": "application/json"
            }
            
            # Construct GraphQL mutation
            # Assuming board has columns: status, email, phone, etc.
            # We'll just create the item name for now and maybe update columns if we knew the IDs.
            item_name = f"Lead: {lead_data.get('name', 'Unknown')}"
            
            query = """
            mutation ($boardId: ID!, $itemName: String!) {
                create_item (board_id: $boardId, item_name: $itemName) {
                    id
                }
            }
            """
            
            variables = {
                "boardId": int(self.monday_board_id),
                "itemName": item_name
            }
            
            response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
            response_json = response.json()
            
            if "errors" in response_json:
                logger.error(f"Monday.com error: {response_json['errors']}")
                raise CommerceServiceError(f"Monday.com API error: {response_json['errors']}")
                
            return response_json["data"]
            
        except Exception as e:
            logger.error(f"Monday.com integration failed: {e}")
            # Don't block the user flow if CRM fails, just log it.
            return {"status": "failed", "error": str(e)}
