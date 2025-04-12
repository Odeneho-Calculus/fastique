# fastique/app/search/file_operations.py
# File operations functionality

import os
import shutil
import subprocess
import platform
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

class FileOperationError(Exception):
    """Custom exception for file operations errors"""
    pass

class FileOperations:
    """Class handling all file operations"""
    
    @staticmethod
    def get_file_info(path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory
        
        Args:
            path: Path to the file or directory
            
        Returns:
            Dictionary with file information
        """
        if not os.path.exists(path):
            raise FileOperationError(f"Path does not exist: {path}")
        
        try:
            stats = os.stat(path)
            is_dir = os.path.isdir(path)
            
            info = {
                'name': os.path.basename(path),
                'path': os.path.dirname(path),
                'full_path': path,
                'size': stats.st_size if not is_dir else FileOperations._get_dir_size(path),
                'created': stats.st_ctime,
                'modified': stats.st_mtime,
                'accessed': stats.st_atime,
                'is_directory': is_dir,
                'permissions': oct(stats.st_mode)[-3:],
                'owner': stats.st_uid,
                'group': stats.st_gid,
            }
            
            if not is_dir:
                info['extension'] = os.path.splitext(path)[1][1:].lower()
            
            return info
        except Exception as e:
            raise FileOperationError(f"Failed to get file info: {str(e)}")
    
    @staticmethod
    def _get_dir_size(path: str) -> int:
        """
        Calculate the total size of a directory
        
        Args:
            path: Directory path
            
        Returns:
            Size in bytes
        """
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (PermissionError, FileNotFoundError):
                    pass  # Skip files we can't access
        return total_size
    
    @staticmethod
    def open_file(path: str) -> bool:
        """
        Open a file with the default application
        
        Args:
            path: Path to the file
            
        Returns:
            True if successful, raises exception otherwise
        """
        if not os.path.exists(path):
            raise FileOperationError(f"File does not exist: {path}")
        
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', path])
            else:  # Linux
                subprocess.call(['xdg-open', path])
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to open file: {str(e)}")
    
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """
        Copy a file or directory
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            True if successful, raises exception otherwise
        """
        if not os.path.exists(source):
            raise FileOperationError(f"Source does not exist: {source}")
        
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                # Create destination directory if it doesn't exist
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to copy: {str(e)}")
    
    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """
        Move a file or directory
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            True if successful, raises exception otherwise
        """
        if not os.path.exists(source):
            raise FileOperationError(f"Source does not exist: {source}")
        
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to move: {str(e)}")
    
    @staticmethod
    def rename_file(path: str, new_name: str) -> str:
        """
        Rename a file or directory
        
        Args:
            path: Path to the file
            new_name: New name (not full path)
            
        Returns:
            New path if successful, raises exception otherwise
        """
        if not os.path.exists(path):
            raise FileOperationError(f"File does not exist: {path}")
        
        try:
            directory = os.path.dirname(path)
            new_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_path):
                raise FileOperationError(f"A file with the name {new_name} already exists")
            
            os.rename(path, new_path)
            return new_path
        except Exception as e:
            raise FileOperationError(f"Failed to rename: {str(e)}")
    
    @staticmethod
    def delete_file(path: str, use_trash: bool = True) -> bool:
        """
        Delete a file or directory
        
        Args:
            path: Path to the file
            use_trash: Move to trash/recycle bin instead of permanent delete
            
        Returns:
            True if successful, raises exception otherwise
        """
        if not os.path.exists(path):
            raise FileOperationError(f"File does not exist: {path}")
        
        try:
            if use_trash:
                # Use platform-specific trash functionality
                # This would ideally use a library like 'send2trash' which needs to be installed
                # For this example, we'll implement a simple fallback to standard delete
                # In a real application, you would want to implement proper trash functionality
                # or use an existing library
                try:
                    import send2trash
                    send2trash.send2trash(path)
                except ImportError:
                    # Fallback to regular delete
                    FileOperations._delete_directly(path)
            else:
                FileOperations._delete_directly(path)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to delete: {str(e)}")
    
    @staticmethod
    def _delete_directly(path: str) -> None:
        """
        Directly delete a file or directory without using the trash
        
        Args:
            path: Path to the file
        """
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    
    @staticmethod
    def create_folder(path: str) -> bool:
        """
        Create a new folder
        
        Args:
            path: Path for the new folder
            
        Returns:
            True if successful, raises exception otherwise
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to create folder: {str(e)}")
    
    @staticmethod
    def create_file(path: str, content: str = "") -> bool:
        """
        Create a new file
        
        Args:
            path: Path for the new file
            content: Optional initial content
            
        Returns:
            True if successful, raises exception otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Create and write to file
            with open(path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to create file: {str(e)}")