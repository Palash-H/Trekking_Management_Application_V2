<template>
  <div class="layout-wrapper">
    <Navbar />
    <main class="main-content">
      <router-view />
      <!-- Home, Login, and Register will load IN HERE -->
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/navigation/PublicNav.vue'
import Footer from '@/components/navigation/Footer.vue'
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.main-content {
  flex: 1;
}
</style>
