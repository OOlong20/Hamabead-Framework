import os
from flask import Flask, jsonify, send_from_directory, request, wrappers

import src.recognize as recognize
import asyncio

app = Flask(
    __name__,
    static_folder="web/build",
)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# @app.route("/")
# def index():
#     return render_template("./index.html")


@app.route("/webcam", methods=["POST"])
def open():
    print(request.get_json())
    if request.get_json()["webcam"] == "open":
        recognize.control_camera("open")
        return jsonify("open")
        # return wrappers.Response(
        #     recognize.detect(), mimetype="multipart/x-mixed-replace; boundary=frame"
        # )
    else:
        recognize.control_camera("close")
        return jsonify("close")
    # if request.form.get("webcom") == "open":
    # recognize.control_camera("open")
    # recognize.control_camera("close")
    # return render_template("index.html")


@app.route("/video")
def video():
    return wrappers.Response(
        recognize.detect(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/results")
def results():
    return jsonify(recognize.recognize_results)


if __name__ == "__main__":
    app.run(debug=True)
