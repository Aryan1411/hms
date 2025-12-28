<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">Login</div>
        <div class="card-body">
          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control" v-model="username" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
          </form>
          <p class="mt-3">Don't have an account? <router-link to="/register">Register</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import API_BASE_URL from '@/config/api.js';
export default {
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async login() {
      try {
        const response = await fetch(API_BASE_URL + '/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username, password: this.password })
        });
        const data = await response.json();
        if (response.ok) {
          sessionStorage.setItem('user_id', data.user_id);
          sessionStorage.setItem('role', data.role);
          if (data.role === 'admin') this.$router.push('/admin');
          else if (data.role === 'doctor') this.$router.push('/doctor');
          else this.$router.push('/patient');
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error(error);
        alert('Login failed');
      }
    }
  }
}
</script>
