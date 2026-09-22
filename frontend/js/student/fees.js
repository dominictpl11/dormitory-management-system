// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

async function loadFeeList() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/fees`);
        const data = await response.json();
        
        if (response.ok) {
            // Update statistics
            if (data.statistics) {
                document.getElementById('total-fees').textContent = data.statistics.total_fees || 0;
                document.getElementById('paid-fees').textContent = data.statistics.paid_fees || 0;
                document.getElementById('unpaid-fees').textContent = data.statistics.unpaid_fees || 0;
                document.getElementById('unpaid-amount').textContent = `¥${(data.statistics.unpaid_amount || 0).toFixed(2)}`;
            }
            
            const feeListDiv = document.getElementById('fee-list');
            
            if (!data.fees || data.fees.length === 0) {
                feeListDiv.innerHTML = '<p class="text-muted">No fees found for your dormitory</p>';
                return;
            }
            
            // Group fees by type
            const feesByType = {};
            data.fees.forEach(fee => {
                const type = fee.fee_type || 'other';
                if (!feesByType[type]) {
                    feesByType[type] = [];
                }
                feesByType[type].push(fee);
            });
            
            // Display fees grouped by type
            let html = '';
            for (const [type, fees] of Object.entries(feesByType)) {
                const typeName = type === 'maintenance' ? 'Maintenance Fees' : 
                                type === 'utilities' ? 'Utilities (Water & Electricity)' : 
                                type.charAt(0).toUpperCase() + type.slice(1) + ' Fees';
                
                html += `
                    <div class="mb-4">
                        <h6 class="mb-3"><i class="fas fa-tag"></i> ${typeName}</h6>
                        <div class="row">
                            ${fees.map(fee => `
                                <div class="col-md-6 mb-3">
                                    <div class="card-item">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span><strong>${fee.fee_name || 'Fee'}</strong></span>
                                            <span class="badge ${fee.status === 'paid' ? 'bg-success' : 'bg-warning'}">
                                                ${fee.status === 'paid' ? 'Paid' : 'Unpaid'}
                                            </span>
                                        </div>
                                        <p class="mb-1"><strong>Amount:</strong> ¥${fee.amount.toFixed(2)}</p>
                                        <p class="mb-1"><small class="text-muted">Date: ${fee.created_at || 'N/A'}</small></p>
                                        ${fee.initiated_by ? `<p class="mb-1"><small class="text-muted">Initiated by: ${fee.initiated_by}</small></p>` : ''}
                                        ${fee.status === 'unpaid' ? `
                                            <button class="btn btn-success btn-sm mt-2" onclick="payFee(${fee.fee_id})">
                                                <i class="fas fa-credit-card"></i> Pay Now
                                            </button>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            feeListDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Load fee list error:', error);
        document.getElementById('fee-list').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

async function payFee(feeId) {
    if (!confirm('Are you sure you want to pay this fee?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/fees/${feeId}/pay`, {
            method: 'POST',
            body: JSON.stringify({ payment_method: 'Online Payment' })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Payment successful!');
            loadFeeList();
        } else {
            alert('Payment failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Pay fee error:', error);
        alert('System error, please try again');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'student') {
        window.location.href = '../index.html';
        return;
    }
    
    loadFeeList();
});

