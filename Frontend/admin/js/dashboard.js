document.addEventListener('DOMContentLoaded', async () => {
    const statsEl = document.getElementById('stats');
    const recentEl = document.getElementById('recentList');

    try {
        const stats = await apiFetch('/dashboard/stats');
        const data = stats.data || {};
        statsEl.innerHTML = `
            <article class="stat"><span>Experience</span><strong>${data.experiences_count || 0}</strong></article>
            <article class="stat"><span>Projects</span><strong>${data.projects_count || 0}</strong></article>
            <article class="stat"><span>Skills</span><strong>${data.skills_count || 0}</strong></article>
            <article class="stat"><span>Admin</span><strong>${escapeHtml(data.admin_name || 'Admin')}</strong></article>
        `;

        const recent = await apiFetch('/dashboard/recent-activity');
        const items = recent.data || [];
        recentEl.innerHTML = items.length ? items.map(item => `
            <article class="item">
                <strong>${escapeHtml(item.judul || item.posisi || item.type)}</strong>
                <p>${escapeHtml(item.deskripsi || item.perusahaan || '')}</p>
            </article>
        `).join('') : '<p>Belum ada aktivitas.</p>';
    } catch (error) {
        statsEl.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    }
});
