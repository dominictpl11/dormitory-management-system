// Use API_BASE_URL from auth.js (loaded before this file)
// Use the global variable directly, don't redeclare
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

// Load profile
async function loadProfile() {
    try {
        console.log('Loading profile...');
        const response = await fetchWithAuth(`${API_BASE_URL}/student/profile`);
        console.log('Response status:', response.status);
        
        const data = await response.json();
        console.log('Profile data:', data);
        
        if (response.ok) {
            document.getElementById('student-id').value = data.student_id || '';
            document.getElementById('name').value = data.name || '';
            document.getElementById('email').value = data.email || '';
            document.getElementById('phone').value = data.phone || '';
            document.getElementById('gender').value = data.gender || '';
            document.getElementById('major').value = data.major || '';
            console.log('Profile loaded successfully');
        } else {
            console.error('Failed to load profile:', data);
            alert('Failed to load profile: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Load profile error:', error);
        alert('System error, please try again. Check console for details.');
    }
}

// Update profile
async function updateProfile() {
    const phone = document.getElementById('phone').value;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/profile`, {
            method: 'PUT',
            body: JSON.stringify({ phone })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Profile updated successfully!');
        } else {
            alert('Update failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Update profile error:', error);
        alert('System error, please try again');
    }
}

// Change password
async function changePassword() {
    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    if (newPassword !== confirmPassword) {
        alert('New passwords do not match');
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/auth/password`, {
            method: 'PUT',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Password changed successfully!');
            document.getElementById('password-form').reset();
        } else {
            alert('Change password failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Change password error:', error);
        alert('System error, please try again');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('Profile page loaded');
    console.log('Token:', sessionStorage.getItem('token') ? 'Exists' : 'Missing');
    console.log('Role:', sessionStorage.getItem('role'));
    
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'student') {
        console.log('Redirecting to login...');
        window.location.href = '../index.html';
        return;
    }
    
    // Check if fetchWithAuth is available
    if (typeof fetchWithAuth === 'undefined') {
        console.error('fetchWithAuth is not defined! Make sure auth.js is loaded before profile.js');
        alert('Error: Authentication functions not loaded. Please refresh the page.');
        return;
    }
    
    loadProfile();
    
    document.getElementById('profile-form').addEventListener('submit', (e) => {
        e.preventDefault();
        updateProfile();
    });
    
    document.getElementById('password-form').addEventListener('submit', (e) => {
        e.preventDefault();
        changePassword();
    });
});

