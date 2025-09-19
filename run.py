from bottle import Bottle, static_file, run

app = Bottle()

ROOT_DIR = "."


@app.route("/")
def root():
    return static_file("index.html", root=ROOT_DIR)


# Serve any path under project root (css, js, img, data, etc.)
@app.route("/<filepath:path>")
def serve_static(filepath: str):
    return static_file(filepath, root=ROOT_DIR)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, debug=True, reloader=True)
