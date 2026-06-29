document.addEventListener('DOMContentLoaded', async () => {
    const username = document.getElementById('username');
    const akunMessage = document.getElementById('akunMessage');
    const passwordMessage = document.getElementById('passwordMessage');
    const createAkunMessage = document.getElementById('createAkunMessage');

    try {
        const result = await apiFetch('/akun');
        username.value = result.data?.username || '';
    } catch (error) {
        akunMessage.textContent = error.message;
    }

    document.getElementById('akunForm').addEventListener('submit', async event => {
        event.preventDefault();
        try {
            const result = await apiFetch('/akun', {
                method: 'PUT',
                body: JSON.stringify({ username: username.value })
            });
            akunMessage.textContent = result.message;
        } catch (error) {
            akunMessage.textContent = error.message;
        }
    });

    document.getElementById('createAkunForm').addEventListener('submit', async event => {
        event.preventDefault();
        createAkunMessage.textContent = 'Menyimpan...';

        try {
            const result = await apiFetch('/akun/create', {
                method: 'POST',
                body: JSON.stringify({
                    username: document.getElementById('newUsername').value,
                    password: document.getElementById('createPassword').value,
                    role: document.getElementById('newRole').value
                })
            });
            createAkunMessage.textContent = result.message;
            event.target.reset();
        } catch (error) {
            createAkunMessage.textContent = error.message;
        }
    });

    document.getElementById('passwordForm').addEventListener('submit', async event => {
        event.preventDefault();
        try {
            const result = await apiFetch('/akun/change-password', {
                method: 'POST',
                body: JSON.stringify({
                    old_password: document.getElementById('oldPassword').value,
                    new_password: document.getElementById('newPassword').value
                })
            });
            passwordMessage.textContent = result.message;
            event.target.reset();
        } catch (error) {
            passwordMessage.textContent = error.message;
        }
    });
});
