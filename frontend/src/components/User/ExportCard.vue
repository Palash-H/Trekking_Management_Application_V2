<template>
  <div class="card export-card">
    <div class="card-header">
      <h2>Export Trekking History</h2>
      <span class="badge">CSV Task</span>
    </div>
    
    <div class="card-body">
      <p class="desc">
        Download a complete CSV report of all your past and upcoming treks, including dates, locations, and booking statuses. This task processes in the background.
      </p>

      <div class="action-area">
        <button 
          v-if="!downloadFilename" 
          class="btn btn-indigo" 
          @click="$emit('trigger-export')" 
          :disabled="isGenerating"
        >
          {{ isGenerating ? 'Requesting...' : 'Generate History Report' }}
        </button>
        
        <button 
          v-else 
          class="btn btn-green" 
          @click="$emit('download-report')" 
          :disabled="isDownloading"
        >
          {{ isDownloading ? 'Downloading...' : '⬇ Download CSV' }}
        </button>
        
        <button v-if="downloadFilename" class="btn-text" @click="$emit('reset')">Reset</button>
      </div>

      <!-- Live Polling Status -->
      <div v-if="isGenerating || taskStatus" class="status-box">
        <div class="spinner" v-if="isGenerating"></div>
        <p class="status-text">{{ taskStatus }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isGenerating: Boolean,
  taskStatus: String,
  downloadFilename: String,
  isDownloading: Boolean
});

defineEmits(['trigger-export', 'download-report', 'reset']);
</script>

<style scoped>
/* Card Base */
.card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden; height: 100%; }
.card-header { padding: 1.25rem 1.5rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0; }
.card-body { padding: 1.5rem; }

/* Export Specifics */
.badge { background: #f1f5f9; color: #475569; padding: 0.25rem 0.75rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.desc { color: #475569; line-height: 1.6; margin-bottom: 1.5rem; font-size: 0.95rem; }
.action-area { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }

/* Status Box & Spinner */
.status-box { margin-top: 1.5rem; padding: 1rem; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; gap: 1rem; border: 1px solid #e2e8f0; }
.status-text { color: #334155; font-weight: 500; font-size: 0.9rem; margin: 0; }
.spinner { width: 18px; height: 18px; border: 3px solid #cbd5e1; border-top-color: #4f46e5; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Buttons */
.btn { padding: 0.75rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; border: none; transition: 0.2s; text-align: center; }
.btn-indigo { background: #4f46e5; color: white; }
.btn-indigo:hover:not(:disabled) { background: #4338ca; }
.btn-green { background: #16a34a; color: white; }
.btn-green:hover:not(:disabled) { background: #15803d; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-text { background: none; color: #64748b; border: none; font-weight: 600; cursor: pointer; }
.btn-text:hover { color: #0f172a; text-decoration: underline; }
</style>