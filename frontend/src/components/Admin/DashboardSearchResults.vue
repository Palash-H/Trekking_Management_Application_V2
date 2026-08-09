<template>
  <div>
    <div v-if="isSearching" class="loading-state">Searching the database...</div>
      
    <div v-else class="search-results-container">
      
      <!-- TREKS RESULTS -->
      <div class="result-section">
        <h2>Treks ({{ results.treks.length }})</h2>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in results.treks" :key="trek.id">
                <td class="font-bold">{{ trek.name }}</td>
                <td>{{ trek.location }}</td>
                <td><span :class="['status-badge', (trek.status || 'Pending').toLowerCase()]">{{ trek.status || 'Pending' }}</span></td>
              </tr>
              <tr v-if="results.treks.length === 0">
                <td colspan="3" class="empty-state">No treks match this search.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- USERS RESULTS -->
      <div class="result-section">
        <h2>Users & Staff ({{ results.users.length }})</h2>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in results.users" :key="user.id">
                <td class="font-bold">{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td><span :class="['role-badge', user.role]">{{ user.role === 'trekstaff' ? 'Staff' : 'Trekker' }}</span></td>
              </tr>
              <tr v-if="results.users.length === 0">
                <td colspan="3" class="empty-state">No users match this search.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BOOKINGS RESULTS -->
      <div class="result-section">
        <h2>Bookings ({{ results.bookings.length }})</h2>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Trekker</th>
                <th>Trek Route</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in results.bookings" :key="booking.id">
                <td class="font-bold">{{ booking.user_name }}</td>
                <td>{{ booking.trek_name }}</td>
                <td><span :class="['status-badge', (booking.status || 'Pending').toLowerCase()]">{{ booking.status }}</span></td>
              </tr>
              <tr v-if="results.bookings.length === 0">
                <td colspan="3" class="empty-state">No bookings match this search.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  results: {
    type: Object,
    required: true
  },
  isSearching: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.loading-state { text-align: center; padding: 3rem; color: #64748b; font-size: 1.1rem; }

/* Search Results Layout */
.search-results-container { display: flex; flex-direction: column; gap: 2.5rem; }
.result-section h2 { font-size: 1.25rem; color: #0f172a; margin-bottom: 1rem; font-weight: 600; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }

/* Shared Table Styles */
.table-container { background: var(--card-bg, #ffffff); border-radius: 12px; border: 1px solid var(--border, #e2e8f0); overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th, .data-table td { padding: 0.75rem 1.5rem; border-bottom: 1px solid var(--border, #e2e8f0); }
.data-table th { background-color: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.data-table tr:hover { background-color: #f1f5f9; }
.font-bold { font-weight: 600; color: #0f172a; }
.empty-state { text-align: center; padding: 2rem; color: #64748b; font-style: italic; }

/* Shared Badges */
.status-badge, .role-badge { padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; display: inline-block; text-transform: capitalize; }
.status-badge.active, .status-badge.confirmed { background-color: #dcfce3; color: #166534; }
.status-badge.pending { background-color: #fef08a; color: #854d0e; }
.status-badge.cancelled, .status-badge.danger { background-color: #fee2e2; color: #991b1b; }
.status-badge.completed { background-color: #e2e8f0; color: #475569; }
.role-badge.trekstaff { background-color: #e0e7ff; color: #3730a3; }
.role-badge.trekker { background-color: #f1f5f9; color: #475569; }
</style>