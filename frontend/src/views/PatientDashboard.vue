<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm mb-4 rounded">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">Patient Dashboard</span>
        <div class="d-flex gap-2 align-items-center flex-grow-1 mx-4">
          <!-- Search Bar -->
          <div class="input-group" style="max-width: 400px;">
            <span class="input-group-text bg-white border-end-0"><i class="bi bi-search"></i></span>
            <input 
              type="text" 
              class="form-control border-start-0" 
              placeholder="Search doctors by name or department..." 
              v-model="searchQuery"
              @input="performSearch"
            >
          </div>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary btn-sm" @click="$router.push('/patient/profile')">Edit Profile</button>
          <button class="btn btn-outline-info btn-sm" @click="$router.push('/patient/history')">My History</button>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Search Results -->
    <div v-if="view === 'search' && searchResults.length > 0" class="mb-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Search Results ({{ searchResults.length }})</h4>
        <button class="btn btn-sm btn-secondary" @click="clearSearch">Clear Search</button>
      </div>
      <div class="list-group">
        <div class="list-group-item d-flex justify-content-between align-items-center" v-for="doc in searchResults" :key="doc.id">
          <div>
            <h5 class="mb-1">{{ doc.name }}</h5>
            <small class="text-muted">{{ doc.specialization }} - {{ doc.department }}</small>
          </div>
          <button class="btn btn-primary btn-sm" @click="checkAvailability(doc)">Check Availability</button>
        </div>
      </div>
    </div>

    <!-- No Search Results -->
    <div v-if="view === 'search' && searchResults.length === 0 && searchQuery" class="text-center text-muted py-5">
      <i class="bi bi-search fs-1 opacity-25 mb-3 d-block"></i>
      No doctors found matching "{{ searchQuery }}"
    </div>

    <!-- Departments List -->
    <div v-if="view === 'departments'">
      <h4 class="mb-3">Select Department</h4>
      <div class="row" v-if="departments.length > 0">
        <div class="col-md-4 mb-3" v-for="dept in departments" :key="dept">
          <div class="card h-100 hover-card" @click="selectDepartment(dept)" style="cursor: pointer">
            <div class="card-body text-center p-4">
              <h5 class="card-title text-primary">{{ dept }}</h5>
              <button class="btn btn-sm btn-outline-primary mt-2">View Doctors</button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-muted py-5">
        <i class="bi bi-hospital fs-1 opacity-25 mb-3 d-block"></i>
        No departments found. Please contact admin to add doctors with departments.
      </div>
    </div>

    <!-- Doctors List -->
    <div v-if="view === 'doctors'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Doctors in {{ selectedDepartment }}</h4>
        <button class="btn btn-sm btn-secondary" @click="view = 'departments'">Back</button>
      </div>
      <div class="list-group">
        <div class="list-group-item d-flex justify-content-between align-items-center" v-for="doc in doctors" :key="doc.id">
          <div>
            <h5 class="mb-1">{{ doc.name }}</h5>
            <small class="text-muted">{{ doc.specialization }}</small>
          </div>
          <button class="btn btn-primary btn-sm" @click="checkAvailability(doc)">Check Availability</button>
        </div>
      </div>
    </div>

    <!-- Availability Slots (Grid View) -->
    <div v-if="view === 'slots'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4>Available Slots for {{ selectedDoctor.name }}</h4>
        <button class="btn btn-sm btn-secondary" @click="view = 'doctors'">Back</button>
      </div>

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
                  @click="bookSlot(day.dateStr, time)"
                  :disabled="!isSlotAvailable(day.dateStr, time)"
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
      </div>
    </div>

    <!-- Appointment Booking Modal -->
    <div v-if="showBookingModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Appointment</h5>
            <button type="button" class="btn-close" @click="cancelBooking"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <p class="mb-2"><strong>Doctor:</strong> {{ selectedDoctor?.name }}</p>
              <p class="mb-2"><strong>Specialization:</strong> {{ selectedDoctor?.specialization }}</p>
              <p class="mb-2"><strong>Date:</strong> {{ bookingDetails.date }}</p>
              <p class="mb-2"><strong>Time:</strong> {{ bookingDetails.time }}</p>
            </div>
            <hr>
            <form @submit.prevent="confirmBooking">
              <div class="mb-3">
                <label class="form-label">Reason for Appointment <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control" 
                  rows="4" 
                  v-model="bookingDetails.reason"
                  placeholder="Please describe your symptoms or reason for visit..."
                  required
                ></textarea>
                <small class="text-muted">This will help the doctor prepare for your consultation</small>
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-secondary flex-fill" @click="cancelBooking">Cancel</button>
                <button type="submit" class="btn btn-primary flex-fill">Confirm Booking</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      view: 'departments', // departments, doctors, slots, search
      departments: [],
      doctors: [],
      slots: [],
      selectedDepartment: '',
      selectedDoctor: null,
      searchQuery: '',
      searchResults: [],
      showBookingModal: false,
      bookingDetails: {
        slot: null,
        date: '',
        time: '',
        reason: ''
      },
      
      // Grid Data
      currentDate: new Date(),
      timeSlots: [
        '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'
      ]
    }
  },
  computed: {
    weekDates() {
      const dates = [];
      const start = new Date(this.currentDate);
      for (let i = 0; i < 5; i++) { // Show 5 days
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
    const res = await fetch('http://localhost:5000/patient/departments');
    this.departments = await res.json();
  },
  methods: {
    async selectDepartment(dept) {
      this.selectedDepartment = dept;
      const res = await fetch(`http://localhost:5000/patient/department/${dept}/doctors`);
      this.doctors = await res.json();
      this.view = 'doctors';
    },
    async checkAvailability(doc) {
      this.selectedDoctor = doc;
      const res = await fetch(`http://localhost:5000/patient/doctor/${doc.id}/availability`);
      this.slots = await res.json();
      this.view = 'slots';
    },
    
    // Grid Methods
    shiftWeek(days) {
      const newDate = new Date(this.currentDate);
      newDate.setDate(newDate.getDate() + (days * 5));
      this.currentDate = newDate;
    },
    getSlot(date, time) {
      return this.slots.find(s => s.date === date && s.start_time.startsWith(time));
    },
    getSlotClass(date, time) {
      const slot = this.getSlot(date, time);
      if (!slot) return 'btn-light border text-muted';
      if (slot.is_booked) return 'btn-danger text-white';
      return 'btn-success text-white';
    },
    isSlotAvailable(date, time) {
      const slot = this.getSlot(date, time);
      return slot && !slot.is_booked;
    },
    
    async bookSlot(date, time) {
      const slot = this.getSlot(date, time);
      if (!slot) return;
      
      const patientId = sessionStorage.getItem('patient_id');
      if (!patientId) {
        alert('Please login again');
        this.$router.push('/login/patient');
        return;
      }

      // Show booking modal with details
      this.bookingDetails = {
        slot: slot,
        date: date,
        time: time,
        reason: ''
      };
      this.showBookingModal = true;
    },

    async confirmBooking() {
      const patientId = sessionStorage.getItem('patient_id');
      
      const res = await fetch('http://localhost:5000/patient/book_slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          slot_id: this.bookingDetails.slot.id,
          patient_id: patientId,
          reason: this.bookingDetails.reason
        })
      });
      
      if (res.ok) {
        alert('Appointment booked successfully! You can view it in "My History".');
        this.showBookingModal = false;
        // Refresh the slots to show updated availability
        await this.checkAvailability(this.selectedDoctor);
      } else {
        const data = await res.json();
        alert(data.message || 'Booking failed');
      }
    },

    cancelBooking() {
      this.showBookingModal = false;
      this.bookingDetails = {
        slot: null,
        date: '',
        time: '',
        reason: ''
      };
    },
    
    async performSearch() {
      if (!this.searchQuery || this.searchQuery.trim().length < 2) {
        if (this.view === 'search') {
          this.view = 'departments';
        }
        this.searchResults = [];
        return;
      }

      const res = await fetch(`http://localhost:5000/patient/search?q=${encodeURIComponent(this.searchQuery)}`);
      if (res.ok) {
        this.searchResults = await res.json();
        this.view = 'search';
      }
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
      this.view = 'departments';
    },
    
    logout() {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user_id');
      sessionStorage.removeItem('role');
      sessionStorage.removeItem('patient_id');
      this.$router.push('/');
    }
  }
}
</script>
