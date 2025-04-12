# fastique/tests/test_file_operations.py
# Tests for file operations functionality

import unittest
import os
import tempfile
import shutil
from app.search.file_operations import FileOperations, FileOperationError

class TestFileOperations(unittest.TestCase):
    """Test case for the FileOperations class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.test_dir.name
        
        # Create a test file
        self.test_file_path = os.path.join(self.temp_path, 'test_file.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('Test content')
        
        # Create a test directory
        self.test_subdir_path = os.path.join(self.temp_path, 'test_subdir')
        os.makedirs(self.test_subdir_path)
    
    def tearDown(self):
        """Clean up after tests"""
        self.test_dir.cleanup()
    
    def test_get_file_info(self):
        """Test getting file information"""
        info = FileOperations.get_file_info(self.test_file_path)
        
        # Check basic properties
        self.assertEqual(info['name'], 'test_file.txt')
        self.assertEqual(info['path'], self.temp_path)
        self.assertEqual(info['is_directory'], False)
        self.assertEqual(info['extension'], 'txt')
        
        # Size should be the content length
        self.assertEqual(info['size'], len('Test content'))
        
        # Test directory info
        dir_info = FileOperations.get_file_info(self.test_subdir_path)
        self.assertEqual(dir_info['name'], 'test_subdir')
        self.assertEqual(dir_info['is_directory'], True)
    
    def test_create_file(self):
        """Test creating a new file"""
        new_file_path = os.path.join(self.temp_path, 'new_file.txt')
        content = 'New file content'
        
        # Create the file
        result = FileOperations.create_file(new_file_path, content)
        self.assertTrue(result)
        
        # Check if file exists and has correct content
        self.assertTrue(os.path.exists(new_file_path))
        with open(new_file_path, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_create_folder(self):
        """Test creating a new folder"""
        new_folder_path = os.path.join(self.temp_path, 'new_folder')
        
        # Create the folder
        result = FileOperations.create_folder(new_folder_path)
        self.assertTrue(result)
        
        # Check if folder exists
        self.assertTrue(os.path.exists(new_folder_path))
        self.assertTrue(os.path.isdir(new_folder_path))
    
    def test_copy_file(self):
        """Test copying a file"""
        dest_path = os.path.join(self.temp_path, 'copy_of_test_file.txt')
        
        # Copy the file
        result = FileOperations.copy_file(self.test_file_path, dest_path)
        self.assertTrue(result)
        
        # Check if destination file exists and has same content
        self.assertTrue(os.path.exists(dest_path))
        with open(dest_path, 'r') as f:
            self.assertEqual(f.read(), 'Test content')
    
    def test_move_file(self):
        """Test moving a file"""
        # Create a file to move
        move_source = os.path.join(self.temp_path, 'file_to_move.txt')
        with open(move_source, 'w') as f:
            f.write('File to move')
        
        move_dest = os.path.join(self.test_subdir_path, 'moved_file.txt')
        
        # Move the file
        result = FileOperations.move_file(move_source, move_dest)
        self.assertTrue(result)
        
        # Source should no longer exist
        self.assertFalse(os.path.exists(move_source))
        
        # Destination should exist with the same content
        self.assertTrue(os.path.exists(move_dest))
        with open(move_dest, 'r') as f:
            self.assertEqual(f.read(), 'File to move')
    
    def test_rename_file(self):
        """Test renaming a file"""
        # Create a file to rename
        rename_source = os.path.join(self.temp_path, 'original_name.txt')
        with open(rename_source, 'w') as f:
            f.write('File to rename')
        
        # Rename the file
        new_name = 'renamed_file.txt'
        new_path = FileOperations.rename_file(rename_source, new_name)
        
        # Original should no longer exist
        self.assertFalse(os.path.exists(rename_source))
        
        # New path should match expected
        expected_path = os.path.join(self.temp_path, new_name)
        self.assertEqual(new_path, expected_path)
        
        # New file should exist with same content
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, 'r') as f:
            self.assertEqual(f.read(), 'File to rename')
    
    def test_delete_file(self):
        """Test deleting a file"""
        # Create a file to delete
        delete_path = os.path.join(self.temp_path, 'file_to_delete.txt')
        with open(delete_path, 'w') as f:
            f.write('File to delete')
        
        # Delete the file (directly, not to trash)
        result = FileOperations.delete_file(delete_path, use_trash=False)
        self.assertTrue(result)
        
        # File should no longer exist
        self.assertFalse(os.path.exists(delete_path))
    
    def test_file_operation_error(self):
        """Test error handling for non-existent files"""
        non_existent_path = os.path.join(self.temp_path, 'does_not_exist.txt')
        
        # Should raise FileOperationError
        with self.assertRaises(FileOperationError):
            FileOperations.get_file_info(non_existent_path)
        
        with self.assertRaises(FileOperationError):
            FileOperations.copy_file(non_existent_path, os.path.join(self.temp_path, 'whatever.txt'))
        
        with self.assertRaises(FileOperationError):
            FileOperations.move_file(non_existent_path, os.path.join(self.temp_path, 'whatever.txt'))
        
        with self.assertRaises(FileOperationError):
            FileOperations.rename_file(non_existent_path, 'new_name.txt')
        
        with self.assertRaises(FileOperationError):
            FileOperations.delete_file(non_existent_path)

if __name__ == '__main__':
    unittest.main()