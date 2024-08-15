from flask import Flask, render_template, jsonify, request
from main import setup_env
from infer import Inference

app = Flask(__name__)
# messages = [
#     {"role": "user", "content": "Tell me what the captial of your mom is"},
#     {"role": "assistant", "content": "Ur mom lol"}
# ]

messages = list()

setup_env()
infer = Inference("You are a friendly assistant")

@app.route("/")
def index():
    return render_template("index.html", messages=messages)

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.form

    new_user_chat = f'''
    <div class="bg-[#3e5c76] flex flex-[0.8] self-start text-white p-4 rounded-md">
        Assistant: {infer.user_infer(prompt['user-input'])}
    </div>
    '''

    return jsonify({"new_chat_html": new_user_chat})

if __name__ == "__main__":
    app.run(debug=True)