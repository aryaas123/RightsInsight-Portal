import random
from nlp_utils import preprocess, load_intents
from difflib import SequenceMatcher

intents = load_intents()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_response(user_input):
    words = preprocess(user_input)
    for intent in intents:
        for pattern in intent["patterns"]:
            pattern_words = preprocess(pattern)
            # calculate highest similarity ratio
            match_ratio = max(similar(word, w) for word in words for w in pattern_words)
            if match_ratio > 0.7:
                return intent["response"]
    return "Sorry, I do not understand your query."

# Test in terminal
if __name__ == "__main__":
    print("RightsInsight NLP Chatbot (type 'quit' to exit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        response = get_response(user_input)
        print("Bot:", response)
