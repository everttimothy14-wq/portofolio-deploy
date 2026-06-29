const API_BASE = '/api';

function getToken() {
    return localStorage.getItem('token') || '';
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearToken() {
    localStorage.removeItem('token');
}

async function apiFetch(path, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {})
    };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers
    });
    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json')
        ? await response.json()
        : {};

    if (!response.ok) {
        throw new Error(data.error || 'Request gagal');
    }
    return data;
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, value => map[value]);
}

function bindLogout() {
    const button = document.getElementById('logoutBtn');
    if (!button) return;
    button.addEventListener('click', async () => {
        try {
            await apiFetch('/logout', { method: 'POST' });
        } catch (error) {
            console.warn(error.message);
        } finally {
            clearToken();
            window.location.href = 'login.html';
        }
    });
}

function requireAuth() {
    const publicPages = ['/login.html', '/register.html'];
    const isPublicPage = publicPages.some(page => location.pathname.endsWith(page));

    if (!getToken() && !isPublicPage) {
        window.location.href = 'login.html';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    bindLogout();
});
