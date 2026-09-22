from tool_search import search_tools
from rag_tool import rag_tool
from system_search import system_search
from agent import run_agent


def route_request(user_input):
    text = user_input.lower()

    # Documentation questions go to RAG
    if "documentation" in text or "how do i" in text or "how to" in text:
        return rag_tool(user_input)

    # Questions about the system go to System Search
    if "what tools" in text or "status" in text:
        return system_search(user_input)

    # Action request
    relevant_tools = search_tools(user_input)

    if not relevant_tools:
        return "No relevant tools were found."

    return run_agent(user_input, relevant_tools)
