// Authentication functions
// Define API_BASE_URL globally to avoid duplicate declarations
// Use relative path or detect current origin to avoid CORS issues
var API_BASE_URL = window.location.origin + '/api';
window.API_BASE_URL = API_BASE_URL;

// Check authentication on page load
function checkAuth() {
    const token = sessionStorage.getItem('token');
    const role = sessionStorage.getItem('role');
    
    if (token && role) {
        // Redirect based on role
        if (role === 'student') {
            window.location.href = 'student/dashboard.html';
        } else if (role === 'admin') {
            window.location.href = 'admin/dashboard.html';
        }
    }
}

// Login function
async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token and role in sessionStorage (each tab is independent)
            sessionStorage.setItem('token', data.access_token);
            sessionStorage.setItem('role', data.role);
            sessionStorage.setItem('user_id', data.user_id);
            
            // Redirect based on role
            if (data.role === 'student') {
                window.location.href = 'student/dashboard.html';
            } else {
                window.location.href = 'admin/dashboard.html';
            }
        } else {
            showError(data.error || 'Login failed');
        }
    } catch (error) {
        showError('Login failed. Please try again.');
        console.error('Login error:', error);
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }
}

// Fetch with authentication
async function fetchWithAuth(url, options = {}) {
    const token = sessionStorage.getItem('token');
    
    if (!token) {
        console.error('No token found, redirecting to login');
        // Determine correct path based on current location
        const currentPath = window.location.pathname;
        if (currentPath.includes('/student/') || currentPath.includes('/admin/')) {
            window.location.href = '../index.html';
        } else {
            window.location.href = 'index.html';
        }
        return Promise.reject(new Error('Not authenticated'));
    }
    
    const headers = {
        ...options.headers,
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
    
    try {
        console.log('Making authenticated request to:', url);
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        console.log('Response status:', response.status);
        
        // Handle unauthorized
        if (response.status === 401) {
            console.error('Unauthorized, clearing token and redirecting');
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('role');
            sessionStorage.removeItem('user_id');
            const currentPath = window.location.pathname;
            if (currentPath.includes('/student/') || currentPath.includes('/admin/')) {
                window.location.href = '../index.html';
            } else {
                window.location.href = 'index.html';
            }
            return Promise.reject(new Error('Unauthorized'));
        }
        
        return response;
    } catch (error) {
        console.error('Request error:', error);
        throw error;
    }
}

// Make fetchWithAuth available globally
window.fetchWithAuth = fetchWithAuth;

// Logout function
function logout() {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('user_id');
    window.location.href = '../index.html';
}

// Login form handler
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        await login(username, password);
    });
}

// Check auth on page load (for login page)
if (window.location.pathname.includes('index.html')) {
    checkAuth();
    // Clear input fields on page load
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    if (usernameInput) usernameInput.value = '';
    if (passwordInput) passwordInput.value = '';
}

