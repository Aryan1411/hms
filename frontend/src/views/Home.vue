<template>
  <div class="home-container d-flex align-items-center justify-content-center">
    <div class="text-center">
      <h1 class="display-4 mb-4 fw-bold text-primary">Welcome to CareConnect HMS</h1>
      <p class="lead mb-5 text-muted">Your Health, Our Priority. Please select your role to continue.</p>
      
      <div class="row justify-content-center gap-4">
        <div class="col-md-3">
          <div class="card h-100 shadow-sm hover-card border-0">
            <div class="card-body p-4">
              <div class="icon-circle bg-primary-subtle text-primary mb-3 mx-auto">
                <i class="bi bi-person-fill fs-2"></i>
              </div>
              <h5 class="card-title fw-bold">Patient</h5>
              <p class="card-text text-muted small">Book appointments and view history.</p>
              <router-link to="/login/patient" class="btn btn-outline-primary w-100 rounded-pill">Login as Patient</router-link>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card h-100 shadow-sm hover-card border-0">
            <div class="card-body p-4">
              <div class="icon-circle bg-success-subtle text-success mb-3 mx-auto">
                <i class="bi bi-heart-pulse-fill fs-2"></i>
              </div>
              <h5 class="card-title fw-bold">Doctor</h5>
              <p class="card-text text-muted small">Manage appointments and treatments.</p>
              <router-link to="/login/doctor" class="btn btn-outline-success w-100 rounded-pill">Login as Doctor</router-link>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card h-100 shadow-sm hover-card border-0">
            <div class="card-body p-4">
              <div class="icon-circle bg-dark-subtle text-dark mb-3 mx-auto">
                <i class="bi bi-shield-lock-fill fs-2"></i>
              </div>
              <h5 class="card-title fw-bold">Admin</h5>
              <p class="card-text text-muted small">Manage hospital resources.</p>
              <router-link to="/login/admin" class="btn btn-outline-dark w-100 rounded-pill">Login as Admin</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 80vh;
}
.hover-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}
.icon-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
