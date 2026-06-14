import os
import uuid
import logging
from typing import Dict, Any, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Try importing stripe. If not present, run in mock bypass.
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_API_KEY", "")
    HAS_STRIPE = bool(stripe.api_key)
except ImportError:
    HAS_STRIPE = False
    logger.warning("stripe-python is not installed. Billing will run in mock simulation mode.")

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PLAN_LIMITS = {
    "free": 10,
    "pro": 500,
    "team": 2000,
    "enterprise": 999999
}

class StripeService:
    @staticmethod
    def create_checkout_session(user_id: str, email: str, plan: str, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe checkout session URL for upgrading plans.
        """
        if not HAS_STRIPE:
            logger.info(f"Bypassing checkout. Creating mock checkout URL for user {user_id} upgrading to {plan}")
            # Mock success redirection
            return f"{success_url}?session_id=mock_session_{uuid.uuid4().hex[:8]}&plan={plan}"

        try:
            # Map standard price IDs from environment
            price_ids = {
                "pro": os.getenv("STRIPE_PRICE_PRO", "price_pro_default"),
                "team": os.getenv("STRIPE_PRICE_TEAM", "price_team_default"),
            }
            
            price_id = price_ids.get(plan)
            if not price_id:
                raise ValueError(f"Invalid plan selected for checkout: {plan}")

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                customer_email=email,
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={"user_id": user_id, "plan": plan}
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe checkout session failed: {str(e)}. Falling back to mock URL.")
            return f"{success_url}?session_id=mock_session_fallback&plan={plan}"

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> str:
        """
        Creates a Stripe billing portal redirection URL.
        """
        if not HAS_STRIPE or not customer_id or customer_id.startswith("mock_"):
            logger.info("Bypassing customer billing portal. Returning mock portal URL.")
            return return_url

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session.url
        except Exception as e:
            logger.error(f"Stripe portal session failed: {str(e)}")
            return return_url

    @staticmethod
    async def process_webhook(payload: bytes, sig_header: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Processes Stripe subscription webhook event updates.
        """
        if not HAS_STRIPE:
            logger.warning("Stripe webhook received but stripe is unconfigured.")
            return {"status": "unconfigured"}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise ValueError("Invalid signature")

        event_type = event.get("type")
        data_object = event.get("data", {}).get("object", {})
        
        logger.info(f"Received Stripe webhook event: {event_type}")

        # Import User model inside method
        from app.models.user import User

        if event_type == "checkout.session.completed":
            user_id = data_object.get("metadata", {}).get("user_id")
            plan = data_object.get("metadata", {}).get("plan", "free")
            customer_id = data_object.get("customer")
            subscription_id = data_object.get("subscription")
            
            if user_id:
                user_uuid = uuid.UUID(user_id)
                result = await db.execute(select(User).filter(User.id == user_uuid))
                user = result.scalars().first()
                if user:
                    user.stripe_customer_id = customer_id
                    user.subscription_id = subscription_id
                    user.billing_plan = plan
                    user.billing_status = "active"
                    user.monthly_analyses_limit = PLAN_LIMITS.get(plan, 10)
                    await db.commit()
                    logger.info(f"User {user_id} upgraded to {plan} via stripe webhook.")

        elif event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
            subscription_id = data_object.get("id")
            status = data_object.get("status")
            customer_id = data_object.get("customer")
            
            result = await db.execute(select(User).filter(User.stripe_customer_id == customer_id))
            user = result.scalars().first()
            if user:
                if event_type == "customer.subscription.deleted" or status in ["canceled", "unpaid"]:
                    user.billing_plan = "free"
                    user.billing_status = "canceled"
                    user.monthly_analyses_limit = 10
                else:
                    user.billing_status = status
                await db.commit()
                logger.info(f"Subscription {subscription_id} updated: status {status}")

        return {"status": "processed", "event": event_type}
