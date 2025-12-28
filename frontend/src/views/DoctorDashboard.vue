<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-dark">Doctor Dashboard</h2>
      <div>
        <button class="btn btn-outline-info btn-sm me-2" @click="generateMonthlyReport" :disabled="reportLoading">
          <i class="bi bi-file-earmark-text"></i> 
          {{ reportLoading ? 'Sending...' : 'Get Monthly Report' }}
        </button>
        <button class="btn btn-outline-primary btn-sm me-2" @click="showAvailabilityModal = true">Provide Availability</button>
        <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="card mb-4">
      <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
        <h5 class="fw-bold">Upcoming Appointments</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Patient</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in appointments" :key="app.id">
                <td>{{ app.patient }}</td>
                <td>{{ app.date }}</td>
                <td>{{ app.time }}</td>
                <td><small class="text-muted">{{ app.reason }}</small></td>
                <td class="text-end">
                  <button class="btn btn-sm btn-success me-1" @click="openTreatment(app)">
                    <i class="bi bi-clipboard-plus"></i> Treat
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(app.id)">
                    <i class="bi bi-x-circle"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Assigned Patients -->
    <div class="card mb-4">
      <div class="card-header bg-white border-bottom-0 pt-4 pb-0">
        <h5 class="fw-bold">Assigned Patients</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pat in assignedPatients" :key="pat.id">
                <td>{{ pat.name }}</td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-info" @click="viewPatientHistory(pat.id)">View History</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Treatment Modal -->
    <div v-if="selectedAppointment" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Treatment for {{ selectedAppointment.patient }}</h5>
            <button type="button" class="btn-close" @click="selectedAppointment = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <p><strong>Reason for visit:</strong> {{ selectedAppointment.reason }}</p>
            </div>
            <form @submit.prevent="submitTreatment">
              <div class="mb-3">
                <label class="form-label">Diagnosis</label>
                <textarea class="form-control" v-model="treatment.diagnosis" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea class="form-control" v-model="treatment.prescription" required></textarea>
              </div>
              <button type="submit" class="btn btn-primary w-100">Save Record</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Availability Modal (Grid View) -->
    <div v-if="showAvailabilityModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Manage Availability</h5>
            <button type="button" class="btn-close" @click="showAvailabilityModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="d-flex justify-content-between mb-3">
               <button class="btn btn-sm btn-outline-secondary" @click="shiftWeek(-1)">Previous</button>
               <span class="fw-bold">{{ dateRangeLabel }}</span>
               <button class="btn btn-sm btn-outline-secondary" @click="shiftWeek(1)">Next</button>
            </div>
            
            <div class="table-responsive">
              <table class="table table-bordered text-center">
                <thead>
                  <tr>
                    <th v-for="day in weekDates" :key="day.dateStr">{{ day.display }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="time in timeSlots" :key="time">
                    <td v-for="day in weekDates" :key="day.dateStr + time" class="p-1">
                      <button 
                        class="btn btn-sm w-100" 
                        :class="getSlotClass(day.dateStr, time)"
                        @click="toggleSlot(day.dateStr, time)"
                        :disabled="isSlotBooked(day.dateStr, time)"
                      >
                        {{ time }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="mt-3 small text-muted">
              <span class="badge bg-success me-1">Available</span>
              <span class="badge bg-danger me-1">Booked</span>
              <span class="badge bg-light text-dark border me-1">Not Scheduled</span>
              Click to toggle availability.
            </div>
          </div>
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
      appointments: [],
      assignedPatients: [],
      selectedAppointment: null,
      showAvailabilityModal: false,
      treatment: { diagnosis: '', prescription: '' },
      reportLoading: false,
      
      // Availability Grid Data
      currentDate: new Date(),
      existingSlots: [],
      timeSlots: [
        '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'
      ]
    }
  },
  computed: {
    weekDates() {
      const dates = [];
      const start = new Date(this.currentDate);
      for (let i = 0; i < 5; i++) {
        const d = new Date(start);
        d.setDate(start.getDate() + i);
        dates.push({
          dateStr: d.toISOString().split('T')[0],
          display: d.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' })
        });
      }
      return dates;
    },
    dateRangeLabel() {
      if (this.weekDates.length === 0) return '';
      return `${this.weekDates[0].display} - ${this.weekDates[this.weekDates.length-1].display}`;
    }
  },
  async mounted() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      const doctorId = sessionStorage.getItem('doctor_id');
      if (!doctorId) {
        alert('Doctor ID not found. Please login again.');
        this.$router.push('/login/doctor');
        return;
      }
      
      const appRes = await fetch(`${API_BASE_URL}/doctor/appointments/${doctorId}`); 
      if (appRes.ok) this.appointments = await appRes.json();
      
      const patRes = await fetch(`${API_BASE_URL}/doctor/assigned_patients/${doctorId}`);
      if (patRes.ok) this.assignedPatients = await patRes.json();
      
      const availRes = await fetch(`${API_BASE_URL}/patient/doctor/${doctorId}/availability`);
      if (availRes.ok) this.existingSlots = await availRes.json();
    },
    openTreatment(app) {
      this.selectedAppointment = app;
      this.treatment = { diagnosis: '', prescription: '' };
    },
    async submitTreatment() {
      const res = await fetch(API_BASE_URL + '/doctor/treatment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          appointment_id: this.selectedAppointment.id,
          diagnosis: this.treatment.diagnosis,
          prescription: this.treatment.prescription
        })
      });
      if (res.ok) {
        alert('Treatment record saved');
        this.selectedAppointment = null;
        this.fetchData();
      }
    },
    async cancelAppointment(id) {
      if (!confirm('Cancel this appointment?')) return;
      const res = await fetch(`${API_BASE_URL}/doctor/appointments/${id}/cancel`, { method: 'PUT' });
      if (res.ok) this.fetchData();
    },
    viewPatientHistory(id) {
      this.$router.push(`/doctor/patient-history/${id}`);
    },
    
    // Availability Grid Methods
    shiftWeek(days) {
      const newDate = new Date(this.currentDate);
      newDate.setDate(newDate.getDate() + (days * 5));
      this.currentDate = newDate;
    },
    getSlot(date, time) {
      return this.existingSlots.find(s => s.date === date && s.start_time.startsWith(time));
    },
    getSlotClass(date, time) {
      const slot = this.getSlot(date, time);
      if (!slot) return 'btn-light border';
      if (slot.is_booked) return 'btn-danger text-white';
      return 'btn-success text-white';
    },
    isSlotBooked(date, time) {
      const slot = this.getSlot(date, time);
      return slot && slot.is_booked;
    },
    async toggleSlot(date, time) {
      const slot = this.getSlot(date, time);
      if (slot) {
        // Slot exists - remove it (only if not booked)
        if (slot.is_booked) {
          alert('Cannot remove a booked slot. Cancel the appointment first.');
          return;
        }
        
        if (!confirm('Remove this availability slot?')) return;
        
        const doctorId = sessionStorage.getItem('doctor_id');
        const res = await fetch(`${API_BASE_URL}/doctor/availability/${doctorId}/${date}/${time}`, {
          method: 'DELETE'
        });
        
        if (res.ok) {
          this.fetchData();
        } else {
          const data = await res.json();
          alert(data.message || 'Failed to remove slot');
        }
      } else {
        // Slot doesn't exist - add it
        let [h, m] = time.split(':').map(Number);
        let endH = h + 1;
        let endTimeStr = `${endH.toString().padStart(2, '0')}:00`;

        const doctorId = sessionStorage.getItem('doctor_id');
        const res = await fetch(API_BASE_URL + '/doctor/availability', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            doctor_id: doctorId,
            date: date,
            start_time: time,
            end_time: endTimeStr
          })
        });
        if (res.ok) {
          this.fetchData();
        }
      }
    },
    async generateMonthlyReport() {
      const doctorId = sessionStorage.getItem('doctor_id');
      if (!doctorId) {
        alert('Doctor ID not found. Please login again.');
        return;
      }
      
      this.reportLoading = true;
      try {
        const res = await fetch(`${API_BASE_URL}/doctor/monthly-report/${doctorId}`, {
          method: 'POST'
        });
        
        const data = await res.json();
        
        if (res.ok) {
          if (data.status === 'info') {
            alert(data.message);
          } else {
            alert(`✅ ${data.message}\n\nStats:\n- Total: ${data.stats.total}\n- Completed: ${data.stats.completed}\n- Cancelled: ${data.stats.cancelled}\n- Month: ${data.stats.month}`);
          }
        } else {
          alert(`Error: ${data.message}`);
        }
      } catch (error) {
        alert('Failed to generate report. Please try again.');
        console.error('Error:', error);
      } finally {
        this.reportLoading = false;
      }
    },
    logout() {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user_id');
      sessionStorage.removeItem('role');
      sessionStorage.removeItem('doctor_id');
      this.$router.push('/');
    }
  }
}
</script>
