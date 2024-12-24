import os
import httpx
from uagents import Agent, Context, Field, Model
from payment_model import PaymentRequest, PaymentResponse

user_agent = Agent(
    name="User Agent",
    seed="USER_AGENT_SEED_PHRASE",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

class UserRequest(Model):
    amount: float
    product_name: str
    quantity: int
    email: str

class UserResponse(Model):
    status: str = Field(
        description="Status of the user request.",
        choices=["success", "pending", "error"]
    )
    details: str = Field(description="Additional details about the request status.")
    payment_link: str = Field(description="URL of the payment link.")

class InvoiceRequest(Model):
    payment_id: str

class InvoiceResponse(Model):
    status: str
    details: str

@user_agent.on_rest_post("/create_payment", UserRequest, UserResponse)
async def handle_user_request(ctx: Context, req: UserRequest) -> UserResponse:
    ctx.logger.info(f"Received user request. Details: {req}")

    payment_request = PaymentRequest(
        amount=req.amount,
        currency="USD",
        product_name=req.product_name,
        quantity=req.quantity,
        customer_email=req.email
    )
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:5000/generate_payment_link",
                json=payment_request.dict()
            )
            response_data = response.json()

            return UserResponse(status=response_data["status"], details=response_data["details"], payment_link=response_data["payment_link"])
    except Exception as e:
        return UserResponse(status="error", details=str(e))

@user_agent.on_rest_post("/generate_invoice", InvoiceRequest, InvoiceResponse)
async def handle_invoice_request(ctx: Context, req: InvoiceRequest) -> InvoiceResponse:
    ctx.logger.info(f"Received invoice generation request. Payment ID: {req.payment_id}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:5000/generate_invoice",
                json=req.dict()
            )
            response_data = response.json()
            return InvoiceResponse(status=response_data["status"], details=response_data["details"])
    except Exception as e:
        return InvoiceResponse(status="error", details=str(e))

@user_agent.on_rest_post("/payment_confirmation", PaymentResponse, UserResponse)
async def handle_payment_confirmation(ctx: Context, resp: PaymentResponse) -> UserResponse:
    ctx.logger.info(f"Received payment confirmation. Details: {resp}")
    return UserResponse(status=resp.status, details=resp.details)

if __name__ == "__main__":
    user_agent.run()