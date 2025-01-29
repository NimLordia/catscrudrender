// API and Axios Configuration
const API_URL = 'https://catscrudrender.onrender.com';

// Create axios instance with default configuration
const axiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    withCredentials: false
});

// Add a request interceptor
axiosInstance.interceptors.request.use(
    config => {
        // You could add loading state here
        document.body.style.cursor = 'wait';
        return config;
    },
    error => {
        document.body.style.cursor = 'default';
        return Promise.reject(error);
    }
);

// Add a response interceptor
axiosInstance.interceptors.response.use(
    response => {
        document.body.style.cursor = 'default';
        return response;
    },
    error => {
        document.body.style.cursor = 'default';
        console.error('API Error:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
        });
        return Promise.reject(error);
    }
);

// Fetch all cats
async function fetchCats() {
    try {
        const response = await axiosInstance.get('/cats/');
        displayCats(response.data);
    } catch (error) {
        handleError('fetching', error);
    }
}

// Error handler function
function handleError(action, error) {
    const errorMessage = error.response?.data?.detail || error.message;
    console.error(`Error ${action} cat:`, error);
    alert(`Error ${action} cat: ${errorMessage}`);
}

// Display cats in table
function displayCats(cats) {
    const tableBody = document.getElementById('catsTableBody');
    tableBody.innerHTML = '';

    cats.forEach(cat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${cat.id}</td>
            <td>${escapeHtml(cat.name)}</td>
            <td>${escapeHtml(cat.breed)}</td>
            <td>${cat.age}</td>
            <td>${cat.weight}</td>
            <td>
                <button onclick="openEditModal(${JSON.stringify(cat).replace(/"/g, '&quot;')})"
                    class="btn-edit">Edit</button>
                <button onclick="deleteCat(${cat.id})"
                    class="btn-delete">Delete</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// HTML escape function for security
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Add new cat
document.getElementById('addCatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const catData = {
        name: formData.get('name'),
        breed: formData.get('breed'),
        age: parseFloat(formData.get('age')),
        weight: parseFloat(formData.get('weight'))
    };

    try {
        await axiosInstance.post('/cats/', catData);
        e.target.reset();
        fetchCats();
    } catch (error) {
        handleError('adding', error);
    }
});

// Delete cat
async function deleteCat(id) {
    if (confirm('Are you sure you want to delete this cat?')) {
        try {
            await axiosInstance.delete(`/cats/${id}`);
            fetchCats();
        } catch (error) {
            handleError('deleting', error);
        }
    }
}

// Edit cat modal functions
function openEditModal(cat) {
    const modal = document.getElementById('editModal');
    modal.style.display = 'block';
    
    // Fill in the form fields
    document.getElementById('editCatId').value = cat.id;
    document.getElementById('editName').value = cat.name;
    document.getElementById('editBreed').value = cat.breed;
    document.getElementById('editAge').value = cat.age;
    document.getElementById('editWeight').value = cat.weight;
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
}

// Modal click outside to close
window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target === modal) {
        closeEditModal();
    }
}

// Edit cat form submission
document.getElementById('editCatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('editCatId').value;
    const catData = {
        name: document.getElementById('editName').value,
        breed: document.getElementById('editBreed').value,
        age: parseFloat(document.getElementById('editAge').value),
        weight: parseFloat(document.getElementById('editWeight').value)
    };

    try {
        await axiosInstance.put(`/cats/${id}`, catData);
        closeEditModal();
        fetchCats();
    } catch (error) {
        handleError('updating', error);
    }
});

// Keyboard support for modal
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeEditModal();
    }
});

// Initial load
fetchCats();