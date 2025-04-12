# fastique/app/config.py
# Configuration settings for the application

import os
from pathlib import Path

class Config:
    """Application configuration settings"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-fastique'
    
    # Default search locations
    DEFAULT_SEARCH_PATHS = [
        str(Path.home()),  # User's home directory
    ]
    
    # Limit for search results (prevent overwhelming the UI)
    MAX_SEARCH_RESULTS = 500
    
    # File operations allowed
    ALLOWED_OPERATIONS = ['copy', 'move', 'rename', 'delete', 'new_folder', 'new_file']
    
    # Cache settings
    ENABLE_CACHE = True
    CACHE_EXPIRY = 600  # 10 minutes
    
    # Search settings
    SEARCH_THREADS = 4