# fastique/app/routes/main_routes.py
# Main routes for the application

from flask import Blueprint, render_template, current_app
import os
from pathlib import Path
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the main page"""
    # Get default search locations
    search_paths = current_app.config.get('DEFAULT_SEARCH_PATHS', [str(Path.home())])
    
    # Check if paths exist
    valid_paths = [path for path in search_paths if os.path.exists(path)]
    
    # If no valid paths, use home directory
    if not valid_paths:
        valid_paths = [str(Path.home())]

    # Get current year for copyright
    current_year = datetime.now().year
    
    return render_template('index.html', search_paths=valid_paths, current_year=current_year)

@main_bp.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')