import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = word_tokenize(text.lower())  # uses 'punkt'
    return [w for w in tokens if w.isalpha() and w not in stop_words]

def load_intents():
    import json
    with open("intents.json") as f:
        return json.load(f)["intents"]
