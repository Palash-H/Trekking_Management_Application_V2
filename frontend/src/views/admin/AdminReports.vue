<template>
  <div class="admin-reports">
    <header class="page-header">
      <div>
        <h1>Reports & Analytics</h1>
        <p>Export database records and view platform performance.</p>
      </div>
    </header>

    <div class="reports-layout">
      <!-- LEFT COLUMN: Background Tasks / Exports -->
      <div class="report-card export-card">
        <div class="card-header">
          <h2>Booking Data Export</h2>
          <span class="badge">CSV Task</span>
        </div>
        <p class="desc">
          Generate a complete, downloadable report of all global bookings. This task runs securely in the background via Celery.
        </p>

        <div class="action-area">
          <button v-if="!downloadFilename" class="btn btn-primary" @click="triggerReportGeneration" :disabled="isGenerating">
            {{ isGenerating ? 'Task Queued...' : 'Generate Full Report' }}
          </button>
          
          <button v-else class="btn btn-green" @click="downloadReport" :disabled="isDownloading">
            {{ isDownloading ? 'Downloading...' : '⬇ Download CSV Report' }}
          </button>
          
          <button v-if="downloadFilename" class="btn btn-text" @click="resetExporter">Generate Another</button>
        </div>

        <div v-if="isGenerating || taskStatus" class="status-box">
          <div class="spinner" v-if="isGenerating"></div>
          <p class="status-text">{{ taskStatus }}</p>
        </div>
      </div>

      
      <div class="report-card stats-card">
        <div class="card-header">
          <h2>Trekking Statistics</h2>
          
          <span :class="['badge', statistics.is_cached ? 'cached' : 'live']">
            {{ statistics.is_cached ? '⚡ Cached Data' : '🔴 Live Data' }}
          </span>
        </div>
        
        <div v-if="loadingStats" class="loading-state">Crunching numbers...</div>
        
        <div v-else class="stats-content">
          <!-- Status Breakdown -->
          <div class="status-summary">
            <div class="summary-item">
              <span class="dot confirmed"></span>
              <strong>{{ statistics.status_breakdown.Confirmed || 0 }}</strong> Confirmed
            </div>
            <div class="summary-item">
              <span class="dot pending"></span>
              <strong>{{ statistics.status_breakdown.Pending || 0 }}</strong> Pending
            </div>
            <div class="summary-item">
              <span class="dot cancelled"></span>
              <strong>{{ statistics.status_breakdown.Cancelled || 0 }}</strong> Cancelled
            </div>
          </div>

          <!-- Top Treks (CSS Bar Chart) -->
          <h3 class="chart-title">Most Popular Treks</h3>
          <div class="bar-chart">
            <div v-for="trek in statistics.popular_treks" :key="trek.name" class="bar-row">
              <div class="bar-label">
                <span>{{ trek.name }}</span>
                <span class="bar-count">{{ trek.bookings }}</span>
              </div>
              <div class="bar-track">
                
                <div class="bar-fill" :style="{ width: calculatePercentage(trek.bookings) + '%' }"></div>
              </div>
            </div>
            <div v-if="statistics.popular_treks.length === 0" class="empty-state">
              Not enough data yet.
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

// --- State for Export ---
const isGenerating = ref(false);
const taskStatus = ref('');
const downloadFilename = ref(null);
const isDownloading = ref(false);
let pollingInterval = null;

// --- State for Statistics ---
const statistics = ref({ popular_treks: [], status_breakdown: {}, total_bookings: 0, is_cached:false});
const loadingStats = ref(true);

// --- Fetch Statistics ---
const fetchStatistics = async () => {
  try {
    const response = await axios.get('/api/admin/statistics');
    statistics.value = response.data;
    const clientTimeNow = Date.now()/1000;
    const dataAge = clientTimeNow - response.data.generated_at;
    statistics.value.is_cached = dataAge>1.5;
  } catch (error) {
    console.error("Failed to fetch statistics:", error);
  } finally {
    loadingStats.value = false;
  }
};


const calculatePercentage = (count) => {
  if (statistics.value.popular_treks.length === 0) return 0;
  
  const maxBookings = Math.max(...statistics.value.popular_treks.map(t => t.bookings));
  return (count / maxBookings) * 100;
};


