<template>
  <div class="manage-bookings">
    <header class="page-header">
      <h1>All Bookings</h1>
      <p>View and monitor all trek reservations.</p>
    </header>

    <!-- 🌟 Use the Child Component 🌟 -->
    <BookingTable 
      :bookings="bookings" 
      :loading="loading" 
    />
    
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'; 
import { useRoute } from 'vue-router'; 
import axios from 'axios';

// Import the table component
import BookingTable from '@/components/Admin/BookingTable.vue';

const route = useRoute();
const bookings = ref([]);
const loading = ref(true);

const fetchBookings = async () => {
  try {
    const searchTerm = route.query.search || '';
    const response = await axios.get(`/api/admin/bookings?search=${searchTerm}`);
    bookings.value = response.data.bookings;
  } catch (error) {
    console.error("Error fetching bookings:", error);
  } finally {
    loading.value = false;
  }
};

// Re-fetch if the URL search query changes
watch(() => route.query.search, () => {
  loading.value = true;
  fetchBookings();
});

onMounted(() => {
  fetchBookings();
});
</script>

<style scoped>
/* Only macro-layout styles remain in the parent */
.manage-bookings {
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 2rem 1rem;
}
.page-header { margin-bottom: 2.5rem; }
.page-header h1 { font-size: 2.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; letter-spacing: -0.025em; }
.page-header p { color: #64748b; font-size: 1.1rem; }
</style>