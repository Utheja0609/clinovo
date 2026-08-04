/**
 * CLINICAL DASHBOARD CONTROLLER
 * Section 1: Site breakdown (Max 3 Sites).
 * Section 2: Role comparison bar chart matching the role palette color.
 * Section 3: Role vs Role line graph evaluating all available sites.
 * GIS Map: Dynamic Leaflet map bound to active data store & submission metrics.
 */

// 1. Data Store Declarations
let clinicalSites = {};
const clinicalRoles = [
  'Principal Investigator',
  'Primary Contact For Site Communication',
  'Study Coordinator',
  'Pharmacist',
  'Test Article Shipment',
  'All Other Regulatory Supplies',
  'Regulatory Manager',
  'Central Unit Manager',
  'Data Manager'
];

Chart.register(ChartDataLabels);

let barChartInstance = null;
let lineChartInstance = null;
let pieInstances = {};

const state = {
  selectedSites: [],
  selectedGreenRoles: ['Principal Investigator', 'Study Coordinator']
};

const roleColors = [
  '#facc15', '#06b6d4', '#f87171', '#a855f7', '#3b82f6',
  '#f97316', '#10b981', '#ec4899', '#64748b'
];

// Helper to safely fetch data store from API/Window
function getActiveDataStore() {
  if (typeof window.dashboardDataStore !== 'undefined' && window.dashboardDataStore.sitesYesData) {
    return window.dashboardDataStore.sitesYesData;
  }
  if (typeof window.serverDbSitesData !== 'undefined') {
    return window.serverDbSitesData;
  }
  return {};
}

/* ==========================================================================
   2. DYNAMIC GEOGRAPHIC LOOKUP & SITE METADATA EXTRACTOR
   ========================================================================== */

/**
 * Dynamically constructs site metadata and coordinates directly from active live database API endpoint
 */
async function getDynamicSiteLocations() {
  const dataStore = getActiveDataStore();
  const sitesList = Object.keys(dataStore);

  try {
    const res = await fetch('/api/site-locations');
    const apiLocations = await res.json();

    if (Array.isArray(apiLocations) && apiLocations.length > 0) {
      return apiLocations.map((site, index) => {
        const siteRoleScores = dataStore[site.site_name] || {};
        const scores = Object.values(siteRoleScores);
        const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;

        return {
          id: site.site_name,
          name: site.site_name,
          official_address: site.official_address || 'Clinical Center',
          code: `SITE-${index + 101}`,
          city: site.city || 'Clinical Center',
          country: site.country || 'Global Site',
          latitude: parseFloat(site.latitude) || 17.3850,
          longitude: parseFloat(site.longitude) || 78.4867,
          compliance_score: avgScore,
          roleScores: siteRoleScores,
          active_studies: Math.floor(Math.random() * 4) + 1,
          active_staff: Math.floor(Math.random() * 15) + 10
        };
      });
    }
  } catch (err) {
    console.warn("[GIS Map] Failed to fetch live site locations from API:", err);
  }

  // Fallback if API response is empty
  return sitesList.map((siteName, index) => {
    const siteRoleScores = dataStore[siteName] || {};
    const scores = Object.values(siteRoleScores);
    const avgScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;

    return {
      id: siteName,
      name: siteName,
      official_address: 'Clinical Center',
      code: `SITE-${index + 101}`,
      city: "Clinical Center",
      country: "Global Site",
      latitude: 17.3850 + (index * 0.05),
      longitude: 78.4867 + (index * 0.05),
      compliance_score: avgScore,
      roleScores: siteRoleScores,
      active_studies: 2,
      active_staff: 10
    };
  });
}

/* ==========================================================================
   3. GIS MAP CONTROLLER OBJECT (LEAFLET INTEGRATION)
   ========================================================================== */
