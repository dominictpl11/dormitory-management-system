// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'approved': 'status-approved',
        'rejected': 'status-rejected',
        'completed': 'status-approved'
    };
    return statusMap[status] || '';
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'completed': 'Completed'
    };
    return statusMap[status] || status;
}

async function loadMaintenances() {
    const status = document.getElementById('status-filter').value;
    const url = status 
        ? `${API_BASE_URL}/admin/maintenances?status=${status}`
        : `${API_BASE_URL}/admin/maintenances`;
    
    try {
        const response = await fetchWithAuth(url);
        const data = await response.json();
        
        if (response.ok) {
            const listDiv = document.getElementById('maintenance-list');
            
            if (data.length === 0) {
                listDiv.innerHTML = '<p class="text-muted">No requests found</p>';
                return;
            }
            
            listDiv.innerHTML = data.map(req => `
                <div class="card-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span><strong>Request ID:</strong> ${req.maintenance_id}</span>
                        <span class="status-badge ${getStatusClass(req.status)}">${getStatusText(req.status)}</span>
                    </div>
                    <p><strong>Student:</strong> ${req.student_name} (${req.student_id})</p>
                    <p><strong>Dormitory:</strong> ${req.building_id || 'N/A'} - ${req.room_no || 'N/A'}</p>
                    <p><strong>Type:</strong> ${req.type_name || 'N/A'}</p>
                    <p><strong>Description:</strong> ${req.description}</p>
                    <p><strong>Request Date:</strong> ${req.request_date || 'N/A'}</p>
                    ${req.processed_date ? `<p><strong>Processed Date:</strong> ${req.processed_date}</p>` : ''}
                    ${req.status === 'pending' ? `
                        <div>
                            <button class="btn btn-success btn-sm" onclick="processRequest(${req.maintenance_id}, 'approved')">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="processRequest(${req.maintenance_id}, 'rejected')">
                                <i class="fas fa-times"></i> Reject
                            </button>
                        </div>
                    ` : req.status === 'approved' ? `
                        <button class="btn btn-primary btn-sm" onclick="processRequest(${req.maintenance_id}, 'completed')">
                            <i class="fas fa-check-circle"></i> Mark as Completed
                        </button>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load maintenances error:', error);
        document.getElementById('maintenance-list').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

async function processRequest(maintenanceId, status) {
    const action = status === 'approved' ? 'approve' : status === 'rejected' ? 'reject' : 'complete';
    if (!confirm(`Are you sure you want to ${action} this request?`)) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/maintenances/${maintenanceId}`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Request ${action}d successfully!`);
            loadMaintenances();
        } else {
            alert('Process failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Process request error:', error);
        alert('System error, please try again');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'admin') {
        window.location.href = '../index.html';
        return;
    }
    
    loadMaintenances();
});

