from router import route_request


def main():
    print("======================================")
    print(" Datazoic Scalable Agentic System")
    print("======================================")
    print("Type 'exit' to stop.")
    print()

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            answer = route_request(user_input)
            print("Agent:", answer)
        except Exception as error:
            print("Agent: Something went wrong.")
            print("Error:", error)

        print()


if __name__ == "__main__":
    main()
