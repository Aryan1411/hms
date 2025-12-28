<template>
  <div class="row justify-content-center align-items-center" style="min-height: 70vh;">
    <div class="col-md-4">
      <div class="card shadow border-0">
        <div class="card-body p-5">
          <div class="text-center mb-4">
            <h3 class="fw-bold text-primary">Patient Login</h3>
            <p class="text-muted small">Welcome Back</p>
          </div>
          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label small text-uppercase fw-bold text-muted">Username</label>
              <input type="text" class="form-control form-control-lg bg-light border-0" v-model="username" required>
            </div>
            <div class="mb-4">
              <label class="form-label small text-uppercase fw-bold text-muted">Password</label>
              <input type="password" class="form-control form-control-lg bg-light border-0" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100 btn-lg rounded-pill shadow-sm">Login</button>
          </form>
          <div class="text-center mt-3">
             <p class="small text-muted">Don't have an account? <router-link to="/register" class="fw-bold text-primary">Register</router-link></p>
             <router-link to="/" class="text-decoration-none small text-muted">Back to Home</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return { username: '', password: '' }
  },
  methods: {
    async login() {
      try {
        const response = await fetch(import.meta.env.VITE_API_URL + '/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username, password: this.password })
        });
        const data = await response.json();
        if (response.ok && data.role === 'patient') {
          sessionStorage.setItem('token', data.token);
          sessionStorage.setItem('user_id', data.user_id);
          sessionStorage.setItem('role', data.role);
          if (data.patient_id) sessionStorage.setItem('patient_id', data.patient_id);
          this.$router.push('/patient');
        } else {
          alert(data.message || 'Invalid credentials');
        }
      } catch (error) {
        console.error(error);
        alert('Login failed');
      }
    }
  }
}
</script>