const ClinovoMapController = {
  leafletMap: null,
  mapMarkers: [],

  // Initialize Leaflet World Map
  initLeafletMap() {
    const container = document.getElementById('leaflet-map');
    if (!container || this.leafletMap) return;

    this.leafletMap = L.map('leaflet-map', {
      center: [17.3850, 78.4867],
      zoom: 5,
      minZoom: 2,
      maxZoom: 18
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.leafletMap);

    const resetBtn = document.getElementById('btn-reset-map');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => this.resetMapView());
    }
  },

  // Render Pin Markers & Zoom to Selected Sites
  renderMapMarkers(allHospitals, selectedSiteNames) {
    if (!this.leafletMap) this.initLeafletMap();
    if (!this.leafletMap) return;

    // Clear old markers
    this.mapMarkers.forEach(m => this.leafletMap.removeLayer(m));
    this.mapMarkers = [];

    const selectedHospitals = allHospitals.filter(h => selectedSiteNames.includes(h.name) || selectedSiteNames.includes(h.id));

    if (selectedHospitals.length === 0) {
      this.leafletMap.flyTo([17.3850, 78.4867], 5, { duration: 1.2 });
      return;
    }

    selectedHospitals.forEach((h, index) => {
      const markerColor = index === 0 ? '#10b981' : '#6366f1';

      const iconHtml = `
        <div class="pulse-marker" style="background-color: ${markerColor}; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; border: 2px solid white; box-shadow: 0 0 14px ${markerColor}; font-size: 12px;">
          <i class="fa-solid fa-hospital"></i>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-leaflet-marker',
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      const lat = parseFloat(h.latitude) || 17.3850;
      const lng = parseFloat(h.longitude) || 78.4867;

      const marker = L.marker([lat, lng], { icon: customIcon })
        .addTo(this.leafletMap)
        .bindPopup(`
          <div style="font-family: Arial, sans-serif; padding: 4px;">
            <strong style="color: #0d3b66; font-size: 14px;">${h.name}</strong><br>
            <span style="color: #475569; font-size: 12px;">${h.official_address}</span><br>
            <span style="color: #059669; font-weight: bold; font-size: 11px;">Compliance Score: ${h.compliance_score}%</span>
          </div>
        `);

      marker.on('click', () => {
        this.leafletMap.flyTo([lat, lng], 13, { duration: 1.5 });
      });

      this.mapMarkers.push(marker);
    });

    if (selectedHospitals.length === 1) {
      this.leafletMap.flyTo([parseFloat(selectedHospitals[0].latitude), parseFloat(selectedHospitals[0].longitude)], 13, { duration: 1.5 });
    } else if (selectedHospitals.length >= 2) {
      const bounds = L.latLngBounds(selectedHospitals.map(h => [parseFloat(h.latitude), parseFloat(h.longitude)]));
      this.leafletMap.fitBounds(bounds, { padding: [60, 60] });
    }
  },

  // Reset Map View
  resetMapView() {
    if (!this.leafletMap) return;
    this.leafletMap.flyTo([17.3850, 78.4867], 5, { duration: 1.2 });
  }
};

/* ==========================================================================
   4. INITIALIZATION & REFRESH LOGIC
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  const activeStore = getActiveDataStore();
  clinicalSites = Object.keys(activeStore);
  
  if (clinicalSites.length > 0 && state.selectedSites.length === 0) {
    state.selectedSites = clinicalSites.slice(0, 2); // Default to first 2 sites
  }

  initCustomDropdowns();
  refreshDashboardView();
});

window.refreshDashboardView = async function() {
  updateRedZone();
  updateYellowZone();
  updateGreenZone();
  updateLiveBar();
  renderMasterLegend();

  // Extract dynamic site locations asynchronously from API
  const dynamicSites = await getDynamicSiteLocations();

  ClinovoMapController.initLeafletMap();
  ClinovoMapController.renderMapMarkers(dynamicSites, state.selectedSites);
};

function getPoppedOutRoles() {
  const singleRoleSelect = document.getElementById('singleRoleSelect');
  const singleRole = singleRoleSelect ? singleRoleSelect.value : '';
  const activeSet = new Set(state.selectedGreenRoles);
  if (singleRole && singleRole !== 'None') activeSet.add(singleRole);
  return Array.from(activeSet);
}

function renderMasterLegend() {
  const container = document.getElementById('masterLegendList');
  if (!container) return;

  const poppedRoles = getPoppedOutRoles();

  container.innerHTML = clinicalRoles.map((roleName, idx) => {
    const color = roleColors[idx % roleColors.length];
    const isPopped = poppedRoles.includes(roleName);
    return `
      <div class="master-legend-item ${isPopped ? 'popped-highlight' : ''}">
        <span class="master-legend-box" style="background:${color}"></span>
        <span>${roleName} ${isPopped ? '⚡' : ''}</span>
      </div>
    `;
  }).join('');
}

function initCustomDropdowns() {
  const activeStore = getActiveDataStore();
  const siteOptions = Object.keys(activeStore).length > 0 ? Object.keys(activeStore) : clinicalSites;

  // SECTION 1: Site Selector (Max 3 Sites)
  createCustomMultiselect('ms-sites', 'chips-sites', {
    options: Array.isArray(siteOptions) ? siteOptions : [],
    max: 3, // Capped to max 3 sites for side-by-side grid
    get: () => state.selectedSites,
    toggle: (site) => {
      const idx = state.selectedSites.indexOf(site);
      if (idx < 0) state.selectedSites.push(site);
      else state.selectedSites.splice(idx, 1);
    },
    onChange: () => { refreshDashboardView(); }
  });

  // SECTION 2: Single Role Selector (Includes "None")
  const roleSelect = document.getElementById('singleRoleSelect');
  if (roleSelect) {
    const roleOptions = ['None', ...clinicalRoles];
    roleSelect.innerHTML = roleOptions.map(r => `<option value="${r}">${r}</option>`).join('');
    roleSelect.value = 'None';
    roleSelect.addEventListener('change', () => {
      refreshDashboardView();
    });
  }

  // SECTION 3: Role vs Role Selector
  createCustomMultiselect('ms-roles-green', 'chips-roles-green', {
    options: clinicalRoles,
    max: 4,
    get: () => state.selectedGreenRoles,
    toggle: (role) => {
      const idx = state.selectedGreenRoles.indexOf(role);
      if (idx < 0) state.selectedGreenRoles.push(role);
      else state.selectedGreenRoles.splice(idx, 1);
    },
    onChange: () => { refreshDashboardView(); }
  });
}

function createCustomMultiselect(elId, chipId, opts) {
  const el = document.getElementById(elId);
  const chipsEl = document.getElementById(chipId);
  if (!el || !chipsEl) return;
  
  el.innerHTML = `
    <button class="ms-btn" type="button">
      <span class="label">Select Options...</span>
      <span class="chev">▼</span>
    </button>
    <div class="ms-panel"></div>
  `;

  const btn = el.querySelector('.ms-btn');
  const panel = el.querySelector('.ms-panel');
  const label = el.querySelector('.label');

  function render() {
    const sel = opts.get();
    label.textContent = sel.length ? `${sel.length} Selected` : 'Select Options...';
    
    const optionList = Array.isArray(opts.options) ? opts.options : [];
    
    panel.innerHTML = optionList.map(optName => {
      const isSel = sel.includes(optName);
      const disabled = opts.max && !isSel && sel.length >= opts.max;
      return `
        <div class="ms-opt ${isSel ? 'sel' : ''} ${disabled ? 'disabled' : ''}" data-value="${optName}">
          <span class="box"></span>
          <span>${optName}</span>
        </div>
      `;
    }).join('');

    chipsEl.innerHTML = sel.map(optName => `
      <span class="chip">${optName} <b data-value="${optName}">×</b></span>
    `).join('');
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    el.classList.toggle('open');
  });

  panel.addEventListener('click', (e) => {
    const row = e.target.closest('.ms-opt');
    if (!row || row.classList.contains('disabled')) return;
    opts.toggle(row.dataset.value);
    render();
    opts.onChange();
  });

  chipsEl.addEventListener('click', (e) => {
    const b = e.target.closest('b');
    if (!b) return;
    opts.toggle(b.dataset.value);
    render();
    opts.onChange();
  });

  document.addEventListener('click', () => el.classList.remove('open'));
  render();
}

/* ==========================================================================
   5. CHART RENDERING FUNCTIONS
   ========================================================================== */

// SECTION 1 PIE CHARTS
function updateRedZone() {
  const grid = document.getElementById('pieChartsGrid');
  if (!grid) return;
  
  Object.keys(pieInstances).forEach(k => { if (pieInstances[k]) pieInstances[k].destroy(); });
  pieInstances = {};

  if (state.selectedSites.length === 0) {
    grid.innerHTML = '<p style="color:#8a97ad; text-align:center; padding:20px;">No sites selected in Section 1.</p>';
    return;
  }

  const poppedRoles = getPoppedOutRoles();
  const sitesDataStore = getActiveDataStore();

  grid.innerHTML = state.selectedSites.map((site, idx) => `
    <div class="pie-card">
      <h4>${site}</h4>
      <div class="pie-canvas-container">
        <canvas id="pieCanvas_${idx}"></canvas>
      </div>
    </div>
  `).join('');

  setTimeout(() => {
    state.selectedSites.forEach((site, idx) => {
      const canvas = document.getElementById(`pieCanvas_${idx}`);
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      const siteData = sitesDataStore[site] || {};
      
      const labels = Object.keys(siteData);
      const values = Object.values(siteData);
      const totalSum = values.reduce((a, b) => a + b, 0);

      const pieColors = labels.map(roleName => {
        const originalIndex = clinicalRoles.indexOf(roleName);
        return roleColors[(originalIndex >= 0 ? originalIndex : 0) % roleColors.length];
      });

      const offsetArray = labels.map(roleName => poppedRoles.includes(roleName) ? 12 : 0);

      pieInstances[`pieCanvas_${idx}`] = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: pieColors,
            borderWidth: 1,
            borderColor: '#ffffff',
            offset: offsetArray,
            hoverOffset: 16
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          layout: { padding: 10 },
          plugins: {
            legend: { display: false },
            datalabels: {
              color: '#ffffff',
              font: { weight: '800', size: 12, family: 'Sora' },
              anchor: 'center',
              align: 'center',
              formatter: (val) => {
                if (totalSum === 0) return '';
                const pct = Math.round((val / totalSum) * 100);
                return pct > 3 ? `${pct}%` : '';
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return ` ${context.label}: ${context.raw}%`;
                }
              }
            }
          }
        }
      });
    });
  }, 30);
}

// SECTION 2 BAR CHART (Matched to Pie Palette Color & Section 1 Sites)
function updateYellowZone() {
  const singleRoleSelect = document.getElementById('singleRoleSelect');
  if (!singleRoleSelect) return;

  const selectedRole = singleRoleSelect.value;
  const labelEl = document.getElementById('selectedRoleLabel');
  const canvas = document.getElementById('barChartCanvas');
  if (!canvas) return;

  if (barChartInstance) {
    barChartInstance.destroy();
    barChartInstance = null;
  }

  // Handle "None" or no sites selected condition
  if (!selectedRole || selectedRole === 'None' || state.selectedSites.length === 0) {
    if (labelEl) labelEl.innerText = `Role Focused: None Selected`;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    return;
  }

  if (labelEl) labelEl.innerText = `Role Focused: ${selectedRole}`;

  const sitesDataStore = getActiveDataStore();
  
  // Filter sites strictly according to Section 1 selection
  const siteLabels = state.selectedSites;
  const yesScores = siteLabels.map(site => (sitesDataStore[site] && sitesDataStore[site][selectedRole]) || 0);

  // Match bar chart color to the selected role's color in pie palette
  const roleIndex = clinicalRoles.indexOf(selectedRole);
  const matchedColor = roleColors[(roleIndex >= 0 ? roleIndex : 0) % roleColors.length];

  const ctx = canvas.getContext('2d');

  barChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: siteLabels,
      datasets: [{
        label: `${selectedRole} Score (%)`,
        data: yesScores,
        backgroundColor: matchedColor,
        borderColor: matchedColor,
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        datalabels: { display: false },
        legend: {
          display: true,
          position: 'top',
          labels: { font: { family: 'DM Sans', size: 12 }, color: '#51607a' }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Selected Clinical Trial Sites', color: '#0e1726', font: { family: 'Sora', size: 12, weight: 'bold' } },
          ticks: { color: '#51607a', font: { family: 'DM Sans', size: 11 } },
          grid: { display: false }
        },
        y: {
          min: 0,
          max: 100,
          title: { display: true, text: 'Compliance Score (%)', color: '#0e1726', font: { family: 'Sora', size: 12, weight: 'bold' } },
          ticks: { color: '#51607a', font: { family: 'DM Sans', size: 11 } },
          grid: { color: '#e7ebf3' }
        }
      }
    }
  });
}

// SECTION 3 LINE GRAPH (Evaluates All Clinical Sites)
function updateGreenZone() {
  const sitesDataStore = getActiveDataStore();
  const siteLabels = Object.keys(sitesDataStore);

  const datasets = state.selectedGreenRoles.map((role) => {
    const scoresAcrossSites = siteLabels.map(site => (sitesDataStore[site] && sitesDataStore[site][role]) || 0);
    const originalIndex = clinicalRoles.indexOf(role);
    const color = roleColors[(originalIndex >= 0 ? originalIndex : 0) % roleColors.length];

    return {
      label: role,
      data: scoresAcrossSites,
      borderColor: color,
      backgroundColor: color,
      borderWidth: 2,
      fill: false,
      tension: 0.3
    };
  });

  const canvas = document.getElementById('lineChartCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (lineChartInstance) lineChartInstance.destroy();

  lineChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: siteLabels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: {
        datalabels: { display: false },
        legend: {
          display: true,
          position: 'top',
          labels: { font: { family: 'DM Sans', size: 11 }, color: '#51607a', usePointStyle: true }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}%`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Clinical Trial Sites', color: '#0e1726', font: { family: 'Sora', size: 12, weight: 'bold' } },
          ticks: { color: '#51607a', font: { family: 'DM Sans', size: 11 } },
          grid: { display: false }
        },
        y: {
          min: 0,
          max: 100,
          title: { display: true, text: 'Compliance Score (%)', color: '#0e1726', font: { family: 'Sora', size: 12, weight: 'bold' } },
          ticks: { color: '#51607a', font: { family: 'DM Sans', size: 11 } },
          grid: { color: '#e7ebf3' }
        }
      }
    }
  });
}

function updateLiveBar() {
  const sitesEl = document.getElementById('lv-sites');
  const roleEl = document.getElementById('lv-role');
  const singleRoleSelect = document.getElementById('singleRoleSelect');

  if (sitesEl) sitesEl.textContent = state.selectedSites.join(', ') || 'None';
  if (roleEl && singleRoleSelect) roleEl.textContent = singleRoleSelect.value;
}