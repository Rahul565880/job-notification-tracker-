const API_BASE = '/api';
let allJobs = [];
let savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');

// Theme
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
themeIcon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';

themeToggle.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  themeIcon.textContent = next === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('theme', next);
});

document.addEventListener('DOMContentLoaded', () => {
  loadJobs();
  loadStats();
  setupListeners();
  setInterval(() => {
    loadJobs();
    loadStats();
  }, 5 * 60 * 1000);
});

function setupListeners() {
  document.getElementById('searchBtn').addEventListener('click', applyFilters);
  document.getElementById('searchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') applyFilters();
  });
  document.getElementById('locationFilter').addEventListener('change', applyFilters);
  document.getElementById('experienceFilter').addEventListener('change', applyFilters);
  document.getElementById('jobTypeFilter').addEventListener('change', applyFilters);
  document.getElementById('sourceFilter').addEventListener('change', applyFilters);
  document.getElementById('clearFilters').addEventListener('click', clearFilters);
  document.getElementById('refreshBtn').addEventListener('click', () => {
    loadJobs();
    loadStats();
  });
  document.getElementById('scrapeBtn').addEventListener('click', triggerScrape);
}

async function loadJobs() {
  showLoading(true);
  try {
    const res = await fetch(`${API_BASE}/jobs`);
    const data = await res.json();
    allJobs = data.jobs || [];
    applyFilters();
    updateLocationOptions();
  } catch (err) {
    console.error('Error loading jobs:', err);
    showError('Failed to load jobs. Please try again.');
  } finally {
    showLoading(false);
  }
}

async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    const data = await res.json();
    document.getElementById('totalJobs').textContent = data.total_jobs || 0;
    document.getElementById('newJobs').textContent = data.new_jobs || 0;
  } catch (err) {
    console.error('Error loading stats:', err);
  }
}

function updateLocationOptions() {
  const sel = document.getElementById('locationFilter');
  const val = sel.value;
  const locations = [...new Set(allJobs.map((j) => j.location).filter(Boolean))].sort();
  sel.innerHTML = '<option value="">All Locations</option>';
  locations.forEach((loc) => {
    const opt = document.createElement('option');
    opt.value = loc;
    opt.textContent = loc;
    sel.appendChild(opt);
  });
  sel.value = val;
}

function applyFilters() {
  const search = document.getElementById('searchInput').value.toLowerCase().trim();
  const location = document.getElementById('locationFilter').value.toLowerCase();
  const experience = document.getElementById('experienceFilter').value.toLowerCase();
  const jobType = document.getElementById('jobTypeFilter').value.toLowerCase();
  const source = document.getElementById('sourceFilter').value;

  const filtered = allJobs.filter((job) => {
    if (search) {
      const text = `${(job.job_title || '')} ${(job.company_name || '')}`.toLowerCase();
      if (!text.includes(search)) return false;
    }
    if (location && !((job.location || '').toLowerCase().includes(location))) return false;
    if (experience && !((job.experience_level || '').toLowerCase().includes(experience))) return false;
    if (jobType && !((job.job_type || '').toLowerCase().includes(jobType))) return false;
    if (source && job.source_platform !== source) return false;
    return true;
  });

  displayJobs(filtered);
}

function displayJobs(jobs) {
  const container = document.getElementById('jobsContainer');
  const noJobs = document.getElementById('noJobs');

  if (jobs.length === 0) {
    container.innerHTML = '';
    noJobs.style.display = 'block';
    return;
  }

  noJobs.style.display = 'none';
  container.innerHTML = jobs.map((job) => createJobCard(job)).join('');
}

function createJobCard(job) {
  const isNew = job.is_new === 1;
  const isSaved = savedJobs.includes(job.id);
  const newBadge = isNew ? '<span class="new-job-badge">NEW</span>' : '';
  const savedClass = isSaved ? ' saved' : '';
  const savedText = isSaved ? '💾 Saved' : '💾 Save Job';

  const escape = (s) => {
    if (s == null) return '';
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  };

  return `
    <div class="job-card${isNew ? ' new-job' : ''}" data-job-id="${escape(String(job.id))}">
      ${newBadge}
      <div class="job-title">${escape(job.job_title)}</div>
      <div class="company-name">${escape(job.company_name)}</div>
      <div class="job-meta">
        ${job.location ? `<span>📍 ${escape(job.location)}</span>` : ''}
        ${job.experience_level ? `<span>💼 ${escape(job.experience_level)}</span>` : ''}
        ${job.job_type ? `<span>⏰ ${escape(job.job_type)}</span>` : ''}
        ${job.posted_date ? `<span>📅 ${escape(job.posted_date)}</span>` : ''}
      </div>
      <div class="source-platform">Source: ${escape(job.source_platform)}</div>
      <button class="apply-btn" data-job-id="${job.id}">Apply Now</button>
      <button class="save-btn${savedClass}" data-job-id="${job.id}">${savedText}</button>
    </div>
  `;
}

document.addEventListener('click', (e) => {
  if (e.target.classList.contains('save-btn')) {
    const jobId = parseInt(e.target.dataset.jobId, 10);
    if (jobId && !isNaN(jobId)) toggleSaveJob(jobId);
  } else if (e.target.classList.contains('apply-btn')) {
    const jobId = parseInt(e.target.dataset.jobId, 10);
    const job = (allJobs || []).find((j) => j.id === jobId);
    if (job && job.job_url && (job.job_url.startsWith('http://') || job.job_url.startsWith('https://'))) {
      window.open(job.job_url, '_blank', 'noopener,noreferrer');
    }
  }
});

function toggleSaveJob(jobId) {
  if (savedJobs.includes(jobId)) {
    savedJobs = savedJobs.filter((id) => id !== jobId);
  } else {
    savedJobs.push(jobId);
  }
  localStorage.setItem('savedJobs', JSON.stringify(savedJobs));
  applyFilters();
}

function clearFilters() {
  document.getElementById('searchInput').value = '';
  document.getElementById('locationFilter').value = '';
  document.getElementById('experienceFilter').value = '';
  document.getElementById('jobTypeFilter').value = '';
  document.getElementById('sourceFilter').value = '';
  updateLocationOptions();
  applyFilters();
}

async function triggerScrape() {
  const btn = document.getElementById('scrapeBtn');
  btn.disabled = true;
  btn.textContent = 'Scraping...';

  try {
    const res = await fetch(`${API_BASE}/scrape`, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) {
      alert(`Scraping failed: ${data.error || res.statusText || 'Unknown error'}`);
      return;
    }
    alert(`Scraping completed. ${data.new_jobs_count || 0} new jobs found.`);
    loadJobs();
    loadStats();
  } catch (err) {
    console.error('Error triggering scrape:', err);
    alert('Error triggering scrape. Please try again.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Scrape Now';
  }
}

function showLoading(show) {
  document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
}

function showError(msg) {
  alert(msg);
}
