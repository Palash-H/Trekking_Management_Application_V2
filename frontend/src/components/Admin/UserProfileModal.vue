<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h2>User Profile</h2>
        <button class="btn-close" @click="$emit('close')">&times;</button>
      </div>
      
      <div v-if="loading" class="modal-body text-center">
        Loading details...
      </div>

      <div v-else-if="user" class="modal-body">
        <!-- Read-Only Information -->
        <div class="info-group">
          <p><strong>Name:</strong> {{ user.name }}</p>
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Contact:</strong> {{ user.contact || 'N/A' }}</p>
        </div>

        <!-- Status Actions -->
        <div class="status-actions">
          <h3>Account Management</h3>
          
          <div class="action-buttons">
            <!-- Activate / Deactivate -->
            <button 
              v-if="user.active_status == 1" 
              class="btn-status btn-danger" 
              @click="$emit('change-status', 'deactivate')">
              Deactivate Account
            </button>
            <button 
              v-else 
              class="btn-status btn-success" 
              @click="$emit('change-status', 'activate')">
              Activate Account
            </button>

            <!-- Blacklist / Unblacklist -->
            <button 
              v-if="!user.blacklist_status" 
              class="btn-status btn-dark" 
              @click="$emit('change-status', 'blacklist')">
              Blacklist User
            </button>
            <button 
              v-else 
              class="btn-status btn-warning" 
              @click="$emit('change-status', 'unblacklist')">
              Remove from Blacklist
            </button>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: Boolean,
  loading: Boolean,
  user: Object
});

defineEmits(['close', 'change-status']);
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeIn 0.13s ease-out; }
.modal-card { background: #ffffff; width: 100%; max-width: 480px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 1.5rem 1rem; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0; }
.btn-close { background: none; border: none; font-size: 1.5rem; line-height: 1; color: #64748b; cursor: pointer; padding: 0.25rem; border-radius: 4px; transition: 0.2s; }
.btn-close:hover { color: #0f172a; background: #f8fafc; }
.modal-body { padding: 1.5rem; }
.text-center { text-align: center; color: #64748b; }

.info-group { display: flex; flex-direction: column; gap: 0.75rem; background: #f8fafc; padding: 1.25rem; border-radius: 8px; border: 1px solid #e2e8f0; }
.info-group p { margin: 0; font-size: 0.95rem; color: #0f172a; display: flex; justify-content: space-between; }
.info-group strong { color: #64748b; font-weight: 500; }

.status-actions { margin-top: 2rem; }
.status-actions h3 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 1rem; font-weight: 600; }
.action-buttons { display: flex; gap: 0.75rem; }
.btn-status { flex: 1; padding: 0.6rem 1rem; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; text-align: center; }

.btn-danger { background-color: #fee2e2; color: #b91c1c; } 
.btn-danger:hover { background-color: #fca5a5; }
.btn-success { background-color: #dcfce3; color: #15803d; } 
.btn-success:hover { background-color: #bbf7d0; }
.btn-dark { background-color: #1e293b; color: #ffffff; } 
.btn-dark:hover { background-color: #334155; }
.btn-warning { background-color: #fef3c7; color: #b45309; } 
.btn-warning:hover { background-color: #fde68a; }

.modal-footer { padding: 1.25rem 1.5rem; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; }
.btn-secondary { background-color: white; color: #0f172a; border: 1px solid #e2e8f0; padding: 0.5rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-secondary:hover { background-color: #f8fafc; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(15px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
</style>