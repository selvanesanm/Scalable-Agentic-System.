from config import MAX_RETRIES


def run_with_retry(function, tool_name, parameters):
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            return function(tool_name, parameters)
        except Exception as error:
            last_error = error

    return "Tool failed after retries: " + str(last_error)
