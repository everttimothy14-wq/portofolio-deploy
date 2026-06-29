const savedUsername = new URLSearchParams(window.location.search).get('username');
if (savedUsername) {
    document.getElementById('username').value = savedUsername;
}

document.getElementById('loginForm').addEventListener('submit', async event => {
    event.preventDefault();
    const message = document.getElementById('message');
    message.textContent = 'Memproses...';

    try {
        const result = await apiFetch('/login', {
            method: 'POST',
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            })
        });

        setToken(result.token);
        window.location.href = 'dashboard.html';
    } catch (error) {
        message.textContent = error.message;
    }
});
