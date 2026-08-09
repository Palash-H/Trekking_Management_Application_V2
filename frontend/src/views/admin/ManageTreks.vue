<template>
  <div class="manage-treks">
    <header class="page-header">
      <div>
        <h1>Manage Treks</h1>
        <p>View, update, and create treks for the platform.</p>
      </div>
      <router-link to="/admin/treks/create" class="btn btn-green">+ Create New Trek</router-link>
    </header>

    <!-- Child: Trek Table -->
    <TrekTable 
      :treks="treks" 
      :loading="loading" 
      @edit-trek="openEditModal" 
    />

    <!-- Child: Edit Trek Modal -->
    <EditTrekModal 
      :show="showEditModal"
      :trek="selectedTrek"
      :staffMembers="staffMembers"
      :isUpdating="isUpdating"
      :isDeleting="isDeleting"
      @close="closeEditModal"
      @save="handleUpdateTrek"
      @delete="handleDeleteTrek"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'; 
import { useRoute } from 'vue-router'; 
import axios from 'axios';

// Import our new components
import TrekTable from '@/components/Admin/TrekTable.vue';
import EditTrekModal from '@/components/Admin/EditTrekModal.vue';

const route = useRoute(); 

// --- State ---
const users = ref([]);
const treks = ref([]);
const loading = ref(true);

const showEditModal = ref(false);
const isUpdating = ref(false);
const isDeleting = ref(false);
const selectedTrek = ref({});

// --- Computed ---
const staffMembers = computed(() => {
  return users.value.filter(u => u.role === 'trekstaff');
});

// --- Fetch API Calls ---
const fetchUsers = async () => {
  try {
    const response = await axios.get('/admin/users');
    users.value = response.data.users;
  } catch (error) {
    console.error("Failed to fetch users/staff:", error);
  }
};

const fetchTreks = async () => {
  try {
    const timestamp = new Date().getTime();
    const searchTerm = route.query.search || '';
    const response = await axios.get(`/api/admin/treks?search=${searchTerm}&t=${timestamp}`); 
    
    if (response.data.treks) {
      treks.value = response.data.treks;
    } else {
      treks.value = response.data;
    }
  } catch (error) {
    console.error("Failed to fetch treks:", error);
  } finally {
    loading.value = false;
  }
};

// --- Modal Handlers ---
const openEditModal = (trek) => {
  selectedTrek.value = trek;
  showEditModal.value = true;
};

const closeEditModal = () => {
  showEditModal.value = false;
  selectedTrek.value = {};
};

// --- Mutation API Calls ---
const handleUpdateTrek = async (updatedTrekData) => {
  isUpdating.value = true;
  try {
    const response = await axios.put(`/admin/treks/${updatedTrekData.id}`, updatedTrekData);
    alert(response.data.msg);
    closeEditModal();
    await fetchTreks(); 
  } catch (error) {
    console.error("Failed to update trek:", error);
    alert(error.response?.data?.msg || "Failed to update trek.");
  } finally {
    isUpdating.value = false;
  }
};

const handleDeleteTrek = async (trekData) => {
  if (!confirm(`Are you sure you want to delete "${trekData.name}"? This will also delete all associated bookings. This cannot be undone.`)) {
    return;
  }
  
  isDeleting.value = true;
  try {
    const response = await axios.delete(`/admin/treks/${trekData.id}`);
    alert(response.data.msg);
    closeEditModal();
    await fetchTreks(); 
  } catch (error) {
    console.error("Failed to delete trek:", error);
    alert(error.response?.data?.msg || "Failed to delete trek.");
  } finally {
    isDeleting.value = false;
  }
};

// --- Lifecycle ---
watch(() => route.query.search, () => {
  loading.value = true;
  fetchTreks();
});

onMounted(() => {
  fetchTreks();
  fetchUsers();
});
</script>

<style scoped>
/* Only structural CSS remains in the parent */
.manage-treks { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem;}
.page-header h1 { font-size: 2.25rem; color: #0f172a; font-weight: 700; margin-bottom: 0.25rem; }
.page-header p { color: #64748b; font-size: 1.1rem; }

.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; text-decoration: none; display: inline-block; }
.btn-green { background-color: #16a34a; color: white; box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.2); }
.btn-green:hover { background-color: #15803d; transform: translateY(-1px); }
</style>