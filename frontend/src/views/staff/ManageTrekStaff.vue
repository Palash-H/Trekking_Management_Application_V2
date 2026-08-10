<template>
  <div class="manage-trek-staff">
    <!-- Header -->
    <header class="page-header">
      <div>
        <router-link to="/staff/dashboard" class="back-link">← Back to Dashboard</router-link>
        <h1>Manage Trek: {{ trekName }}</h1>
        <p>Update trek status and manage your participants.</p>
      </div>
    </header>

    <div v-if="loading" class="loading-state">Loading trek details...</div>

    <div v-else class="layout-grid">
      
      <!-- LEFT COLUMN: Trek Settings Component -->
      <div class="settings-column">
        <TrekSettingsForm 
          :dbTrekStatus="dbTrekStatus"
          :isUpdatingSettings="isUpdatingSettings"
          @update-settings="updateTrekSettings"
        />
      </div>

      <!-- RIGHT COLUMN: Participant Roster Component -->
      <div class="participants-column">
        <ParticipantRoster 
          :participants="participants"
          :dbTrekStatus="dbTrekStatus"
          @remove-participant="removeParticipant"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';


import TrekSettingsForm from '@/components/Staff/TrekSettingsForm.vue';
import ParticipantRoster from '@/components/Staff/ParticipantRoster.vue';

const route = useRoute();
const trekId = route.params.id; 

const loading = ref(true);
const trekName = ref('');
const dbTrekStatus = ref('');
const participants = ref([]);
const isUpdatingSettings = ref(false);

// --- 1. Fetch Data ---
const fetchTrekData = async () => {
  try {
    const response = await axios.get(`/staff/treks/${trekId}/participants`);
    
    trekName.value = response.data.trek_name;
    participants.value = response.data.participants;
    dbTrekStatus.value = response.data.trek_status;
    
  } catch (error) {
    console.error("Failed to load trek data:", error);
    alert("Error loading trek data. Ensure you are assigned to this trek.");
  } finally {
    loading.value = false;
  }
};


// Triggered by emit from TrekSettingsForm
const updateTrekSettings = async (payload) => {
  isUpdatingSettings.value = true;
  try {
    const apiPayload = { status: payload.status };
    if (payload.add_slots > 0) {
      apiPayload.add_slots = payload.add_slots;
    }

    const response = await axios.put(`/api/staff/treks/${trekId}/status`, apiPayload);
    
    alert(response.data.msg);
    
    await fetchTrekData();
  } catch (error) {
    console.error("Failed to update trek:", error);
    alert(error.response?.data?.msg || "Failed to update trek settings.");
  } finally {
    isUpdatingSettings.value = false;
  }
};


// Triggered by emit from ParticipantRoster
const removeParticipant = async (user) => {
  if (!confirm(`Are you sure you want to remove ${user.trekker_name}? This will cancel their booking and free up ${user.booked_slots} slot(s).`)) {
    return;
  }

  try {
    const response = await axios.post(`/api/staff/bookings/${user.booking_id}/remove`);
    alert(response.data.msg);
    fetchTrekData(); // Refresh the roster
  } catch (error) {
    console.error("Failed to remove participant:", error);
    alert(error.response?.data?.msg || "Failed to remove participant.");
  }
};

onMounted(() => {
  fetchTrekData();
});
</script>

<style scoped>

.manage-trek-staff { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }

/* Header & Typography */
.page-header { margin-bottom: 2rem; }
.back-link { color: #4f46e5; text-decoration: none; font-weight: 600; margin-bottom: 0.5rem; display: inline-block; }
.back-link:hover { text-decoration: underline; }
.page-header h1 { font-size: 2.25rem; color: #0f172a; font-weight: 700; margin-bottom: 0.25rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }

.loading-state { text-align: center; padding: 3rem; color: #64748b; }

/* Layout Grid */
.layout-grid {
  display: grid;
  grid-template-columns: 1fr 2fr; 
  gap: 2rem;
  align-items: start;
}

/* Responsive */
@media (max-width: 900px) {
  .layout-grid { grid-template-columns: 1fr; } 
}
</style>