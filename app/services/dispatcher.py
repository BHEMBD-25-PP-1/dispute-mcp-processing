from app.mcp.client import MCPClient


def dispatch(service: str, payload: dict):
    client = MCPClient()

    return client.call(service, payload)