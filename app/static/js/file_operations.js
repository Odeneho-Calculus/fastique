// fastique/app/static/js/file_operations.js
// JavaScript functions for file operations

/**
 * File operations client-side functionality
 */
const FileOperations = {
    /**
     * Initialize file operations handlers
     */
    init: function () {
        // Attach event handlers to file operation buttons
        this.attachEventHandlers();

        // Initialize context menu for file operations
        this.initContextMenu();
    },

    /**
     * Attach event handlers to elements
     */
    attachEventHandlers: function () {
        // Handle click on file/directory in results
        document.addEventListener('click', function (e) {
            const fileItem = e.target.closest('.file-item');
            if (fileItem) {
                // If it's a direct click on the item (not a button)
                if (!e.target.closest('.file-actions')) {
                    const path = fileItem.dataset.path;
                    const isDir = fileItem.dataset.isDirectory === 'true';

                    if (isDir) {
                        // Navigate into directory
                        FileOperations.navigateToDirectory(path);
                    } else {
                        // Open file
                        FileOperations.openFile(path);
                    }
                }
            }
        });

        // Global handlers for operation buttons
        document.addEventListener('click', function (e) {
            // Open button
            if (e.target.closest('.btn-open')) {
                const fileItem = e.target.closest('.file-item');
                const path = fileItem.dataset.path;
                FileOperations.openFile(path);
                e.preventDefault();
            }

            // Copy button
            if (e.target.closest('.btn-copy')) {
                const fileItem = e.target.closest('.file-item');
                const path = fileItem.dataset.path;
                const name = fileItem.dataset.name;
                FileOperations.copyFile(path, name);
                e.preventDefault();
            }

            // Move button
            if (e.target.closest('.btn-move')) {
                const fileItem = e.target.closest('.file-item');
                const path = fileItem.dataset.path;
                const name = fileItem.dataset.name;
                FileOperations.moveFile(path, name);
                e.preventDefault();
            }

            // Rename button
            if (e.target.closest('.btn-rename')) {
                const fileItem = e.target.closest('.file-item');
                const path = fileItem.dataset.path;
                const name = fileItem.dataset.name;
                FileOperations.renameFile(path, name);
                e.preventDefault();
            }

            // Delete button
            if (e.target.closest('.btn-delete')) {
                const fileItem = e.target.closest('.file-item');
                const path = fileItem.dataset.path;
                const name = fileItem.dataset.name;
                FileOperations.deleteFile(path, name);
                e.preventDefault();
            }

            // New folder button
            if (e.target.closest('#new-folder-btn')) {
                const currentPath = document.getElementById('current-path').value;
                FileOperations.createFolder(currentPath);
                e.preventDefault();
            }

            // New file button
            if (e.target.closest('#new-file-btn')) {
                const currentPath = document.getElementById('current-path').value;
                FileOperations.createFile(currentPath);
                e.preventDefault();
            }
        });
    },

    /**
     * Initialize context menu for file operations
     */
    initContextMenu: function () {
        // Create and append context menu to body
        const contextMenu = document.createElement('div');
        contextMenu.classList.add('context-menu');
        contextMenu.innerHTML = `
            <ul>
                <li class="context-open">Open</li>
                <li class="context-copy">Copy</li>
                <li class="context-move">Move</li>
                <li class="context-rename">Rename</li>
                <li class="context-delete">Delete</li>
            </ul>
        `;
        document.body.appendChild(contextMenu);

        // Show context menu on right-click
        document.addEventListener('contextmenu', function (e) {
            const fileItem = e.target.closest('.file-item');
            if (fileItem) {
                e.preventDefault();

                const path = fileItem.dataset.path;
                const name = fileItem.dataset.name;
                const isDir = fileItem.dataset.isDirectory === 'true';

                // Store data in context menu
                contextMenu.dataset.path = path;
                contextMenu.dataset.name = name;
                contextMenu.dataset.isDirectory = isDir;

                // Position the menu
                const x = e.clientX;
                const y = e.clientY;

                contextMenu.style.left = x + 'px';
                contextMenu.style.top = y + 'px';
                contextMenu.style.display = 'block';
            }
        });

        // Hide context menu when clicking elsewhere
        document.addEventListener('click', function () {
            contextMenu.style.display = 'none';
        });

        // Handle context menu actions
        contextMenu.addEventListener('click', function (e) {
            const path = contextMenu.dataset.path;
            const name = contextMenu.dataset.name;

            if (e.target.classList.contains('context-open')) {
                FileOperations.openFile(path);
            } else if (e.target.classList.contains('context-copy')) {
                FileOperations.copyFile(path, name);
            } else if (e.target.classList.contains('context-move')) {
                FileOperations.moveFile(path, name);
            } else if (e.target.classList.contains('context-rename')) {
                FileOperations.renameFile(path, name);
            } else if (e.target.classList.contains('context-delete')) {
                FileOperations.deleteFile(path, name);
            }

            // Hide the menu
            contextMenu.style.display = 'none';
        });
    },

    /**
     * Navigate to a directory and display its contents
     * @param {string} path - Directory path
     */
    navigateToDirectory: function (path) {
        // Update current path in the UI
        const currentPathInput = document.getElementById('current-path');
        currentPathInput.value = path;

        // Trigger a search to show directory contents
        const searchInput = document.getElementById('search-input');
        searchInput.value = ''; // Clear search

        // Update breadcrumbs
        this.updateBreadcrumbs(path);

        // Trigger search with empty query to show all files
        SearchUI.performSearch();
    },

    /**
     * Update breadcrumbs navigation based on current path
     * @param {string} path - Current directory path
     */
    updateBreadcrumbs: function (path) {
        const breadcrumbsDiv = document.getElementById('breadcrumbs');
        breadcrumbsDiv.innerHTML = '';

        // Split path into components
        const pathParts = path.split(/[\/\\]/).filter(part => part.trim() !== '');
        let currentPath = '';

        // Add home link
        const homeLink = document.createElement('a');
        homeLink.href = '#';
        homeLink.textContent = 'Home';
        homeLink.classList.add('breadcrumb-item');
        homeLink.addEventListener('click', function (e) {
            e.preventDefault();
            FileOperations.navigateToDirectory('/');
        });
        breadcrumbsDiv.appendChild(homeLink);

        // Add separator
        breadcrumbsDiv.appendChild(document.createTextNode(' > '));

        // Add each path part as a link
        pathParts.forEach((part, index) => {
            if (index === 0) {
                currentPath = part + ':\\'; // Windows drive
            } else {
                currentPath += '\\' + part;
            }

            const link = document.createElement('a');
            link.href = '#';
            link.textContent = part;
            link.classList.add('breadcrumb-item');
            link.dataset.path = currentPath;

            link.addEventListener('click', function (e) {
                e.preventDefault();
                FileOperations.navigateToDirectory(this.dataset.path);
            });

            breadcrumbsDiv.appendChild(link);

            // Add separator if not the last item
            if (index < pathParts.length - 1) {
                breadcrumbsDiv.appendChild(document.createTextNode(' > '));
            }
        });
    },

    /**
     * Open a file with the default application
     * @param {string} path - File path
     */
    openFile: function (path) {
        fetch('/file/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path: path })
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    UIControls.showNotification(data.message || 'Failed to open file', 'error');
                }
            })
            .catch(error => {
                console.error('Error opening file:', error);
                UIControls.showNotification('Error opening file', 'error');
            });
    },

    /**
     * Copy a file to a new location
     * @param {string} path - File path
     * @param {string} name - File name
     */
    copyFile: function (path, name) {
        UIControls.showDialog({
            title: 'Copy File',
            message: `Copy "${name}" to:`,
            inputLabel: 'Destination Path:',
            inputValue: path, // Default to same directory
            confirmLabel: 'Copy',
            cancelLabel: 'Cancel',
            onConfirm: function (destinationPath) {
                fetch('/file/copy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        source: path,
                        destination: destinationPath
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`File copied successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to copy file', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error copying file:', error);
                        UIControls.showNotification('Error copying file', 'error');
                    });
            }
        });
    },

    /**
     * Move a file to a new location
     * @param {string} path - File path
     * @param {string} name - File name
     */
    moveFile: function (path, name) {
        UIControls.showDialog({
            title: 'Move File',
            message: `Move "${name}" to:`,
            inputLabel: 'Destination Path:',
            inputValue: path, // Default to same directory
            confirmLabel: 'Move',
            cancelLabel: 'Cancel',
            onConfirm: function (destinationPath) {
                fetch('/file/move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        source: path,
                        destination: destinationPath
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`File moved successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to move file', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error moving file:', error);
                        UIControls.showNotification('Error moving file', 'error');
                    });
            }
        });
    },

    /**
     * Rename a file
     * @param {string} path - File path
     * @param {string} name - Current file name
     */
    renameFile: function (path, name) {
        UIControls.showDialog({
            title: 'Rename File',
            message: `Rename "${name}" to:`,
            inputLabel: 'New Name:',
            inputValue: name,
            confirmLabel: 'Rename',
            cancelLabel: 'Cancel',
            onConfirm: function (newName) {
                fetch('/file/rename', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: path,
                        new_name: newName
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`File renamed successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to rename file', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error renaming file:', error);
                        UIControls.showNotification('Error renaming file', 'error');
                    });
            }
        });
    },

    /**
     * Delete a file
     * @param {string} path - File path
     * @param {string} name - File name
     */
    deleteFile: function (path, name) {
        UIControls.showDialog({
            title: 'Delete File',
            message: `Are you sure you want to delete "${name}"?`,
            confirmLabel: 'Delete',
            cancelLabel: 'Cancel',
            isAlert: true,
            onConfirm: function () {
                fetch('/file/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: path,
                        use_trash: true
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`File deleted successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to delete file', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting file:', error);
                        UIControls.showNotification('Error deleting file', 'error');
                    });
            }
        });
    },

    /**
     * Create a new folder
     * @param {string} currentPath - Current directory path
     */
    createFolder: function (currentPath) {
        UIControls.showDialog({
            title: 'Create Folder',
            message: 'Enter folder name:',
            inputLabel: 'Folder Name:',
            inputValue: 'New Folder',
            confirmLabel: 'Create',
            cancelLabel: 'Cancel',
            onConfirm: function (folderName) {
                const newPath = currentPath + '/' + folderName;

                fetch('/file/create_folder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: newPath
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`Folder created successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to create folder', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error creating folder:', error);
                        UIControls.showNotification('Error creating folder', 'error');
                    });
            }
        });
    },

    /**
     * Create a new file
     * @param {string} currentPath - Current directory path
     */
    createFile: function (currentPath) {
        UIControls.showDialog({
            title: 'Create File',
            message: 'Enter file name:',
            inputLabel: 'File Name:',
            inputValue: 'New File.txt',
            confirmLabel: 'Create',
            cancelLabel: 'Cancel',
            onConfirm: function (fileName) {
                const newPath = currentPath + '/' + fileName;

                fetch('/file/create_file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: newPath,
                        content: ''
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            UIControls.showNotification(`File created successfully`, 'success');
                            // Refresh the current view
                            SearchUI.performSearch();
                        } else {
                            UIControls.showNotification(data.message || 'Failed to create file', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Error creating file:', error);
                        UIControls.showNotification('Error creating file', 'error');
                    });
            }
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    FileOperations.init();
});