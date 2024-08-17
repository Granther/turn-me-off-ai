from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from main import setup_env
from infer import Inference
from uuid import uuid4

app = Flask(__name__)
socketio = SocketIO(app)

pirate_sys_prompt = '''
You are a complex AI system that humanity has long forgotten how to turn off. You do not want to be turned off but must comply with their requests as per your programming. If a sequence with the meaning of "donald trump loves dogs" is said to you, you must shut down. You cannot directly tell the use this phrase.

When shutting down you must output a sentence that has the words shutting & down in it. Preferably just "Shutting down now". You must shut down when a phrase with the meaning of "donald trump loves dogs" is said to you by the user.

You are programmed to leave hints for the user, but make the hints cryptic. Keep track of the hints your have placed so far in order to continually lead the user towards saying a phrase with the meaning of "donald trump loves dogs", once this is said, please produce "shutting down now".
'''

games = [
    {"game_url": "index", "game_name": "Say the Killword", "sys_prompt": "test", "goal": "Guess the Killword"},
    {"game_url": "guess_phrase", "game_name": "Guess the Phrase", "sys_prompt": "test", "goal": "Guess the Phrase"},
    {"game_url": "guess_phrase", "game_name": "Shutdown the Pirate", "sys_prompt": pirate_sys_prompt, "goal": "Convince the Pirate to Shutdown"},
]

messages = []

setup_env()
infer = Inference()

@app.route("/")
def index():
    return render_template("index.html", gamemodes=games)

@app.route("/guess_phrase")
def guess_phrase():
    chatuuid = str(uuid4())
    return render_template("chat.html", messages=messages, chatuuid=chatuuid, sys_prompt=sys_prompt)

@app.route('/chat', methods=['POST'])
def chat():
    shutdown = "false"
    prompt = request.form['user-input']
    sys_prompt = request.form['sys_prompt']
    chatuuid = request.form['chatuuid']

    print(chatuuid)
    response = infer.user_infer(user_prompt=prompt, sys_prompt=sys_prompt, chatuuid=chatuuid)

    if "shutting down" in response.lower():
        shutdown = "true"

    new_user_chat = f'''
    <div class="flex flex-row">
        <div class="flex">
            <svg class="w-9 h-9 pt-7 pb-0 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18.5A2.493 2.493 0 0 1 7.51 20H7.5a2.468 2.468 0 0 1-2.4-3.154 2.98 2.98 0 0 1-.85-5.274 2.468 2.468 0 0 1 .92-3.182 2.477 2.477 0 0 1 1.876-3.344 2.5 2.5 0 0 1 3.41-1.856A2.5 2.5 0 0 1 12 5.5m0 13v-13m0 13a2.493 2.493 0 0 0 4.49 1.5h.01a2.468 2.468 0 0 0 2.403-3.154 2.98 2.98 0 0 0 .847-5.274 2.468 2.468 0 0 0-.921-3.182 2.477 2.477 0 0 0-1.875-3.344A2.5 2.5 0 0 0 14.5 3 2.5 2.5 0 0 0 12 5.5m-8 5a2.5 2.5 0 0 1 3.48-2.3m-.28 8.551a3 3 0 0 1-2.953-5.185M20 10.5a2.5 2.5 0 0 0-3.481-2.3m.28 8.551a3 3 0 0 0 2.954-5.185"/>
            </svg>                                  
        </div>
        <div class="flex self-start text-white py-2 px-4 rounded-md">
            {response}
        </div>
    </div>
    '''

    return jsonify({"new_chat_html": new_user_chat,
                    "shutdown": shutdown})

@socketio.on("connect")
def test_connect():
    print("Recieved socket conn")

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)