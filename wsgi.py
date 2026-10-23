"""WSGI 入口。

Linux / Render：gunicorn wsgi:app
Windows 生产：  pip install waitress && python wsgi.py
"""
import os

from app import app


if __name__ == "__main__":
    try:
        from waitress import serve  # type: ignore[import-not-found]
    except ImportError:
        raise SystemExit(
            "waitress is required for Windows production: pip install waitress"
        )
    serve(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        threads=4,
    )