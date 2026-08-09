<template>
  <div class="user-profile">
    <header class="page-header">
      <div>
        <h1>Profile & Settings</h1>
        <p>Update your personal information and export your trekking data.</p>
      </div>
    </header>

    <div v-if="loadingProfile" class="loading-state">Loading profile...</div>

    <div v-else class="layout-grid">
      
      <!-- LEFT COLUMN: Edit Profile Component -->
      <div class="profile-column">
        <ProfileForm 
          :profile="profile" 
          :isSaving="isSaving" 
          @submit-profile="updateProfile" 
        />
      </div>

      <!-- RIGHT COLUMN: Export History Component -->
      <div class="export-column">
        <ExportCard 
          :isGenerating="isGenerating"
          :taskStatus="taskStatus"
          :downloadFilename="downloadFilename"
          :isDownloading="isDownloading"
          @trigger-export="triggerExport"
          @download-report="downloadReport"
          @reset="resetExporter"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
// Import child components
import ProfileForm from '@/components/User/ProfileForm.vue';
import ExportCard from '@/components/User/ExportCard.vue';

// --- Profile State ---
const loadingProfile = ref(true);
const isSaving = ref(false);
const profile = ref({});

// --- Export State ---
const isGenerating = ref(false);
const taskStatus = ref('');
const downloadFilename = ref(null);
const isDownloading = ref(false);
let pollingInterval = null;

// ==========================================
// PROFILE API LOGIC
// ==========================================

const fetchProfile = async () => {
  try {
    const response = await axios.get('/api/profile');
    profile.value = response.data;
  } catch (error) {
    console.error("Failed to load profile:", error);
  } finally {
    loadingProfile.value = false;
  }
};

const updateProfile = async (formData) => {
  isSaving.value = true;
  try {
    const payload = { 
      name: formData.name,
      contact: formData.contact
    };
    
    // Only send password if updated
    if (formData.password && formData.password.trim() !== '') {
      payload.password = formData.password;
    }

    const response = await axios.put('/api/user/profile', payload);
    alert(response.data.msg);
    
    // Refresh to get updated DB data
    await fetchProfile();
  } catch (error) {
    console.error("Failed to update profile:", error);
    alert(error.response?.data?.msg || "Error updating profile.");
  } finally {
    isSaving.value = false;
  }
};

// ==========================================
// EXPORT API LOGIC (CELERY)
// ==========================================

const triggerExport = async () => {
  isGenerating.value = true;
  taskStatus.value = "Starting background task...";
  downloadFilename.value = null;

  try {
    const response = await axios.post('/api/user/export-history');
    pollTaskStatus(response.data.task_id);
  } catch (error) {
    console.error("Failed to start export:", error);
    taskStatus.value = "Error starting export.";
    isGenerating.value = false;
  }
};

const pollTaskStatus = (taskId) => {
  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get(`/api/user/export-status/${taskId}`);
      const data = response.data;
      
      taskStatus.value = data.status;

      if (data.state === 'SUCCESS') {
        clearInterval(pollingInterval);
        isGenerating.value = false;
        downloadFilename.value = data.filename;
        taskStatus.value = "Report is ready!";
      } else if (data.state === 'FAILURE' || data.state === 'REVOKED') {
        clearInterval(pollingInterval);
        isGenerating.value = false;
        taskStatus.value = "Task failed: " + data.status;
      }
    } catch (error) {
      clearInterval(pollingInterval);
      isGenerating.value = false;
      taskStatus.value = "Lost connection to server.";
    }
  }, 2000);
};

const downloadReport = async () => {
  if (!downloadFilename.value) return;
  isDownloading.value = true;

  try {
    const response = await axios.get(`/api/user/download/${downloadFilename.value}`, {
      responseType: 'blob' 
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', downloadFilename.value);
    document.body.appendChild(link);
    link.click();
    
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Download failed:", error);
    alert("Error downloading the file.");
  } finally {
    isDownloading.value = false;
  }
};

const resetExporter = () => {
  downloadFilename.value = null;
  taskStatus.value = '';
};

// --- Lifecycle Hooks ---
onMounted(() => {
  fetchProfile();
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style scoped>
/* The Parent only handles layout CSS! */
.user-profile { max-width: 1000px; margin: 0 auto; padding: 2rem 1rem; }

.page-header { margin-bottom: 2rem; }
.page-header h1 { font-size: 2.25rem; color: #0f172a; font-weight: 700; margin-bottom: 0.25rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }
.loading-state { text-align: center; padding: 3rem; color: #64748b; }

/* Grid */
.layout-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 2rem; 
  align-items: stretch; /* Ensures both cards match in height */
}

@media (max-width: 768px) { 
  .layout-grid { grid-template-columns: 1fr; } 
}
</style>