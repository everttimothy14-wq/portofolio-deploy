document.getElementById('registerForm').addEventListener('submit', async event => {
    event.preventDefault();
    const message = document.getElementById('registerMessage');
    const username = document.getElementById('registerUsername').value;

    message.textContent = 'Mendaftarkan...';

    try {
        const result = await apiFetch('/register', {
            method: 'POST',
            body: JSON.stringify({
                username,
                password: document.getElementById('registerPassword').value,
                confirm_password: document.getElementById('confirmPassword').value
            })
        });

        message.textContent = result.message;
        event.target.reset();
        setTimeout(() => {
            window.location.href = `login.html?username=${encodeURIComponent(username)}`;
        }, 700);
    } catch (error) {
        message.textContent = error.message;
    }
});
