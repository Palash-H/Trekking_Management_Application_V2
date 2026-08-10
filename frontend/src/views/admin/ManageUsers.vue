<template>
  <div class="manage-users">
    
    <header class="page-header header-flex">
      <div>
        <h1>Manage Users</h1>
        <p>View user details and manage account statuses.</p>
      </div>
      <button class="btn btn-primary" @click="showCreateStaffModal = true">
        + Add Trek Staff
      </button>
    </header>

    <div v-if="loading" class="loading-state">Loading users...</div>
    
    <div v-else>
      <UserTable 
        title="Staff Members" 
        :users="staffList" 
        @view-user="openViewModal" 
      />

      
      <UserTable 
        title="Registered Trekkers" 
        :users="trekkerList" 
        @view-user="openViewModal" 
      />
    </div>

    
    <UserProfileModal 
      :show="showModal"
      :loading="modalLoading"
      :user="selectedUser"
      @close="closeModal"
      @change-status="changeUserStatus"
    />

    
    <CreateStaffModal 
      :show="showCreateStaffModal"
      :isCreating="isCreatingStaff"
      @close="showCreateStaffModal = false"
      @submit-form="handleCreateStaff"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

// Import our new components
import UserTable from '@/components/Admin/UserTable.vue';
import UserProfileModal from '@/components/Admin/UserProfileModal.vue';
import CreateStaffModal from '@/components/Admin/CreateStaffModal.vue';

const route = useRoute();

// --- State ---
const users = ref([]);
const loading = ref(true);

// Modal States
const showCreateStaffModal = ref(false);
const isCreatingStaff = ref(false);

const showModal = ref(false);
const modalLoading = ref(false);
const selectedUser = ref(null);

// --- Computed Lists ---
const staffList = computed(() => users.value.filter(u => u.role === 'trekstaff'));
const trekkerList = computed(() => users.value.filter(u => u.role === 'trekker'));

// --- API Calls ---

const fetchUsers = async () => {
  try {
    const searchTerm = route.query.search || '';
    const response = await axios.get(`/admin/users?search=${searchTerm}`); 
    users.value = response.data.users; 
  } catch (error) {
    console.error("Failed to fetch users:", error);
  } finally {
    loading.value = false;
  }
};

const handleCreateStaff = async (formData) => {
  isCreatingStaff.value = true;
  try {
    const response = await axios.post('/admin/create_staff', formData);
    alert(response.data.msg);
    showCreateStaffModal.value = false;
    await fetchUsers(); // Refresh table
  } catch (error) {
    console.error("Failed to create staff:", error);
    alert(error.response?.data?.msg || "An error occurred while creating staff.");
  } finally {
    isCreatingStaff.value = false;
  }
};

const openViewModal = async (userId) => {
  showModal.value = true;
  modalLoading.value = true;
  try {
    const response = await axios.get(`/api/admin/users/${userId}`);
    selectedUser.value = response.data;
  } catch (error) {
    console.error("Failed to fetch user details:", error);
    alert("Failed to load user profile.");
    closeModal();
  } finally {
    modalLoading.value = false;
  }
};

const changeUserStatus = async (action) => {
  if (['blacklist', 'deactivate'].includes(action)) {
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;
  }

  try {
    const response = await axios.patch(`/api/admin/users/${selectedUser.value.id}/${action}`);
    alert(response.data.msg);
    await fetchUsers();
    closeModal();
  } catch (error) {
    console.error(`Failed to ${action} user:`, error);
    alert(error.response?.data?.msg || `Failed to ${action} user.`);
  }
};

const closeModal = () => {
  showModal.value = false;
  selectedUser.value = null;
};

watch(() => route.query.search, () => {
  loading.value = true;
  fetchUsers();
});

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
/* Main wrapper and layout styles only */
.manage-users { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; font-family: 'Inter', system-ui, -apple-system, sans-serif; }

.header-flex { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.page-header { margin-bottom: 2.5rem; }
.page-header h1 { font-size: 2.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.025em; }
.page-header p { color: #64748b; font-size: 1.1rem; }
.loading-state { text-align: center; color: #64748b; padding: 3rem; }

/* Global Button for Parent */
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-primary { background-color: #4f46e5; color: white; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2); }
.btn-primary:hover:not(:disabled) { background-color: #4338ca; transform: translateY(-1px); }
</style>