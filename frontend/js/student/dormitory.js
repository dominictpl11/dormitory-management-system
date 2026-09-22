// Use API_BASE_URL from auth.js
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';

async function loadDormitoryInfo() {
    try {
        const response = await fetchWithAuth(`${API_BASE_URL}/student/dormitory`);
        const data = await response.json();
        
        if (response.ok) {
            const infoDiv = document.getElementById('dormitory-info');
            infoDiv.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Building:</strong> ${data.dorm_building}</p>
                        <p><strong>Room Number:</strong> ${data.room_number}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Roommates:</strong></p>
                        <ul>
                            ${data.roommates.length > 0 
                                ? data.roommates.map(r => `<li>${r}</li>`).join('')
                                : '<li>No roommates</li>'
                            }
                        </ul>
                    </div>
                </div>
            `;
        } else {
            document.getElementById('dormitory-info').innerHTML = 
                '<p class="text-danger">No dormitory assigned</p>';
        }
    } catch (error) {
        console.error('Load dormitory error:', error);
        document.getElementById('dormitory-info').innerHTML = 
            '<p class="text-danger">System error, please try again</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('token') || sessionStorage.getItem('role') !== 'student') {
        window.location.href = '../index.html';
        return;
    }
    
    loadDormitoryInfo();
});

