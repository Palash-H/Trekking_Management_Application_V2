<template>
  <div v-if="show" class="modal-overlay" @click.self="closeModal">
    <div class="modal-card">
      <div class="modal-header">
        <h2>Add New Trek Staff</h2>
        <button class="btn-close" @click="closeModal">&times;</button>
      </div>
      
      <form @submit.prevent="handleSubmit">
        <div class="modal-body form-layout">
          <div class="input-group">
            <label>Full Name</label>
            <input type="text" v-model="form.name" required placeholder="e.g. Rahul Sharma" />
          </div>
          <div class="input-group">
            <label>Email Address</label>
            <input type="email" v-model="form.email" required placeholder="staff@example.com" />
          </div>
          <div class="input-group">
            <label>Initial Password</label>
            <input type="password" v-model="form.password" required minlength="6" placeholder="Assign a password" />
          </div>
          <div class="input-group">
            <label>Contact Number (Optional)</label>
            <input type="text" v-model="form.contact" placeholder="+91 98765..." />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="isCreating">
            {{ isCreating ? 'Creating...' : 'Create Staff' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  show: Boolean,
  isCreating: Boolean
});

const emit = defineEmits(['close', 'submit-form']);

// Local state
const form = ref({ name: '', email: '', password: '', contact: '' });

const closeModal = () => {
  // Reset form locally before closing
  form.value = { name: '', email: '', password: '', contact: '' };
  emit('close');
};

const handleSubmit = () => {
  emit('submit-form', { ...form.value });
};
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.2s ease-out; }
.modal-card { background: #ffffff; width: 100%; max-width: 480px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 1.5rem 1rem; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.btn-close { background: none; border: none; font-size: 1.5rem; line-height: 1; color: #64748b; cursor: pointer; padding: 0.25rem; border-radius: 4px; transition: 0.2s; }
.btn-close:hover { color: #0f172a; background: #f8fafc; }
.modal-body { padding: 1.5rem; }

.form-layout { display: flex; flex-direction: column; gap: 1.25rem; }
.input-group { display: flex; flex-direction: column; gap: 0.4rem; }
.input-group label { font-size: 0.85rem; font-weight: 600; color: #64748b; }
.input-group input { padding: 0.75rem 1rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; color: #0f172a; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
.input-group input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); }

.modal-footer { padding: 1.25rem 1.5rem; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 1rem; }
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 600; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn-secondary { background-color: white; color: #0f172a; border: 1px solid #e2e8f0; }
.btn-secondary:hover { background-color: #f8fafc; }
.btn-primary { background-color: #4f46e5; color: white; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2); }
.btn-primary:hover:not(:disabled) { background-color: #4338ca; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(15px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
</style>