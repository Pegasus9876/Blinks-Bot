import time
from src.intent_recognition import classify_intent
from src.entities import parse_intent

def rick_roll_lyrics():
    lyrics = "Never gonna give you up, never gonna let you down".split()
    for word in lyrics:
        print(word, end=" ", flush=True)
        time.sleep(0.40)  
    print("\n")

def main():
    print("Blink Bot CLI is running. Type 'exit' to quit.\n")

    while True:
        query = input("Enter your query: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("\Incoming!")
            rick_roll_lyrics()
            break

        intent = classify_intent(query)
        if not intent:
            print("Sorry, I could not determine your intent.\n")
            continue

        result = parse_intent(intent, query)
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
