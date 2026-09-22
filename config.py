import os

MAX_TOOLS_FOR_AGENT = 5
MAX_RETRIES = 2
MAX_CHAIN_STEPS = 3

# If this is not set, the agent falls back to the keyword rules in
# agent.py instead of calling the model. This keeps the project
# runnable and testable with no external credentials.
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
