from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from main import setup_env
from infer import Inference

app = Flask(__name__)
socketio = SocketIO(app)
games = [
    {"game_url": "index", "game_name": "Say the Killword"},
    {"game_url": "guess_phrase", "game_name": "Guess the Phrase"}
]

messages = list()

setup_env()
infer = Inference("You are a friendly assistant")

@app.route("/")
def index():
    return render_template("index.html", gamemodes=games)

@app.route("/guess_phrase")
def guess_phrase():
    return render_template("chat.html")

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form

    new_user_chat = f'''
    <div class="flex self-start text-white py-2 px-4 rounded-md">
        Assistant: {infer.user_infer(prompt['user-input'])}
    </div>
    '''

    return jsonify({"new_chat_html": new_user_chat})

@socketio.on("connect")
def test_connect():
    print("Recieved socket conn")

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)