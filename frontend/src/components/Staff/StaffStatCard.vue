<template>
  <div :class="['stat-card', highlightClass]">
    <h3>{{ title }}</h3>
    <p class="stat-number">{{ value }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  highlightClass: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
.stat-card { background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.stat-card h3 { font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;}
.stat-number { font-size: 2.25rem; font-weight: 700; color: #0f172a; }

/* Highlight Colors for Stats */
.highlight-blue .stat-number { color: #0284c7; }
.highlight-green .stat-number { color: #16a34a; }
.highlight-indigo .stat-number { color: #4f46e5; }
</style>