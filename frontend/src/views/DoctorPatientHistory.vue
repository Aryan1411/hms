<template>
  <div>
    <nav class="navbar navbar-light bg-white shadow-sm mb-4 rounded">
      <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">Patient History - {{ patientName }}</span>
        <button class="btn btn-outline-secondary btn-sm" @click="$router.push('/doctor')">Back to Dashboard</button>
      </div>
    </nav>

    <div class="card">
      <div class="card-header bg-white">
        <h5 class="mb-0">Treatment History</h5>
      </div>
      <div class="card-body">
        <div v-if="history.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-clipboard-data fs-1 opacity-25 mb-3 d-block"></i>
          No treatment history found for this patient.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Date</th>
                <th>Doctor</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in history" :key="index">
                <td>{{ record.date }}</td>
                <td>{{ record.doctor }}</td>
                <td>{{ record.diagnosis }}</td>
                <td>{{ record.prescription }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="openEditModal(record)">
                    <i class="bi bi-pencil"></i> Edit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Treatment Modal -->
    <div v-if="showEditModal" class="modal d-block" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Treatment Record</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateTreatment">
              <div class="mb-3">
                <label class="form-label">Date</label>
                <input type="text" class="form-control" :value="editingRecord.date" disabled>
              </div>
              <div class="mb-3">
                <label class="form-label">Diagnosis <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="editingRecord.diagnosis"
                  required
                ></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription <span class="text-danger">*</span></label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="editingRecord.prescription"
                  required
                ></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea 
                  class="form-control" 
                  rows="2" 
                  v-model="editingRecord.notes"
                ></textarea>
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-secondary flex-fill" @click="closeEditModal">Cancel</button>
                <button type="submit" class="btn btn-primary flex-fill">Save Changes</button>
              </div>
            </form>
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
      history: [],
      patientName: '',
      showEditModal: false,
      editingRecord: {
        id: null,
        date: '',
        diagnosis: '',
        prescription: '',
        notes: ''
      }
    }
  },
  async mounted() {
    await this.loadHistory();
  },
  methods: {
    async loadHistory() {
      const patientId = this.$route.params.id;
      const res = await fetch(`${API_BASE_URL}/doctor/patient_history/${patientId}`);
      if (res.ok) {
        this.history = await res.json();
      }
      
      // Get patient name
      const doctorId = sessionStorage.getItem('doctor_id');
      const patientsRes = await fetch(`${API_BASE_URL}/doctor/assigned_patients/${doctorId}`);
      if (patientsRes.ok) {
        const patients = await patientsRes.json();
        const patient = patients.find(p => p.id == patientId);
        if (patient) this.patientName = patient.name;
      }
    },
    openEditModal(record) {
      this.editingRecord = { ...record };
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingRecord = {
        id: null,
        date: '',
        diagnosis: '',
        prescription: '',
        notes: ''
      };
    },
    async updateTreatment() {
      const res = await fetch(`${API_BASE_URL}/doctor/treatment/${this.editingRecord.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          diagnosis: this.editingRecord.diagnosis,
          prescription: this.editingRecord.prescription,
          notes: this.editingRecord.notes
        })
      });
      
      if (res.ok) {
        alert('Treatment record updated successfully!');
        this.closeEditModal();
        await this.loadHistory();
      } else {
        alert('Failed to update treatment record');
      }
    }
  }
}
</script>
