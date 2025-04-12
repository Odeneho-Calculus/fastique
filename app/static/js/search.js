// fastique/app/static/js/search.js
// Handles search functionality and results display

document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const searchPaths = document.getElementById('search-paths');
    const resultsContainer = document.getElementById('results-container');
    const resultsCount = document.getElementById('results-count');
    const loadingIndicator = document.getElementById('loading-indicator');
    const advancedOptions = document.getElementById('advanced-options');
    const advancedToggle = document.getElementById('advanced-toggle');

    // Search state
    let searchTimeout;
    let currentSearch = '';
    let isSearching = false;

    // Initialize
    function init() {
        // Add event listeners
        searchForm.addEventListener('submit', handleSearch);
        searchInput.addEventListener('input', debounceSearch);
        advancedToggle.addEventListener('click', toggleAdvancedOptions);

        // Setup path selection
        initializePaths();
    }

    // Initialize path selection
    function initializePaths() {
        // Get paths from server-side data or localStorage
        const savedPaths = localStorage.getItem('fastique-paths');
        if (savedPaths) {
            const paths = JSON.parse(savedPaths);
            paths.forEach(path => {
                if (!pathExists(path)) {
                    addPathOption(path);
                }
            });
        }

        // Setup add path button
        const addPathButton = document.getElementById('add-path-button');
        if (addPathButton) {
            addPathButton.addEventListener('click', function () {
                // Using a fake file input to trigger directory selector
                // In a real app with proper permissions, you'd use showDirectoryPicker
                // or a similar API, but for this demo we'll use a simple prompt
                const path = prompt('Enter directory path:');
                if (path) {
                    addPathOption(path);
                    savePathsToLocalStorage();
                }
            });
        }
    }

    // Check if path already exists in options
    function pathExists(path) {
        const options = searchPaths.querySelectorAll('option');
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === path) {
                return true;
            }
        }
        return false;
    }

    // Add path option to select
    function addPathOption(path) {
        const option = document.createElement('option');
        option.value = path;
        option.textContent = path;
        searchPaths.appendChild(option);
    }

    // Save paths to localStorage
    function savePathsToLocalStorage() {
        const paths = [];
        const options = searchPaths.querySelectorAll('option');
        options.forEach(option => {
            paths.push(option.value);
        });
        localStorage.setItem('fastique-paths', JSON.stringify(paths));
    }

    // Toggle advanced options
    function toggleAdvancedOptions() {
        advancedOptions.classList.toggle('hidden');
        if (advancedOptions.classList.contains('hidden')) {
            advancedToggle.textContent = 'Show Advanced Options';
        } else {
            advancedToggle.textContent = 'Hide Advanced Options';
        }
    }

    // Debounce search to avoid too many requests
    function debounceSearch() {
        clearTimeout(searchTimeout);

        // Don't search if input is too short
        if (searchInput.value.length < 2) {
            return;
        }

        searchTimeout = setTimeout(function () {
            handleSearch(null, true);
        }, 300);
    }

    // Handle search form submission
    function handleSearch(event, isDebounced = false) {
        if (event) {
            event.preventDefault();
        }

        // Don't search if already searching or if the search is the same
        if (isSearching || (isDebounced && searchInput.value === currentSearch)) {
            return;
        }

        currentSearch = searchInput.value;

        // Don't search if input is empty
        if (!currentSearch.trim()) {
            return;
        }

        // Show loading indicator
        isSearching = true;
        loadingIndicator.classList.remove('hidden');

        // Get search parameters
        const searchParams = {
            query: currentSearch,
            paths: Array.from(searchPaths.selectedOptions).map(option => option.value),
        };

        // Add advanced options if they're visible
        if (!advancedOptions.classList.contains('hidden')) {
            searchParams.file_types = getSelectedFileTypes();
            searchParams.case_sensitive = document.getElementById('case-sensitive').checked;
            searchParams.include_hidden = document.getElementById('include-hidden').checked;
            searchParams.use_regex = document.getElementById('use-regex').checked;

            // Get date range if specified
            const dateFrom = document.getElementById('date-from').value;
            const dateTo = document.getElementById('date-to').value;
            if (dateFrom || dateTo) {
                searchParams.date_range = [dateFrom, dateTo];
            }

            // Get size range if specified
            const sizeMin = document.getElementById('size-min').value;
            const sizeMax = document.getElementById('size-max').value;
            const sizeUnit = document.getElementById('size-unit').value;

            if (sizeMin || sizeMax) {
                // Convert to bytes based on unit
                const multiplier = getByteMultiplier(sizeUnit);
                searchParams.size_range = [
                    sizeMin ? parseFloat(sizeMin) * multiplier : 0,
                    sizeMax ? parseFloat(sizeMax) * multiplier : Number.MAX_SAFE_INTEGER
                ];
            }
        }

        // Send search request
        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(searchParams)
        })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                displayError('An error occurred while searching. Please try again.');
            })
            .finally(() => {
                isSearching = false;
                loadingIndicator.classList.add('hidden');
            });
    }

    // Get selected file types
    function getSelectedFileTypes() {
        const fileTypeCheckboxes = document.querySelectorAll('input[name="file-type"]:checked');
        return Array.from(fileTypeCheckboxes).map(checkbox => checkbox.value);
    }

    // Get byte multiplier based on unit
    function getByteMultiplier(unit) {
        switch (unit) {
            case 'KB': return 1024;
            case 'MB': return 1024 * 1024;
            case 'GB': return 1024 * 1024 * 1024;
            default: return 1; // Bytes
        }
    }

    // Display search results
    function displayResults(data) {
        // Clear previous results
        resultsContainer.innerHTML = '';

        // Update results count
        resultsCount.textContent = `${data.results.length} results found`;

        // Check if we have results
        if (data.results.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results">No results found</div>';
            return;
        }

        // Create results list
        const resultsList = document.createElement('div');
        resultsList.className = 'results-list';

        // Add results
        data.results.forEach(result => {
            const resultItem = createResultItem(result);
            resultsList.appendChild(resultItem);
        });

        // Add to container
        resultsContainer.appendChild(resultsList);
    }

    // Create a result item element
    function createResultItem(result) {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.dataset.path = result.full_path;

        // Add icon based on file type
        const iconClass = result.icon_class || (result.is_directory ? 'folder-icon' : 'file-icon');

        // Create HTML structure
        item.innerHTML = `
            <div class="result-icon ${iconClass}"></div>
            <div class="result-details">
                <div class="result-filename">${result.filename}</div>
                <div class="result-path">${result.path}</div>
                <div class="result-meta">
                    <span class="result-size">${result.size_formatted}</span>
                    <span class="result-date">${result.modified_time_formatted}</span>
                </div>
            </div>
            <div class="result-actions">
                <button class="action-button open-button" title="Open">Open</button>
                <button class="action-button menu-button" title="More Actions">⋮</button>
            </div>
        `;

        // Add event listeners
        item.querySelector('.open-button').addEventListener('click', function (e) {
            e.stopPropagation();
            openFile(result.full_path);
        });

        item.querySelector('.menu-button').addEventListener('click', function (e) {
            e.stopPropagation();
            showActionMenu(e, result);
        });

        // Double-click to open
        item.addEventListener('dblclick', function () {
            openFile(result.full_path);
        });

        return item;
    }

    // Open file or directory
    function openFile(path) {
        fetch('/file-operations/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: path })
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    displayError(data.error || 'Failed to open file');
                }
            })
            .catch(error => {
                console.error('Error opening file:', error);
                displayError('An error occurred while opening the file.');
            });
    }

    // Show action menu for a result
    function showActionMenu(event, result) {
        // Remove any existing menus
        const existingMenu = document.querySelector('.action-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Create menu
        const menu = document.createElement('div');
        menu.className = 'action-menu';

        // Add menu items
        const actions = [
            { name: 'Copy', icon: '📋', action: () => copyFile(result) },
            { name: 'Move', icon: '✂️', action: () => moveFile(result) },
            { name: 'Rename', icon: '✏️', action: () => renameFile(result) },
            { name: 'Delete', icon: '🗑️', action: () => deleteFile(result) },
            { name: 'Properties', icon: 'ℹ️', action: () => showProperties(result) }
        ];

        actions.forEach(action => {
            const item = document.createElement('div');
            item.className = 'menu-item';
            item.innerHTML = `<span class="menu-icon">${action.icon}</span> ${action.name}`;
            item.addEventListener('click', function () {
                menu.remove();
                action.action();
            });
            menu.appendChild(item);
        });

        // Position menu
        const rect = event.target.getBoundingClientRect();
        menu.style.top = `${rect.bottom}px`;
        menu.style.left = `${rect.left}px`;

        // Add to document
        document.body.appendChild(menu);

        // Close menu when clicking outside
        document.addEventListener('click', function closeMenu(e) {
            if (!menu.contains(e.target) && e.target !== event.target) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        });
    }

    // Display error message
    function displayError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        document.body.appendChild(errorDiv);

        // Remove after a few seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Initialize the module
    init();

    // Export public methods (for other modules to use)
    window.SearchModule = {
        search: handleSearch,
        refreshResults: function () {
            if (currentSearch) {
                handleSearch(null);
            }
        }
    };
});