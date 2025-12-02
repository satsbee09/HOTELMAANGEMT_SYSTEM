// Dark Mode Toggle Functionality
class DarkModeManager {
    constructor() {
        this.init();
    }

    init() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Create and add toggle button
        this.createToggleButton();
        
        // Add event listeners
        this.addEventListeners();
    }

    createToggleButton() {
        // Check if button already exists
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        const toggleButton = document.createElement('button');
        toggleButton.className = 'theme-toggle';
        toggleButton.innerHTML = `
            <span class="icon">🌙</span>
            <span class="text">Dark Mode</span>
        `;
        toggleButton.setAttribute('aria-label', 'Toggle dark mode');
        toggleButton.setAttribute('title', 'Toggle dark/light mode');
        
        document.body.appendChild(toggleButton);
        
        // Update button based on current theme
        this.updateToggleButton();
    }

    addEventListeners() {
        // Toggle button click event
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle')) {
                this.toggleTheme();
            }
        });

        // Keyboard accessibility
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('.theme-toggle') && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        // Set theme on document element
        document.documentElement.setAttribute('data-theme', theme);
        
        // Save preference to localStorage
        localStorage.setItem('theme', theme);
        
        // Update toggle button
        this.updateToggleButton();
        
        // Dispatch custom event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme }
        }));
    }

    updateToggleButton() {
        const toggleButton = document.querySelector('.theme-toggle');
        if (!toggleButton) return;

        const currentTheme = document.documentElement.getAttribute('data-theme');
        const icon = toggleButton.querySelector('.icon');
        const text = toggleButton.querySelector('.text');

        if (currentTheme === 'dark') {
            icon.textContent = '☀️';
            text.textContent = 'Light Mode';
            toggleButton.setAttribute('title', 'Switch to light mode');
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Dark Mode';
            toggleButton.setAttribute('title', 'Switch to dark mode');
        }
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    // Method to programmatically set theme
    setDarkMode(isDark) {
        this.setTheme(isDark ? 'dark' : 'light');
    }

    // Method to check if dark mode is active
    isDarkMode() {
        return this.getCurrentTheme() === 'dark';
    }
}

// Auto-detect system preference if no saved preference exists
function getSystemThemePreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Initialize dark mode when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode manager
    window.darkModeManager = new DarkModeManager();
    
    // Add smooth transition class after initial load to prevent flash
    setTimeout(() => {
        document.body.classList.add('theme-transitions-enabled');
    }, 100);
});

// Prevent flash of unstyled content
(function() {
    // Apply theme immediately before DOM loads
    const savedTheme = localStorage.getItem('theme') || getSystemThemePreference();
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

// Export for use in other scripts if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DarkModeManager;
}
