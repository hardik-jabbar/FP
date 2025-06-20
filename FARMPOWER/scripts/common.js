/**
 * Common JavaScript for FarmPower
 * Handles loading common components like header and footer
 */

// Load common components when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    loadCommonComponents();
    // Check authentication state after components are loaded
    if (typeof checkAuth === 'function') {
        checkAuth();
    }
});

/**
 * Loads common components (header, footer, etc.)
 */
async function loadCommonComponents() {
    try {
        // Load header
        const headerResponse = await fetch('components/header.html');
        if (headerResponse.ok) {
            const headerHtml = await headerResponse.text();
            const headerElement = document.getElementById('header');
            if (headerElement) {
                headerElement.innerHTML = headerHtml;
                // Initialize cart count if cart.js is loaded
                if (typeof cart !== 'undefined' && typeof cart.updateCartCount === 'function') {
                    cart.updateCartCount();
                }
            }
        }

        // Load footer if element exists
        const footerElement = document.getElementById('footer');
        if (footerElement) {
            const footerResponse = await fetch('components/footer.html');
            if (footerResponse.ok) {
                const footerHtml = await footerResponse.text();
                footerElement.innerHTML = footerHtml;
            }
        }
    } catch (error) {
        console.error('Error loading common components:', error);
    }
}

// Make functions available globally
window.Common = {
    loadCommonComponents
};
