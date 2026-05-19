from app.core.logger import logger
from app.mcp.client import MCPClient


client = MCPClient()


def dispatch(service: str, payload: dict):
    if service not in {"taxi", "afisha"}:
        logger.info("MCP dispatch skipped: service is unknown")
        return client.call("unknown", payload)

    logger.info("Dispatching to MCP service: %s", service)
    return client.call(service, payload)
