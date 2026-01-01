// AutoEQ Dashboard JavaScript
// Handles data loading and visualization for all pages

// Data storage
let clustersData = null;
let likesData = null;
let presetsData = null;
let presetsDetailedData = null;
let hydrationData = null;

// Cluster colors
const clusterColors = {
    'arabic_classical': '#ff5500',
    'sufi_religious': '#8b5cf6',
    'arabic_pop': '#ec4899',
    'electronic_edm': '#3b82f6',
    'instrumental': '#10b981',
    'world_fusion': '#f59e0b',
    'rock_alternative': '#ef4444',
    'hip_hop_rap': '#6366f1',
    'uncategorized': '#6b7280'
};

// Load JSON data
async function loadData() {
    try {
        const basePath = 'data/';
        const [clusters, likes, presets, presetsDetailed, hydration] = await Promise.all([
            fetch(basePath + 'track_clusters.json').then(r => r.json()),
            fetch(basePath + 'soundcloud_likes.json').then(r => r.json()),
            fetch(basePath + 'eq_presets.json').then(r => r.json()),
            fetch(basePath + 'eq_presets_detailed.json').then(r => r.json()),
            fetch(basePath + 'soundcloud_hydration.json').then(r => r.json()).catch(() => null)
        ]);

        clustersData = clusters;
        likesData = likes;
        presetsData = presets;
        presetsDetailedData = presetsDetailed;
        hydrationData = hydration;

        return true;
    } catch (error) {
        console.error('Error loading data:', error);
        return false;
    }
}

// ==================== DASHBOARD PAGE ====================
async function loadDashboard() {
    await loadData();

    // Update stats
    document.getElementById('total-tracks').textContent = likesData.track_count.toLocaleString();
    document.getElementById('total-clusters').textContent = clustersData.clusters.length;

    // Count unique artists
    const artists = new Set(likesData.tracks.map(t => t.artist));
    document.getElementById('total-artists').textContent = artists.size.toLocaleString();
    document.getElementById('eq-presets').textContent = presetsData.presets.length;

    // Create cluster chart
    createClusterChart();

    // Populate top clusters
    populateTopClusters();

    // Populate EQ preview
    populateEQPreview();

    // Populate sample tracks
    populateSampleTracks();

    // Populate user info
    populateUserInfo();
}

