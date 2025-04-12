# fastique/app/search/indexer.py
# File indexing for faster searches

import os
import time
import json
import threading
from typing import Dict, List, Any, Set
from pathlib import Path

class SearchIndex:
    """
    Class for creating and managing a search index for frequently accessed directories
    to improve search performance
    """
    def __init__(self, cache_dir: str = None, expiry_time: int = 3600):
        """
        Initialize the search index
        
        Args:
            cache_dir: Directory to store the index cache files
            expiry_time: Time in seconds after which an index entry is considered stale
        """
        self.expiry_time = expiry_time
        
        # Set up cache directory
        if cache_dir is None:
            self.cache_dir = os.path.join(str(Path.home()), '.fastique', 'cache')
        else:
            self.cache_dir = cache_dir
            
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # In-memory cache for faster access
        self.index_cache: Dict[str, Dict[str, Any]] = {}
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
    def get_index(self, directory: str) -> Dict[str, Any]:
        """
        Get the index for a directory, creating or updating it if necessary
        
        Args:
            directory: Path to the directory to index
            
        Returns:
            Dictionary with indexed files and metadata
        """
        with self.lock:
            # Check if we have a valid cached index
            if self._has_valid_cache(directory):
                return self.index_cache[directory]
            
            # Create or update the index
            index_data = self._build_index(directory)
            self._save_index(directory, index_data)
            return index_data
    
    def invalidate_index(self, directory: str) -> None:
        """
        Invalidate the index for a directory, forcing a rebuild on next access
        
        Args:
            directory: Path to the directory to invalidate
        """
        with self.lock:
            if directory in self.index_cache:
                del self.index_cache[directory]
            
            # Also delete the cache file
            cache_file = self._get_cache_file_path(directory)
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except Exception:
                    pass
    
    def _has_valid_cache(self, directory: str) -> bool:
        """
        Check if we have a valid cached index for the directory
        
        Args:
            directory: Directory path
            
        Returns:
            True if a valid cache exists, False otherwise
        """
        # Check in-memory cache first
        if directory in self.index_cache:
            if time.time() - self.index_cache[directory]['timestamp'] < self.expiry_time:
                return True
        
        # Check on-disk cache
        cache_file = self._get_cache_file_path(directory)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Check if the cache is still valid
                if time.time() - cache_data.get('timestamp', 0) < self.expiry_time:
                    self.index_cache[directory] = cache_data
                    return True
            except Exception:
                # If there's any error reading the cache, we'll rebuild it
                pass
                
        return False
    
    def _build_index(self, directory: str) -> Dict[str, Any]:
        """
        Build the index for a directory
        
        Args:
            directory: Directory path
            
        Returns:
            Dictionary with indexed files and metadata
        """
        indexed_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    # Skip hidden files
                    if file.startswith('.'):
                        continue
                        
                    full_path = os.path.join(root, file)
                    try:
                        stats = os.stat(full_path)
                        indexed_files.append({
                            'name': file,
                            'path': root,
                            'full_path': full_path,
                            'size': stats.st_size,
                            'modified': stats.st_mtime,
                            'is_directory': False
                        })
                    except (PermissionError, FileNotFoundError):
                        # Skip files we can't access
                        continue
                
                # Add directories too
                for d in dirs:
                    full_path = os.path.join(root, d)
                    try:
                        stats = os.stat(full_path)
                        indexed_files.append({
                            'name': d,
                            'path': root,
                            'full_path': full_path,
                            'size': 0,  # We don't calculate directory size during indexing for performance
                            'modified': stats.st_mtime,
                            'is_directory': True
                        })
                    except (PermissionError, FileNotFoundError):
                        # Skip directories we can't access
                        continue
        except Exception as e:
            print(f"Error indexing directory {directory}: {str(e)}")
        
        # Create the index data
        index_data = {
            'directory': directory,
            'timestamp': time.time(),
            'files': indexed_files
        }
        
        return index_data
    
    def _save_index(self, directory: str, index_data: Dict[str, Any]) -> None:
        """
        Save the index to both memory and disk cache
        
        Args:
            directory: Directory path
            index_data: Index data to save
        """
        # Save to memory cache
        self.index_cache[directory] = index_data
        
        # Save to disk cache
        cache_file = self._get_cache_file_path(directory)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f)
        except Exception as e:
            print(f"Error saving index for {directory} to {cache_file}: {str(e)}")
    
    def _get_cache_file_path(self, directory: str) -> str:
        """
        Get the path to the cache file for a directory
        
        Args:
            directory: Directory path
            
        Returns:
            Path to the cache file
        """
        # Create a safe filename from the directory path
        # Replace special characters with underscore
        safe_name = directory.replace('\\', '_').replace('/', '_').replace(':', '_')
        
        # Ensure the filename is not too long
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
            
        return os.path.join(self.cache_dir, f"{safe_name}.json")