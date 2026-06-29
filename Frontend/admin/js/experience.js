const experienceForm = document.getElementById('experienceForm');
const experienceList = document.getElementById('experienceList');

async function loadExperiences() {
    const result = await apiFetch('/experiences');
    const items = result.data || [];
    experienceList.innerHTML = items.length ? items.map(item => `
        <article class="item">
            <h3>${escapeHtml(item.posisi)}</h3>
            <p>${escapeHtml(item.perusahaan)} - ${escapeHtml(item.durasi)}</p>
            <p>${escapeHtml(item.deskripsi)}</p>
            <div class="item-actions">
                <button type="button" onclick='editExperience(${JSON.stringify(item)})'>Edit</button>
                <button type="button" class="danger" onclick="deleteExperience(${item.id})">Hapus</button>
            </div>
        </article>
    `).join('') : '<p>Belum ada experience.</p>';
}

function editExperience(item) {
    document.getElementById('itemId').value = item.id;
    document.getElementById('posisi').value = item.posisi || '';
    document.getElementById('perusahaan').value = item.perusahaan || '';
    document.getElementById('durasi').value = item.durasi || '';
    document.getElementById('deskripsi').value = item.deskripsi || '';
}

async function deleteExperience(id) {
    if (!confirm('Hapus experience ini?')) return;
    await apiFetch(`/experiences/${id}`, { method: 'DELETE' });
    await loadExperiences();
}

experienceForm.addEventListener('submit', async event => {
    event.preventDefault();
    const id = document.getElementById('itemId').value;
    await apiFetch(id ? `/experiences/${id}` : '/experiences', {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify({
            posisi: document.getElementById('posisi').value,
            perusahaan: document.getElementById('perusahaan').value,
            durasi: document.getElementById('durasi').value,
            deskripsi: document.getElementById('deskripsi').value
        })
    });
    experienceForm.reset();
    await loadExperiences();
});

document.getElementById('resetBtn').addEventListener('click', () => experienceForm.reset());
document.addEventListener('DOMContentLoaded', loadExperiences);
