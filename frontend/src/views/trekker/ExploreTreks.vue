<template>
  <div class="explore-treks">
    <header class="explore-hero">
      <h3>Find Your Next Adventure</h3>
      <p>Discover, filter, and book the most breathtaking treks.</p>
    </header>

    <!-- Filters Section -->
    <div class="filters-container">
      <div class="search-box">
        <span class="icon">🔍</span>
        <input type="text" v-model="filters.search" @input="fetchTreks" placeholder="Search name or location..." />
      </div>
      
      <select v-model="filters.difficulty" @change="fetchTreks" class="filter-input">
        <option value="">Any Difficulty</option>
        <option value="Easy">Easy</option>
        <option value="Moderate">Moderate</option>
        <option value="Hard">Hard</option>
      </select>
      
      <div class="search-box">
        <span class="icon">⏱️</span>
        <input type="number" v-model="filters.duration" @input="fetchTreks" placeholder="Max Days (e.g. 5)" class="filter-input" />
      </div>
    </div>

    <!-- Layout States -->
    <div v-if="loading" class="loading-state">Scouting the trails...</div>
    
    <div v-else-if="treks.length === 0" class="empty-state">
      <h3>No Treks Found</h3>
      <p>Try adjusting your filters to see more results.</p>
    </div>


    <div v-else class="trek-grid">
      <TrekCard 
        v-for="trek in treks" 
        :key="trek.id" 
        :trek="trek" 
        :isBooked="bookedTrekIds.has(trek.id)"
        @book="openBookingModal"
      />
    </div>


    <BookingModal 
      v-if="showBookingModal"
      :trek="selectedTrek"
      :isBooking="isBooking"
      @close="closeBookingModal"
      @submit-booking="handleBookingSubmit"
    />

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

import TrekCard from '@/components/User/TrekCard.vue';
import BookingModal from '@/components/User/BookingModal.vue';

const treks = ref([]);
const loading = ref(true);

const filters = ref({
  search: '',
  difficulty: '',
  duration: ''
});

const bookedTrekIds = ref(new Set());

// --- Fetch User's Existing Bookings ---
const fetchUserBookings = async () => {
  try {
    const response = await axios.get('/api/user/bookings');
    const activeBookings = response.data.history.filter(b => b.status !== 'Cancelled');
    bookedTrekIds.value = new Set(activeBookings.map(b => b.trek_id));
  } catch (error) {
    console.error("Failed to load user bookings:", error);
  }
};

// --- Fetch Treks using catalog API ---
const fetchTreks = async () => {
  try {
    const params = new URLSearchParams();
    if (filters.value.search) params.append('search', filters.value.search);
    if (filters.value.difficulty) params.append('difficulty', filters.value.difficulty);
    if (filters.value.duration) params.append('duration', filters.value.duration);

    const response = await axios.get(`/api/treks?${params.toString()}`);
    treks.value = response.data.treks;
  } catch (error) {
    console.error("Failed to load treks:", error);
  } finally {
    loading.value = false;
  }
};

// --- Booking Modal State ---
const showBookingModal = ref(false);
const isBooking = ref(false);
const selectedTrek = ref(null);


const openBookingModal = (trek) => {
  selectedTrek.value = trek;
  showBookingModal.value = true;
};


const closeBookingModal = () => {
  showBookingModal.value = false;
  selectedTrek.value = null;
};

const handleBookingSubmit = async (formData) => {
  isBooking.value = true;
  try {
    const response = await axios.post(`/api/treks/${selectedTrek.value.id}/book`, formData);
    alert(response.data.msg);
    bookedTrekIds.value.add(selectedTrek.value.id);
    closeBookingModal();
    fetchTreks(); 
  } catch (error) {
    console.error("Booking failed:", error);
    alert(error.response?.data?.msg || "Failed to book trek.");
  } finally {
    isBooking.value = false;
  }
};

onMounted(async() => {
    await fetchUserBookings();
    fetchTreks();
});
</script>

<style scoped>

.explore-treks { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }

.explore-hero { text-align: center; margin-bottom: 3rem; }
.explore-hero h3 { font-size: 2.5rem; color: #0f172a; margin-bottom: 0.5rem; font-weight: 800; }
.explore-hero p { color: #64748b; font-size: 1.1rem; }

/* Filters */
.filters-container { display: flex; gap: 1rem; margin-bottom: 2.5rem; background: #ffffff; padding: 1rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); flex-wrap: wrap; }
.search-box { flex: 1; min-width: 200px; position: relative; }
.search-box .icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); }
.search-box input { width: 100%; padding: 0.75rem 1rem 0.75rem 2.5rem; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.filter-input { padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 8px; min-width: 150px; outline: none; }

.loading-state, .empty-state { text-align: center; padding: 4rem; color: #64748b; background: #f8fafc; border-radius: 12px; border: 1px dashed #cbd5e1; }


.trek-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 2rem; 
  align-items: stretch; 
}
</style>