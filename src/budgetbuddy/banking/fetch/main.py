from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext

CONF_PATH = "/Users/mannes/setting_files/bunq_api_context.conf"

api_context = ApiContext.restore(CONF_PATH)
BunqContext.load_api_context(api_context)
