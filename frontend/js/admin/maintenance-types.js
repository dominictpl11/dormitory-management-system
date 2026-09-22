// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

async function loadMaintenanceTypes() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/maintenance-types`);
        const data = await response.json();
        
        if (response.ok) {
            const tbody = document.getElementById('type-table');
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No types found</td></tr>';
                return;
            }
            
            tbody.innerHTML = data.map(type => `
                <tr>
                    <td>${type.type_id}</td>
                    <td>${type.type_name}</td>
                    <td>¥${type.cost.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editType(${type.type_id}, '${type.type_name}', ${type.cost})">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="deleteType(${type.type_id})">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Load maintenance types error:', error);
        document.getElementById('type-table').innerHTML = 
            '<tr><td colspan="4" class="text-center text-danger">System error, please try again</td></tr>';
    }
}

async function addType() {
    const typeName = document.getElementById('type-name').value;
    const cost = parseFloat(document.getElementById('type-cost').value);
    
    if (!typeName || !cost) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/maintenance-types`, {
            method: 'POST',
            body: JSON.stringify({
                type_name: typeName,
                cost: cost
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Maintenance type added successfully!');
            document.getElementById('type-form').reset();
            loadMaintenanceTypes();
        } else {
            alert('Add failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Add type error:', error);
        alert('System error, please try again');
    }
}

async function editType(typeId, currentName, currentCost) {
    const newName = prompt('Enter new type name:', currentName);
    if (!newName) return;
    
    const newCost = prompt('Enter new cost:', currentCost);
    if (!newCost) return;
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/maintenance-types/${typeId}`, {
            method: 'PUT',
            body: JSON.stringify({
                type_name: newName,
                cost: parseFloat(newCost)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Maintenance type updated successfully!');
            loadMaintenanceTypes();
        } else {
            alert('Update failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Edit type error:', error);
        alert('System error, please try again');
    }
}

async function deleteType(typeId) {
    if (!confirm('Are you sure you want to delete this maintenance type?')) {
        return;
    }
    
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/admin/maintenance-types/${typeId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Maintenance type deleted successfully!');
            loadMaintenanceTypes();
        } else {
            alert('Delete failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Delete type error:', error);
        alert('System error, please try again');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'admin') {
        window.location.href = '../index.html';
        return;
    }
    
    loadMaintenanceTypes();
    
    document.getElementById('type-form').addEventListener('submit', (e) => {
        e.preventDefault();
        addType();
    });
});

