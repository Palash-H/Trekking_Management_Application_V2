<template>
  <div class="card">
    <div class="card-header">
      <h2>Personal Information</h2>
    </div>
    
    <form @submit.prevent="handleSubmit" class="profile-form">
      <div class="input-group read-only">
        <label>Email Address</label>
        <input type="email" :value="profile.email" disabled />
        <small>Email cannot be changed.</small>
      </div>

      <div class="input-group">
        <label>Full Name</label>
        <input type="text" v-model="localForm.name" required />
      </div>
      
      <div class="input-group">
        <label>Contact Number</label>
        <input type="text" v-model="localForm.contact" placeholder="e.g. +91 9876543210" />
      </div>

      <div class="section-divider">
        <h3>Change Password</h3>
        <p>Leave blank to keep your current password.</p>
      </div>

      <div class="input-group">
        <label>New Password</label>
        <input type="password" v-model="localForm.password" placeholder="Enter new password" minlength="6" />
      </div>

      <button type="submit" class="btn btn-primary" :disabled="isSaving">
        {{ isSaving ? 'Saving...' : 'Save Changes' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  profile: {
    type: Object,
    required: true
  },
  isSaving: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['submit-profile']);

// Local state for the form inputs
const localForm = ref({
  name: '',
  contact: '',
  password: ''
});

// Watch for the profile data to load from the parent, then pre-fill the form
watch(() => props.profile, (newProfile) => {
  if (newProfile) {
    localForm.value.name = newProfile.name || '';
    localForm.value.contact = newProfile.contact || '';
  }
}, { immediate: true });

const handleSubmit = () => {
  emit('submit-profile', localForm.value);
  // Clear the password field after emitting
  localForm.value.password = '';
};
</script>

<style scoped>
/* Card Base */
.card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); overflow: hidden; height: 100%; }
.card-header { padding: 1.25rem 1.5rem; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.card-header h2 { font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0; }

/* Form Elements */
.profile-form { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.4rem; }
.input-group label { font-size: 0.85rem; font-weight: 600; color: #475569; }
.input-group input { padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; outline: none; transition: 0.2s; }
.input-group input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }
.input-group small { font-size: 0.75rem; color: #64748b; }
.read-only input { background: #f1f5f9; color: #64748b; cursor: not-allowed; }

.section-divider { margin-top: 1rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.5rem; }
.section-divider h3 { font-size: 1rem; color: #0f172a; margin: 0 0 0.2rem 0; }
.section-divider p { font-size: 0.85rem; color: #64748b; margin: 0; }

/* Button */
.btn { padding: 0.75rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; border: none; transition: 0.2s; text-align: center; }
.btn-primary { background: #0f172a; color: white; width: 100%; }
.btn-primary:hover:not(:disabled) { background: #334155; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>