const triggerReportGeneration = async () => {
  isGenerating.value = true;
  taskStatus.value = "Starting background task...";
  downloadFilename.value = null;
  try {
    const response = await axios.post('/api/admin/reports/generate-bookings');
    pollTaskStatus(response.data.task_id);
  } catch (error) {
    taskStatus.value = "Error starting task.";
    isGenerating.value = false;
  }
};

const pollTaskStatus = (taskId) => {
  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get(`/api/admin/reports/status/${taskId}`);
      const data = response.data;
      taskStatus.value = data.status;
      if (data.state === 'SUCCESS') {
        clearInterval(pollingInterval);
        isGenerating.value = false;
        downloadFilename.value = data.filename;
        taskStatus.value = "Report generated successfully!";
      } else if (data.state === 'FAILURE' || data.state === 'REVOKED') {
        clearInterval(pollingInterval);
        isGenerating.value = false;
        taskStatus.value = "Task failed: " + data.status;
      }
    } catch (error) {
      clearInterval(pollingInterval);
      isGenerating.value = false;
      taskStatus.value = "Lost connection to task worker.";
    }
  }, 2000);
};

const downloadReport = async () => {
  if (!downloadFilename.value) return;
  isDownloading.value = true;
  try {
    const response = await axios.get(`/api/admin/reports/download/${downloadFilename.value}`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', downloadFilename.value);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert("Error downloading the file.");
  } finally {
    isDownloading.value = false;
  }
};

const resetExporter = () => { downloadFilename.value = null; taskStatus.value = ''; };

onMounted(() => {
  fetchStatistics();
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style scoped>
/* Keep existing header styles */
.page-header { margin-bottom: 2.5rem; }
.page-header h1 { font-size: 2rem; color: #0f172a; font-weight: 700; margin-bottom: 0.5rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }

/* Update your badge styles */
.badge { 
  background: #f1f5f9; color: #475569; padding: 0.25rem 0.75rem; 
  border-radius: 99px; font-size: 0.75rem; font-weight: 600; 
  text-transform: uppercase; transition: all 0.3s ease;
}
.badge.live { 
  background: #fee2e2; 
  color: #991b1b; 
}
.badge.cached { 
  background: #fef08a; 
  color: #854d0e; 
}

/* Grid Layout */
.reports-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  align-items: start;
}

.report-card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.card-header h2 { font-size: 1.25rem; font-weight: 700; color: #0f172a; }

.badge { background: #f1f5f9; color: #475569; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.badge.live { background: #dcfce3; color: #166534; }

/* Statistics Custom Styles */
.status-summary {
  display: flex;
  justify-content: space-between;
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border: 1px solid #e2e8f0;
}
.summary-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem; color: #475569; }
.summary-item strong { color: #0f172a; font-size: 1.1rem; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.confirmed { background-color: #16a34a; }
.dot.pending { background-color: #eab308; }
.dot.cancelled { background-color: #ef4444; }

.chart-title { font-size: 1rem; color: #64748b; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em; }
.bar-row { margin-bottom: 1.25rem; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 0.4rem; }
.bar-count { color: #64748b; font-weight: 500; }
.bar-track { width: 100%; background: #f1f5f9; border-radius: 99px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; background: #4f46e5; border-radius: 99px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
.empty-state { color: #94a3b8; font-style: italic; }

/* Button & Utility styles */
.desc { color: #475569; line-height: 1.6; margin-bottom: 2rem; }
.action-area { display: flex; align-items: center; gap: 1rem; }
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-primary { background-color: #4f46e5; color: white; }
.btn-primary:hover:not(:disabled) { background-color: #4338ca; }
.btn-primary:disabled { background-color: #a5b4fc; cursor: not-allowed; }
.btn-green { background-color: #16a34a; color: white; }
.btn-green:hover:not(:disabled) { background-color: #15803d; }
.btn-green:disabled { background-color: #86efac; cursor: not-allowed; }
.btn-text { background: none; color: #64748b; padding: 0.75rem; }
.btn-text:hover { color: #0f172a; text-decoration: underline; }
.status-box { margin-top: 1.5rem; padding: 1rem; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; gap: 1rem; border: 1px solid #e2e8f0;}
.status-text { color: #334155; font-weight: 500; font-size: 0.9rem; margin: 0; }
.spinner { width: 20px; height: 20px; border: 3px solid #cbd5e1; border-top-color: #4f46e5; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>