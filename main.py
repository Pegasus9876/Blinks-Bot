from src.intent_recognition import classify_intent
from src.entities import parse_intent

def main():
    print("Blink Bot CLI is running. Type 'exit' to quit.\n")

    while True:
        query = input("Enter your query: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Step 1: classify the intent (handles static + Pinecone similarity)
        intent = classify_intent(query)
        if not intent:
            print("Sorry, I could not determine your intent.\n")
            continue

        # Step 2: parse details for that intent
        result = parse_intent(intent, query)

        # Step 3: output result
        if result:
            print(f"\nDetected intent: {intent}")
            print("Result:", result)
            if "url" in result:
                print("Link:", result["url"])
        else:
            print(f"Detected intent: {intent}, but could not extract details.\n")

        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
