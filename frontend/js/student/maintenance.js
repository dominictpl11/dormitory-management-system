// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

async function loadMaintenanceTypes() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/maintenance-types`);
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('maintenance-type');
            select.innerHTML = '<option value="">Select type...</option>';
            data.forEach(type => {
                const option = document.createElement('option');
                option.value = type.type_id;
                option.textContent = `${type.type_name} (¥${type.cost})`;
                select.appendChild(option);
            });
        } else {
            console.error('Failed to load maintenance types:', data.error);
            document.getElementById('maintenance-type').innerHTML = 
                '<option value="">Failed to load types. Please refresh the page.</option>';
        }
    } catch (error) {
        console.error('Load maintenance types error:', error);
        document.getElementById('maintenance-type').innerHTML = 
            '<option value="">Error loading types. Please refresh the page.</option>';
    }
}

function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'approved': 'status-approved',
        'rejected': 'status-rejected',
        'completed': 'status-approved',
        'cancelled': 'status-cancelled'
    };
    return statusMap[status] || '';
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
}

async function submitMaintenanceRequest() {
    const typeId = document.getElementById('maintenance-type').value;
    const description = document.getElementById('description').value;
    
    if (!typeId || !description) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/maintenances`, {
            method: 'POST',
            body: JSON.stringify({
                type_id: parseInt(typeId),
                description: description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Maintenance request submitted successfully!');
            document.getElementById('maintenance-form').reset();
            loadMaintenanceRequests();
        } else {
            alert('Submit failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Submit maintenance error:', error);
        alert('System error, please try again');
    }
}

async function loadMaintenanceRequests() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/maintenances`);
        const data = await response.json();
        
        if (response.ok) {
            const requestsDiv = document.getElementById('maintenance-requests');
            
            if (data.length === 0) {
                requestsDiv.innerHTML = '<p class="text-muted">No requests found</p>';
                return;
            }
            
            requestsDiv.innerHTML = data.map(req => `
                <div class="card-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span><strong>Request ID:</strong> ${req.maintenance_id}</span>
                        <span class="status-badge ${getStatusClass(req.status)}">${getStatusText(req.status)}</span>
                    </div>
                    <p><strong>Type:</strong> ${req.type_name || 'N/A'}</p>
                    <p><strong>Description:</strong> ${req.description}</p>
                    <p><strong>Request Date:</strong> ${req.request_date || 'N/A'}</p>
                    ${req.processed_date ? `<p><strong>Processed Date:</strong> ${req.processed_date}</p>` : ''}
                    ${req.status === 'pending' ? `
                        <div>
                            <button class="btn btn-warning btn-sm" onclick="editRequest(${req.maintenance_id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="cancelRequest(${req.maintenance_id})">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load maintenance requests error:', error);
        document.getElementById('maintenance-requests').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

async function cancelRequest(maintenanceId) {
    if (!confirm('Are you sure you want to cancel this request?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/maintenances/${maintenanceId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Request cancelled successfully!');
            loadMaintenanceRequests();
        } else {
            alert('Cancel failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Cancel request error:', error);
        alert('System error, please try again');
    }
}

async function editRequest(maintenanceId) {
    // Simple edit - in production, use a modal
    const newDescription = prompt('Enter new description:');
    if (!newDescription) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/maintenances/${maintenanceId}`, {
            method: 'PUT',
            body: JSON.stringify({ description: newDescription })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Request updated successfully!');
            loadMaintenanceRequests();
        } else {
            alert('Update failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Edit request error:', error);
        alert('System error, please try again');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'student') {
        window.location.href = '../index.html';
        return;
    }
    
    loadMaintenanceTypes();
    loadMaintenanceRequests();
    
    document.getElementById('maintenance-form').addEventListener('submit', (e) => {
        e.preventDefault();
        submitMaintenanceRequest();
    });
});

