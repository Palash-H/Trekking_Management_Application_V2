<template>
  <div class="create-trek">
    <header class="page-header">
      <div>
        <router-link to="/admin/treks" class="back-link">← Back to Treks</router-link>
        <h1>Create New Trek</h1>
        <p>Fill in the details to publish a new trek to the catalog.</p>
      </div>
    </header>

    <!-- Alert Messages -->
    <div v-if="message" :class="['alert', isSuccess ? 'alert-success' : 'alert-error']">
      {{ message }}
    </div>


    <CreateTrekForm 
      :staffList="staffList"
      :loading="loading"
      :today="today"
      @submit-form="submitTrek"
      @cancel="handleCancel"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; 
import { useRouter } from 'vue-router';
import axios from 'axios';


import CreateTrekForm from '@/components/Admin/CreateTrekForm.vue';

const router = useRouter();

// --- State ---
const loading = ref(false);
const message = ref('');
const isSuccess = ref(false);
const staffList = ref([]);

// --- Computed ---
const today = computed(() => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
});

// --- API Logic ---
const fetchStaff = async () => {
  try {
    const response = await axios.get('/api/admin/staff');
    staffList.value = response.data.staff;
  } catch (error) {
    console.error("Failed to load staff list:", error);
    message.value = "Warning: Could not load staff members.";
    isSuccess.value = false;
  }
};

// Triggered by the child component's @submit-form event
const submitTrek = async (formData) => {
  loading.value = true;
  message.value = '';

  try {
    const response = await axios.post('/admin/create_trek', formData);
    
    isSuccess.value = true;
    message.value = response.data.msg || 'Trek created successfully! Redirecting...';
    
    setTimeout(() => {
      router.push('/admin/treks');
    }, 1500);

  } catch (error) {
    isSuccess.value = false;
    message.value = error.response?.data?.msg || 'Failed to create trek. Check console.';
    console.error("Create error:", error);
  } finally {
    loading.value = false;
  }
};

// Routing for cancel button
const handleCancel = () => {
  router.push('/admin/treks');
};

onMounted(() => {
  fetchStaff();
});
</script>

<style scoped>

.create-trek {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header { margin-bottom: 2rem; }
.back-link { color: var(--primary, #16a34a); text-decoration: none; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; display: inline-block; }
.back-link:hover { text-decoration: underline; }
.page-header h1 { font-size: 2rem; color: var(--text-main, #0f172a); margin: 0 0 0.25rem 0; }
.page-header p { color: var(--text-muted, #64748b); margin: 0; }

.alert { padding: 1rem; border-radius: 8px; font-weight: 600; text-align: center; margin-bottom: 1.5rem; max-width: 900px; }
.alert-success { background: #dcfce3; color: #166534; border: 1px solid #bbf7d0; }
.alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
</style>