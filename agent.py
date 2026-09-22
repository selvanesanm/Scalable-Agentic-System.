from tools import execute_tool
from state import update_state
from error_handler import run_with_retry
from llm_client import choose_tool_call, is_available
from config import MAX_CHAIN_STEPS


# --------------------------------------------------------------------
# Fallback rules
#
# These are only used when llm_client.is_available() is False (no
# ANTHROPIC_API_KEY set, or the anthropic package is not installed).
# They keep the project runnable with zero external dependencies,
# which is useful for quick local testing and for the automated
# tests in tests/.
# --------------------------------------------------------------------

def choose_tool_fallback(user_input, relevant_tools):
    text = user_input.lower()

    if "dispute" in text:
        return "get_dispute"

    if "sales" in text or "report" in text:
        return "get_sales_report"

    if "invoice" in text:
        # Covers both "create an invoice" and "create an invoice and
        # send it". The second part is handled by maybe_chain() below
        # once this first tool has actually run.
        return "create_invoice"

    if relevant_tools:
        return relevant_tools[0]["name"]

    return None


def build_parameters_fallback(tool_name, user_input):
    text = user_input.lower()

    if tool_name == "get_dispute":
        return {"user_id": "user_123"}

    if tool_name in ["create_invoice", "send_invoice"]:
        amount = 50
        words = text.replace("$", " ").split()

        for word in words:
            if word.isdigit():
                amount = int(word)
                break

        return {
            "customer": "customer_1",
            "amount": amount
        }

    return {}


def normalize_parameters(parameters):
    # The model sometimes returns numbers as strings (tool inputs are
    # JSON, and JSON schema here declares everything as a string).
    # Coerce the ones we know matter for execution.
    parameters = dict(parameters)

    if "amount" in parameters:
        try:
            parameters["amount"] = int(float(parameters["amount"]))
        except (TypeError, ValueError):
            pass

    return parameters


def validate_parameters(tool_name, parameters):
    if tool_name == "get_dispute":
        return bool(parameters.get("user_id"))

    if tool_name in ["create_invoice", "send_invoice"]:
        return (
            bool(parameters.get("customer"))
            and parameters.get("amount", 0) > 0
        )

    return True


# --------------------------------------------------------------------
# Multi-step chaining
#
# Some requests need more than one tool call, e.g. "create an invoice
# and send it". The result of the first call (the invoice_id) becomes
# an input to the second call. This is deliberately kept as a simple,
# explicit lookup rather than letting the model free-wheel through an
# open-ended loop of tool calls: it is predictable, easy to test, and
# it is enough for the kind of two- or three-step flows this system
# needs to support. A more open-ended planner could replace this later
# without touching the rest of the agent.
# --------------------------------------------------------------------

CHAIN_RULES = {
    "create_invoice": {
        "next_tool": "send_invoice",
        "trigger_words": ["send"],
    },
}


def maybe_chain(tool_name, result, user_input):
    rule = CHAIN_RULES.get(tool_name)

    if not rule:
        return None, None

    text = user_input.lower()

    if not any(word in text for word in rule["trigger_words"]):
        return None, None

    next_tool = rule["next_tool"]
    parameters = build_parameters_fallback(next_tool, user_input)

    if isinstance(result, dict) and "invoice_id" in result:
        parameters["invoice_id"] = result["invoice_id"]

    return next_tool, parameters


def run_single_step(tool_name, parameters):
    """Validate and execute one tool call. Returns (result, error) where
    exactly one of the two is None. State is updated by the caller,
    since only it knows the original user_input for this step."""
    parameters = normalize_parameters(parameters)

    if not validate_parameters(tool_name, parameters):
        return None, "Required information is missing."

    result = run_with_retry(execute_tool, tool_name, parameters)

    if isinstance(result, str) and result.startswith("Tool failed"):
        return None, result

    return result, None


def run_agent(user_input, relevant_tools):
    if is_available():
        tool_name, parameters = choose_tool_call(user_input, relevant_tools)
    else:
        tool_name, parameters = None, None

    if tool_name is None:
        tool_name = choose_tool_fallback(user_input, relevant_tools)
        parameters = build_parameters_fallback(tool_name, user_input) if tool_name else {}

    if tool_name is None:
        return "I could not decide which tool to use."

    result, error = run_single_step(tool_name, parameters)

    if error:
        return error

    update_state(user_input, tool_name, result)
    responses = [str(result)]

    # Follow the chain (if any) for up to MAX_CHAIN_STEPS total calls.
    steps_taken = 1
    next_tool, next_parameters = maybe_chain(tool_name, result, user_input)

    while next_tool and steps_taken < MAX_CHAIN_STEPS:
        next_result, next_error = run_single_step(next_tool, next_parameters)

        if next_error:
            responses.append(next_error)
            break

        update_state(user_input, next_tool, next_result)
        responses.append(str(next_result))

        steps_taken += 1
        next_tool, next_parameters = maybe_chain(next_tool, next_result, user_input)

    return " ".join(responses)
