<!-- <template>
  <div class="hero-section">
    <div class="overlay">
      <div class="hero-content">
        <h1>Conquer the Mountains.</h1>
        <p>Book safe, expertly guided treks across the world's most breathtaking landscapes.</p>
        <router-link
          to="/register"
          class="btn btn-primary"
          style="font-size: 1.1rem; padding: 1rem 2.5rem"
          >Start Your Journey</router-link
        >
      </div>
    </div>
  </div>
</template>
<style scoped>
.hero-section {
  height: calc(100vh - 75px);
  background-image: url('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2070');
  background-size: cover;
  background-position: center;
}
.overlay {
  height: 100%;
  width: 100%;
  background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.hero-content {
  color: white;
  max-width: 800px;
  padding: 0 20px;
  animation: fadeIn 1s ease-out;
}
h1 {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
}
p {
  font-size: 1.25rem;
  color: #f1f5f9;
  margin-bottom: 2.5rem;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> -->
<template>
  <div class="hero-section">
    <div class="overlay">
      <div class="hero-content">
        <h1 class="title">Conquer the Mountains.</h1>
        <p class="subtitle">
          Book safe, expertly guided treks across the world's most breathtaking landscapes.
        </p>
        <div class="action-wrapper">
          <router-link to="/register" class="btn-cta">
            <span>Start Your Journey</span>
            <!-- Premium UI touch: An arrow that animates on hover -->
            <svg class="arrow-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero-section {
  height: calc(100vh - 75px);
  /* A bulletproof, highly reliable Unsplash URL of a majestic mountain */
  background-image: url('https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&q=80&w=2070');
  background-size: cover;
  background-position: center;
  position: relative;
}

.overlay {
  position: absolute;
  inset: 0;
  /* Darkens heavily at the bottom to make the white button and text pop */
  background: linear-gradient(to bottom, rgba(15, 23, 42, 0.2) 0%, rgba(15, 23, 42, 0.8) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 15vh;
  text-align: center;
}

.hero-content {
  color: white;
  max-width: 700px;
  padding: 0 2rem;
}

.title {
  font-size: 4.5rem;
  font-weight: 800;
  line-height: 1.05;
  margin-bottom: 1.25rem;
  letter-spacing: -0.03em;
  opacity: 0;
  animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}

.subtitle {
  font-size: 1.25rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin-bottom: 3rem;
  opacity: 0;
  animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
}

.action-wrapper {
  opacity: 0;
  animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
}

/* Premium Button Styling */
.btn-cta {
  background-color: var(--primary);
  color: white;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 600;
  padding: 1.1rem 2.5rem;
  border-radius: 50px;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 10px 25px rgba(46, 125, 50, 0.3);
}

.arrow-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.btn-cta:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(46, 125, 50, 0.4);
}

.btn-cta:active {
  transform: translateY(1px) scale(0.98); /* The "squish" effect when clicked */
}

.btn-cta:hover .arrow-icon {
  transform: translateX(5px); /* Arrow slides right on hover */
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .title { font-size: 3.2rem; }
  .subtitle { font-size: 1.1rem; }
}
</style>