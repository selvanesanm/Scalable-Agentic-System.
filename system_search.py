from tool_registry import tools
from state import get_state


def system_search(question):
    text = question.lower()

    if "invoice" in text and "tool" in text:
        names = [
            tool["name"]
            for tool in tools
            if tool["category"] == "invoice"
        ]

        return "Invoice tools: " + ", ".join(names)

    if "status" in text:
        current_state = get_state()

        if current_state["last_tool"] is None:
            return "There is no previous request."

        return (
            "Last request used "
            + current_state["last_tool"]
            + " and the result was: "
            + str(current_state["last_result"])
        )

    return "No system information found."
