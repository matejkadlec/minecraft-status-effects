import os
import json
from bottle import Bottle, static_file, run, HTTPError, redirect, request, response
from export.export_handler import ExportHandler

app = Bottle()

ROOT_DIR = "."  # Public web root (keep sensitive files outside this if possible)

# Files in the root directory we explicitly never want to serve
SENSITIVE_ROOT_FILES = {"Dockerfile", "docker-compose.yml", "requirements.txt"}

# Forbidden extensions anywhere
FORBIDDEN_EXTS = {
    ".md",
    ".markdown",
    ".py",
    ".sh",
}


def is_forbidden_path(requested: str) -> bool:
    """Return True if the requested path should be denied (403).

    Mirrors defense-in-depth rules that would normally live in an upstream
    server like Nginx. Doing them here too helps if the app is ever run
    directly (e.g. during local dev or fallback hosting environments).
    Rules:
      1. No path traversal (..)
      2. No hidden/dot path segments (".git", ".env", etc.)
      3. No sensitive root files (Dockerfile, requirements.txt, etc.)
      4. No markdown or python source files
    """

    # Normalize path to remove redundant separators / up-level references
    norm = os.path.normpath(requested)

    # Reject attempts to break out of ROOT_DIR
    if norm.startswith(".."):
        return True

    # Split into segments and check dotfiles
    segments = [s for s in norm.split("/") if s and s not in (".",)]
    if any(seg.startswith(".") for seg in segments):
        return True

    # Block sensitive files only if requested directly from root
    if len(segments) == 1 and segments[0] in SENSITIVE_ROOT_FILES:
        return True

    # Block forbidden extensions
    _, ext = os.path.splitext(norm)
    if ext.lower() in FORBIDDEN_EXTS:
        return True

    return False


@app.route("/")
def root():
    return static_file("index.html", root=ROOT_DIR)


@app.route("/sitemap.xml")
def sitemap():
    """Serve sitemap with proper content type."""
    return static_file("sitemap.xml", root=ROOT_DIR, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    """Serve robots.txt with proper content type."""
    return static_file("robots.txt", root=ROOT_DIR, mimetype="text/plain")


@app.route("/index.html")
def redirect_index_html():
    # Preserve query string if present
    qs = request.query_string
    target = "/"
    if qs:
        target += f"?{qs}"
    redirect(target, 301)


@app.route("/export/<format_type>")
def export_effects(format_type):
    """Export effects data in specified format with current filters."""
    try:
        # Get request parameters
        theme = request.query.get("theme", "light")
        ignore_filters = request.query.get("ignore_filters", "false").lower() == "true"

        # Parse filters from request
        filters = {}
        if not ignore_filters:
            # Search filter
            if search := request.query.get("search", "").strip():
                filters["search"] = search

            # Type filters
            type_filters = {}
            type_filters["positive"] = (
                request.query.get("positive", "true").lower() == "true"
            )
            type_filters["negative"] = (
                request.query.get("negative", "true").lower() == "true"
            )
            type_filters["scaling"] = (
                request.query.get("scaling", "true").lower() == "true"
            )
            filters["type_filters"] = type_filters

            # Vanilla filter
            vanilla_filter = request.query.get("vanilla", "true").lower() == "true"
            filters["vanilla_filter"] = vanilla_filter

        # Generate export
        handler = ExportHandler()
        content, filename = handler.export_data(
            format_type, theme, filters, ignore_filters
        )

        # Set appropriate headers
        if format_type.lower() == "json":
            response.content_type = "application/json"
        elif format_type.lower() == "csv":
            response.content_type = "text/csv"
        elif format_type.lower() == "xlsx":
            response.content_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        return content

    except Exception as e:
        return HTTPError(500, f"Export failed: {str(e)}")


@app.route("/export/static/<filename>")
def serve_static_export(filename):
    """Serve pre-generated export files."""
    try:
        return static_file(filename, root="export/files")
    except:
        return HTTPError(404, "Export file not found")


@app.route("/<requested:path>")
def serve_any(requested: str):
    """Serve static assets with extensionless support.

    Resolution order (stop at first existing file):
      1. Exact path as-is (requested)
      2. As directory index (requested + '/index.html')
      3. As HTML file (requested + '.html')
    Returns 404 if none match.
    """

    # Security / deny rules (defense-in-depth). Return 403 for forbidden targets.
    if is_forbidden_path(requested):
        return HTTPError(403, "Forbidden")

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
