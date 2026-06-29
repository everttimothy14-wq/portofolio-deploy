const profileFields = [
    'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir',
    'email', 'telepon', 'universitas', 'fakultas', 'prodi',
    'semester', 'alamat', 'foto_url'
];

function fillProfileForm(profile) {
    profileFields.forEach(field => {
        const input = document.getElementById(field);
        if (input) input.value = profile?.[field] || '';
    });
}

function getProfilePayload() {
    return profileFields.reduce((payload, field) => {
        const input = document.getElementById(field);
        payload[field] = input ? input.value.trim() : '';
        return payload;
    }, {});
}

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('profileForm');
    const message = document.getElementById('profileMessage');

    try {
        const result = await apiFetch('/profiles');
        fillProfileForm(result.data || {});
    } catch (error) {
        message.textContent = error.message;
    }

    form.addEventListener('submit', async event => {
        event.preventDefault();
        message.textContent = 'Menyimpan...';

        try {
            const result = await apiFetch('/profiles', {
                method: 'PUT',
                body: JSON.stringify(getProfilePayload())
            });
            fillProfileForm(result.data || {});
            message.textContent = result.message || 'Profil berhasil disimpan';
        } catch (error) {
            message.textContent = error.message;
        }
    });
});
