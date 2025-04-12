#!/usr/bin/env python3
# fastique/run.py
# Main entry point for the application

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)