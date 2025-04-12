// fastique/app/static/js/ui_controls.js
// UI controls and utility functions

/**
 * UI Controls for notifications, dialogs, and other UI elements
 */
const UIControls = {
    /**
     * Initialize UI controls
     */
    init: function () {
        // Create notification container if it doesn't exist
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
        }

        // Create dialog container if it doesn't exist
        if (!document.getElementById('dialog-container')) {
            const container = document.createElement('div');
            container.id = 'dialog-container';
            document.body.appendChild(container);
        }

        // Initialize any other UI elements
        this.initThemeToggle();
        this.initSidebarToggle();
        this.initResizablePreview();
    },

    /**
     * Initialize theme toggle functionality
     */
    initThemeToggle: function () {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            // Check for saved theme preference or use system preference
            const savedTheme = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

            // Apply initial theme
            if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
                document.body.classList.add('dark-theme');
                themeToggle.textContent = '☀️'; // Sun emoji for toggling to light
            } else {
                themeToggle.textContent = '🌙'; // Moon emoji for toggling to dark
            }

            // Add toggle event
            themeToggle.addEventListener('click', function () {
                if (document.body.classList.contains('dark-theme')) {
                    document.body.classList.remove('dark-theme');
                    localStorage.setItem('theme', 'light');
                    themeToggle.textContent = '🌙';
                } else {
                    document.body.classList.add('dark-theme');
                    localStorage.setItem('theme', 'dark');
                    themeToggle.textContent = '☀️';
                }
            });
        }
    },

    /**
     * Initialize sidebar toggle functionality
     */
    initSidebarToggle: function () {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function () {
                sidebar.classList.toggle('collapsed');

                // Update toggle icon
                const isCollapsed = sidebar.classList.contains('collapsed');
                sidebarToggle.textContent = isCollapsed ? '▶' : '◀';

                // Save state in localStorage
                localStorage.setItem('sidebar-collapsed', isCollapsed ? 'true' : 'false');
            });

            // Apply saved state
            const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
                sidebarToggle.textContent = '▶';
            }
        }
    },

    /**
     * Initialize resizable preview panel
     */
    initResizablePreview: function () {
        const resizer = document.getElementById('preview-resizer');
        const previewPanel = document.getElementById('preview-panel');

        if (resizer && previewPanel) {
            let startX, startWidth;

            resizer.addEventListener('mousedown', function (e) {
                startX = e.clientX;
                startWidth = parseInt(document.defaultView.getComputedStyle(previewPanel).width, 10);
                document.documentElement.style.cursor = 'ew-resize';

                document.addEventListener('mousemove', resize);
                document.addEventListener('mouseup', stopResize);

                e.preventDefault(); // Prevent text selection
            });

            function resize(e) {
                const width = startWidth - (e.clientX - startX);
                if (width > 200) { // Minimum width
                    previewPanel.style.width = width + 'px';
                }
            }

            function stopResize() {
                document.documentElement.style.cursor = '';
                document.removeEventListener('mousemove', resize);
                document.removeEventListener('mouseup', stopResize);

                // Save width in localStorage
                const currentWidth = parseInt(document.defaultView.getComputedStyle(previewPanel).width, 10);
                localStorage.setItem('preview-width', currentWidth);
            }

            // Apply saved width
            const savedWidth = localStorage.getItem('preview-width');
            if (savedWidth) {
                previewPanel.style.width = savedWidth + 'px';
            }
        }
    },

    /**
     * Show a notification
     * @param {string} message - Notification message
     * @param {string} type - Notification type (success, error, info)
     * @param {number} duration - Duration in milliseconds (default 3000)
     */
    showNotification: function (message, type = 'info', duration = 3000) {
        const container = document.getElementById('notification-container');

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', function () {
            container.removeChild(notification);
        });
        notification.appendChild(closeBtn);

        // Add to container
        container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode === container) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode === container) {
                            container.removeChild(notification);
                        }
                    }, 300); // Allow time for fade out animation
                }
            }, duration);
        }

        return notification;
    },

    /**
     * Show a dialog
     * @param {Object} options - Dialog options
     * @param {string} options.title - Dialog title
     * @param {string} options.message - Dialog message
     * @param {string} options.inputLabel - Label for input field (if input dialog)
     * @param {string} options.inputValue - Default value for input field
     * @param {string} options.confirmLabel - Label for confirm button
     * @param {string} options.cancelLabel - Label for cancel button
     * @param {boolean} options.isAlert - If true, style as an alert/warning
     * @param {Function} options.onConfirm - Callback for confirm button
     * @param {Function} options.onCancel - Callback for cancel button
     * @returns {HTMLElement} The dialog element
     */
    showDialog: function (options) {
        const container = document.getElementById('dialog-container');

        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'dialog-backdrop';

        // Create dialog
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        if (options.isAlert) {
            dialog.classList.add('dialog-alert');
        }

        // Build dialog content
        let dialogHTML = `
            <div class="dialog-header">
                <h3>${options.title || 'Dialog'}</h3>
                <button class="dialog-close">&times;</button>
            </div>
            <div class="dialog-body">
                <p>${options.message || ''}</p>
        `;

        // Add input field if specified
        if (options.inputLabel) {
            dialogHTML += `
                <div class="dialog-input-group">
                    <label for="dialog-input">${options.inputLabel}</label>
                    <input type="text" id="dialog-input" value="${options.inputValue || ''}">
                </div>
            `;
        }

        dialogHTML += `
            </div>
            <div class="dialog-footer">
                <button class="btn btn-secondary dialog-cancel">${options.cancelLabel || 'Cancel'}</button>
                <button class="btn btn-primary dialog-confirm">${options.confirmLabel || 'OK'}</button>
            </div>
        `;

        dialog.innerHTML = dialogHTML;

        // Add to container
        backdrop.appendChild(dialog);
        container.appendChild(backdrop);

        // Animate in
        setTimeout(() => {
            backdrop.classList.add('show');
            dialog.classList.add('show');
        }, 10);

        // Focus input if present
        setTimeout(() => {
            const input = dialog.querySelector('#dialog-input');
            if (input) {
                input.focus();
                input.select();
            } else {
                dialog.querySelector('.dialog-confirm').focus();
            }
        }, 100);

        // Handle close button
        dialog.querySelector('.dialog-close').addEventListener('click', closeDialog);

        // Handle cancel button
        dialog.querySelector('.dialog-cancel').addEventListener('click', () => {
            if (typeof options.onCancel === 'function') {
                options.onCancel();
            }
            closeDialog();
        });

        // Handle confirm button
        dialog.querySelector('.dialog-confirm').addEventListener('click', () => {
            if (typeof options.onConfirm === 'function') {
                const input = dialog.querySelector('#dialog-input');
                if (input) {
                    options.onConfirm(input.value);
                } else {
                    options.onConfirm();
                }
            }
            closeDialog();
        });

        // Handle enter key for confirm
        dialog.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                dialog.querySelector('.dialog-confirm').click();
            } else if (e.key === 'Escape') {
                e.preventDefault();
                dialog.querySelector('.dialog-cancel').click();
            }
        });

        // Function to close dialog
        function closeDialog() {
            backdrop.classList.remove('show');
            dialog.classList.remove('show');

            // Remove after animation
            setTimeout(() => {
                if (backdrop.parentNode === container) {
                    container.removeChild(backdrop);
                }
            }, 300);
        }

        return dialog;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    UIControls.init();
});