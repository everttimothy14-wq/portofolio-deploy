const projectForm = document.getElementById('projectForm');
const projectList = document.getElementById('projectList');

async function loadProjects() {
    const result = await apiFetch('/projects');
    const items = result.data || [];
    projectList.innerHTML = items.length ? items.map(item => `
        <article class="item">
            <h3>${escapeHtml(item.judul)}</h3>
            <p>${escapeHtml(item.deskripsi)}</p>
            <div class="item-actions">
                <button type="button" onclick='editProject(${JSON.stringify(item)})'>Edit</button>
                <button type="button" class="danger" onclick="deleteProject(${item.id})">Hapus</button>
            </div>
        </article>
    `).join('') : '<p>Belum ada project.</p>';
}

function editProject(item) {
    document.getElementById('itemId').value = item.id;
    document.getElementById('judul').value = item.judul || '';
    document.getElementById('deskripsi').value = item.deskripsi || '';
    document.getElementById('gambar_url').value = item.gambar_url || '';
    document.getElementById('link_project').value = item.link_project || '';
}

async function deleteProject(id) {
    if (!confirm('Hapus project ini?')) return;
    await apiFetch(`/projects/${id}`, { method: 'DELETE' });
    await loadProjects();
}

projectForm.addEventListener('submit', async event => {
    event.preventDefault();
    const id = document.getElementById('itemId').value;
    await apiFetch(id ? `/projects/${id}` : '/projects', {
        method: id ? 'PUT' : 'POST',
        body: JSON.stringify({
            judul: document.getElementById('judul').value,
            deskripsi: document.getElementById('deskripsi').value,
            gambar_url: document.getElementById('gambar_url').value,
            link_project: document.getElementById('link_project').value
        })
    });
    projectForm.reset();
    await loadProjects();
});

document.getElementById('resetBtn').addEventListener('click', () => projectForm.reset());
document.addEventListener('DOMContentLoaded', loadProjects);
