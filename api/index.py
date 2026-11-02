"""Vercel Python entry point for the STEPZONE Flask application."""

from app import create_app


app = create_app("production")

