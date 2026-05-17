from app.mcp.client import MCPClient
from app.core.logger import logger

client = MCPClient()

def dispatch(service: str, payload: dict):
    logger.info(f"Dispatching to MCP service: {service}")
    return client.call(service, payload)