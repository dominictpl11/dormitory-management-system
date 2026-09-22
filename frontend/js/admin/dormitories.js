// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

let currentAssignStudentId = null;

async function loadDormitories() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/dormitories`);
        const data = await response.json();
        
        if (response.ok) {
            const tbody = document.getElementById('dormitory-table');
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="text-center">No dormitories found</td></tr>';
                return;
            }
            
            tbody.innerHTML = data.map(dorm => {
                // has_vacancy now contains the count of vacant beds, not boolean
                const vacantBeds = dorm.vacant_beds !== undefined ? dorm.vacant_beds : (typeof dorm.has_vacancy === 'number' ? dorm.has_vacancy : (dorm.max_capacity - dorm.current_occupancy));
                const hasVacancy = vacantBeds > 0;
                
                // Payment information
                const paymentInfo = dorm.payment_info || {
                    total_fees: 0,
                    paid_fees: 0,
                    unpaid_fees: 0,
                    total_amount: 0,
                    paid_amount: 0,
                    unpaid_amount: 0,
                    payment_rate: 0
                };
                
                // Format payment status display
                let paymentStatusHtml = '';
                if (paymentInfo.total_fees === 0) {
                    paymentStatusHtml = '<span class="text-muted">No fees</span>';
                } else {
                    const paymentRate = paymentInfo.payment_rate || 0;
                    const paymentBadgeClass = paymentRate === 100 ? 'bg-success' : (paymentRate >= 50 ? 'bg-warning' : 'bg-danger');
                    paymentStatusHtml = `
                        <div class="small">
                            <div>Paid: ${paymentInfo.paid_fees}/${paymentInfo.total_fees}</div>
                            <div>
                                <span class="badge ${paymentBadgeClass}">
                                    ${paymentRate}%
                                </span>
                            </div>
                            ${paymentInfo.unpaid_amount > 0 ? `<div class="text-danger">Unpaid: ¥${paymentInfo.unpaid_amount}</div>` : ''}
                        </div>
                    `;
                }
                
                return `
                <tr>
                    <td>${dorm.dorm_id}</td>
                    <td>${dorm.building_name || dorm.building_id}</td>
                    <td>${dorm.floor_no || 'N/A'}</td>
                    <td>${dorm.room_no}</td>
                    <td>${dorm.gender || 'N/A'}</td>
                    <td>${dorm.current_occupancy}</td>
                    <td>${dorm.max_capacity}</td>
                    <td>${vacantBeds}</td>
                    <td>${paymentStatusHtml}</td>
                    <td>
                        <span class="badge ${hasVacancy ? 'bg-success' : 'bg-danger'}">
                            ${hasVacancy ? 'Available' : 'Full'}
                        </span>
                    </td>
                </tr>
            `;
            }).join('');
        }
    } catch (error) {
        console.error('Load dormitories error:', error);
        document.getElementById('dormitory-table').innerHTML = 
            '<tr><td colspan="10" class="text-center text-danger">System error, please try again</td></tr>';
    }
}

async function loadUnassignedStudents() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/students/unassigned`);
        const data = await response.json();
        
        if (response.ok) {
            const div = document.getElementById('unassigned-students');
            
            if (data.length === 0) {
                div.innerHTML = '<p class="text-muted">No unassigned students found. All students have been assigned to dormitories.</p>';
                return;
            }
            
            div.innerHTML = data.map(student => `
                <div class="card-item mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p class="mb-1"><strong>${student.name}</strong> (${student.student_id})</p>
                            <p class="mb-1 text-muted"><small>Email: ${student.email} | Phone: ${student.phone}</small></p>
                            <p class="mb-1 text-muted"><small>Gender: ${student.gender} | Major: ${student.major}</small></p>
                            <p class="mb-0 text-muted"><small>Current: ${student.dormitory} - ${student.room_number}</small></p>
                        </div>
                        <button class="btn btn-primary btn-sm" onclick="showAssignModal('${student.student_id}', '${student.name}', '${student.gender}')">
                            <i class="fas fa-bed"></i> Assign Dormitory
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Load unassigned students error:', error);
        document.getElementById('unassigned-students').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

async function loadAvailableDormsForAssign(studentGender) {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/dormitories`);
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('assign-dorm-select');
            select.innerHTML = '<option value="">Select a dormitory...</option>';
            
            // Filter only dormitories with vacancy and matching gender
            const availableDorms = data.filter(dorm => {
                const vacantBeds = dorm.vacant_beds !== undefined ? dorm.vacant_beds : (typeof dorm.has_vacancy === 'number' ? dorm.has_vacancy : (dorm.max_capacity - dorm.current_occupancy));
                return vacantBeds > 0 && dorm.gender === studentGender;
            });
            
            availableDorms.forEach(dorm => {
                const option = document.createElement('option');
                option.value = dorm.dorm_id;
                const availableSpots = dorm.vacant_beds !== undefined ? dorm.vacant_beds : (dorm.max_capacity - dorm.current_occupancy);
                option.textContent = `${dorm.building_name || dorm.building_id}-F${dorm.floor_no}-${dorm.room_no} (${dorm.gender}, ${availableSpots} spots available)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Load available dorms error:', error);
    }
}

function showAssignModal(studentId, studentName, studentGender) {
    currentAssignStudentId = studentId;
    document.getElementById('assign-student-name').textContent = studentName;
    document.getElementById('assign-student-id').textContent = studentId;
    loadAvailableDormsForAssign(studentGender);
    const modal = new bootstrap.Modal(document.getElementById('assignModal'));
    modal.show();
}

async function assignDormitory() {
    const dormId = document.getElementById('assign-dorm-select').value;
    
    if (!dormId) {
        alert('Please select a dormitory');
        return;
    }
    
    if (!confirm(`Are you sure you want to assign this student to the selected dormitory?`)) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/students/${currentAssignStudentId}/assign-dorm`, {
            method: 'POST',
            body: JSON.stringify({ dorm_id: dormId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Dormitory assigned successfully!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignModal'));
            modal.hide();
            loadUnassignedStudents();
            loadDormitories(); // Refresh dormitory list to update occupancy
        } else {
            alert('Assignment failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Assign dormitory error:', error);
        alert('System error, please try again');
    }
}

// Tab change handler
document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'admin') {
        window.location.href = '../index.html';
        return;
    }
    
    loadDormitories();
    
    // Load unassigned students when tab is shown
    const unassignedTab = document.getElementById('unassigned-tab');
    if (unassignedTab) {
        unassignedTab.addEventListener('shown.bs.tab', () => {
            loadUnassignedStudents();
        });
    }
});

