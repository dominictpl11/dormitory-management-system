// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'approved': 'status-approved',
        'rejected': 'status-rejected'
    };
    return statusMap[status] || '';
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected'
    };
    return statusMap[status] || status;
}

async function loadAdjustments() {
    const status = document.getElementById('status-filter').value;
    const url = status 
        ? `${API_BASE_URL}/admin/adjustments?status=${status}`
        : `${API_BASE_URL}/admin/adjustments`;
    
    try {
        const response = await fetchWithAuth(url);
        const data = await response.json();
        
        if (response.ok) {
            const listDiv = document.getElementById('adjustment-list');
            
            if (data.length === 0) {
                listDiv.innerHTML = '<p class="text-muted">No requests found</p>';
                return;
            }
            
            listDiv.innerHTML = data.map(req => `
                <div class="card-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span><strong>Request ID:</strong> ${req.request_id}</span>
                        <span class="status-badge ${getStatusClass(req.status)}">${getStatusText(req.status)}</span>
                    </div>
                    <p><strong>Student:</strong> ${req.student_name} (${req.student_id})</p>
                    <p><strong>Current Dorm:</strong> ${req.current_dorm || 'N/A'}</p>
                    <p><strong>Reason:</strong> ${req.request_reason}</p>
                    <p><strong>Request Date:</strong> ${req.request_date || 'N/A'}</p>
                    ${req.processed_date ? `<p><strong>Processed Date:</strong> ${req.processed_date}</p>` : ''}
                    ${req.status === 'pending' ? `
                        <div>
                            <button class="btn btn-success btn-sm" onclick="showApproveModal(${req.request_id}, '${req.current_dorm || ''}', '${req.current_dorm_id || ''}', '${req.student_id || ''}')">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="processRequest(${req.request_id}, 'rejected')">
                                <i class="fas fa-times"></i> Reject
                            </button>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load adjustments error:', error);
        document.getElementById('adjustment-list').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

let currentRequestId = null;
let currentDormId = null;

async function loadAvailableDorms(excludeDormId, studentId) {
    try {
        let url = `${API_BASE_URL}/admin/adjustments/available-dorms`;
        const params = [];
        if (excludeDormId) params.push(`exclude_dorm_id=${excludeDormId}`);
        if (studentId) params.push(`student_id=${studentId}`);
        if (params.length > 0) url += '?' + params.join('&');
        
        const response = await fetchWithAuth(url);
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('new-dorm-select');
            select.innerHTML = '<option value="">Select a dormitory...</option>';
            data.forEach(dorm => {
                const option = document.createElement('option');
                option.value = dorm.dorm_id;
                const availableSpots = dorm.available_spots !== undefined ? dorm.available_spots : (dorm.has_vacancy > 0 ? dorm.has_vacancy : 0);
                option.textContent = `${dorm.building_name || dorm.building_id}-F${dorm.floor_no}-${dorm.room_no} (${dorm.gender || ''}, ${availableSpots} spots available)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Load available dorms error:', error);
    }
}

function showApproveModal(requestId, currentDorm, currentDormIdParam, studentId) {
    currentRequestId = requestId;
    currentDormId = currentDormIdParam;
    document.getElementById('current-dorm-display').textContent = currentDorm || 'N/A';
    loadAvailableDorms(currentDormId, studentId);
    const modal = new bootstrap.Modal(document.getElementById('approveModal'));
    modal.show();
}

async function approveWithDorm() {
    const newDormId = document.getElementById('new-dorm-select').value;
    
    if (!newDormId) {
        alert('Please select a dormitory');
        return;
    }
    
    if (!confirm('Are you sure you want to approve this request and assign the student to the selected dormitory?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/adjustments/${currentRequestId}`, {
            method: 'PUT',
            body: JSON.stringify({ 
                status: 'approved',
                new_dorm_id: newDormId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Request approved and student assigned to new dormitory successfully!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('approveModal'));
            modal.hide();
            loadAdjustments();
        } else {
            alert('Process failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Process request error:', error);
        alert('System error, please try again');
    }
}

async function processRequest(requestId, status) {
    const action = status === 'approved' ? 'approve' : 'reject';
    if (!confirm(`Are you sure you want to ${action} this request?`)) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/adjustments/${requestId}`, {
            method: 'PUT',
            body: JSON.stringify({ status })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(`Request ${action}d successfully!`);
            loadAdjustments();
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
    
    loadAdjustments();
});

