<template>
  <div>
    <nav class="navbar navbar-light bg-white shadow-sm mb-4 rounded">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">Edit Profile</span>
        <button class="btn btn-outline-secondary btn-sm" @click="$router.push('/patient')">Back to Dashboard</button>
      </div>
    </nav>

    <div class="card">
      <div class="card-body">
        <form @submit.prevent="updateProfile">
          <div class="mb-3">
            <label class="form-label">Name</label>
            <input type="text" class="form-control" v-model="profile.name" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Date of Birth</label>
            <input type="date" class="form-control" v-model="profile.dob">
          </div>
          <div class="mb-3">
            <label class="form-label">Contact Number</label>
            <input type="tel" class="form-control" v-model="profile.contact">
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" v-model="profile.email">
          </div>
          <button type="submit" class="btn btn-primary w-100">Update Profile</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      profile: {
        name: '',
        dob: '',
        contact: '',
        email: ''
      }
    }
  },
  async mounted() {
    const patientId = sessionStorage.getItem('patient_id');
    if (!patientId) {
      this.$router.push('/login/patient');
      return;
    }
    
    const res = await fetch(`http://localhost:5000/patient/profile/${patientId}`);
    if (res.ok) {
      this.profile = await res.json();
    }
  },
  methods: {
    async updateProfile() {
      const patientId = sessionStorage.getItem('patient_id');
      const res = await fetch(`http://localhost:5000/patient/profile/${patientId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.profile)
      });
      
      if (res.ok) {
        alert('Profile updated successfully!');
        this.$router.push('/patient');
      } else {
        alert('Update failed');
      }
    }
  }
}
</script>
