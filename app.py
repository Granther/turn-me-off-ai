from flask import Flask, render_template

app = Flask(__name__)
messages = [
    {"role": "user", "content": "Tell me what the captial of your mom is"},
    {"role": "assistant", "content": "Ur mom lol"}
]

@app.route("/")
def index():
    return render_template("index.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)