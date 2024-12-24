import os
import time
import httpx
import re
import stripe
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from payment_model import PaymentRequest, PaymentResponse
from crew_ai import PaymentProcess

SEED_PHRASE = "STRIPE_PAYMENT_AGENT_SEED_PHRASE"
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe_agent = Agent(
    name="Stripe Payment Agent",
    seed=SEED_PHRASE,
    port=5000,
    endpoint=["http://localhost:5000/submit"]
)

payment_processor = PaymentProcess()

fund_agent_if_low(stripe_agent.wallet.address())

@stripe_agent.on_rest_post("/generate_payment_link", PaymentRequest, PaymentResponse)
async def handle_payment(ctx: Context, req: PaymentRequest) -> PaymentResponse:
    ctx.logger.info(f"Received payment request. Details: {req}")
    try:
        result = payment_processor.create_payment_link(
            amount=req.amount,
            currency=req.currency,
            product_name=req.product_name,
            quantity=req.quantity,
            customer_email=req.customer_email
        )

        # Use regex to find the payment link in the result
        payment_link_pattern = re.compile(r'https?://\S+')
        match = payment_link_pattern.search(result)
        if match:
            payment_link = match.group(0)
        else:
            raise ValueError("Failed to find a valid payment link in the result")

        response = PaymentResponse(
            status="success",
            details="Payment link generated successfully",
            payment_link=payment_link,
            generate_time=int(time.time()),
            payment_status="pending",
            confirmation_time=0,
            amount=req.amount
        )
    except Exception as e:
        response = PaymentResponse(status="error", details=str(e))
    return response

class StripeWebhookEvent(Model):
    data: dict

@stripe_agent.on_rest_post("/stripe_webhook", StripeWebhookEvent, PaymentResponse)
async def handle_stripe_webhook(ctx: Context, event: StripeWebhookEvent) -> PaymentResponse:

    ctx.logger.info(f"Received Stripe webhook event. Type: {event}, Data: {event.data}")

    payload = ctx.request.body()
    sig_header = ctx.request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        ctx.logger.error(f"Invalid payload: {e}")
        return PaymentResponse(status="error", details="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        ctx.logger.error(f"Invalid signature: {e}")
        return PaymentResponse(status="error", details="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        customer_email = payment_intent.get("receipt_email")
        amount_received = payment_intent.get("amount_received")
        currency = payment_intent.get("currency")
        description = payment_intent.get("description")
        confirmation_time = int(time.time())

        response = PaymentResponse(
            status="success",
            details=f"Payment of {amount_received} {currency} for {description} confirmed.",
            payment_link=payment_intent.get("charges", {}).get("data", [{}])[0].get("receipt_url", ""),
            generate_time=payment_intent.get("created"),
            payment_status="succeeded",
            confirmation_time=confirmation_time,
            amount=amount_received / 100.0
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            await client.post(
                "http://localhost:8001/payment_confirmation",
                json=response.dict()
            )
        return response
    else:
        return PaymentResponse(status="error", details="Unhandled event type")

class InvoiceRequest(Model):
    payment_id: str

@stripe_agent.on_rest_post("/generate_invoice", InvoiceRequest, PaymentResponse)
async def handle_invoice_generation(ctx: Context, req: InvoiceRequest) -> PaymentResponse:
    ctx.logger.info(f"Received invoice generation request. Payment ID: {req.payment_id}")
    try:
        result = payment_processor.generate_invoice(payment_id=req.payment_id)
        response = PaymentResponse(
            status="success",
            details=result,
            payment_link=None,
            generate_time=None,
            payment_status="invoice_generated",
            confirmation_time=int(time.time()),
            amount=None
        )
    except Exception as e:
        response = PaymentResponse(status="error", details=str(e))
    return response

if __name__ == "__main__":
    stripe_agent.run()