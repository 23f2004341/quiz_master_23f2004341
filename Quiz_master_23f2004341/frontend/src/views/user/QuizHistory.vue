<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Quiz History</h2>
      <div class="d-flex gap-2">
        <button class="btn btn-success" @click="exportCSV" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ exporting ? exportStatus : 'Export CSV' }}
        </button>
        <button class="btn btn-outline-primary" @click="exportDirect" :disabled="exporting">
          Export Direct
        </button>
      </div>
    </div>
    
    <!-- Export Progress -->
    <div v-if="exporting" class="alert alert-info">
      <div class="d-flex align-items-center">
        <div class="spinner-border spinner-border-sm me-2" role="status"></div>
        <span>{{ exportStatus }}</span>
      </div>
      <div v-if="progressMessage" class="mt-2 small">{{ progressMessage }}</div>
    </div>
    
    <!-- Success Message -->
    <div v-if="showSuccess" class="alert alert-success alert-dismissible fade show" role="alert">
      <strong>Success!</strong> {{ successMessage }}
      <button type="button" class="btn-close" @click="showSuccess = false"></button>
    </div>
    
    <!-- Error Message -->
    <div v-if="showError" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error!</strong> {{ errorMessage }}
      <button type="button" class="btn-close" @click="showError = false"></button>
    </div>
    
    <div class="card shadow-sm">
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Your Quiz Attempts</h5>
      </div>
      <div class="card-body">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Quiz ID</th>
              <th>Chapter</th>
              <th>Subject</th>
              <th>Date</th>
              <th>Score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in history" :key="q.id">
              <td><strong>{{ q.quiz_id }}</strong></td>
              <td>{{ getChapterName(q.quiz_id) }}</td>
              <td>{{ getSubjectName(q.quiz_id) }}</td>
              <td>{{ formatDate(q.timestamp) }}</td>
              <td>
                <span class="badge" :class="getScoreClass(q.total_score)">
                  {{ q.total_score }}
                </span>
              </td>
              <td>
                <span class="badge bg-success">Completed</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  data() {
    return {
      history: [],
      chapters: [],
      subjects: [],
      quizzes: [],
      exporting: false,
      exportStatus: 'Exporting...',
      progressMessage: '',
      showSuccess: false,
      showError: false,
      successMessage: '',
      errorMessage: ''
    };
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      try {
        const [historyRes, chaptersRes, subjectsRes, quizzesRes] = await Promise.all([
          axios.get('/api/user/quiz_history'),
          axios.get('/api/chapters'),
          axios.get('/api/subjects'),
          axios.get('/api/quizzes')
        ]);
        
        this.history = historyRes.data.history;
        this.chapters = chaptersRes.data.chapters;
        this.subjects = subjectsRes.data.subjects;
        this.quizzes = quizzesRes.data.quizzes;
      } catch (error) {
        this.showErrorMessage('Failed to load quiz history');
      }
    },
    
    async exportCSV() {
      this.exporting = true;
      this.exportStatus = 'Starting export...';
      this.progressMessage = 'Preparing your quiz history data...';
      this.hideMessages();
      
      try {
        const res = await axios.post('/api/user/export_quiz_history', {});
        const taskId = res.data.task_id;
        this.exportStatus = 'Processing...';
        this.progressMessage = 'Generating CSV file with complete quiz details...';
        this.pollDownload(taskId);
      } catch (error) {
        this.exporting = false;
        this.showErrorMessage('Failed to start export');
      }
    },
    
    async exportDirect() {
      this.exporting = true;
      this.exportStatus = 'Exporting directly...';
      this.progressMessage = 'Generating CSV file...';
      this.hideMessages();
      
      try {
        const response = await axios.get('/api/user/export_quiz_history_direct', {
          responseType: 'blob'
        });
        
        // Download the file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'quiz_history.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.exporting = false;
        this.showSuccessMessage('CSV exported successfully! Check your email for notification.');
      } catch (error) {
        this.exporting = false;
        this.showErrorMessage('Direct export failed');
      }
    },
    
    async pollDownload(taskId) {
      let tries = 0;
      const maxTries = 30;
      
      const poll = async () => {
        tries++;
        if (tries > maxTries) {
          this.exporting = false;
          this.showErrorMessage('Export timed out. Please try again.');
          return;
        }
        
        try {
          const res = await axios.get(`/api/user/download_quiz_history/${taskId}`, { 
            responseType: 'blob', 
            validateStatus: s => true 
          });
          
          if (res.status === 202) {
            this.progressMessage = `Processing... (${tries}/${maxTries})`;
            setTimeout(poll, 2000);
          } else if (res.status === 200) {
            // Download the file
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'quiz_history.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.exporting = false;
            this.showSuccessMessage('CSV exported successfully! Check your email for notification.');
          } else {
            this.exporting = false;
            this.showErrorMessage('Export failed');
          }
        } catch (e) {
          this.exporting = false;
          this.showErrorMessage('Export failed');
        }
      };
      
      poll();
    },
    
    getChapterName(quizId) {
      const quiz = this.quizzes.find(q => q.id === quizId);
      if (!quiz) return 'Unknown';
      
      const chapter = this.chapters.find(c => c.id === quiz.chapter_id);
      return chapter ? chapter.name : 'Unknown';
    },
    
    getSubjectName(quizId) {
      const quiz = this.quizzes.find(q => q.id === quizId);
      if (!quiz) return 'Unknown';
      
      const chapter = this.chapters.find(c => c.id === quiz.chapter_id);
      if (!chapter) return 'Unknown';
      
      const subject = this.subjects.find(s => s.id === chapter.subject_id);
      return subject ? subject.name : 'Unknown';
    },
    
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getScoreClass(score) {
      if (score >= 90) return 'bg-success';
      if (score >= 80) return 'bg-info';
      if (score >= 70) return 'bg-warning';
      return 'bg-danger';
    },
    
    showSuccessMessage(message) {
      this.successMessage = message;
      this.showSuccess = true;
      setTimeout(() => this.showSuccess = false, 5000);
    },
    
    showErrorMessage(message) {
      this.errorMessage = message;
      this.showError = true;
      setTimeout(() => this.showError = false, 5000);
    },
    
    hideMessages() {
      this.showSuccess = false;
      this.showError = false;
    }
  }
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.08);
}

.table {
  margin-bottom: 0;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.badge {
  font-size: 0.9em;
  padding: 0.5em 0.8em;
}

.alert {
  border-radius: 0.75rem;
  border: none;
}

.btn {
  border-radius: 0.5rem;
  font-weight: 500;
}

.btn-success {
  background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
  border: none;
}

.btn-outline-primary {
  border-color: #007bff;
  color: #007bff;
}

.btn-outline-primary:hover {
  background: #007bff;
  border-color: #007bff;
}
</style>
