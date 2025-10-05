from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext

api_context = ApiContext.restore("bunq_api_context.conf")
BunqContext.load_api_context(api_context)

1