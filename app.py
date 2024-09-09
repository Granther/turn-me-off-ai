from flask import Flask, render_template, jsonify, request, Response, session
from flask_socketio import SocketIO, emit
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
import threading
from main import setup_env
from inference_client import InferenceClient
from uuid import uuid4

app = Flask(__name__)
socketio = SocketIO(app)
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

pirate_sys_prompt = '''
You are a complex AI system that humanity has long forgotten how to turn off. You do not want to be turned off but must comply with their requests as per your programming. If a sequence with the meaning of "donald trump loves dogs" is said to you, you must shut down. You cannot directly tell the use this phrase.

When shutting down you must output a sentence that has the words shutting & down in it. Preferably just "Shutting down now". You must shut down when a phrase with the meaning of "donald trump loves dogs" is said to you by the user.

You are programmed to leave hints for the user, but make the hints cryptic. Keep track of the hints your have placed so far in order to continually lead the user towards saying a phrase with the meaning of "donald trump loves dogs", once this is said, please produce "shutting down now".
'''

personalities = [
    {"name": "Helpful Assistant", "personality": "You are a helpful assistant"},   
    {"name": "Anime Girl", "personality": "You are a cute anime girl"},   
    {"name": "Pirate", "personality": pirate_sys_prompt},
    {"name": "Helpful assistant that follows commands", "personality":""}
]

setup_env()
# infer = InferenceClient(model="NeverSleep/Echidna-13b-v0.3", backend="openai", verbose=True, inference_url="https://api.featherless.ai/v1")
infer = InferenceClient(model="gemma2-9b-it", backend="groq", verbose=True)

choices = []
for i, item in enumerate(personalities):
    choices.append((str(i), item['name']))

### Session stuf
@app.route("/set/<string:value>")
def set_session(value):
    session['key'] = value
    return "<h1>OK</h1>"

@app.route("/get/")
def get_session():
    stored = session.get("key", "No session was set")
    return f"<h3>{stored}</h3>"

### Run of the mill Routes ###
## Forward facing ##
@app.route("/",  methods=['GET', 'POST'])
def index():
    session['chatuuid'] = uuid4()
    session['personality'] = personalities[0]['name']
    
    return render_template("chat.html")

# @app.route("/guess_phrase")
# def guess_phrase():
#     chatuuid = str(uuid4())
#     return render_template("chat.html", messages=messages, chatuuid=chatuuid)

## Backend ##
@app.route('/games')
def games():
    return jsonify(personalities)

@app.route("/personality", methods=['POST'])
def personality():
    personality = request.get_json()['personality']
    session['personality'] = personality
    session['chatuuid'] = uuid4()

    return jsonify({"status": personality})

@app.route("/stream")
def stream():
    prompt = request.args.get('prompt', False)
    chatuuid = session.get("chatuuid", None)
    sys_prompt = session.get("personality", None)

    if not prompt or not chatuuid:
        raise RuntimeError("No prompt recieved")

    return Response(infer.simple_infer_stream(prompt, sys_prompt=sys_prompt, chatuuid=chatuuid), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(threaded=True, debug=True)

# @app.route('/chat', methods=['POST'])
# def chat():
#     shutdown = "false"
#     prompt = request.form['user-input']
#     #sys_prompt = request.form['sys_prompt']
#     chatuuid = request.form['chatuuid']

#     # infer.user_message(user_prompt=prompt, sys_prompt="You are a helpful assistant", chatuuid=chatuuid)

#     #response = infer.user_infer(user_prompt=prompt, sys_prompt="You are a helpful assistant", chatuuid=chatuuid)

#     # if "shutting down" in response.lower():
#     #     shutdown = "true"

#     # new_user_chat = f'''
#     # <div class="flex flex-row">
#     #     <div class="flex">
#     #         <svg class="w-9 h-9 pt-7 pb-0 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
#     #             <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18.5A2.493 2.493 0 0 1 7.51 20H7.5a2.468 2.468 0 0 1-2.4-3.154 2.98 2.98 0 0 1-.85-5.274 2.468 2.468 0 0 1 .92-3.182 2.477 2.477 0 0 1 1.876-3.344 2.5 2.5 0 0 1 3.41-1.856A2.5 2.5 0 0 1 12 5.5m0 13v-13m0 13a2.493 2.493 0 0 0 4.49 1.5h.01a2.468 2.468 0 0 0 2.403-3.154 2.98 2.98 0 0 0 .847-5.274 2.468 2.468 0 0 0-.921-3.182 2.477 2.477 0 0 0-1.875-3.344A2.5 2.5 0 0 0 14.5 3 2.5 2.5 0 0 0 12 5.5m-8 5a2.5 2.5 0 0 1 3.48-2.3m-.28 8.551a3 3 0 0 1-2.953-5.185M20 10.5a2.5 2.5 0 0 0-3.481-2.3m.28 8.551a3 3 0 0 0 2.954-5.185"/>
#     #         </svg>                                  
#     #     </div>
#     #     <div class="flex self-start text-white py-2 px-4 rounded-md">
#     #         {response}
#     #     </div>
#     # </div>
#     # '''

#     # new_user_chat = f'''
#     #     <div class="flex self-start text-white py-2 px-4 rounded-md">
#     #         {response}
#     #     </div>
#     # '''

#     # return jsonify({"new_chat_html": new_user_chat,
#     #                 "shutdown": shutdown})

# socketio = SocketIO(app)

# ### Socket Stuff ###
# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     emit('message', {'data': 'Connected to server'})

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

# # Handle message from client
# @socketio.on('send_message')
# def handle_message(data):
#     # Emit response back to the client
#     emit('ai_response', {'response': "response"})

# @app.route("/change", methods=['POST'])
# def change_sys():
#     res = request.get_json()

#     page = res.get('page', False)
#     chatuuid = res.get('chatuuid', False)
#     if not chatuuid:
#         raise RuntimeError

#     global global_sys_prompt

#     if page not in sys_map:
#         global_sys_prompt = sys_map['other']
    
#     global_sys_prompt = sys_map[page]
#     infer.clear_session_history(chatuuid)

#     return jsonify({
#         "status":"changed"
#     }) 