function createClusterChart() {
    const ctx = document.getElementById('clusterChart').getContext('2d');
    const clusters = clustersData.clusters;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: clusters.map(c => c.name),
            datasets: [{
                data: clusters.map(c => c.track_count),
                backgroundColor: clusters.map(c => clusterColors[c.id] || '#6b7280'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Create custom legend
    const legend = document.getElementById('cluster-legend');
    legend.innerHTML = clusters.map(c => `
        <div class="legend-item">
            <div class="legend-color" style="background: ${clusterColors[c.id] || '#6b7280'}"></div>
            <span>${c.name} (${c.track_count})</span>
        </div>
    `).join('');
}

function populateTopClusters() {
    const container = document.getElementById('top-clusters-list');
    const topClusters = clustersData.clusters.slice(0, 5);

    container.innerHTML = topClusters.map(c => `
        <div class="cluster-item" onclick="window.location.href='clusters.html#${c.id}'">
            <span class="cluster-name">${c.name}</span>
            <span class="cluster-count">${c.track_count}</span>
        </div>
    `).join('');
}

function populateEQPreview() {
    const container = document.getElementById('eq-preview-list');
    const presets = presetsDetailedData.presets.slice(0, 4);

    container.innerHTML = presets.map(p => `
        <div class="eq-item" onclick="window.location.href='eq-presets.html#${p.cluster_id}'">
            <div class="eq-name">${p.preset_name}</div>
            <div class="eq-description">${p.track_count} tracks</div>
        </div>
    `).join('');
}

function populateSampleTracks() {
    const container = document.getElementById('recent-tracks-list');
    const tracks = likesData.tracks.slice(0, 5);

    container.innerHTML = tracks.map(t => `
        <div class="track-item" onclick="window.open('${t.url}', '_blank')">
            <img src="${t.artwork_url || ''}" alt="" class="track-artwork" onerror="this.style.display='none'">
            <div class="track-info">
                <div class="track-title">${escapeHtml(t.title)}</div>
                <div class="track-artist">${escapeHtml(t.artist)}</div>
            </div>
            <div class="track-meta">
                ${t.duration || ''}
            </div>
        </div>
    `).join('');
}

function populateUserInfo() {
    const container = document.getElementById('user-info-content');

    if (hydrationData) {
        const user = hydrationData.find(h => h.hydratable === 'user')?.data;
        if (user) {
            container.innerHTML = `
                <div class="user-stat">
                    <div class="user-stat-label">Username</div>
                    <div class="user-stat-value">${user.username}</div>
                </div>
                <div class="user-stat">
                    <div class="user-stat-label">Full Name</div>
                    <div class="user-stat-value">${user.full_name || 'N/A'}</div>
                </div>
                <div class="user-stat">
                    <div class="user-stat-label">Followers</div>
                    <div class="user-stat-value">${user.followers_count?.toLocaleString() || 'N/A'}</div>
                </div>
                <div class="user-stat">
                    <div class="user-stat-label">Following</div>
                    <div class="user-stat-value">${user.followings_count?.toLocaleString() || 'N/A'}</div>
                </div>
                <div class="user-stat">
                    <div class="user-stat-label">Likes</div>
                    <div class="user-stat-value">${user.likes_count?.toLocaleString() || 'N/A'}</div>
                </div>
                <div class="user-stat">
                    <div class="user-stat-label">Member Since</div>
                    <div class="user-stat-value">${new Date(user.created_at).toLocaleDateString()}</div>
                </div>
            `;
            return;
        }
    }

    container.innerHTML = `
        <div class="user-stat">
            <div class="user-stat-label">Source</div>
            <div class="user-stat-value">${likesData.source}</div>
        </div>
        <div class="user-stat">
            <div class="user-stat-label">Scraped At</div>
            <div class="user-stat-value">${new Date(likesData.scraped_at).toLocaleString()}</div>
        </div>
    `;
}

// ==================== CLUSTERS PAGE ====================
async function loadClustersPage() {
    await loadData();

    // Update stats
    document.getElementById('cluster-count').textContent = clustersData.clusters.length;
    document.getElementById('total-tracks').textContent = clustersData.total_tracks.toLocaleString();
    document.getElementById('largest-cluster').textContent = clustersData.clusters[0].track_count.toLocaleString();

    const avgSize = Math.round(clustersData.total_tracks / clustersData.clusters.length);
    document.getElementById('avg-cluster-size').textContent = avgSize.toLocaleString();

    // Create distribution chart
    createDistributionChart();

    // Render cluster cards
    renderClusterCards();
}

function createDistributionChart() {
    const ctx = document.getElementById('clusterDistributionChart').getContext('2d');
    const clusters = clustersData.clusters;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: clusters.map(c => c.name),
            datasets: [{
                label: 'Track Count',
                data: clusters.map(c => c.track_count),
                backgroundColor: clusters.map(c => clusterColors[c.id] || '#6b7280'),
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255,255,255,0.1)'
                    },
                    ticks: {
                        color: '#a0a0a0'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#a0a0a0',
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

function renderClusterCards() {
    const container = document.getElementById('clusters-container');

    container.innerHTML = clustersData.clusters.map(cluster => {
        const percentage = ((cluster.track_count / clustersData.total_tracks) * 100).toFixed(1);
        const sampleTracks = cluster.sample_tracks || [];

        return `
            <div class="card" id="${cluster.id}" style="margin-bottom: 1.5rem;">
                <h2 style="border-left: 4px solid ${clusterColors[cluster.id] || '#6b7280'}; padding-left: 1rem;">
                    ${cluster.name}
                </h2>
                <div class="cluster-stats" style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                    <div>
                        <span style="font-size: 1.5rem; font-weight: bold; color: var(--primary);">${cluster.track_count}</span>
                        <span style="color: var(--text-muted);"> tracks (${percentage}%)</span>
                    </div>
                    <div>
                        <span style="font-size: 1.5rem; font-weight: bold;">${cluster.unique_artists}</span>
                        <span style="color: var(--text-muted);"> artists</span>
                    </div>
                    <div>
                        <span style="font-size: 1.5rem; font-weight: bold;">${cluster.avg_duration_min}</span>
                        <span style="color: var(--text-muted);"> min avg</span>
                    </div>
                </div>

                <h3 style="font-size: 1rem; color: var(--text-muted); margin-bottom: 0.5rem;">Sample Tracks</h3>
                <div class="tracks-list" style="max-height: 200px;">
                    ${sampleTracks.map(t => `
                        <div class="track-item" onclick="window.open('${t.url}', '_blank')">
                            <div class="track-info">
                                <div class="track-title">${escapeHtml(t.title)}</div>
                                <div class="track-artist">${escapeHtml(t.artist)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>

                <a href="eq-presets.html#${cluster.id}" class="btn btn-secondary" style="margin-top: 1rem;">
                    View EQ Preset
                </a>
            </div>
        `;
    }).join('');
}

function closeModal() {
    document.getElementById('clusterModal').classList.remove('active');
}

// ==================== EQ PRESETS PAGE ====================
async function loadEQPresetsPage() {
    await loadData();

    // Update stats
    document.getElementById('preset-count').textContent = presetsData.presets.length;

    // Render presets
    renderPresetCards();
}

function renderPresetCards() {
    const container = document.getElementById('presets-container');

    container.innerHTML = presetsDetailedData.presets.map(preset => {
        const eqSettings = preset.eq_settings;
        const frequencies = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];

        return `
            <div class="card" id="${preset.cluster_id}" style="margin-bottom: 1.5rem;">
                <h2 style="border-left: 4px solid ${clusterColors[preset.cluster_id] || '#6b7280'}; padding-left: 1rem;">
                    ${preset.preset_name}
                </h2>
                <p style="color: var(--text-muted); margin-bottom: 1rem;">${preset.description}</p>

                <div class="eq-visualizer">
                    ${frequencies.map(freq => {
                        const db = eqSettings[freq] || 0;
                        const height = Math.abs(db) * 8;
                        const isNegative = db < 0;

                        return `
                            <div class="eq-band">
                                <div class="eq-db" style="color: ${db > 0 ? '#ff5500' : db < 0 ? '#3b82f6' : '#a0a0a0'}">
                                    ${db > 0 ? '+' : ''}${db}dB
                                </div>
                                <div class="eq-bar-container">
                                    <div class="eq-zero-line"></div>
                                    <div class="eq-bar ${isNegative ? 'negative' : ''}"
                                         style="height: ${height}px;"></div>
                                </div>
                                <div class="eq-freq">${formatFreq(freq)}</div>
                            </div>
                        `;
                    }).join('')}
                </div>

                <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                    <div>
                        <span style="font-weight: bold;">${preset.track_count}</span>
                        <span style="color: var(--text-muted);"> tracks</span>
                    </div>
                </div>

                <h3 style="font-size: 1rem; color: var(--text-muted); margin: 1rem 0 0.5rem;">Characteristics</h3>
                <div class="tags">
                    ${preset.characteristics.map(c => `<span class="tag">${c}</span>`).join('')}
                </div>

                <h3 style="font-size: 1rem; color: var(--text-muted); margin: 1rem 0 0.5rem;">Sample Tracks</h3>
                <div class="tracks-list" style="max-height: 150px;">
                    ${preset.sample_tracks.map(t => `
                        <div class="track-item" onclick="window.open('${t.url}', '_blank')">
                            <div class="track-info">
                                <div class="track-title">${escapeHtml(t.title)}</div>
                                <div class="track-artist">${escapeHtml(t.artist)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function formatFreq(freq) {
    if (freq >= 1000) {
        return (freq / 1000) + 'k';
    }
    return freq.toString();
}

function downloadPresets() {
    const dataStr = JSON.stringify(presetsData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'eq_presets.json';
    a.click();
    URL.revokeObjectURL(url);
}

function downloadDetailedPresets() {
    const dataStr = JSON.stringify(presetsDetailedData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'eq_presets_detailed.json';
    a.click();
    URL.revokeObjectURL(url);
}

// ==================== TRACKS PAGE ====================
let allTracks = [];
let filteredTracks = [];
let currentPage = 1;
const tracksPerPage = 50;

async function loadTracksPage() {
    await loadData();

    // Merge cluster info into tracks
    allTracks = clustersData.clusters.flatMap(cluster =>
        cluster.tracks.map(t => ({...t, cluster_name: cluster.name, cluster_id: cluster.id}))
    );

    filteredTracks = [...allTracks];

    // Update stats
    document.getElementById('total-tracks').textContent = allTracks.length.toLocaleString();

    const artists = new Set(allTracks.map(t => t.artist));
    document.getElementById('unique-artists').textContent = artists.size.toLocaleString();

    const totalDurationMs = allTracks.reduce((sum, t) => sum + (t.duration_ms || 0), 0);
    const totalHours = Math.round(totalDurationMs / 3600000);
    document.getElementById('total-duration').textContent = `${totalHours}h`;

    const avgDuration = totalDurationMs / allTracks.length / 60000;
    document.getElementById('avg-duration').textContent = `${avgDuration.toFixed(1)}m`;

    // Populate cluster filter
    const clusterFilter = document.getElementById('cluster-filter');
    clustersData.clusters.forEach(c => {
        const option = document.createElement('option');
        option.value = c.id;
        option.textContent = `${c.name} (${c.track_count})`;
        clusterFilter.appendChild(option);
    });

    // Set up event listeners
    document.getElementById('search-input').addEventListener('input', filterTracks);
    document.getElementById('cluster-filter').addEventListener('change', filterTracks);
    document.getElementById('sort-select').addEventListener('change', sortAndRenderTracks);

    // Initial render
    renderTracks();
}

function filterTracks() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const clusterFilter = document.getElementById('cluster-filter').value;

    filteredTracks = allTracks.filter(t => {
        const matchesSearch = !searchTerm ||
            t.title?.toLowerCase().includes(searchTerm) ||
            t.artist?.toLowerCase().includes(searchTerm) ||
            t.genre?.toLowerCase().includes(searchTerm);

        const matchesCluster = !clusterFilter || t.cluster_id === clusterFilter;

        return matchesSearch && matchesCluster;
    });

    currentPage = 1;
    sortAndRenderTracks();
}

function sortAndRenderTracks() {
    const sortBy = document.getElementById('sort-select').value;

    filteredTracks.sort((a, b) => {
        switch (sortBy) {
            case 'title':
                return (a.title || '').localeCompare(b.title || '');
            case 'artist':
                return (a.artist || '').localeCompare(b.artist || '');
            case 'duration':
                return (b.duration_ms || 0) - (a.duration_ms || 0);
            case 'plays':
                return (b.plays || 0) - (a.plays || 0);
            case 'liked_at':
            default:
                return new Date(b.liked_at || 0) - new Date(a.liked_at || 0);
        }
    });

    renderTracks();
}

function renderTracks() {
    const startIndex = (currentPage - 1) * tracksPerPage;
    const endIndex = startIndex + tracksPerPage;
    const pageTracks = filteredTracks.slice(startIndex, endIndex);

    document.getElementById('tracks-count').textContent =
        `Showing ${startIndex + 1}-${Math.min(endIndex, filteredTracks.length)} of ${filteredTracks.length.toLocaleString()} tracks`;

    const tbody = document.getElementById('tracks-tbody');
    tbody.innerHTML = pageTracks.map(t => `
        <tr onclick="openTrackModal('${t.track_id}')" style="cursor: pointer;">
            <td>
                <img src="${t.artwork_url?.replace('-large', '-small') || ''}"
                     alt="" style="width: 40px; height: 40px; border-radius: 4px; object-fit: cover;"
                     onerror="this.style.display='none'">
            </td>
            <td>
                <div style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${escapeHtml(t.title)}
                </div>
            </td>
            <td>${escapeHtml(t.artist)}</td>
            <td>${t.duration || '-'}</td>
            <td><span class="tag">${escapeHtml(t.genre || 'N/A')}</span></td>
            <td>
                <span class="tag" style="background: ${clusterColors[t.cluster_id] || '#6b7280'}; color: white;">
                    ${t.cluster_name}
                </span>
            </td>
            <td>${t.plays?.toLocaleString() || '-'}</td>
        </tr>
    `).join('');

    renderPagination();
}

function renderPagination() {
    const totalPages = Math.ceil(filteredTracks.length / tracksPerPage);
    const pagination = document.getElementById('pagination');

    let html = '';

    html += `<button onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Prev</button>`;

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        html += `<button onclick="goToPage(1)">1</button>`;
        if (startPage > 2) html += `<button disabled>...</button>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button onclick="goToPage(${i})" class="${i === currentPage ? 'active' : ''}">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<button disabled>...</button>`;
        html += `<button onclick="goToPage(${totalPages})">${totalPages}</button>`;
    }

    html += `<button onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Next</button>`;

    pagination.innerHTML = html;
}

function goToPage(page) {
    const totalPages = Math.ceil(filteredTracks.length / tracksPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTracks();
    document.querySelector('.table-container').scrollTop = 0;
}

function openTrackModal(trackId) {
    const track = allTracks.find(t => t.track_id == trackId);
    if (!track) return;

    document.getElementById('modal-track-title').textContent = track.title;
    document.getElementById('modal-track-content').innerHTML = `
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
            <img src="${track.artwork_url || ''}" alt=""
                 style="width: 150px; height: 150px; border-radius: 8px; object-fit: cover;"
                 onerror="this.style.display='none'">
            <div>
                <p><strong>Artist:</strong> ${escapeHtml(track.artist)}</p>
                <p><strong>Duration:</strong> ${track.duration || 'N/A'}</p>
                <p><strong>Genre:</strong> ${escapeHtml(track.genre || 'N/A')}</p>
                <p><strong>Plays:</strong> ${track.plays?.toLocaleString() || 'N/A'}</p>
                <p><strong>Likes:</strong> ${track.likes?.toLocaleString() || 'N/A'}</p>
                <p><strong>Cluster:</strong> <span class="tag" style="background: ${clusterColors[track.cluster_id] || '#6b7280'}; color: white;">${track.cluster_name}</span></p>
            </div>
        </div>
        ${track.description ? `<p style="color: var(--text-muted); margin-bottom: 1rem;">${escapeHtml(track.description.substring(0, 300))}...</p>` : ''}
        <a href="${track.url}" target="_blank" class="btn btn-primary">Open on SoundCloud</a>
    `;

    document.getElementById('trackModal').classList.add('active');
}

function closeTrackModal() {
    document.getElementById('trackModal').classList.remove('active');
}

// ==================== UTILITIES ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modals on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeTrackModal();
    }
});

// Close modals on background click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});
