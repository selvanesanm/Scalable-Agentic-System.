from tool_registry import tools
from config import MAX_TOOLS_FOR_AGENT

# Common words that would otherwise match almost every tool description
# ("the", "a", "for", ...) and drown out the real keywords. This is a
# cheap fix for the naive keyword matcher below; it does not change
# the fact that at real scale (hundreds/thousands of tools) this
# whole function would be replaced by embeddings + vector search, see
# DESIGN.md section 13.
STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "to", "of",
    "for", "on", "in", "at", "my", "me", "and", "or", "it", "its",
    "this", "that", "what", "who", "how", "do", "does", "did",
}


def search_tools(user_input):
    text = user_input.lower()
    words = {word for word in text.split() if word not in STOPWORDS}

    results = []

    for tool in tools:
        score = 0

        # Category match
        if tool["category"] in text:
            score += 3

        # Description match
        for word in words:
            if len(word) > 2 and word in tool["description"].lower():
                score += 1

        if score > 0:
            results.append((score, tool))

    # Highest score first
    results.sort(key=lambda item: item[0], reverse=True)

    return [tool for score, tool in results[:MAX_TOOLS_FOR_AGENT]]
