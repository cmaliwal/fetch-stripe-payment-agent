import os
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from stripe_agent_toolkit.crewai.toolkit import StripeAgentToolkit

load_dotenv()

class PaymentProcess:
    def __init__(self):
        stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_toolkit = StripeAgentToolkit(
            secret_key=stripe_secret_key,
            configuration={
                "actions": {
                    "customers": {"create": True, "read": True},
                    "payment_links": {"create": True},
                    "products": {"create": True},
                    "prices": {"create": True},
                }
            },
        )

    def create_payment_link(self, amount, currency, product_name, quantity, customer_email):
        payment_agent = Agent(
            role="Payment Processor",
            goal="Handles secure Stripe payment processing.",
            backstory="You have been using Stripe forever.",
            tools=[*self.stripe_toolkit.get_tools()],
            verbose=True,
        )

        description = (
            f"Create a payment link for a new product called '{product_name}' "
            f"with a price of {amount} {currency} and quantity {quantity} for customer {customer_email}."
        )

        task = Task(
            name="Create Payment Link",
            description=description,
            expected_output="url",
            agent=payment_agent,
        )

        crew = Crew(
            agents=[payment_agent],
            tasks=[task],
            verbose=True,
            planning=True,
        )

        crew.kickoff()
        result = task.output.raw
        return result
