"""Validate the public-only Markdown catalog before building or publishing."""

from reconflow.services.public_docs import validate

if __name__ == "__main__":
    print(f"PASS: {validate()} public Markdown pages and their local document/heading links")
