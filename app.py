from flask import Flask, jsonify, render_template, request, wrappers
import src.recognize as recognize
import asyncio

app = Flask(__name__, template_folder="./templates")


@app.route("/")
def index():
    return render_template("index.html")


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
