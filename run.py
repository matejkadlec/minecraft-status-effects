import os
from bottle import Bottle, static_file, run, HTTPError, redirect, request

app = Bottle()

ROOT_DIR = "."


@app.route("/")
def root():
    return static_file("index.html", root=ROOT_DIR)


@app.route("/index.html")
def redirect_index_html():
    # Preserve query string if present
    qs = request.query_string
    target = "/"
    if qs:
        target += f"?{qs}"
    redirect(target, 301)


@app.route("/<requested:path>")
def serve_any(requested: str):
    """Serve static assets with extensionless support.

    Resolution order (stop at first existing file):
      1. Exact path as-is (requested)
      2. As directory index (requested + '/index.html')
      3. As HTML file (requested + '.html')
    Returns 404 if none match.
    """

    # Direct file hit (includes assets and .html when explicitly requested)
    direct_path = os.path.join(ROOT_DIR, requested)
    if os.path.isfile(direct_path):
        return static_file(requested, root=ROOT_DIR)

    # Directory index fallback
    idx_path = os.path.join(ROOT_DIR, requested, "index.html")
    if os.path.isfile(idx_path):
        return static_file(os.path.join(requested, "index.html"), root=ROOT_DIR)

    # .html implicit fallback
    html_path = os.path.join(ROOT_DIR, requested + ".html")
    if os.path.isfile(html_path):
        return static_file(requested + ".html", root=ROOT_DIR)

    return HTTPError(404, "Not Found")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "true").lower() == "true"
    # Disable reloader in production-like runs
    run(app, host="0.0.0.0", port=port, debug=debug, reloader=debug)
