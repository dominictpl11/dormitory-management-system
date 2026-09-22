// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'approved': 'status-approved',
        'rejected': 'status-rejected',
        'cancelled': 'status-cancelled'
    };
    return statusMap[status] || '';
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
}

async function submitAdjustmentRequest() {
    const reason = document.getElementById('request-reason').value;
    
    if (!reason) {
        alert('Please enter request reason');
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/adjustments`, {
            method: 'POST',
            body: JSON.stringify({ request_reason: reason })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Adjustment request submitted successfully!');
            document.getElementById('adjustment-form').reset();
            loadAdjustmentRequests();
        } else {
            alert('Submit failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Submit adjustment error:', error);
        alert('System error, please try again');
    }
}

async function loadAdjustmentRequests() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/adjustments`);
        const data = await response.json();
        
        if (response.ok) {
            const requestsDiv = document.getElementById('adjustment-requests');
            
            if (data.length === 0) {
                requestsDiv.innerHTML = '<p class="text-muted">No requests found</p>';
                return;
            }
            
            requestsDiv.innerHTML = data.map(req => `
                <div class="card-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span><strong>Request ID:</strong> ${req.request_id}</span>
                        <span class="status-badge ${getStatusClass(req.status)}">${getStatusText(req.status)}</span>
                    </div>
                    <p><strong>Reason:</strong> ${req.request_reason}</p>
                    <p><strong>Request Date:</strong> ${req.request_date || 'N/A'}</p>
                    ${req.processed_date ? `<p><strong>Processed Date:</strong> ${req.processed_date}</p>` : ''}
                    ${req.status === 'pending' ? `
                        <button class="btn btn-danger btn-sm" onclick="cancelRequest(${req.request_id})">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    ` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load adjustment requests error:', error);
        document.getElementById('adjustment-requests').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

async function cancelRequest(requestId) {
    if (!confirm('Are you sure you want to cancel this request?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/adjustments/${requestId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Request cancelled successfully!');
            loadAdjustmentRequests();
        } else {
            alert('Cancel failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Cancel request error:', error);
        alert('System error, please try again');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'student') {
        window.location.href = '../index.html';
        return;
    }
    
    loadAdjustmentRequests();
    
    document.getElementById('adjustment-form').addEventListener('submit', (e) => {
        e.preventDefault();
        submitAdjustmentRequest();
    });
});

