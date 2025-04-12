# fastique/tests/test_search.py
# Tests for the search engine functionality

import unittest
import os
import tempfile
import time
from app.search.search_engine import SearchEngine, SearchResult
from pathlib import Path

class TestSearchEngine(unittest.TestCase):
    """Test case for the SearchEngine class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.test_dir.name
        
        # Create some test files
        file_structure = {
            'file1.txt': 'This is file 1',
            'file2.doc': 'This is file 2',
            'image.jpg': 'Image content',
            'subfolder/subfile.txt': 'Subfile content',
            'subfolder/another.pdf': 'PDF content',
            'hidden/.hidden_file.txt': 'Hidden content'
        }
        
        # Create the files
        for file_path, content in file_structure.items():
            full_path = os.path.join(self.temp_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Initialize search engine
        self.search_engine = SearchEngine(max_results=100, threads=2)
    
    def tearDown(self):
        """Clean up after tests"""
        self.test_dir.cleanup()
    
    def test_basic_search(self):
        """Test basic search functionality"""
        # Search for all .txt files
        results = self.search_engine.search(
            query="*.txt",
            paths=[self.temp_path],
            include_hidden=False
        )
        
        # Should find 2 .txt files (excluding hidden)
        self.assertEqual(len(results), 2)
        
        # File names should include file1.txt and subfile.txt
        file_names = [os.path.basename(r['full_path']) for r in results]
        self.assertIn('file1.txt', file_names)
        self.assertIn('subfile.txt', file_names)
    
    def test_search_with_file_types(self):
        """Test search with file type filter"""
        # Search for only .doc files
        results = self.search_engine.search(
            query="*",
            paths=[self.temp_path],
            file_types=['doc'],
            include_hidden=False
        )
        
        # Should find 1 .doc file
        self.assertEqual(len(results), 1)
        self.assertEqual(os.path.basename(results[0]['full_path']), 'file2.doc')
    
    def test_regex_search(self):
        """Test search with regex pattern"""
        # Search for files containing 'file' in the name
        results = self.search_engine.search(
            query="file\\d",  # Match file followed by a digit
            paths=[self.temp_path],
            use_regex=True,
            include_hidden=False
        )
        
        # Should find file1.txt and file2.doc
        self.assertEqual(len(results), 2)
        
        file_names = [os.path.basename(r['full_path']) for r in results]
        self.assertIn('file1.txt', file_names)
        self.assertIn('file2.doc', file_names)
    
    def test_search_with_hidden_files(self):
        """Test search including hidden files"""
        # Search for all .txt files including hidden
        results = self.search_engine.search(
            query="*.txt",
            paths=[self.temp_path],
            include_hidden=True
        )
        
        # Should find 3 .txt files (including hidden)
        self.assertEqual(len(results), 3)
        
        # Hidden file should be included
        hidden_files = [r for r in results if '.hidden_file.txt' in r['full_path']]
        self.assertEqual(len(hidden_files), 1)
    
    def test_search_result_class(self):
        """Test the SearchResult class"""
        # Create a test result
        result = SearchResult(
            path=self.temp_path,
            filename='file1.txt',
            size=100,
            modified_time=time.time(),
            is_directory=False
        )
        
        # Convert to dict
        result_dict = result.to_dict()
        
        # Check fields
        self.assertEqual(result_dict['path'], self.temp_path)
        self.assertEqual(result_dict['filename'], 'file1.txt')
        self.assertEqual(result_dict['size'], 100)
        self.assertEqual(result_dict['extension'], 'txt')
        self.assertEqual(result_dict['is_directory'], False)
        
        # Check icon class
        self.assertEqual(result_dict['icon_class'], 'text-icon')
        
        # Test directory result
        dir_result = SearchResult(
            path=self.temp_path,
            filename='subfolder',
            size=0,
            modified_time=time.time(),
            is_directory=True
        )
        dir_dict = dir_result.to_dict()
        
        self.assertEqual(dir_dict['icon_class'], 'folder-icon')
        self.assertEqual(dir_dict['size_formatted'], 'Directory')

if __name__ == '__main__':
    unittest.main()