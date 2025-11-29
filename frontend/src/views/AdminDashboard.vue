<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-dark">Admin Dashboard</h2>
      <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
    </div>

    <!-- Search Bar -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0"><i class="bi bi-search"></i></span>
          <input type="text" class="form-control border-start-0" placeholder="Search doctors or patients..." v-model="searchQuery">
        </div>
      </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-white-50 mb-1">Total Doctors</h6>
                <h2 class="mb-0">{{ stats.totalDoctors }}</h2>
              </div>
              <i class="bi bi-person-badge fs-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-white-50 mb-1">Total Patients</h6>
                <h2 class="mb-0">{{ stats.totalPatients }}</h2>
              </div>
              <i class="bi bi-people fs-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-white-50 mb-1">Pending Appointments</h6>
                <h2 class="mb-0">{{ stats.pendingAppointments }}</h2>
              </div>
              <i class="bi bi-calendar-check fs-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-white-50 mb-1">Total Appointments</h6>
                <h2 class="mb-0">{{ stats.totalAppointments }}</h2>
              </div>
              <i class="bi bi-calendar3 fs-1 opacity-50"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctors and Patients -->
    <div class="row">
      <!-- Doctors List -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Doctors</h5>
            <button class="btn btn-sm btn-primary" @click="showAddDoctorModal = true">
              <i class="bi bi-plus-circle"></i> Add Doctor
            </button>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doc in filteredDoctors" :key="doc.id">
                    <td><small class="text-muted">#{{ doc.id }}</small></td>
                    <td>{{ doc.name }}</td>
                    <td><small class="text-muted">{{ doc.department }}</small></td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary me-1" @click="openEditDoctor(doc)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-dark me-1" @click="toggleBlacklist(doc.user_id, doc.is_blacklisted)">
                        <i :class="doc.is_blacklisted ? 'bi bi-slash-circle-fill text-danger' : 'bi bi-slash-circle'"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(doc.id)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Patients List -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Patients</h5>
            <button class="btn btn-sm btn-success" @click="showAddPatientModal = true">
              <i class="bi bi-plus-circle"></i> Add Patient
            </button>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Contact</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pat in filteredPatients" :key="pat.id">
                    <td><small class="text-muted">#{{ pat.id }}</small></td>
                    <td>{{ pat.name }}</td>
                    <td><small class="text-muted">{{ pat.contact || 'N/A' }}</small></td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary me-1" @click="openEditPatient(pat)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-dark me-1" @click="toggleBlacklist(pat.user_id, pat.is_blacklisted)">
                        <i :class="pat.is_blacklisted ? 'bi bi-slash-circle-fill text-danger' : 'bi bi-slash-circle'"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" @click="deletePatient(pat.id)">
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments Section -->
    <div class="row">
      <!-- Pending Appointments -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">Pending Appointments</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in pendingAppointments" :key="apt.id">
                    <td>{{ apt.patient }}</td>
                    <td>{{ apt.doctor }}</td>
                    <td>{{ apt.date }}</td>
                    <td>{{ apt.time }}</td>
                  </tr>
                  <tr v-if="pendingAppointments.length === 0">
                    <td colspan="4" class="text-center text-muted">No pending appointments</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Previous Appointments -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">Previous Appointments</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in previousAppointments" :key="apt.id">
                    <td>{{ apt.patient }}</td>
                    <td>{{ apt.doctor }}</td>
                    <td>{{ apt.date }}</td>
                    <td>
                      <span class="badge" :class="apt.status === 'Completed' ? 'bg-success' : 'bg-secondary'">
                        {{ apt.status }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="previousAppointments.length === 0">
                    <td colspan="4" class="text-center text-muted">No previous appointments</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showAddDoctorModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Doctor</h5>
            <button type="button" class="btn-close" @click="showAddDoctorModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addDoctor">
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Username" v-model="newDoctor.username" required>
              </div>
              <div class="mb-2">
                <input type="password" class="form-control" placeholder="Password" v-model="newDoctor.password" required>
              </div>
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Name" v-model="newDoctor.name" required>
              </div>
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Specialization" v-model="newDoctor.specialization" required>
              </div>
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Department" v-model="newDoctor.department" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Create</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddPatientModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Patient</h5>
            <button type="button" class="btn-close" @click="showAddPatientModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addPatient">
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Username" v-model="newPatient.username" required>
              </div>
              <div class="mb-2">
                <input type="email" class="form-control" placeholder="Email" v-model="newPatient.email" required>
              </div>
              <div class="mb-2">
                <input type="password" class="form-control" placeholder="Password" v-model="newPatient.password" required>
              </div>
              <div class="mb-2">
                <input type="text" class="form-control" placeholder="Name" v-model="newPatient.name" required>
              </div>
              <div class="mb-2">
                <input type="date" class="form-control" placeholder="Date of Birth" v-model="newPatient.dob">
              </div>
              <div class="mb-2">
                <input type="tel" class="form-control" placeholder="Contact Number" v-model="newPatient.contact">
              </div>
              <button type="submit" class="btn btn-success w-100">Create</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditDoctorModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Doctor</h5>
            <button type="button" class="btn-close" @click="showEditDoctorModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateDoctor">
              <div class="mb-2">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="editingDoctor.name" required>
              </div>
              <div class="mb-2">
                <label class="form-label">Specialization</label>
                <input type="text" class="form-control" v-model="editingDoctor.specialization" required>
              </div>
              <div class="mb-2">
                <label class="form-label">Department</label>
                <input type="text" class="form-control" v-model="editingDoctor.department" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Update</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditPatientModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Patient</h5>
            <button type="button" class="btn-close" @click="showEditPatientModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updatePatient">
              <div class="mb-2">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="editingPatient.name" required>
              </div>
              <div class="mb-2">
                <label class="form-label">Date of Birth</label>
                <input type="date" class="form-control" v-model="editingPatient.dob">
              </div>
              <div class="mb-2">
                <label class="form-label">Contact</label>
                <input type="text" class="form-control" v-model="editingPatient.contact">
              </div>
              <button type="submit" class="btn btn-primary w-100">Update</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Confirmation Modal -->
    <div v-if="confirmDialog.show" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Action</h5>
          </div>
          <div class="modal-body">
            <p>{{ confirmDialog.message }}</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="confirmDialog.show = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmAction">Confirm</button>
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
      doctors: [],
      patients: [],
      appointments: [],
      stats: {
        totalDoctors: 0,
        totalPatients: 0,
        pendingAppointments: 0,
        totalAppointments: 0
      },
      searchQuery: '',
      showAddDoctorModal: false,
      showAddPatientModal: false,
      showEditDoctorModal: false,
      showEditPatientModal: false,
      newDoctor: { username: '', password: '', name: '', specialization: '', department: '' },
      newPatient: {
        username: '',
        email: '',
        password: '',
        name: '',
        dob: '',
        contact: ''
      },
      editingDoctor: { id: null, name: '', specialization: '', department: '' },
      editingPatient: { id: null, name: '', dob: '', contact: '' },
      confirmDialog: {
        show: false,
        message: '',
        callback: null
      }
    }
  },
  computed: {
    filteredDoctors() {
      if (!this.searchQuery) return this.doctors;
      const query = this.searchQuery.toLowerCase();
      return this.doctors.filter(d => 
        d.name.toLowerCase().includes(query) ||
        d.department.toLowerCase().includes(query) ||
        d.id.toString().includes(query)
      );
    },
    filteredPatients() {
      if (!this.searchQuery) return this.patients;
      const query = this.searchQuery.toLowerCase();
      return this.patients.filter(p => 
        p.name.toLowerCase().includes(query) ||
        p.id.toString().includes(query) ||
        (p.contact && p.contact.toLowerCase().includes(query))
      );
    },
    pendingAppointments() {
      return this.appointments.filter(a => a.status === 'Booked');
    },
    previousAppointments() {
      return this.appointments.filter(a => a.status === 'Completed' || a.status === 'Cancelled');
    }
  },
  async mounted() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      const doctorsRes = await fetch('http://localhost:5000/admin/doctors');
      if (doctorsRes.ok) this.doctors = await doctorsRes.json();
      
      const patientsRes = await fetch('http://localhost:5000/admin/patients');
      if (patientsRes.ok) this.patients = await patientsRes.json();
      
      const appointmentsRes = await fetch('http://localhost:5000/admin/appointments');
      if (appointmentsRes.ok) this.appointments = await appointmentsRes.json();
      
      this.stats.totalDoctors = this.doctors.length;
      this.stats.totalPatients = this.patients.length;
      this.stats.pendingAppointments = this.appointments.filter(a => a.status === 'Booked').length;
      this.stats.totalAppointments = this.appointments.length;
    },
    async addDoctor() {
      const res = await fetch('http://localhost:5000/admin/doctors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.newDoctor)
      });
      if (res.ok) {
        alert('Doctor added');
        this.showAddDoctorModal = false;
        this.newDoctor = { username: '', password: '', name: '', specialization: '', department: '' };
        this.fetchData();
      } else {
        const error = await res.json();
        alert(`Error: ${error.message || 'Failed to add doctor'}`);
      }
    },
    async addPatient() {
      console.log('Attempting to add patient:', this.newPatient);
      try {
        const res = await fetch('http://localhost:5000/admin/patients', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newPatient)
        });
        if (res.ok) {
          alert('Patient added successfully');
          this.showAddPatientModal = false;
          this.newPatient = { email: '', password: '', name: '', dob: '', contact: '' };
          this.fetchData();
        } else {
          const error = await res.json();
          alert(`Error: ${error.message || 'Failed to add patient'}`);
        }
      } catch (e) {
        console.error('Error adding patient:', e);
        alert('Failed to connect to server. Please check console for details.');
      }
    },
    showConfirm(message, callback) {
      this.confirmDialog.message = message;
      this.confirmDialog.callback = callback;
      this.confirmDialog.show = true;
    },
    confirmAction() {
      this.confirmDialog.show = false;
      if (this.confirmDialog.callback) {
        this.confirmDialog.callback();
      }
    },
    async deleteDoctor(id) {
      this.showConfirm('Delete this doctor? This will also delete all their appointments.', async () => {
        const res = await fetch(`http://localhost:5000/admin/doctors/${id}`, { method: 'DELETE' });
        if (res.ok) {
          alert('Doctor deleted successfully');
          this.fetchData();
        } else {
          const error = await res.json();
          alert(`Error: ${error.message || 'Failed to delete doctor'}`);
        }
      });
    },
    async deletePatient(id) {
      this.showConfirm('Delete this patient? This will also delete all their appointments.', async () => {
        const res = await fetch(`http://localhost:5000/admin/patients/${id}`, { method: 'DELETE' });
        if (res.ok) {
          alert('Patient deleted successfully');
          this.fetchData();
        } else {
          const error = await res.json();
          alert(`Error: ${error.message || 'Failed to delete patient'}`);
        }
      });
    },
    async toggleBlacklist(userId, currentStatus) {
      const action = currentStatus ? 'Unblacklist' : 'Blacklist';
      this.showConfirm(`${action} this user?`, async () => {
        const res = await fetch(`http://localhost:5000/admin/blacklist/${userId}`, { method: 'PUT' });
        if (res.ok) {
          alert(`User ${action.toLowerCase()}ed successfully`);
          this.fetchData();
        } else {
          const error = await res.json();
          alert(`Error: ${error.message || 'Failed to toggle blacklist'}`);
        }
      });
    },
    openEditDoctor(doc) {
      this.editingDoctor = { ...doc };
      this.showEditDoctorModal = true;
    },
    async updateDoctor() {
      const res = await fetch(`http://localhost:5000/admin/doctors/${this.editingDoctor.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.editingDoctor)
      });
      if (res.ok) {
        alert('Doctor updated');
        this.showEditDoctorModal = false;
        this.fetchData();
      } else {
        alert('Update failed');
      }
    },
    openEditPatient(pat) {
      this.editingPatient = { ...pat };
      this.showEditPatientModal = true;
    },
    async updatePatient() {
      const res = await fetch(`http://localhost:5000/admin/patients/${this.editingPatient.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.editingPatient)
      });
      if (res.ok) {
        alert('Patient updated');
        this.showEditPatientModal = false;
        this.fetchData();
      } else {
        alert('Update failed');
      }
    },
    logout() {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user_id');
      sessionStorage.removeItem('role');
      this.$router.push('/');
    }
  }
}
</script>
