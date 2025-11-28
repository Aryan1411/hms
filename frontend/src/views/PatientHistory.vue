<template>
  <div>
    <nav class="navbar navbar-light bg-white shadow-sm mb-4 rounded">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">My Medical Records</span>
        <button class="btn btn-outline-secondary btn-sm" @click="$router.push('/patient')">Back to Dashboard</button>
      </div>
    </nav>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a class="nav-link" :class="{active: activeTab === 'appointments'}" @click="activeTab = 'appointments'" style="cursor: pointer">My Appointments</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{active: activeTab === 'history'}" @click="activeTab = 'history'" style="cursor: pointer">Treatment History</a>
      </li>
    </ul>

    <!-- My Appointments Tab -->
    <div v-if="activeTab === 'appointments'" class="card">
      <div class="card-header bg-white">
        <h5 class="mb-0">My Appointments</h5>
      </div>
      <div class="card-body">
        <div v-if="appointments.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-calendar-x fs-1 opacity-25 mb-3 d-block"></i>
          No appointments found.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in appointments" :key="app.id">
                <td>{{ app.doctor }}</td>
                <td><small class="text-muted">{{ app.specialization }}</small></td>
                <td>{{ app.date }}</td>
                <td>{{ app.time }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-success': app.status === 'Completed',
                    'bg-warning': app.status === 'Booked',
                    'bg-danger': app.status === 'Cancelled'
                  }">{{ app.status }}</span>
                </td>
                <td class="text-end">
                  <button v-if="app.status === 'Booked'" class="btn btn-sm btn-outline-danger me-1" @click="cancelAppointment(app.id)">
                    <i class="bi bi-x-circle"></i> Cancel
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Treatment History Tab -->
    <div v-if="activeTab === 'history'" class="card">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Treatment History</h5>
        <button class="btn btn-sm btn-success" @click="exportTreatments" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-download me-2"></i>
          {{ exporting ? 'Exporting...' : 'Export as CSV' }}
        </button>
      </div>
      <div class="card-body">
        <div v-if="history.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-clipboard-data fs-1 opacity-25 mb-3 d-block"></i>
          No treatment history found.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Date</th>
                <th>Doctor</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in history" :key="index">
                <td>{{ record.date }}</td>
                <td>{{ record.doctor }}</td>
                <td>{{ record.diagnosis }}</td>
                <td>{{ record.prescription }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeTab: 'appointments',
      appointments: [],
      history: [],
      exporting: false,
      taskId: null
    }
  },
  async mounted() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      const patientId = sessionStorage.getItem('patient_id');
      if (!patientId) {
        this.$router.push('/login/patient');
        return;
      }
      
      // Fetch appointments
      const appRes = await fetch(`http://localhost:5000/patient/appointments/${patientId}`);
      if (appRes.ok) this.appointments = await appRes.json();
      
      // Fetch history
      const histRes = await fetch(`http://localhost:5000/patient/history/${patientId}`);
      if (histRes.ok) this.history = await histRes.json();
    },
    async cancelAppointment(id) {
      if (!confirm('Are you sure you want to cancel this appointment?')) return;
      
      const res = await fetch(`http://localhost:5000/patient/appointments/${id}/cancel`, {
        method: 'PUT'
      });
      
      if (res.ok) {
        alert('Appointment cancelled successfully');
        await this.fetchData();
      } else {
        alert('Failed to cancel appointment');
      }
    },
    async exportTreatments() {
      const patientId = sessionStorage.getItem('patient_id');
      if (!patientId) return;
      
      this.exporting = true;
      
      try {
        // Trigger export job
        const res = await fetch(`http://localhost:5000/patient/export-treatments/${patientId}`, {
          method: 'POST'
        });
        
        if (!res.ok) {
          alert('Failed to start export');
          this.exporting = false;
          return;
        }
        
        const data = await res.json();
        this.taskId = data.task_id;
        
        // Poll for completion
        this.checkExportStatus();
        
      } catch (error) {
        alert('Error starting export: ' + error.message);
        this.exporting = false;
      }
    },
    async checkExportStatus() {
      if (!this.taskId) return;
      
      try {
        const res = await fetch(`http://localhost:5000/patient/export-status/${this.taskId}`);
        const data = await res.json();
        
        if (data.state === 'SUCCESS') {
          this.exporting = false;
          // Download the file
          const filename = data.result.filename;
          window.location.href = `http://localhost:5000/patient/download-export/${filename}`;
          alert(`Export complete! Downloaded ${data.result.record_count} records.`);
        } else if (data.state === 'FAILURE') {
          this.exporting = false;
          alert('Export failed: ' + data.status);
        } else {
          // Still processing, check again in 2 seconds
          setTimeout(() => this.checkExportStatus(), 2000);
        }
      } catch (error) {
        this.exporting = false;
        alert('Error checking export status: ' + error.message);
      }
    }
  }
}
</script>
