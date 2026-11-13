# Production image of the website: the app and its data, run by an unprivileged user.
#
# The base image is pinned by digest; change the tag and the digest together. The Python
# dependencies come from requirements.lock (exact versions with hashes), see AGENTS.md.
FROM python:3.12.16-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY requirements.lock ./
RUN pip install --require-hashes --no-deps -r requirements.lock

# The same layout as the repository, so config.ROOT_DIR resolves to /app without any setting.
COPY src/status_effects src/status_effects
COPY public public
COPY data/effects.json data/mods.json data/

USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --start-interval=1s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["python", "-m", "status_effects", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--no-access-log"]
