const skillForm = document.getElementById('skillForm');
const skillList = document.getElementById('skillList');

async function loadSkills() {
    const result = await apiFetch('/skills');
    const items = result.data || [];
    skillList.innerHTML = items.length ? items.map(item => `
        <article class="item">
            <h3>${escapeHtml(item.nama_skill)}</h3>
            <p>${escapeHtml(item.icon_class || 'fas fa-code')}</p>
            <div class="item-actions">
                <button type="button" onclick='editSkill(${JSON.stringify(item)})'>Edit</button>
                <button type="button" class="danger" onclick="deleteSkill(${item.id})">Hapus</button>
            </div>
        </article>
    `).join('') : '<p>Belum ada skill.</p>';
}

function editSkill(item) {
    document.getElementById('itemId').value = item.id;
    document.getElementById('nama_skill').value = item.nama_skill || '';
    document.getElementById('icon_class').value = item.icon_class || '';
}

async function deleteSkill(id) {
    if (!confirm('Hapus skill ini?')) return;
    await apiFetch(`/skills/${id}`, { method: 'DELETE' });
    await loadSkills();
}

skillForm.addEventListener('submit', async event => {
    event.preventDefault();
    const id = document.getElementById('itemId').value;
    await apiFetch(id ? `/skills/${id}` : '/skills', {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify({
            nama_skill: document.getElementById('nama_skill').value,
            icon_class: document.getElementById('icon_class').value
        })
    });
    skillForm.reset();
    await loadSkills();
});

document.getElementById('resetBtn').addEventListener('click', () => skillForm.reset());
document.addEventListener('DOMContentLoaded', loadSkills);
