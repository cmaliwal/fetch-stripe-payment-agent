# Fetch Stripe Payment Agent

A system for payment processing and invoice generation using Stripe, uAgents, and CrewAI.

![image](https://github.com/user-attachments/assets/10574242-3260-4113-9b2a-9c7b314bb7c4)


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

### Running the Agents

1. Log in to your [Agentverse account](https://agentverse.ai/).
2. Run the user and Stripe agents individually by executing the following command:
   ```sh
      python <agent>.py
   ```
   Replace <agent> with the specific agent name (e.g., user_agent.py or stripe_agent.py).
3. In the respective consoles, click the "Agent Inspector" links to open the Agent Inspector window for each agent.
4. Click the "Connect" button in the Agent Inspector.
5. In the opened window, select "Mailbox" and follow the instructions to configure your agents by adding the following lines to their settings:
   ```txt
    mailbox=True,
    endpoint=['https://agentverse.ai/v1/submit']
   ```
6. Start the Bureau to re-run both the Stripe Payment Agent and the User Agent:
    ```sh
    poetry run python run_agents.py
    ```

7. Expose the local server using ngrok:
    ```sh
    ngrok http 8000
    ```

8. Update your Stripe webhook settings to point to the ngrok URL (e.g., `https://<ngrok-id>.ngrok.io/webhook`).

### Running the Flask Server for Webhooks

1. Start the Flask server for handling Stripe webhooks:
    ```sh
    poetry run python webhook.py
    ```

### Creating a Payment Link

You can create a payment link by sending a POST request to the User Agent's `/create_payment` endpoint. Here is an example using `curl`:

```sh
curl -X POST http://localhost:8000/create_payment \
     -H "Content-Type: application/json" \
     -d '{
           "amount": 100.0,
           "product_name": "Sample Product",
           "quantity": 1,
           "email": "customer@example.com",
           "name": "Customer Name"
         }'
```