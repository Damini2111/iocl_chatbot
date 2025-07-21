from flask import Flask, request, jsonify, send_from_directory
from final import ask_bot  # Correct import

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory("static", "frontjs.html")  # Your HTML file

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    message = data.get("message", "")
    response = ask_bot(message)  # Call chatbot logic
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

