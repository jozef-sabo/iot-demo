from pathlib import Path

from flask_socketio import SocketIO
from flask import Flask, render_template, jsonify

from extensions import cache

app = Flask(__name__, template_folder='templates')

try:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
except ImportError as e:
    pass

cache.init_app(app=app, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": Path("./tmp")})
app.config["cache"] = cache
app.config["SECRET"] = "secret123456fd!!::-"
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

@app.route("/", methods=["GET"])
def index():
    clicks = cache.get("clicks")

    if clicks is None:
        clicks = 0

    return render_template("index.html", clicks=clicks)

@app.route("/", methods=["POST"])
def index_post():
    clicks = cache.get("clicks")

    if clicks is None:
        clicks = 0

    clicks += 1

    cache.set("clicks", clicks)

    socketio.emit("command", {"command": "update", "clicks": clicks})
    return jsonify({"status": "ok", "clicks": clicks})


if __name__ == "__main__":
    socketio.run(app, port=8844)

