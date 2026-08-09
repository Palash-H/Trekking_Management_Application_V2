<template>
  <div class="table-section">
    <h2 class="section-title">{{ title }} ({{ users.length }})</h2>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td>
              <button class="clickable-name" @click="$emit('view-user', user.id)">
                {{ user.name }}
              </button>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <!-- Dynamic Badges based on user status properties -->
              <span v-if="user.blacklist_status" class="status-badge danger">Blacklisted</span>
              <span v-else-if="!user.active_status" class="status-badge warning">Deactivated</span>
              <span v-else class="status-badge success">Active</span>
            </td>
            <td>
              <span :class="['role-badge', user.role === 'trekstaff' ? 'staff' : 'trekker']">
                {{ user.role === 'trekstaff' ? 'Staff' : 'Trekker' }}
              </span>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="5" class="empty-state">No users found in this category.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  users: {
    type: Array,
    required: true
  }
});

defineEmits(['view-user']);
</script>

<style scoped>
.table-section { margin-bottom: 3.5rem; }
.section-title { font-size: 1.25rem; font-weight: 600; color: #0f172a; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.table-container { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05); overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; }
.data-table th, .data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.data-table th { background-color: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
.data-table tbody tr { transition: background-color 0.2s ease; }
.data-table tbody tr:hover { background-color: #f8fafc; }
.data-table tbody tr:last-child td { border-bottom: none; }
.empty-state { text-align: center; color: #64748b; padding: 2rem; }

/* Clickable Name */
.clickable-name { background: none; border: none; color: #4f46e5; font-weight: 600; font-size: 0.95rem; cursor: pointer; padding: 0; text-decoration: none; transition: color 0.2s ease; }
.clickable-name:hover { color: #4338ca; text-decoration: underline; text-underline-offset: 4px; }

/* Badges */
.role-badge, .status-badge { padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; letter-spacing: 0.025em; }
.role-badge.staff { background-color: #e0e7ff; color: #3730a3; } 
.role-badge.trekker { background-color: #f1f5f9; color: #475569; } 
.status-badge.success { background-color: #dcfce3; color: #166534; } 
.status-badge.warning { background-color: #f1f5f9; color: #475569; } 
.status-badge.danger { background-color: #fee2e2; color: #991b1b; } 
</style>