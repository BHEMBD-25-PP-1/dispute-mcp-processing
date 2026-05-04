def build_response(parsed, nlu, mcp_data):
    return {
        "status": "resolved",
        "service": nlu.get("service"),
        "parsed": parsed,
        "data": mcp_data
    }