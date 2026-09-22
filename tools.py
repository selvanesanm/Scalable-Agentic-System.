def create_invoice(parameters):
    customer = parameters["customer"]
    amount = parameters["amount"]

    return {
        "invoice_id": "INV1001",
        "message": f"Invoice created for {customer} for ${amount}."
    }


def send_invoice(parameters):
    customer = parameters["customer"]
    amount = parameters["amount"]
    invoice_id = parameters.get("invoice_id")

    if invoice_id:
        return {
            "message": f"Invoice {invoice_id} of ${amount} sent to {customer}."
        }

    return {
        "message": f"Invoice of ${amount} sent to {customer}."
    }


def get_sales_report(parameters):
    return {
        "message": "Total sales volume for last month is $10,500."
    }


def get_dispute(parameters):
    user_id = parameters["user_id"]

    return {
        "message": f"No open dispute found for {user_id}."
    }


TOOL_HANDLERS = {
    "create_invoice": create_invoice,
    "send_invoice": send_invoice,
    "get_sales_report": get_sales_report,
    "get_dispute": get_dispute,
}


def simulate_call(tool_name, parameters):
    """Stand-in for the tools that don't need custom demo logic.

    In production this branch would not exist: every tool in the
    registry would be backed by a real HTTP client call (PayPal API,
    internal service, etc). For this assignment only the four tools
    used in the example scenarios have real mock behaviour above; the
    rest of the registry exists to demonstrate that search/routing
    still works once there are dozens of tools, and returns a
    simulated response so the full flow (select -> validate -> execute
    -> state) can still be exercised end to end.
    """
    return {
        "message": f"Simulated call to '{tool_name}' with {parameters}."
    }


def execute_tool(tool_name, parameters):
    from tool_registry import tools as registry

    handler = TOOL_HANDLERS.get(tool_name)

    if handler:
        return handler(parameters)

    known_names = {tool["name"] for tool in registry}

    if tool_name in known_names:
        return simulate_call(tool_name, parameters)

    raise ValueError("Tool not found")
