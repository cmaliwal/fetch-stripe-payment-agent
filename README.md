# Fetch Stripe Payment Agent

A system for payment processing and invoice generation using Stripe, uAgents, and CrewAI.

## Overview

This project consists of two main components:
1. **Stripe Payment Agent**: Handles payment link generation and processes Stripe webhook events.
2. **User Agent**: Interacts with the Stripe Payment Agent to create payment links and generate invoices.

## Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- [ngrok](https://ngrok.com/) for exposing local servers to the internet

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd fetch-stripe-payment-agent
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install
    ```

3. Create a `.env` file in the root directory and add the following environment variables:
    ```env
    STRIPE_SECRET_KEY=<your-stripe-secret-key>
    STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret>
    OPENAI_API_KEY=<your-openai-api-key>
    ```

## Usage

### Running the Stripe Payment Agent

1. Start the Stripe Payment Agent:
    ```sh
    poetry run python agent.py
    ```

2. Expose the local server using ngrok:
    ```sh
    ngrok http 5000
    ```

3. Update your Stripe webhook settings to point to the ngrok URL (e.g., `https://<ngrok-id>.ngrok.io/stripe_webhook`).

### Running the User Agent

1. Start the User Agent:
    ```sh
    poetry run python user_agent.py
    ```

### Creating a Payment Link

You can create a payment link by sending a POST request to the User Agent's `/create_payment` endpoint. Here is an example using `curl`:

```sh
curl -X POST http://localhost:8001/create_payment \
     -H "Content-Type: application/json" \
     -d '{
           "amount": 100.0,
           "product_name": "Sample Product",
           "quantity": 1,
           "email": "customer@example.com"
         }'
```

### Generating an Invoice

You can generate an invoice by sending a POST request to the User Agent's /generate_invoice endpoint. Here is an example using curl:
```sh
curl -X POST http://localhost:8001/generate_invoice \
     -H "Content-Type: application/json" \
     -d '{
           "payment_id": "pi_1F8vQX2eZvKYlo2C1l9f7H8z"
         }'
```
