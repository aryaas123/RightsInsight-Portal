from flask import Flask, render_template, request, jsonify
from chatbot import get_response
from complaint_ai import generate_complaint


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

# ---------------- EDUCATION PAGE ----------------
@app.route("/education")
def education():
    return render_template("education.html")

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

# ---------------- COMPLAINT MODULE ----------------
@app.route("/complaint")
def complaint_page():
    return render_template("complaint.html")

@app.route("/generate-complaint", methods=["POST"])
def generate():
    data = request.json
    complaint = generate_complaint(data["category"], data["incident"])
    return jsonify({"complaint": complaint})


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
