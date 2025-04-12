# fastique/app/routes/search_routes.py
# Routes for search functionality

from flask import Blueprint, request, jsonify, current_app
from app.search.search_engine import SearchEngine
import time
from datetime import datetime

search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/', methods=['POST'])
def search():
    """Handle search requests"""
    data = request.json
    
    # Get search parameters
    query = data.get('query', '')
    paths = data.get('paths', current_app.config.get('DEFAULT_SEARCH_PATHS', []))
    file_types = data.get('file_types', None)
    use_regex = data.get('use_regex', False)
    case_sensitive = data.get('case_sensitive', False)
    include_hidden = data.get('include_hidden', False)
    max_depth = data.get('max_depth', None)
    
    # Parse date range if provided
    date_range = None
    if data.get('date_from') or data.get('date_to'):
        date_from = None
        date_to = None
        
        if data.get('date_from'):
            try:
                date_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
            except ValueError:
                pass
                
        if data.get('date_to'):
            try:
                date_to = datetime.strptime(data['date_to'], '%Y-%m-%d')
                # Set time to end of day
                date_to = date_to.replace(hour=23, minute=59, second=59)
            except ValueError:
                pass
                
        date_range = (date_from, date_to)
    
    # Parse size range if provided
    size_range = None
    if data.get('size_min') is not None or data.get('size_max') is not None:
        size_min = data.get('size_min', 0)
        size_max = data.get('size_max', float('inf'))
        size_range = (size_min, size_max)
    
    # Create search engine and execute search
    engine = SearchEngine(
        max_results=current_app.config.get('MAX_SEARCH_RESULTS', 500),
        threads=current_app.config.get('SEARCH_THREADS', 4)
    )
    
    start_time = time.time()
    results = engine.search(
        query=query,
        paths=paths,
        file_types=file_types,
        date_range=date_range,
        size_range=size_range,
        use_regex=use_regex,
        case_sensitive=case_sensitive,
        include_hidden=include_hidden,
        max_depth=max_depth
    )
    search_time = time.time() - start_time
    
    # Return the results
    return jsonify({
        'query': query,
        'count': len(results),
        'time': round(search_time, 3),
        'results': results
    })

@search_bp.route('/quick', methods=['GET'])
def quick_search():
    """Quick search with minimal parameters for fast UI response"""
    query = request.args.get('q', '')
    path = request.args.get('path', None)
    
    if not query:
        return jsonify({'results': [], 'count': 0, 'time': 0})
    
    # Use default paths if none specified
    paths = [path] if path else current_app.config.get('DEFAULT_SEARCH_PATHS', [])
    
    # Create search engine with limited results for quick response
    engine = SearchEngine(
        max_results=20,  # Limit to first 20 results for quick search
        threads=2        # Use fewer threads for quick search
    )
    
    start_time = time.time()
    results = engine.search(
        query=query,
        paths=paths,
        max_depth=2  # Limit depth for quick search
    )
    search_time = time.time() - start_time
    
    return jsonify({
        'query': query,
        'count': len(results),
        'time': round(search_time, 3),
        'results': results
    })