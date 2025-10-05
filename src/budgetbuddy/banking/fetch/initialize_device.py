import os
from dotenv import load_dotenv

from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType

# load_dotenv()

api_context = ApiContext.create(
    ApiEnvironmentType.PRODUCTION,
    os.getenv("BUNQ_KEY_PROD"),
    "macbook_mannes"
)
#
# # Save the API context to a file for future use
api_context.save("bunq_api_context.conf")

# Load the API context into the SDK
# BunqContext.load_api_context(api_context)


# Save API context
# api_context.save("bunq_api_context.conf")

# Restore API context
api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)
context = BunqContext.api_context()

