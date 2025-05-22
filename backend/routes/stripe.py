from fastapi import APIRouter, Body
import stripe, os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
router = APIRouter()

@router.post("/checkout")
def create_checkout(price_id: str = Body(...)):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://yourapp.com/success",
        cancel_url="https://yourapp.com/cancel"
    )
    return {"checkout_url": session.url}
