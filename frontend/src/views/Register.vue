<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">Register (Patient)</div>
        <div class="card-body">
          <form @submit.prevent="register">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control" v-model="username" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="email">
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Register</button>
          </form>
          <p class="mt-3">Already have an account? <router-link to="/login/patient">Login</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      email: ''
    }
  },
  methods: {
    async register() {
      try {
        const response = await fetch('http://localhost:5000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username, password: this.password, email: this.email })
        });
        const data = await response.json();
        if (response.ok) {
          alert('Registration successful');
          this.$router.push('/login/patient');
        } else {
          alert(data.message);
        }
      } catch (error) {
        console.error(error);
        alert('Registration failed');
      }
    }
  }
}
</script>
