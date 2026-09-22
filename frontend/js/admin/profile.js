// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

async function loadProfile() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/profile`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('admin-id').value = data.admin_id;
            document.getElementById('name').value = data.name;
            document.getElementById('email').value = data.email;
            document.getElementById('phone').value = data.phone || '';
        } else {
            alert('Failed to load profile: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Load profile error:', error);
        alert('System error, please try again');
    }
}

async function updateProfile() {
    const phone = document.getElementById('phone').value;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/profile`, {
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

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'admin') {
        window.location.href = '../index.html';
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

