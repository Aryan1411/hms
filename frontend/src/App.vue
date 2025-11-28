<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4">
      <div class="container">
        <router-link class="navbar-brand fw-bold text-primary" to="/">
          <i class="bi bi-hospital-fill me-2"></i>HMS
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css');

body {
  font-family: 'Inter', sans-serif;
  background-color: #f0f2f5;
  color: #343a40;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
}

.card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.btn {
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-weight: 500;
}

.form-control {
  border-radius: 8px;
  padding: 0.6rem 1rem;
}

.form-control:focus {
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
}
</style>
