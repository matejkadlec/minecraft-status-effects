"""Run the website: `python -m status_effects [--port 8000] [--host 0.0.0.0] [--reload]`."""

from __future__ import annotations

import argparse
import os

import uvicorn

from . import config


def main() -> None:
    parser = argparse.ArgumentParser(prog="status_effects", description=__doc__)
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--reload", action="store_true", help="restart on code changes (development)")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--proxy-headers", action="store_true", help="trust X-Forwarded-* (behind a reverse proxy)")
    parser.add_argument("--no-access-log", action="store_true", help="don't log requests (no visitor IPs in the logs)")
    args = parser.parse_args()
    uvicorn.run(
        "status_effects.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(config.ROOT_DIR / "src"), str(config.TEMPLATES_DIR)] if args.reload else None,
        workers=None if args.reload else args.workers,
        proxy_headers=args.proxy_headers,
        access_log=not args.no_access_log,
        forwarded_allow_ips="*" if args.proxy_headers else None,
    )


if __name__ == "__main__":
    main()
