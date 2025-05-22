/**
 * Main JavaScript file for the MLB Statistics Visualizer
 * Handles common functionality across the application
 */

// Set up global chart defaults
if (window.Chart) {
    Chart.defaults.font.family = "'Segoe UI', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.font.size = 14;
    Chart.defaults.color = '#666';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    Chart.defaults.plugins.legend.position = 'top';
    
    // Custom color scheme for charts
    window.chartColors = {
        primary: 'rgb(0, 123, 255)',
        success: 'rgb(40, 167, 69)',
        danger: 'rgb(220, 53, 69)',
        warning: 'rgb(255, 193, 7)',
        info: 'rgb(23, 162, 184)',
        secondary: 'rgb(108, 117, 125)',
        avg: 'rgb(75, 192, 192)',
        ops: 'rgb(255, 99, 132)',
        obp: 'rgb(54, 162, 235)',
        slg: 'rgb(255, 159, 64)',
        hr: 'rgb(255, 99, 132)',
        hit: 'rgb(75, 192, 192)',
        ab: 'rgb(54, 162, 235)',
        bb: 'rgb(255, 206, 86)',
        k: 'rgb(153, 102, 255)',
        rbi: 'rgb(255, 159, 64)'
    };
}

/**
 * Format a number to a specific number of decimal places
 * @param {number} value - The value to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
function formatNumber(value, decimals = 3) {
    if (value === null || value === undefined || isNaN(value)) {
        return '-';
    }
    return Number(value).toFixed(decimals);
}

/**
 * Format a date string to a more readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Toggle loading state on an element
 * @param {HTMLElement} element - The element to toggle loading state
 * @param {boolean} isLoading - Whether to show loading state
 */
function toggleLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
    } else {
        element.classList.remove('loading');
    }
}

/**
 * Highlight a stat value based on its performance level
 * @param {number} value - The stat value
 * @param {number} threshold - Threshold for good performance
 * @param {boolean} higherIsBetter - Whether higher values are better
 * @returns {string} CSS class for highlighting
 */
function getStatHighlight(value, threshold, higherIsBetter = true) {
    if (value === null || value === undefined || isNaN(value)) {
        return '';
    }
    
    if (higherIsBetter) {
        return value >= threshold ? 'high-stat' : (value < threshold / 2 ? 'low-stat' : '');
    } else {
        return value <= threshold ? 'high-stat' : (value > threshold * 2 ? 'low-stat' : '');
    }
}

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    // Add Font Awesome if it's not already loaded (for icons)
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css';
        document.head.appendChild(link);
    }
    
    // Set up tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Format dates in the document
    document.querySelectorAll('.format-date').forEach(function(element) {
        const dateString = element.textContent;
        element.textContent = formatDate(dateString);
    });
    
    // Apply stat highlighting
    document.querySelectorAll('.highlight-avg').forEach(function(element) {
        const value = parseFloat(element.textContent);
        element.classList.add(getStatHighlight(value, 0.300));
    });
    
    document.querySelectorAll('.highlight-ops').forEach(function(element) {
        const value = parseFloat(element.textContent);
        element.classList.add(getStatHighlight(value, 0.800));
    });
});