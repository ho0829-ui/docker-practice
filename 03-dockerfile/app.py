from flask import Flask
import socket

app = Flask(__name__)

@app.route("/")
def hello():
    return f"<h1>Hello from my image!</h1><p>container: {socket.gethostname()}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
