import os

try:
    import anthropic
except ImportError:
    anthropic = None

from config import ANTHROPIC_MODEL
from state import get_state


def is_available():
    """True if the Anthropic SDK is installed and an API key is set.

    The rest of the agent is written so it works either way:
    - With a key, choose_tool_call() below asks the model to pick a
      tool from the narrowed list and fill in its parameters.
    - Without a key, agent.py falls back to simple keyword rules, so
      the project can still be run and tested offline.
    """
    return anthropic is not None and bool(os.environ.get("ANTHROPIC_API_KEY"))


def _tool_schema(tool):
    # Every parameter is treated as a required string. That is enough
    # for this assignment. A production version would pull real types
    # (string, number, enum, ...) from the tool registry.
    properties = {name: {"type": "string"} for name in tool["parameters"]}

    return {
        "name": tool["name"],
        "description": tool["description"],
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": tool["parameters"],
        },
    }


def choose_tool_call(user_input, relevant_tools):
    """Ask the model to pick one tool from relevant_tools and build its
    parameters. Returns (tool_name, parameters), or (None, None) if the
    model is not available or did not call a tool.

    relevant_tools is expected to already be the narrowed list from
    tool_search.py, not the full registry. This is the point of the
    whole design: the model only ever sees a handful of candidates,
    never all 500+ tools at once.
    """
    if not is_available() or not relevant_tools:
        return None, None

    client = anthropic.Anthropic()
    tool_schemas = [_tool_schema(tool) for tool in relevant_tools]

    system_prompt = (
        "You are an operations assistant for a payments platform. "
        "Pick exactly one tool from the tools you have been given and "
        "fill in its parameters to fulfil the user's request. Do not "
        "invent a tool that was not given to you. If a value is not "
        "stated by the user, make a reasonable assumption."
    )

    current_state = get_state()
    if current_state.get("last_tool"):
        system_prompt += (
            f" For context, the previous step in this conversation used "
            f"'{current_state['last_tool']}' and returned: "
            f"{current_state['last_result']}."
        )

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=500,
        system=system_prompt,
        tools=tool_schemas,
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": user_input}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.name, block.input

    return None, None
