document.addEventListener('DOMContentLoaded', () => {
  // Toggle mobile menu
  window.toggleMobileMenu = function() {
    const mobileMenu = document.getElementById('mobileMenu');
    mobileMenu.classList.toggle('translate-x-full');
  };

  // Toggle user dropdown
  window.toggleUserMenu = function() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('hidden');
  };

  // Close dropdowns when clicking outside
  document.addEventListener('click', (e) => {
    const userMenu = document.getElementById('userMenu');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenu && !userMenu.contains(e.target)) {
      userDropdown.classList.add('hidden');
    }
  });

  // Handle authentication state
  window.updateAuthState = function(isLoggedIn, userData = null) {
    const userMenu = document.getElementById('userMenu');
    const authButtons = document.getElementById('authButtons');
    
    if (userMenu && authButtons) {
      if (isLoggedIn && userData) {
        userMenu.classList.remove('hidden');
        authButtons.classList.add('hidden');
        
        // Update user info
        const userName = document.getElementById('userName');
        const userAvatar = document.getElementById('userAvatar');
        if (userName) userName.textContent = userData.name;
        if (userAvatar && userData.avatar) {
          userAvatar.src = userData.avatar;
        }
      } else {
        userMenu.classList.add('hidden');
        authButtons.classList.remove('hidden');
      }
    }
  };

  // Check authentication state on page load
  window.checkAuth = async function() {
    try {
      const response = await fetch('/api/user/me');
      if (response.ok) {
        const userData = await response.json();
        updateAuthState(true, userData);
      } else {
        updateAuthState(false);
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      updateAuthState(false);
    }
  };

  // Logout function
  window.logout = async function() {
    try {
      await fetch('/api/logout', { method: 'POST' });
      updateAuthState(false);
      window.location.href = "login.html";
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  // Initialize
  checkAuth();
}); 