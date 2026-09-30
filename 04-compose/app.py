from flask import Flask
import redis
import socket

app = Flask(__name__)
r = redis.Redis(host="redis", port=6379)

@app.route("/")
def hello():
    count = r.incr("hits")
    return f"<h1>Visits: {count}</h1><p>container: {socket.gethostname()}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
