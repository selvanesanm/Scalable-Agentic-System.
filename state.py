state = {
    "last_request": None,
    "last_tool": None,
    "last_result": None
}


def update_state(request, tool, result):
    state["last_request"] = request
    state["last_tool"] = tool
    state["last_result"] = result


def get_state():
    return state
