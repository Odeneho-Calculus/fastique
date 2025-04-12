# fastique/app/search/search_engine.py
# Core search engine functionality

import os
import re
import fnmatch
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import List, Dict, Any, Iterator, Optional

class SearchResult:
    """Class to store search result information"""
    def __init__(self, path, filename, size, modified_time, is_directory):
        self.path = path
        self.filename = filename
        self.size = size
        self.modified_time = modified_time
        self.is_directory = is_directory
        self.full_path = os.path.join(path, filename)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary for JSON serialization"""
        return {
            'path': self.path,
            'filename': self.filename,
            'full_path': self.full_path,
            'size': self.size,
            'size_formatted': self.format_size(),
            'modified_time': self.modified_time,
            'modified_time_formatted': self.format_time(),
            'is_directory': self.is_directory,
            'extension': os.path.splitext(self.filename)[1][1:].lower() if not self.is_directory else '',
            'icon_class': self.get_icon_class()
        }
    
    def format_size(self) -> str:
        """Format file size to human-readable format"""
        if self.is_directory:
            return "Directory"
        
        # Convert size to KB, MB, GB as appropriate
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024 or unit == 'TB':
                if unit == 'B':
                    return f"{size} {unit}"
                return f"{size:.2f} {unit}"
            size /= 1024
    
    def format_time(self) -> str:
        """Format modified time to readable format"""
        dt = datetime.fromtimestamp(self.modified_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_icon_class(self) -> str:
        """Return CSS class for file type icon"""
        if self.is_directory:
            return "folder-icon"
        
        ext = os.path.splitext(self.filename)[1][1:].lower()
        
        # Common file types
        icon_map = {
            "pdf": "pdf-icon",
            "doc": "word-icon", "docx": "word-icon",
            "xls": "excel-icon", "xlsx": "excel-icon",
            "ppt": "powerpoint-icon", "pptx": "powerpoint-icon",
            "txt": "text-icon",
            "zip": "archive-icon", "rar": "archive-icon", "tar": "archive-icon", "gz": "archive-icon",
            "mp3": "audio-icon", "wav": "audio-icon", "flac": "audio-icon",
            "mp4": "video-icon", "avi": "video-icon", "mkv": "video-icon",
            "jpg": "image-icon", "jpeg": "image-icon", "png": "image-icon", "gif": "image-icon",
            "py": "code-icon", "js": "code-icon", "html": "code-icon", "css": "code-icon", "cpp": "code-icon",
            "java": "code-icon"
        }
        
        return icon_map.get(ext, "file-icon")

class SearchEngine:
    """Main search engine for finding files and directories"""
    def __init__(self, max_results=500, threads=4):
        self.max_results = max_results
        self.threads = threads
        self.results_queue = Queue()
        self.active_threads = 0
        self.search_complete = threading.Event()
    
    def search(self, 
               query: str, 
               paths: List[str],
               file_types: Optional[List[str]] = None,
               date_range: Optional[tuple] = None,
               size_range: Optional[tuple] = None,
               use_regex: bool = False,
               case_sensitive: bool = False,
               include_hidden: bool = False,
               max_depth: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for files and directories matching the query
        
        Args:
            query: The search term
            paths: List of directories to search in
            file_types: List of file extensions to include (None for all)
            date_range: Tuple of (start_date, end_date) for filtering by modification time
            size_range: Tuple of (min_size, max_size) in bytes
            use_regex: Whether to treat query as regex pattern
            case_sensitive: Whether to perform case-sensitive search
            include_hidden: Whether to include hidden files/folders
            max_depth: Maximum directory depth to search
            
        Returns:
            List of matching files and directories as dictionaries
        """
        # Prepare the query
        if not use_regex:
            # Escape special characters and convert wildcard pattern to regex
            query = fnmatch.translate(query)
        
        if not case_sensitive:
            pattern = re.compile(query, re.IGNORECASE)
        else:
            pattern = re.compile(query)
            
        # Convert date range to timestamps if provided
        timestamp_range = None
        if date_range:
            start_date, end_date = date_range
            timestamp_range = (
                start_date.timestamp() if start_date else 0,
                end_date.timestamp() if end_date else float('inf')
            )
        
        # Process search with multiple threads
        self.results = []
        self.search_complete.clear()
        self.active_threads = 0
        
        # Create and start search threads
        for path in paths:
            if os.path.exists(path):
                self.active_threads += 1
                threading.Thread(
                    target=self._search_worker,
                    args=(path, pattern, file_types, timestamp_range, size_range, include_hidden, max_depth, 0),
                    daemon=True
                ).start()
        
        # Wait for all threads to complete or max results reached
        if self.active_threads > 0:
            self.search_complete.wait()
            
        # Get all results from the queue
        results = []
        while not self.results_queue.empty() and len(results) < self.max_results:
            results.append(self.results_queue.get().to_dict())
        
        return results
    
    def _search_worker(self, 
                      directory: str, 
                      pattern: re.Pattern, 
                      file_types: Optional[List[str]],
                      timestamp_range: Optional[tuple],
                      size_range: Optional[tuple],
                      include_hidden: bool,
                      max_depth: Optional[int],
                      current_depth: int):
        """Worker thread for searching a directory"""
        try:
            # Check if we've reached max depth
            if max_depth is not None and current_depth > max_depth:
                self._thread_complete()
                return
                
            # Get all items in directory
            for item in os.scandir(directory):
                # Skip hidden files if not including them
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                # Check if item matches search pattern
                if pattern.search(item.name):
                    # Check file type filter if applicable
                    if file_types and not item.is_dir():
                        ext = os.path.splitext(item.name)[1][1:].lower()
                        if ext not in file_types:
                            continue
                    
                    # Get file stats
                    stats = item.stat()
                    
                    # Check date range if applicable
                    if timestamp_range:
                        mtime = stats.st_mtime
                        if mtime < timestamp_range[0] or mtime > timestamp_range[1]:
                            continue
                    
                    # Check size range if applicable (only for files)
                    if size_range and not item.is_dir():
                        size = stats.st_size
                        if size < size_range[0] or size > size_range[1]:
                            continue
                    
                    # Create and add result
                    result = SearchResult(
                        path=directory,
                        filename=item.name,
                        size=stats.st_size if not item.is_dir() else 0,
                        modified_time=stats.st_mtime,
                        is_directory=item.is_dir()
                    )
                    
                    self.results_queue.put(result)
                    
                    # Check if we've reached the maximum results
                    if self.results_queue.qsize() >= self.max_results:
                        self._thread_complete()
                        return
                
                # Recursively search subdirectories
                if item.is_dir():
                    self.active_threads += 1
                    threading.Thread(
                        target=self._search_worker,
                        args=(item.path, pattern, file_types, timestamp_range, size_range, 
                              include_hidden, max_depth, current_depth + 1),
                        daemon=True
                    ).start()
                
        except (PermissionError, FileNotFoundError) as e:
            # Log the error but continue
            print(f"Error accessing {directory}: {str(e)}")
        
        self._thread_complete()
    
    def _thread_complete(self):
        """Mark a thread as complete and check if search is finished"""
        self.active_threads -= 1
        if self.active_threads <= 0:
            self.search_complete.set()