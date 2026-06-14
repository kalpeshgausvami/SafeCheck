from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/billing", tags=["Billing & Subscriptions"])

@router.post("/checkout", status_code=status.HTTP_200_OK)
async def create_checkout(
    plan: str,
    success_url: str,
    cancel_url: str,
    current_user: User = Depends(get_current_user)
):
    if plan not in ["pro", "team"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid billing plan selection. Choose 'pro' or 'team'."
        )
    
    try:
        checkout_url = StripeService.create_checkout_session(
            user_id=str(current_user.id),
            email=current_user.email,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return {"checkout_url": checkout_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate billing session: {str(e)}"
        )

@router.post("/portal", status_code=status.HTTP_200_OK)
async def create_portal(
    return_url: str,
    current_user: User = Depends(get_current_user)
):
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active billing profile found. Please subscribe first."
        )
    
    try:
        portal_url = StripeService.create_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=return_url
        )
        return {"portal_url": portal_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load billing portal: {str(e)}"
        )

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
        
    try:
        res = await StripeService.process_webhook(payload, sig_header, db)
        return res
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failure: {str(e)}"
        )
