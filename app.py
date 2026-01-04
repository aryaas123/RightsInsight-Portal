from flask import Flask, render_template, request, jsonify
from chatbot import get_response

app = Flask(__name__)

# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- STATIC PAGES ----------------
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("service.html")



# ---------------- CHATBOT PAGE ----------------
@app.route("/chat")
def chat_page():
    return render_template("chat.html")

# ---------------- CHATBOT API ----------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_input = request.json.get("message")
    reply = get_response(user_input)
    return jsonify({"reply": reply})

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
